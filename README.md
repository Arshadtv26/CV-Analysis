# CV-Analysis
A CV analysis system that can process multiple CV documents (PDF), extract information using OCR, and provide a chatbot interface for querying the extracted information



# CV Analysis System
This project processes CV documents using OCR, extracts key details using an LLM API, and provides a chatbot interface for querying CV data.

## Setup
1.Install dependencies:
```bash
pip install - r requirements.txt
```
2.Setenvironmentvariables in `.env` file.
3.Run the FastAPInserver:
```bash
uvicorn main: app - -host 0.0.0.0 - -port 8000
```
4.Use WebSocket at ` / query / ` to interact with extracted CVs.
