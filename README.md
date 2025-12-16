# Cred Saathi

## This is a banking related, AI-agentic loan approval app

### Techs Used:
1. Next.js
2. Tailwind CSS

### Getting Started:

From the `frontend` directory, run:
```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

**Dummy Server (Prompt Demo)**

A small Express server is available to accept user prompts from the frontend and return a demo response.

The server listens on [http://localhost:4000](http://localhost:4000).

- Healthcheck: `GET /health`
- Prompt endpoint: `POST /prompt` with JSON body `{ "prompt": "your text" }`

**Backend**
- create a .env folder inside backend, and generate your groq api key and store it as GROQ_API_KEY=your_key
- Go to data/dummy-servers inside backend and run `python fastapi_server.py`
- `python main.py` in the backend

Sample request in curl - 
`curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"phone\": \"+917835414968\", \"message\": \"Hi, I need a loan\"}"`

Request loan amount (Sales Agent) - 
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+917835414968", 
    "message": "I need 2 lakhs for 24 months",
    "session_id": "YOUR_SESSION_ID_FROM_STEP_2a"
  }'
```

 Proceed with verification - 
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+917835414968", 
    "message": "Yes, proceed",
    "session_id": "YOUR_SESSION_ID"
  }'
```

To check session id -
`curl http://localhost:8000/session/YOUR_SESSION_ID/status`

To upload salary slip - 
`curl -X POST http://localhost:8000/upload-salary-slip/{session_id} -F "file=@sample_salary_slip.pdf"`

Downloading sanction letter - 
`curl http://localhost:8000/download-sanction-letter/YOUR_SESSION_ID --output sanction_letter.pdf`



## About Us:
Team – SyntaxErr<br>
Project – Cred Saathi<br>
Hriddhiman – Frontend(Next.js), UI/UX<br>
Shorya – presentation, logo, AI agents<br>
Shreejan – AI agents<br>
Yasin – Backend , AI agent integration , database<br>