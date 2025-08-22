from typing import Dict, List, Tuple
import re

def split_sections(jd_text: str) -> Dict[str, str]:
    """
    Naive splitter to get 'responsibilities' and 'requirements' sections if present.
    """
    text = jd_text.lower()
    sections = {"all": jd_text}
    # crude anchors
    resp = re.split(r"responsibilit(?:y|ies)\s*[:\-]", text)
    reqs = re.split(r"requirement(?:s)?\s*[:\-]", text)
    # not robust, but keeps MVP moving
    sections["responsibilities"] = jd_text if len(resp) <= 1 else resp[-1]
    sections["requirements"] = jd_text if len(reqs) <= 1 else reqs[-1]
    return sections