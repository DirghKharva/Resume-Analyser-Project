from typing import Dict, List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .parse_resume import normalize, extract_years_experience
from .parse_jd import split_sections
from . import config

# optional sentence-transformers
_ST_MODEL = None
def _load_st_model(name: str):
    global _ST_MODEL
    if _ST_MODEL is not None:
        return _ST_MODEL
    try:
        from sentence_transformers import SentenceTransformer
        _ST_MODEL = SentenceTransformer(name)
    except Exception:
        _ST_MODEL = None
    return _ST_MODEL


def _semantic_similarity(a: str, b: str) -> float:
    a = a.strip()
    b = b.strip()
    if len(a) < config.SIMILARITY_MIN_SENT_LEN or len(b) < config.SIMILARITY_MIN_SENT_LEN:
        return 0.0
    model = _load_st_model(config.SIMILARITY_MODEL)
    if model is not None:
        try:
            va, vb = model.encode([a, b])
            sim = float(cosine_similarity([va], [vb])[0][0])
            return max(0.0, min(1.0, (sim + 1) / 2))  # normalize from [-1,1] to [0,1]
        except Exception:
            pass
    # TF-IDF fallback
    tfidf = TfidfVectorizer(min_df=1, max_features=5000, ngram_range=(1,2))
    X = tfidf.fit_transform([a, b])
    sim = float(cosine_similarity(X[0], X[1])[0][0])
    return max(0.0, min(1.0, sim))


def coverage_score(jd_skills: List[str], resume_skills: List[str], weights: Dict[str, float] = None) -> float:
    if not jd_skills:
        return 0.0
    w = weights or {s: 1.0 for s in jd_skills}
    covered = sum(w.get(s, 0.0) for s in jd_skills if s in resume_skills)
    total = sum(w.get(s, 1.0) for s in jd_skills)
    return float(covered) / float(total) if total > 0 else 0.0


def experience_alignment(jd_text: str, resume_text: str) -> float:
    # crude: if JD asks N years and resume has R years, score is min(1, R/N). If JD doesn't specify, return 1.
    import re
    jd_years = re.findall(r"(\d+)\s*\+?\s*year", jd_text.lower())
    if not jd_years:
        return 1.0
    jd_req = max(int(x) for x in jd_years)
    res_years = extract_years_experience(resume_text)
    if jd_req <= 0:
        return 1.0
    return max(0.0, min(1.0, float(res_years) / float(jd_req)))


def score(resume_text: str, jd_text: str, resume_skills: List[str] = None, jd_skills: List[str] = None) -> Dict:
    # if skills are not provided, try to extract or set empty
    if resume_skills is None:
        resume_skills = []  # TODO: plug your resume skill extractor here
    if jd_skills is None:
        jd_skills = []  # TODO: plug your JD skill extractor here

    sections = split_sections(jd_text)
    jd_core = sections.get("requirements", jd_text)

    cov = coverage_score(jd_skills, resume_skills)
    sim = _semantic_similarity(resume_text, jd_core)
    exp = experience_alignment(jd_text, resume_text)

    final = 100.0 * (
        config.WEIGHTS["coverage"] * cov +
        config.WEIGHTS["similarity"] * sim +
        config.WEIGHTS["experience"] * exp
    )

    return {
        "score": round(float(final), 2),
        "components": {
            "coverage": round(float(cov), 3),
            "similarity": round(float(sim), 3),
            "experience": round(float(exp), 3)
        },
    }
