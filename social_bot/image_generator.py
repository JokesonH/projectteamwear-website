"""
image_generator.py — AI image generation for Project Team Wear social posts.
Uses fal.ai (FLUX model) — free $5 credits on signup, ~$0.003–0.006/image after.

Setup:
  pip install fal-client requests pillow
  export FAL_KEY="your-fal-api-key"   # from fal.ai/dashboard

Usage:
  # Interactive mode
  python image_generator.py

  # Quick CLI
  python image_generator.py --style product --description "Red handball jersey flat lay"

  # Generate + auto-post to Instagram
  python image_generator.py \\
    --style product \\
    --description "Orange Eye of Sauron handball jersey" \\
    --post-to-instagram

Styles:
  product       Studio flat lay, dark background, sharp fabric detail
  lifestyle     Real teams, community energy, outdoor sport setting
  editorial     Bold graphic design, typography-forward, Nike/Adidas aesthetic
  action        Athletes in motion, dynamic, cinematic
  behind-scenes Design process, workspace, craft and detail
"""

import os
import sys
import argparse
import datetime
import json
import requests
from pathlib import Path

# ── Brand context injected into every prompt ────────────────────────────────
BRAND_CONTEXT = (
    "Project Team Wear, Australian custom sportswear brand. "
    "Bold, professional, high quality. Dark aesthetic with orange accents. "
    "Social media ready, square format, Instagram feed post."
)

# ── Style prompt prefixes ────────────────────────────────────────────────────
STYLE_PROMPTS = {
    "product": (
        "Professional product photography. Dark studio background, soft directional lighting. "
        "Clean flat lay or hanging shot. Sharp fabric texture detail, visible print quality. "
        "Commercial sportswear catalogue style. "
    ),
    "lifestyle": (
        "Authentic sports lifestyle photography. Real athletes, outdoor setting, natural light. "
        "Candid community energy, weekend sport, Australian club culture. "
        "Warm tones, genuine emotion, not overly polished. "
    ),
    "editorial": (
        "Bold editorial graphic design. Strong typography, high contrast, dark background. "
        "Nike or Adidas campaign aesthetic. Geometric composition, intentional negative space. "
        "Magazine cover quality. "
    ),
    "action": (
        "Dynamic sports action photography. Athlete in full motion, dramatic lighting. "
        "Cinematic shallow depth of field, high shutter speed freeze. "
        "Powerful, energetic, aspirational. "
    ),
    "behind-scenes": (
        "Behind-the-scenes documentary style. Design studio or print workshop. "
        "Jersey mockup on screen or print table, colour swatches, craft details. "
        "Warm workspace lighting, authentic and approachable. "
    ),
}

# ── Buffer / Instagram channel ID ────────────────────────────────────────────
BUFFER_CHANNEL_ID = "6a069746090476fb99201f09"
BUFFER_MCP_URL    = "https://mcp.buffer.com/mcp"


def get_fal_key() -> str:
    key = os.getenv("FAL_KEY")
    if not key:
        raise EnvironmentError(
            "FAL_KEY not set.\n"
            "  1. Sign up at https://fal.ai (free $5 credits)\n"
            "  2. Get your key at https://fal.ai/dashboard/keys\n"
            "  3. export FAL_KEY='your-key-here'"
        )
    return key


def generate_image(description: str, style: str = "product", output_dir: str = "output/images") -> str:
    """Generate image via fal.ai FLUX. Returns saved branded file path."""
    try:
        import fal_client
    except ImportError:
        print("❌ Run: pip install fal-client")
        sys.exit(1)

    key = get_fal_key()
    os.environ["FAL_KEY"] = key

    style_prefix = STYLE_PROMPTS.get(style, STYLE_PROMPTS["product"])
    full_prompt = f"{style_prefix}{description}. {BRAND_CONTEXT}"

    print(f"\n🎨 Generating image  [{style}]")
    print(f"   {description[:90]}{'...' if len(description) > 90 else ''}\n")

    result = fal_client.subscribe(
        "fal-ai/flux/schnell",
        arguments={
            "prompt": full_prompt,
            "image_size": "square_hd",
            "num_inference_steps": 4,
            "num_images": 1,
            "enable_safety_checker": True,
        },
        with_logs=False,
    )

    image_url = result["images"][0]["url"]

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp  = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_style = style.replace("-", "_")
    filename   = f"{output_dir}/ptw_{safe_style}_{timestamp}.jpg"

    resp = requests.get(image_url, timeout=30)
    resp.raise_for_status()
    with open(filename, "wb") as f:
        f.write(resp.content)

    print(f"✅ Saved: {filename}")
    return add_branding_overlay(filename)


def generate_jersey_scene(jersey_url: str, scene: str, output_dir: str = "output/images") -> str:
    """
    Take a real jersey WEBP and place it in a scene using FLUX Kontext.
    The jersey design is preserved pixel-perfect; only the background changes.

    jersey_url : public URL to one of the WEBP jersey mockups on GitHub Pages
    scene      : description of the background/atmosphere to generate around it

    Example scenes:
      "dramatic indoor handball arena, stadium floodlights, blurred crowd"
      "dark matte studio surface, soft side lighting, premium product photography"
      "beach sand court, golden sunset, warm cinematic atmosphere"
      "locker room, team preparing, authentic sport documentary feel"
    """
    try:
        import fal_client
    except ImportError:
        print("❌ Run: pip install fal-client")
        sys.exit(1)

    os.environ["FAL_KEY"] = get_fal_key()

    prompt = (
        f"Keep the jersey in this image exactly as-is — same design, same colours, "
        f"same graphics. Replace ONLY the white background with: {scene}. "
        f"The jersey should remain the main subject, large and centred. "
        f"Professional sports photography quality."
    )

    print(f"\n🏟️  Jersey scene  [{scene[:60]}...]")

    result = fal_client.subscribe(
        "fal-ai/flux-pro/kontext",
        arguments={
            "image_url": jersey_url,
            "prompt": prompt,
            "guidance_scale": 3.5,
            "num_inference_steps": 28,
            "image_size": "square_hd",
        },
        with_logs=False,
    )

    image_url = result["images"][0]["url"]

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"{output_dir}/ptw_jersey_scene_{timestamp}.jpg"

    resp = requests.get(image_url, timeout=30)
    resp.raise_for_status()
    with open(filename, "wb") as f:
        f.write(resp.content)

    print(f"✅ Saved: {filename}")
    return add_branding_overlay(filename)


def add_branding_overlay(image_path: str) -> str:
    """
    Composites the PTW logo onto the bottom of the image.
    Returns the path to the branded image (overwrites original).

    Layout (bottom strip, 88px tall):
      [dark semi-transparent bar]
      [■ PTW ] PROJECT TEAM WEAR      projectteamwear.com
      [orange]  bold white            mono grey
    """
    from PIL import Image, ImageDraw, ImageFont

    FONT_BOLD  = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    FONT_MONO  = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"
    ACCENT     = (255, 58, 0)       # #FF3A00
    DARK       = (8, 8, 8)          # #080808
    CREAM      = (240, 237, 232)     # #F0EDE8
    MUTED      = (160, 155, 148)

    img = Image.open(image_path).convert("RGBA")
    W, H = img.size

    # ── Dark semi-transparent strip at the bottom ──────────────────────────
    strip_h = max(88, H // 12)
    overlay  = Image.new("RGBA", (W, strip_h), (0, 0, 0, 0))
    draw_ov  = ImageDraw.Draw(overlay)
    draw_ov.rectangle([(0, 0), (W, strip_h)], fill=(8, 8, 8, 210))

    # ── Orange PTW block ───────────────────────────────────────────────────
    pad      = strip_h // 6
    box_h    = strip_h - pad * 2
    box_w    = int(box_h * 1.15)          # slightly wider than tall
    draw_ov.rectangle([(pad, pad), (pad + box_w, pad + box_h)], fill=ACCENT)

    # "PTW" centred in the orange box
    ptw_size = max(20, box_h - 18)
    try:
        ptw_font = ImageFont.truetype(FONT_BOLD, ptw_size)
    except Exception:
        ptw_font = ImageFont.load_default()
    bbox   = draw_ov.textbbox((0, 0), "PTW", font=ptw_font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx     = pad + (box_w - tw) // 2
    ty     = pad + (box_h - th) // 2 - bbox[1]
    draw_ov.text((tx, ty), "PTW", font=ptw_font, fill=DARK)

    # ── "PROJECT TEAM WEAR" wordmark ───────────────────────────────────────
    text_x    = pad + box_w + pad
    brand_sz  = max(14, box_h // 3)
    sub_sz    = max(10, box_h // 5)
    try:
        brand_font = ImageFont.truetype(FONT_BOLD, brand_sz)
        sub_font   = ImageFont.truetype(FONT_MONO,  sub_sz)
    except Exception:
        brand_font = sub_font = ImageFont.load_default()

    # Top line: PROJECT TEAM WEAR
    brand_bb = draw_ov.textbbox((0, 0), "PROJECT TEAM WEAR", font=brand_font)
    brand_h  = brand_bb[3] - brand_bb[1]
    brand_y  = pad + (box_h // 2) - brand_h - 2
    draw_ov.text((text_x, brand_y), "PROJECT TEAM WEAR", font=brand_font, fill=CREAM)

    # Bottom line: projectteamwear.com
    url_y = brand_y + brand_h + 4
    draw_ov.text((text_x, url_y), "projectteamwear.com", font=sub_font, fill=MUTED)

    # ── Paste strip onto image ─────────────────────────────────────────────
    img.paste(overlay, (0, H - strip_h), overlay)

    # Save as RGB JPEG
    out_path = image_path.replace(".jpg", "_branded.jpg").replace(".png", "_branded.jpg")
    img.convert("RGB").save(out_path, "JPEG", quality=92)
    print(f"✅ Branded: {out_path}")
    return out_path


def generate_caption(description: str, style: str) -> str:
    """Generate Instagram caption using Claude."""
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_key:
        return ""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=anthropic_key)

        style_tone = {
            "product":       "bold product showcase — confident, aspirational",
            "lifestyle":     "warm and community-focused — authentic, inclusive",
            "editorial":     "bold and punchy — minimal words, maximum impact",
            "action":        "energetic and motivating — athletic, competitive",
            "behind-scenes": "warm and transparent — craft, care, process",
        }.get(style, "bold and sporty")

        msg = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=350,
            messages=[{
                "role": "user",
                "content": (
                    f"Write an Instagram caption for Project Team Wear "
                    f"(custom Australian sportswear company). "
                    f"Image: {description}. "
                    f"Tone: {style_tone}. "
                    f"Include a CTA to DM for a quote or visit the link in bio. "
                    f"End with 10 targeted hashtags. "
                    f"Max 120 words total."
                )
            }]
        )
        return msg.content[0].text
    except Exception as e:
        print(f"⚠️  Caption generation skipped: {e}")
        return ""


def post_to_instagram(image_path: str, caption: str):
    """Upload image to GitHub Pages and post to Instagram via Buffer MCP."""
    buffer_token = os.getenv("BUFFER_TOKEN")
    if not buffer_token:
        print("\n⚠️  Set BUFFER_TOKEN to auto-post.")
        print(f"   Image ready at: {image_path}")
        print(f"\n📝 Caption:\n{caption}")
        return

    # Host image on GitHub Pages — upload to repo
    print("\n⏳ Uploading image to GitHub Pages...")

    gh_token  = os.getenv("GITHUB_TOKEN", "")
    gh_repo   = "JokesonH/projectteamwear-website"
    filename  = Path(image_path).name
    gh_path   = f"social/generated/{filename}"
    public_url = f"https://jokesonh.github.io/projectteamwear-website/{gh_path}"

    if gh_token:
        import base64
        with open(image_path, "rb") as f:
            content_b64 = base64.b64encode(f.read()).decode()

        resp = requests.put(
            f"https://api.github.com/repos/{gh_repo}/contents/{gh_path}",
            headers={
                "Authorization": f"token {gh_token}",
                "Accept": "application/vnd.github.v3+json",
            },
            json={
                "message": f"Add generated social image {filename}",
                "content": content_b64,
            },
            timeout=30,
        )
        if resp.status_code not in (200, 201):
            print(f"❌ GitHub upload failed: {resp.text}")
            return

        # Wait for Pages to propagate (usually 10–20s)
        import time
        print("⏳ Waiting for GitHub Pages...")
        for _ in range(8):
            time.sleep(10)
            check = requests.get(public_url, timeout=10)
            if check.status_code == 200:
                print(f"✅ Image live at: {public_url}")
                break
        else:
            print(f"⚠️  Pages may still be building. URL: {public_url}")
    else:
        print("⚠️  GITHUB_TOKEN not set — skipping auto-upload.")
        print(f"   Manually upload the image and use its public URL.")
        return

    # Post via Buffer MCP
    print("⏳ Queuing post to Instagram...")
    payload = {
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {
            "name": "create_post",
            "arguments": {
                "channelId": BUFFER_CHANNEL_ID,
                "schedulingType": "automatic",
                "mode": "addToQueue",
                "text": caption,
                "assets": [{
                    "image": {
                        "url": public_url,
                        "metadata": {"altText": description[:100]}
                    }
                }],
                "metadata": {"instagram": {"type": "post", "shouldShareToFeed": True}}
            }
        }
    }

    resp = requests.post(
        BUFFER_MCP_URL,
        headers={
            "Authorization": f"Bearer {buffer_token}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
        json=payload,
        timeout=30,
    )

    result = resp.json().get("result", {}).get("content", [{}])[0].get("text", "")
    try:
        parsed = json.loads(result)
        if parsed.get("status") == "scheduled":
            print(f"✅ Post queued! Scheduled for: {parsed.get('dueAt','')}")
        else:
            print(f"⚠️  Buffer response: {result}")
    except Exception:
        print(f"Buffer: {result or resp.text}")


def interactive_mode():
    print("\n🎨 Project Team Wear — Image Generator\n")
    styles = list(STYLE_PROMPTS.keys())
    for i, s in enumerate(styles, 1):
        desc = STYLE_PROMPTS[s][:60].rstrip()
        print(f"  {i}. {s:<16} {desc}...")

    choice = input("\nChoose style (1-5 or name) [1]: ").strip() or "1"
    if choice.isdigit():
        style = styles[int(choice) - 1]
    else:
        style = choice if choice in STYLE_PROMPTS else "product"

    description = input(f"\nDescribe what you want ({style}):\n> ").strip()
    if not description:
        print("❌ Description required.")
        return

    # Generate image
    path = generate_image(description, style)

    # Generate caption
    print("\n⏳ Writing caption...")
    caption = generate_caption(description, style)
    if caption:
        print(f"\n📝 Caption:\n\n{caption}")

    # Offer to post
    if input("\nPost to Instagram? (y/n) [y]: ").strip().lower() != "n":
        post_to_instagram(path, caption)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate social media images for Project Team Wear")
    parser.add_argument("--description", type=str, help="Describe the image to generate from scratch")
    parser.add_argument("--style", choices=list(STYLE_PROMPTS.keys()), default="product")
    parser.add_argument("--jersey-url", type=str, help="Public URL of a jersey WEBP to use as base image")
    parser.add_argument("--scene", type=str, help="Background/scene description when using --jersey-url")
    parser.add_argument("--output-dir", default="output/images")
    parser.add_argument("--post-to-instagram", action="store_true")
    parser.add_argument("--caption", type=str, help="Custom caption (skips AI generation)")
    args = parser.parse_args()

    if args.jersey_url:
        scene   = args.scene or "dramatic indoor sports arena, stadium floodlights, blurred crowd"
        path    = generate_jersey_scene(args.jersey_url, scene, args.output_dir)
        desc    = f"Jersey scene: {scene}"
        caption = args.caption or generate_caption(desc, "action")
        if caption:
            print(f"\n📝 Caption:\n\n{caption}")
        if args.post_to_instagram:
            post_to_instagram(path, caption)
    elif args.description:
        path    = generate_image(args.description, args.style, args.output_dir)
        caption = args.caption or generate_caption(args.description, args.style)
        if caption:
            print(f"\n📝 Caption:\n\n{caption}")
        if args.post_to_instagram:
            post_to_instagram(path, caption)
    else:
        interactive_mode()
