from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
from src.parse_resume import extract_skills, normalize
from src.scoring import score
import json
from pathlib import Path

class AnalyzeRequest(BaseModel):
    resume_text: str
    jd_text: str

app = FastAPI(title="Resume-JobFit API")

# Load skills DB at startup
_SKILLS_DB = json.loads(Path("src/skills_db.json").read_text(encoding="utf-8"))

def _canonicalize(skills):
    return sorted(set(skills))

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    resume_norm = normalize(req.resume_text)
    jd_norm = normalize(req.jd_text)

    resume_skills, _ = extract_skills(resume_norm, _SKILLS_DB)
    jd_skills, _ = extract_skills(jd_norm, _SKILLS_DB)

    sc = score(resume_norm, jd_norm, resume_skills, jd_skills)
    return {
        "resume_skills": _canonicalize(resume_skills),
        "jd_skills": _canonicalize(jd_skills),
        "result": sc,
        "missing_skills": [s for s in jd_skills if s not in resume_skills],
        "matched_skills": [s for s in jd_skills if s in resume_skills],
    }