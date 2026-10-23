"""
Smart Title Matching Engine for Anime Releases
"""
import re
from typing import Dict, Any, Tuple, Optional

def normalize_text(text: str) -> str:
    """Normalizes text for fuzzy comparisons."""
    # Replace common separators with spaces
    t = text.lower()
    t = re.sub(r"[\._\-\–\—\:]+", " ", t)
    return " ".join(t.split())

def match_anime(item_title: str, anime_rule: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Checks if a release title matches an anime tracking rule.
    Returns: (is_match, reason_or_anime_name)
    """
    anime_name = anime_rule.get("name", "").strip()
    if not anime_name:
        return False, None

    title_lower = item_title.lower()
    norm_title = normalize_text(item_title)
    norm_anime = normalize_text(anime_name)

    # 1. Main Anime Name Match
    # Check if the normalized anime name appears as a phrase or all constituent words appear in order
    if norm_anime not in norm_title:
        # Check if all words from anime name appear in the title
        anime_words = norm_anime.split()
        if not anime_words or not all(word in norm_title for word in anime_words):
            return False, None

    # 2. Exclude Words Check
    exclude_str = anime_rule.get("exclude", "").strip()
    if exclude_str:
        excludes = [e.strip().lower() for e in exclude_str.split(",") if e.strip()]
        for exc in excludes:
            # Word boundary check for exclude terms
            pattern = rf"\b{re.escape(exc)}\b"
            if re.search(pattern, title_lower):
                return False, None

    # 3. Resolution Filter
    res = anime_rule.get("resolution", "Tümü")
    if res and res != "Tümü":
        res_clean = res.lower().replace("p", "")
        # e.g. 1080, 720, 2160
        if res_clean not in title_lower:
            return False, None

    # 4. Group Filter (e.g. SubsPlease, Erai-raws, judas)
    group = anime_rule.get("group", "").strip().lower()
    if group:
        if group not in title_lower:
            return False, None

    return True, anime_name
