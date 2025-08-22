from src.scoring import score

def test_score_runs():
    resume = "Experienced python developer with ML, numpy, pandas, sklearn. 2 years experience. Docker and AWS."
    jd = "Looking for python and machine learning engineer with 1+ years. Skills: numpy, pandas, docker."
    sc = score(resume, jd, ["python","numpy","pandas","scikit-learn","docker","aws"], ["python","numpy","pandas","docker"])
    assert "score" in sc and "components" in sc