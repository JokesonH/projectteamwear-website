"""
scheduler.py — Queue posts to Buffer (free tier supports Instagram + LinkedIn).

Setup:
  pip install requests
  Get your Buffer Access Token from https://buffer.com/developers/apps
  Get your profile IDs from the Buffer API:
    python scheduler.py --list-profiles

  Set environment variables:
    export BUFFER_TOKEN="your-buffer-access-token"
    export BUFFER_INSTAGRAM_ID="your-instagram-profile-id"
    export BUFFER_LINKEDIN_ID="your-linkedin-profile-id"

Usage:
  python scheduler.py --platform instagram --text "Your caption here" --scheduled-at "2025-05-20 09:00"
  python scheduler.py --list-profiles
"""

import os
import argparse
import requests
from datetime import datetime
import pytz


BUFFER_API = "https://api.bufferapp.com/1"
AEST = pytz.timezone("Australia/Sydney")


def get_token() -> str:
    token = os.getenv("BUFFER_TOKEN")
    if not token:
        raise EnvironmentError(
            "BUFFER_TOKEN not set. Export it with:\n"
            "  export BUFFER_TOKEN='your-buffer-token'"
        )
    return token


def get_profile_id(platform: str) -> str:
    env_map = {
        "instagram": "BUFFER_INSTAGRAM_ID",
        "linkedin": "BUFFER_LINKEDIN_ID",
    }
    key = env_map.get(platform)
    profile_id = os.getenv(key, "")
    if not profile_id:
        raise EnvironmentError(
            f"{key} not set. Run --list-profiles to find your ID, then:\n"
            f"  export {key}='your-profile-id'"
        )
    return profile_id


def list_profiles():
    token = get_token()
    resp = requests.get(f"{BUFFER_API}/profiles.json", params={"access_token": token})
    resp.raise_for_status()
    profiles = resp.json()

    print(f"\n{'Platform':<15} {'Username':<30} {'ID'}")
    print("─" * 70)
    for p in profiles:
        print(f"{p.get('service',''):<15} {p.get('formatted_username',''):<30} {p.get('id','')}")


def queue_post(platform: str, text: str, scheduled_at: str | None = None, media_url: str | None = None):
    token = get_token()
    profile_id = get_profile_id(platform)

    payload: dict = {
        "access_token": token,
        "profile_ids[]": profile_id,
        "text": text,
    }

    if scheduled_at:
        dt = datetime.strptime(scheduled_at, "%Y-%m-%d %H:%M")
        dt_aest = AEST.localize(dt)
        payload["scheduled_at"] = dt_aest.isoformat()
        payload["now"] = "false"
    else:
        payload["now"] = "true"

    if media_url:
        payload["media[photo]"] = media_url

    resp = requests.post(f"{BUFFER_API}/updates/create.json", data=payload)

    try:
        resp.raise_for_status()
        result = resp.json()
        if result.get("success"):
            update_id = result.get("updates", [{}])[0].get("id", "")
            print(f"✅ Post queued on {platform} (ID: {update_id})")
            if scheduled_at:
                print(f"   Scheduled for: {scheduled_at} AEST")
        else:
            print(f"❌ Buffer error: {result}")
    except requests.HTTPError as e:
        print(f"❌ HTTP error: {e}\nResponse: {resp.text}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Queue posts to Buffer")
    parser.add_argument("--platform", choices=["instagram", "linkedin"], help="Target platform")
    parser.add_argument("--text", type=str, help="Caption text")
    parser.add_argument("--scheduled-at", type=str, help="Schedule time YYYY-MM-DD HH:MM (AEST)")
    parser.add_argument("--media-url", type=str, help="Public URL of image to attach")
    parser.add_argument("--list-profiles", action="store_true", help="List all connected Buffer profiles")
    args = parser.parse_args()

    if args.list_profiles:
        list_profiles()
    elif args.platform and args.text:
        queue_post(args.platform, args.text, args.scheduled_at, args.media_url)
    else:
        parser.print_help()
