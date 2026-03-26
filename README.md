# PromptiTron

![PromptiTron Hero Screenshot](screenshots/Screenshot_1.jpg)

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

## Visual Overview & Screenshots

[Open the visual overview PDF](https://github.com/giraydorukyurt7/PromptiTron/blob/main/screenshots/PromptiTron_Visual_Overview.pdf)

| | | |
| :---: | :---: | :---: |
| ![1](screenshots/Screenshot_1.jpg) | ![2](screenshots/Screenshot_2.jpg) | ![3](screenshots/Screenshot_3.jpg) |
| ![4](screenshots/Screenshot_4.jpg) | ![5](screenshots/Screenshot_5.jpg) | ![6](screenshots/Screenshot_6.jpg) |
| ![7](screenshots/Screenshot_7.jpg) | ![8](screenshots/Screenshot_8.jpg) | ![9](screenshots/Screenshot_9.jpg) |
| ![10](screenshots/Screenshot_10.jpg) | ![11](screenshots/Screenshot_11.jpg) | ![12](screenshots/Screenshot_12.jpg) |
| ![13](screenshots/Screenshot_13.jpg) | ![14](screenshots/Screenshot_14.jpg) | ![15](screenshots/Screenshot_15.jpg) |
| ![16](screenshots/Screenshot_16.jpg) | ![17](screenshots/Screenshot_17.jpg) | ![18](screenshots/Screenshot_18.jpg) |
| ![19](screenshots/Screenshot_19.jpg) | ![20](screenshots/Screenshot_20.jpg) | ![21](screenshots/Screenshot_21.jpg) |
| ![22](screenshots/Screenshot_22.jpg) | ![23](screenshots/Screenshot_23.jpg) | ![24](screenshots/Screenshot_24.jpg) |

## System Architecture

```mermaid
flowchart TB
    User[👤 Student] --> UI[🖥️ Web UI]

    subgraph Frontend["📱 Frontend Layer"]
        UI --> Pages[📄 Pages]
        Pages --> Components[🧩 Components]
        Components --> Hooks[🔗 API Hooks]
    end

    Hooks --> API[🌐 FastAPI]

    subgraph APILayer["🔧 API Layer"]
        API --> Routers[📍 Routers]
        Routers --> Controllers[⚙️ Controllers]
    end

    Controllers --> AICore[🤖 AI Core]

    subgraph AISystem["🧠 AI System"]
        AICore --> Gemini[✨ Gemini 2.5]
        AICore --> Agents[👨‍🏫 Experts]
        AICore --> Memory[💭 Memory]
    end

    AICore --> RAG[🔍 RAG Engine]

    subgraph RAGSystem["🔍 RAG System"]
        RAG --> ChromaDB[(📊 ChromaDB)]
        RAG --> Search[🔍 Search]
        RAG --> Embeddings[🔢 Embeddings]
    end

    subgraph DataLayer["💾 Data Layer"]
        JSON[(📚 JSON Files)]
        SQLite[(🗄️ SQLite DB)]
        Uploads[(📁 File Storage)]
    end

    subgraph External["🌍 External APIs"]
        GoogleAPI[🔮 Google API]
        YouTubeAPI[🎥 YouTube API]
    end

    ChromaDB --> JSON
    Memory --> SQLite
    Controllers --> Uploads
    Gemini --> GoogleAPI
    AICore --> YouTubeAPI
```

## Data Flow

```mermaid
flowchart TD
    User[👤 User] --> InputType{🎯 Input Type}

    InputType -->|Chat| ChatFlow[💬 Chat]
    InputType -->|Questions| QuestionFlow[❓ Questions]
    InputType -->|File| FileFlow[📄 File]
    InputType -->|YouTube| YouTubeFlow[🎥 YouTube]
    InputType -->|Curriculum| CurriculumFlow[📚 Curriculum]

    ChatFlow --> Validate1[✅ Validation]
    QuestionFlow --> Validate2[✅ Validation]
    FileFlow --> Validate3[✅ Validation]
    YouTubeFlow --> Validate4[✅ Validation]
    CurriculumFlow --> Validate5[✅ Validation]

    Validate1 --> Process1[⚙️ Processing]
    Validate2 --> Process2[⚙️ Processing]
    Validate3 --> Process3[⚙️ Processing]
    Validate4 --> Process4[⚙️ Processing]
    Validate5 --> Process5[⚙️ Processing]

    Process1 --> Context[🔧 Context Builder]
    Process2 --> Context
    Process3 --> Context
    Process4 --> Context
    Process5 --> Context

    Context --> RAGCheck{🔍 RAG Needed?}

    RAGCheck -->|Yes| RAGSystem[🔍 RAG System]
    RAGCheck -->|No| AgentRouter[🤖 Agent Router]

    RAGSystem --> VectorSearch[🔢 Vector Search]
    VectorSearch --> ChromaDB[(📊 ChromaDB)]
    ChromaDB --> ContextAugment[➕ Context Enrichment]

    ContextAugment --> AgentRouter
    AgentRouter --> ExpertSelect{👨‍🏫 Expert Selection}

    ExpertSelect -->|Math| MathExpert[📐 Mathematics]
    ExpertSelect -->|Physics| PhysicsExpert[⚛️ Physics]
    ExpertSelect -->|Chemistry| ChemExpert[🧪 Chemistry]
    ExpertSelect -->|Biology| BioExpert[🧬 Biology]
    ExpertSelect -->|General| GeneralExpert[🎓 General]

    MathExpert --> LLMProcess[🤖 LLM Processing]
    PhysicsExpert --> LLMProcess
    ChemExpert --> LLMProcess
    BioExpert --> LLMProcess
    GeneralExpert --> LLMProcess

    LLMProcess --> GeminiAPI[✨ Gemini API]
    GeminiAPI --> ResponseGen[📝 Response Generation]

    ResponseGen --> ResponseVal[✅ Response Validation]
    ResponseVal --> MemoryUpdate[💭 Memory Update]

    MemoryUpdate --> FinalOutput[📤 Output]
    FinalOutput --> User

    Validate1 -->|Error| ErrorHandler[❌ Error]
    Validate2 -->|Error| ErrorHandler
    Validate3 -->|Error| ErrorHandler
    Validate4 -->|Error| ErrorHandler
    Validate5 -->|Error| ErrorHandler
    GeminiAPI -->|API Error| ErrorHandler

    ErrorHandler --> ErrorResponse[⚠️ Error Response]
    ErrorResponse --> User
```

## Input / Output Processes

```mermaid
flowchart LR
    subgraph Inputs["📥 INPUTS"]
        Chat[💬 Chat Message]
        Questions[❓ Question Parameters]
        Files[📄 File Upload]
        YouTube[🎥 YouTube URL]
        Curriculum[📚 Curriculum Selection]
    end

    subgraph Processing["⚙️ PROCESSING"]
        Validate[✅ Validation]
        Context[🔧 Context Building]
        RAG[🔍 RAG Search]
        Agent[🤖 Agent Selection]
        LLM[✨ LLM Processing]
    end

    subgraph Outputs["📤 OUTPUTS"]
        ChatResp[💬 Chat Response]
        QuestList[❓ Question List]
        Analysis[📊 Content Analysis]
        VideoSum[🎥 Video Summary]
        CurriculumOut[📚 Curriculum Output]
    end

    Chat --> Validate
    Questions --> Validate
    Files --> Validate
    YouTube --> Validate
    Curriculum --> Validate

    Validate --> Context
    Context --> RAG
    RAG --> Agent
    Agent --> LLM

    LLM --> ChatResp
    LLM --> QuestList
    LLM --> Analysis
    LLM --> VideoSum
    LLM --> CurriculumOut
```

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
├── screenshots/          # Product screenshots and visual overview files
├── README.md
├── README-Docker.md
└── README-Dokploy.md
```

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/giraydorukyurt7/PromptiTron.git
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

## System Diagrams

Additional diagram files are available in the [diagrams](./diagrams) directory.

## Related Documentation

- [Docker Deployment Guide](./README-Docker.md)
- [Dokploy Deployment Guide](./README-Dokploy.md)
- [Frontend README](https://github.com/giraydorukyurt7/PromptiTron/blob/main/client/README.md)
- [Visual Overview PDF](https://github.com/giraydorukyurt7/PromptiTron/blob/main/screenshots/PromptiTron_Visual_Overview.pdf)

## Notes

- This repository is intended as a practical showcase of a multi-interface AI education system.
- The strongest parts of the project are the RAG workflow, backend orchestration, and curriculum-aware educational features.
- Deployment-specific details are intentionally separated into dedicated README files to keep this main document concise.
