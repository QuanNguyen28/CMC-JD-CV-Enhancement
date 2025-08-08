# JD & CV Enhancement System

This project is an AI-powered system designed to enhance job descriptions (JDs) and resumes (CVs), enabling companies to streamline recruitment and helping candidates tailor their profiles for specific roles. It uses state-of-the-art NLP techniques, a Retrieval-Augmented Generation (RAG) backend, and modular services to offer intelligent suggestions and semantic search capabilities.

## Features

- **JD Generator**: Automatically generate or improve job descriptions based on role, skills, and industry best practices.
- **CV Enhancer**: Enhance candidate CVs to match target job descriptions using inferred skill gaps and semantic alignment.
- **Semantic Search API**: Match JDs and CVs through intelligent embeddings and vector search.
- **Version Control**: Track history of generated JDs or CVs for audit and iteration.
- **Admin Controls & Access Management**: Role-based access and visibility tailored to recruiters, candidates, or admins.

## Tech Stack

- **Backend**: FastAPI, Python
- **Frontend**: React (planned)
- **Embedding Model**: SentenceTransformers (e.g., `text-embedding-004`)
- **Vector Store**: Milvus
- **Object Store**: MinIO
- **Database**: PostgreSQL
- **Authentication**: JWT-based with role context (Admin, Candidate, Recruiter)
- **Deployment**: Docker, Uvicorn, Nginx

## Folder Structure

```
jd_service/
├── src/
│   ├── main.py                 # Entry-point for FastAPI
│   ├── api/                    # API routers
│   │   └── v1/
│   │       ├── jd.py           # JD-related endpoints
│   │       └── interview.py    # Interview enhancement endpoints
│   ├── services/               # Core logic
│   ├── models/                 # Pydantic models
│   ├── db/                     # Database layer
│   └── utils/                  # Utility functions
├── tests/                      # Unit tests
├── Dockerfile
├── requirements.txt
└── .env.example
```

## Setup Instructions

1. **Clone the repository**
   ```
   git clone https://github.com/QuanNguyen28/CMC-JD-CV-Enhancement.git
   cd jd-cv-enhancement
   ```

2. **Set up Python environment**
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   - Copy `.env.example` to `.env` and fill in values.

4. **Run the app**
   ```
   uvicorn src.main:app --reload
   ```

## Future Plans

- Integration with LinkedIn/Coursera APIs for course recommendations.
- Skill graph visualization.
- Admin dashboard for analytics and feedback.

## Contact

For feedback, reach out to `quanhoangnguyen28@gmail.com`.

---
© 2025 CMC | JD & CV Enhancement Team
