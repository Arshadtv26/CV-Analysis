import os
import pytesseract
import time
import json
import docx
from pdf2image import convert_from_path
from openai import OpenAI, OpenAIError
from fastapi import FastAPI, File, UploadFile, WebSocket, HTTPException
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI()

cv_database = []  # In-memory storage for extracted CV data


def extract_text_from_pdf(pdf_path):
    pages = convert_from_path(pdf_path)
    text = ""
    for page in pages:
        text += pytesseract.image_to_string(page) + "\n"
    return text


def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])


def call_llm_with_retry(prompt, max_retries=3, delay=2):
    """Handles API rate limiting and errors with retries."""
    client = OpenAI(api_key=OPENAI_API_KEY)
    for attempt in range(max_retries):
        try:
            response = client.Completion.create(
                engine="gpt-4",
                prompt=prompt,
                max_tokens=500
            )
            return json.loads(response.choices[0].text.strip())
        except OpenAIError as e:
            if attempt < max_retries - 1:
                time.sleep(delay * (2 ** attempt))  # Exponential backoff
            else:
                raise HTTPException(status_code=500, detail=f"LLM API Error: {str(e)}")


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    filepath = f"uploads/{file.filename}"
    with open(filepath, "wb") as buffer:
        buffer.write(await file.read())

    if file.filename.endswith(".pdf"):
        extracted_text = extract_text_from_pdf(filepath)
    elif file.filename.endswith(".docx"):
        extracted_text = extract_text_from_docx(filepath)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    structured_data = call_llm_with_retry(
        f"Extract personal info, education, work experience, skills, projects, and certifications from the following CV:\n{extracted_text}"
    )
    cv_database.append(structured_data)

    return {"message": "CV processed successfully", "cv_id": len(cv_database) - 1}


@app.websocket("/query/")
async def query_chatbot(websocket: WebSocket):
    await websocket.accept()
    context = []
    while True:
        query = await websocket.receive_text()
        context.append(query)

        prompt = f"Based on the following CV database, answer the query:\n{json.dumps(cv_database)}\nUser Query: {query}\n"
        answer = call_llm_with_retry(prompt)

        await websocket.send_text(answer)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
