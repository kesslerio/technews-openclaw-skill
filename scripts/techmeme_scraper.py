#!/usr/bin/env python3
"""
TechMeme Scraper - Fetches top stories from techmeme.com
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup

TECHMEME_URL = "https://www.techmeme.com"
CACHE_FILE = Path.home() / ".cache/technews/stories.json"


def fetch_techmeme(num_stories: int = 10) -> List[Dict]:
    """Fetch top stories from TechMeme homepage."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    
    response = requests.get(TECHMEME_URL, headers=headers, timeout=30)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    stories = []
    
    # TechMeme uses div.story with data attributes for top stories
    story_elements = soup.select("div.story")
    
    for elem in story_elements[:num_stories]:
        try:
            # Get title from the link
            title_elem = elem.select_one("a.ourh")
            if not title_elem:
                continue
            
            title = title_elem.get_text(strip=True)
            link = title_elem.get("href", "")
            
            # Make absolute URL
            if link.startswith("/"):
                link = TECHMEME_URL + link
            
            # Get summary/description if available
            summary_elem = elem.select_one("div.intr")
            summary = summary_elem.get_text(strip=True) if summary_elem else ""
            
            # Get timestamp if available
            time_elem = elem.select_one("span.dt")
            timestamp = time_elem.get_text(strip=True) if time_elem else ""
            
            stories.append({
                "title": title,
                "url": link,
                "summary": summary,
                "timestamp": timestamp,
                "source": "techmeme"
            })
        except Exception as e:
            continue
    
    return stories


def save_cache(stories: List[Dict]):
    """Cache fetched stories."""
    cache_dir = CACHE_FILE.parent
    cache_dir.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump({"cached_at": __import__("time").time(), "stories": stories}, f, indent=2)


def load_cache(max_age_hours: int = 2) -> Optional[List[Dict]]:
    """Load cached stories if recent enough."""
    if not CACHE_FILE.exists():
        return None
    
    with open(CACHE_FILE) as f:
        data = json.load(f)
    
    age = (__import__("time").time() - data.get("cached_at", 0)) / 3600
    if age < max_age_hours:
        return data.get("stories", [])
    
    return None


def main(num_stories: int = 10, use_cache: bool = True) -> str:
    """Main entry point - returns JSON output."""
    # Try cache first
    if use_cache:
        cached = load_cache()
        if cached:
            return json.dumps({"cached": True, "stories": cached[:num_stories]})
    
    stories = fetch_techmeme(num_stories)
    save_cache(stories)
    
    return json.dumps({"cached": False, "stories": stories})


if __name__ == "__main__":
    import sys
    num = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    print(main(num_stories=num))
