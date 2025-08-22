# Resume–Job Fit Analyzer (Starter)

End-to-end NLP project to score a resume against a job description with explainability. Built for AI/ML campus placements.

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run Streamlit demo
streamlit run demo_streamlit.py

# Run FastAPI
uvicorn app:app --reload
```

## Features
- Parse resume/JD (txt/pdf/docx)
- Extract skills via dictionary + aliases + fuzzy/semantic fallback
- Score = skill coverage + semantic similarity + experience alignment
- Explainability: matched/missing/near-miss skills with reasons
- Streamlit UI + FastAPI backend + Dockerfile

## Repo Layout
```
src/                # core logic
data/sample/        # sample resume/JD
demo_streamlit.py   # UI for quick demo
app.py              # FastAPI service
tests/              # pytest smoke tests
docker/Dockerfile   # container
```

## Notes
- Sentence-transformers is optional; TF-IDF fallback works offline.
- Update `src/skills_db.json` with new skills/aliases as you grow the ontology.