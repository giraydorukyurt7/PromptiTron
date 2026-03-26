# PromptiTron

PromptiTron is a curriculum-aware educational assistant that combines Retrieval-Augmented Generation (RAG), LLM-based workflows, and multiple user interfaces for learning support.

The project is designed as a practical AI education system with support for:

- curriculum-aware question generation
- summarization and explanation workflows
- retrieval over educational content
- document / web / YouTube-based content analysis
- multiple interfaces including console, API, and web UI

## Overview

PromptiTron brings together several components into a single system:

- **Console application** for terminal-based interaction
- **FastAPI backend** for API access and service orchestration
- **Next.js frontend** for web-based usage
- **ChromaDB-based RAG layer** for retrieval and knowledge grounding
- **Google Gemini integration** for generation and reasoning workflows

This repository should be viewed as a multi-interface educational assistant project rather than a single-page chatbot demo.

## Core Features

- Curriculum-aware educational assistance
- Question generation for selected topics
- Summarization and knowledge-assisted responses
- Retrieval-Augmented Generation (RAG) with ChromaDB
- Content analysis for documents, websites, and YouTube resources
- Multi-interface usage through console, API, and web UI
- Docker-ready deployment structure

## Architecture

### Backend
- Python
- FastAPI
- Pydantic
- ChromaDB
- LangChain / LangGraph
- Google Gemini integration

### Frontend
- Next.js
- React
- TypeScript
- Tailwind CSS
- shadcn/ui

### Interfaces
- Console app
- REST API
- Web frontend

## Project Structure

```text
PromptiTron/
├── api/                  # FastAPI backend
├── client/               # Next.js frontend
├── core/                 # Core AI / RAG logic
├── console_app_modules/  # Console app modules
├── data/                 # Curriculum and supporting data
├── chroma_db/            # Vector database persistence
├── scripts/              # Utility scripts
├── diagrams/             # Diagrams and architecture visuals
├── README.md
├── README-Docker.md
└── README-Dokploy.md
```

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/your-username/PromptiTron.git
cd PromptiTron
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

**Windows**
```bash
venv\Scripts\activate
```

**Linux / macOS**
```bash
source venv/bin/activate
```

### 3. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key_here
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development
```

Add any additional variables required by your local setup.

### 5. Run the API

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

API docs will be available at:

```text
http://localhost:8000/docs
```

### 6. Run the frontend

```bash
cd client
npm install
npm run dev
```

Frontend will be available at:

```text
http://localhost:3000
```

## Optional Console Mode

If you want to run the console-oriented interface, use the appropriate entry point available in the repository, such as:

```bash
python main.py
```

or

```bash
python console_app.py
```

Use whichever matches your current repository structure and startup flow.

## Environment Variables

Typical variables used in local development include:

```env
GOOGLE_API_KEY=your_google_api_key_here
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development
CHROMA_HOST=localhost
CHROMA_PORT=8000
```

Frontend example (`client/.env.local`):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Related Documentation

- [Docker Deployment Guide](./README-Docker.md)
- [Dokploy Deployment Guide](./README-Dokploy.md)
- [Frontend README](./client/README.md)

## Notes

- This repository is intended as a practical showcase of a multi-interface AI education system.
- The strongest parts of the project are the RAG workflow, backend orchestration, and curriculum-aware educational features.
- Deployment-specific details are intentionally separated into dedicated README files to keep this main document concise.
