from __future__ import annotations

import io
import unittest

import scripts.technews as technews


class TechNewsTests(unittest.TestCase):
    def test_run_technews_writes_progress_to_stderr_stream_only(self) -> None:
        progress = io.StringIO()
        original_fetch = technews.fetch_techmeme
        original_fetch_multiple = technews.fetch_multiple
        original_analyze = technews.analyze_reactions
        try:
            technews.fetch_techmeme = lambda num_stories: [
                {"title": "Story", "url": "https://example.com/story", "summary": "Summary"}
            ]
            technews.fetch_multiple = lambda urls: [
                {"success": True, "content": "Long article body", "summary": "Summary"}
            ]
            technews.analyze_reactions = lambda stories: [
                {
                    "title": "Story",
                    "url": "https://example.com/story",
                    "summary": "Summary",
                    "reactions": {},
                }
            ]
            rendered = technews.run_technews(num_stories=1, progress_stream=progress)
        finally:
            technews.fetch_techmeme = original_fetch
            technews.fetch_multiple = original_fetch_multiple
            technews.analyze_reactions = original_analyze

        self.assertIn("📰 **Tech News Briefing**", rendered)
        self.assertIn("Fetching TechMeme stories...", progress.getvalue())
        self.assertNotIn("Fetching TechMeme stories...", rendered)

    def test_run_technews_handles_request_errors(self) -> None:
        progress = io.StringIO()
        original_fetch = technews.fetch_techmeme
        try:
            def fail(_num_stories: int):
                raise technews.requests.exceptions.RequestException("boom")

            technews.fetch_techmeme = fail
            rendered = technews.run_technews(num_stories=1, progress_stream=progress)
        finally:
            technews.fetch_techmeme = original_fetch

        self.assertEqual(rendered, "❌ Network error: boom")


if __name__ == "__main__":
    unittest.main()
