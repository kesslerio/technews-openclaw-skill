#!/usr/bin/env python3
"""TechNews orchestrator for deterministic cron delivery."""

from __future__ import annotations

import contextlib
import io
import sys
from pathlib import Path
from typing import Any

import requests

SCRIPT_DIR = Path(__file__).parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from article_fetcher import fetch_multiple  # noqa: E402
from social_reactions import analyze_reactions  # noqa: E402
from techmeme_scraper import fetch_techmeme  # noqa: E402


def format_output(stories: list[dict[str, Any]]) -> str:
    output: list[str] = []
    output.append("📰 **Tech News Briefing**")
    output.append("")

    for index, story in enumerate(stories, start=1):
        output.append(f"**{index}. {story['title']}**")
        output.append(f"🔗 [{story['url']}]({story['url']})")

        if story.get("summary"):
            output.append(f"📝 {story['summary'][:200]}...")

        reactions = story.get("reactions") or {}
        if reactions.get("hacker_news"):
            hn = reactions["hacker_news"]
            hn_url = hn.get("hn_url", "")
            points = hn.get("points", 0)
            comments = hn.get("comment_count", 0)
            output.append(f"💬 [HN: {points}pts, {comments} comments]({hn_url})")

        spicy_quotes = reactions.get("spicy_quotes") or []
        if spicy_quotes:
            output.append(f"🔥 \"{spicy_quotes[0][:100]}...\"")

        output.append("")

    return "\n".join(output).strip() + "\n"


def _log(message: str, progress_stream: io.TextIOBase | None) -> None:
    if progress_stream is not None:
        print(message, file=progress_stream)


def run_technews(num_stories: int = 10, progress_stream: io.TextIOBase | None = sys.stderr) -> str:
    try:
        _log("Fetching TechMeme stories...", progress_stream)
        stories = fetch_techmeme(num_stories)
        if not stories:
            return "❌ Could not fetch stories from TechMeme"

        _log(f"Fetching {len(stories)} articles...", progress_stream)
        urls = [story["url"] for story in stories]
        articles = fetch_multiple(urls)

        for story, article in zip(stories, articles):
            if article.get("success"):
                story["content"] = article.get("content", "")
                story["summary"] = article.get("summary", "")

        _log("Analyzing social reactions...", progress_stream)
        analyzed = analyze_reactions(stories)
        return format_output(analyzed)
    except requests.exceptions.RequestException as exc:
        return f"❌ Network error: {exc}"
    except Exception as exc:
        return f"❌ Unexpected error: {exc}"


def main() -> int:
    num = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    stderr_buffer = io.StringIO()
    with contextlib.redirect_stdout(sys.stderr):
        result = run_technews(num_stories=num, progress_stream=stderr_buffer)
    progress = stderr_buffer.getvalue().strip()
    if progress:
        print(progress, file=sys.stderr)
    print(result.rstrip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
