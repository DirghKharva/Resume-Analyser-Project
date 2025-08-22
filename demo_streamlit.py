# demo_streamlit.py
import streamlit as st
import pandas as pd
from pathlib import Path

# optional plotting imports (try/except to avoid hard crashes)
try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None

try:
    from wordcloud import WordCloud
except Exception:
    WordCloud = None

try:
    import plotly.graph_objects as go
except Exception:
    go = None

from src.parse_resume import extract_text, extract_skills
from src.scoring import score
import json

st.set_page_config(page_title="Resume–JD Fit Analyzer", layout="wide")
st.title("📊 Resume–JD Fit Analyzer")

st.sidebar.header("Welcome")
st.sidebar.write("If extraction fails, try uploading a .txt version.")

# File uploaders
resume_file = st.file_uploader("Upload Resume (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])
jd_file = st.file_uploader("Upload Job Description (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])

if resume_file and jd_file:
    # Extract plain text
    resume_text = extract_text(resume_file)
    jd_text = extract_text(jd_file)

    # DEBUG info: show lengths and preview
    st.markdown("### Debug: extraction results")
    st.write(f"Resume extracted length: **{len(resume_text)}** characters")
    st.write(f"JD extracted length: **{len(jd_text)}** characters")
    st.text_area("Resume preview (first 1000 chars)", value=resume_text[:1000], height=200)
    st.text_area("JD preview (first 1000 chars)", value=jd_text[:1000], height=200)

    if not resume_text.strip() or not jd_text.strip():
        st.warning("⚠️ Extraction returned empty text. Try uploading a plain .txt first to confirm.")
        st.stop()

    # Load skills DB
    skills_db_path = Path("src/skills_db.json")
    if not skills_db_path.exists():
        st.error("skills_db.json not found in src/. Please restore it.")
        st.stop()
    skills_db = json.loads(skills_db_path.read_text(encoding="utf-8"))

    # Extract skills from both texts
    resume_skills, resume_spans = extract_skills(resume_text, skills_db)
    jd_skills, jd_spans = extract_skills(jd_text, skills_db)

    # Compute score (scoring.score expects resume_skills and jd_skills)
    sc = score(resume_text, jd_text, resume_skills, jd_skills)

    # Build display results
    fit_score = sc.get("score", 0.0)         # already 0-100
    components = sc.get("components", {})
    matched = sorted([s for s in jd_skills if s in resume_skills])
    missing = sorted([s for s in jd_skills if s not in resume_skills])
    extra = sorted([s for s in resume_skills if s not in jd_skills])

    # Show metrics
    st.metric("Overall Fit Score", f"{fit_score}/100")
    st.write("Components:", components)

    # Bar chart: matched / missing / extra
    counts = {"Matched": len(matched), "Missing": len(missing), "Extra": len(extra)}
    st.subheader("Skill match counts")
    try:
        st.bar_chart(pd.DataFrame({"count": list(counts.values())}, index=list(counts.keys())))
    except Exception:
        st.write(counts)

    # Optional gauge with plotly if available
    if go is not None:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=fit_score,
            title={'text': "Fit Score"},
            gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "green"}}
        ))
        st.plotly_chart(fig)

    # Word clouds (if available) — generate from the raw text
    st.subheader("Keyword clouds (if installed)")
    if WordCloud is not None:
        if resume_text.strip():
            wc = WordCloud(width=600, height=300).generate(resume_text)
            st.image(wc.to_array(), use_column_width=True)
        else:
            st.warning("No resume text for wordcloud.")
        if jd_text.strip():
            wc = WordCloud(width=600, height=300).generate(jd_text)
            st.image(wc.to_array(), use_column_width=True)
        else:
            st.warning("No JD text for wordcloud.")
    else:
        st.info("wordcloud not installed; install with `pip install wordcloud` to see visuals.")

    # Show lists
    st.subheader("Skills Summary")
    st.success(f"✅ Matched Skills: {matched}")
    st.error(f"❌ Missing Skills: {missing}")
    st.info(f"➕ Extra Skills: {extra}")

    # Show spans for first few matched skills (explainability)
    st.subheader("Explainability: sample matched spans (first 5)")
    sample = {}
    for k in matched[:5]:
        sample[k] = resume_spans.get(k, [])[:5]
    st.write(sample)
