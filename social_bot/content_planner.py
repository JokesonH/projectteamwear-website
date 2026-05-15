"""
content_planner.py — Generate a weekly social media content calendar
for Project Team Wear using the Claude AI API.

Setup:
  pip install anthropic
  export ANTHROPIC_API_KEY="your-key-here"

Run:
  python content_planner.py
  python content_planner.py --week "May 19-25 2025"
"""

import anthropic
import argparse
from datetime import date, timedelta


def get_week_label(offset_weeks: int = 0) -> str:
    today = date.today()
    monday = today - timedelta(days=today.weekday()) + timedelta(weeks=offset_weeks)
    sunday = monday + timedelta(days=6)
    return f"{monday.strftime('%b %d')} – {sunday.strftime('%b %d, %Y')}"


def generate_calendar(week_label: str) -> str:
    client = anthropic.Anthropic()

    prompt = f"""You are a social media strategist for **Project Team Wear** — an Australian custom teamwear company that makes jerseys, hoodies, training tops and full kits for sports clubs (handball, soccer, basketball, AFL, etc).

Brand voice: Bold, confident, community-focused. Not corporate. Use punchy short sentences. Occasional humour is fine.

Generate a 5-post weekly content calendar for the week of **{week_label}** across Instagram and LinkedIn.

For each post include:
1. Platform (Instagram or LinkedIn)
2. Best day + time to post (AEST)
3. Post type (Photo, Reel, Carousel, Story, Text post)
4. Caption (ready to copy-paste, include emojis where appropriate)
5. Hashtags (Instagram: 8-12 tags. LinkedIn: 3-5 tags)
6. Visual description (what the photo/graphic should show)

Make 3 posts for Instagram and 2 for LinkedIn. Mix product showcases, team spotlights, behind-the-scenes, and quote/motivational content.

Format each post clearly with headers."""

    print(f"\n📅 Generating content calendar for {week_label}...\n")

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text


def save_calendar(content: str, week_label: str) -> str:
    safe_label = week_label.replace(" ", "_").replace("–", "-").replace(",", "")
    filename = f"content_calendar_{safe_label}.md"
    filepath = f"output/{filename}"

    import os
    os.makedirs("output", exist_ok=True)

    with open(filepath, "w") as f:
        f.write(f"# Project Team Wear — Content Calendar\n")
        f.write(f"## Week of {week_label}\n\n")
        f.write(content)

    return filepath


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate weekly content calendar")
    parser.add_argument("--week", type=str, help="Week label e.g. 'May 19-25 2025'", default=None)
    parser.add_argument("--next", action="store_true", help="Generate for next week")
    args = parser.parse_args()

    week_label = args.week or get_week_label(1 if args.next else 0)
    calendar = generate_calendar(week_label)
    filepath = save_calendar(calendar, week_label)

    print(calendar)
    print(f"\n✅ Saved to {filepath}")
