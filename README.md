# Cred Saathi

## This is a banking related, AI-agentic loan approval app

### Techs Used:
1. Next.js
2. Tailwind CSS

### Getting Started:

**Frontend**
On your terminal, run the following commands:
```bash
npm i

npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

**Backend**
- create a .env folder inside backend, and generate your groq api key and store it as GROQ_API_KEY=your_key
- Go to data/dummy-servers inside backend and run `python fastapi_server.py`
- `python main.py` in the backend

Sample request in curl - 
`curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"phone\": \"+917835414968\", \"message\": \"Hi, I need a loan\"}"`



## About Us:
Team – SyntaxErr<br>
Project – Cred Saathi<br>
Hriddhiman – Frontend(Next.js), UI/UX<br>
Shorya – presentation, logo, AI agents<br>
Shreejan – AI agents<br>
Yasin – Backend , AI agent integration , database<br>
