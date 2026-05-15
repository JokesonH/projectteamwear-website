"""
caption_generator.py — Generate social media captions for Project Team Wear.

Setup:
  pip install anthropic
  export ANTHROPIC_API_KEY="your-key-here"

Usage:
  python caption_generator.py --platform instagram --type product --description "Blue and white handball jerseys for Toronto Handball Club"
  python caption_generator.py --platform linkedin  --type spotlight --description "Canadian National Handball Team wearing their custom kits at the World Championships"
  python caption_generator.py  (interactive mode)
"""

import anthropic
import argparse


PLATFORM_INSTRUCTIONS = {
    "instagram": {
        "tone": "casual, punchy, emoji-friendly",
        "length": "3-5 short punchy lines + hashtags",
        "hashtag_count": "10-12 relevant hashtags",
        "note": "Include a call to action like 'Link in bio' or 'DM us to order'",
    },
    "linkedin": {
        "tone": "professional but passionate, community-focused",
        "length": "4-6 lines, no excessive hashtags",
        "hashtag_count": "3-5 hashtags",
        "note": "Tell a brief story. End with a question or thought-provoking line.",
    },
}

POST_TYPES = {
    "product": "showcasing a product or jersey design",
    "spotlight": "team spotlight — showing a client team in their kit",
    "behind-the-scenes": "behind the scenes of the design or production process",
    "motivational": "motivational/inspirational sports quote or message",
    "announcement": "announcing a new design, offer, or update",
    "repost": "sharing a customer photo or testimonial",
}


def generate_caption(platform: str, post_type: str, description: str) -> str:
    client = anthropic.Anthropic()

    p = PLATFORM_INSTRUCTIONS[platform]

    prompt = f"""You are writing a social media caption for **Project Team Wear** — a custom teamwear company making jerseys, hoodies, training gear and full kits for sports clubs.

Platform: **{platform.upper()}**
Post type: **{POST_TYPES.get(post_type, post_type)}**

Context / photo description:
{description}

Write a caption that:
- Tone: {p['tone']}
- Length: {p['length']}
- Hashtags: {p['hashtag_count']}
- Extra: {p['note']}

Brand voice: Bold, confident, community-first. Short punchy sentences. A bit of attitude is fine (this is a sporty brand).

Output ONLY the final caption text, ready to paste into {platform}. No explanation."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text


def interactive_mode():
    print("\n🎽 Project Team Wear — Caption Generator")
    print("=" * 45)

    print("\nPlatform:")
    print("  1. Instagram")
    print("  2. LinkedIn")
    choice = input("Choose (1/2): ").strip()
    platform = "instagram" if choice == "1" else "linkedin"

    print("\nPost type:")
    for i, (k, v) in enumerate(POST_TYPES.items(), 1):
        print(f"  {i}. {k} — {v}")
    type_choice = input("Choose (1-6): ").strip()
    post_type = list(POST_TYPES.keys())[int(type_choice) - 1]

    description = input("\nDescribe the photo/content:\n> ").strip()

    print(f"\n⏳ Generating {platform} caption...\n")
    caption = generate_caption(platform, post_type, description)
    print("─" * 45)
    print(caption)
    print("─" * 45)

    save = input("\nSave to file? (y/n): ").strip().lower()
    if save == "y":
        import os
        os.makedirs("output", exist_ok=True)
        fname = f"output/caption_{platform}_{post_type}.txt"
        with open(fname, "w") as f:
            f.write(caption)
        print(f"✅ Saved to {fname}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate social media captions")
    parser.add_argument("--platform", choices=["instagram", "linkedin"], help="Platform")
    parser.add_argument("--type", dest="post_type", choices=list(POST_TYPES.keys()), help="Post type")
    parser.add_argument("--description", type=str, help="Description of the photo/content")
    args = parser.parse_args()

    if args.platform and args.post_type and args.description:
        print(f"\n⏳ Generating {args.platform} caption...\n")
        caption = generate_caption(args.platform, args.post_type, args.description)
        print(caption)
    else:
        interactive_mode()
