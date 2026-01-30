#!/usr/bin/env python3
"""
TechNews Orchestrator - Main entry point for the technews skill
"""

import json
import sys
from pathlib import Path

# Add scripts to path
SCRIPT_DIR = Path(__file__).parent

# Import our modules
sys.path.insert(0, str(SCRIPT_DIR))

from techmeme_scraper import fetch_techmeme, load_cache, save_cache
from article_fetcher import fetch_multiple, summarize_content
from social_reactions import analyze_reactions


def format_output(stories: List[Dict]) -> str:
    """Format stories for display."""
    output = []
    output.append("📰 **Tech News Briefing**")
    output.append("")
    
    for i, story in enumerate(stories, 1):
        output.append(f"**{i}. {story['title']}**")
        output.append(f"   🔗 {story['url']}")
        
        if story.get("summary"):
            output.append(f"   📝 {story['summary'][:200]}...")
        
        # Show reactions if available
        if story.get("reactions"):
            reactions = story["reactions"]
            
            if reactions.get("hacker_news"):
                hn = reactions["hacker_news"]
                output.append(f"   💬 HN: {hn.get('points', 0)} points, {hn.get('comment_count', 0)} comments")
            
            if reactions.get("spicy_quotes"):
                output.append(f"   🔥 Notable quote: \"{reactions['spicy_quotes'][0][:100]}...\"")
        
        output.append("")
    
    return "\n".join(output)


def run_technews(num_stories: int = 10) -> str:
    """Main technews workflow."""
    # Step 1: Fetch from TechMeme
    print("Fetching TechMeme stories...")
    stories = fetch_techmeme(num_stories)
    
    if not stories:
        return "❌ Could not fetch stories from TechMeme"
    
    # Step 2: Fetch article content
    print(f"Fetching {len(stories)} articles...")
    urls = [s["url"] for s in stories]
    articles = fetch_multiple(urls)
    
    # Step 3: Merge content into stories
    for story, article in zip(stories, articles):
        if article.get("success"):
            story["content"] = article.get("content", "")
            story["summary"] = article.get("summary", "")
    
    # Step 4: Analyze reactions
    print("Analyzing social reactions...")
    analyzed = analyze_reactions(stories)
    
    # Step 5: Format output
    return format_output(analyzed)


def main():
    """CLI entry point."""
    num = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    
    result = run_technews(num_stories=num)
    print(result)


if __name__ == "__main__":
    main()
