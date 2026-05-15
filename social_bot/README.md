# Project Team Wear — Social Media Bot

Three Python scripts that automate your Instagram and LinkedIn presence.

## Quick Start

```bash
pip install anthropic requests pytz
```

Set your environment variables:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."        # from console.anthropic.com
export BUFFER_TOKEN="..."                     # from buffer.com/developers/apps
export BUFFER_INSTAGRAM_ID="..."             # run: python scheduler.py --list-profiles
export BUFFER_LINKEDIN_ID="..."              # run: python scheduler.py --list-profiles
```

---

## 1. Content Planner — `content_planner.py`

Generates a full week of post ideas (3 Instagram + 2 LinkedIn) every Monday.

```bash
# This week
python content_planner.py

# Next week
python content_planner.py --next

# Specific week
python content_planner.py --week "May 26-Jun 1 2025"
```

Output is saved to `output/content_calendar_*.md`.

---

## 2. Caption Generator — `caption_generator.py`

Give it a photo description, get a ready-to-post caption with hashtags.

```bash
# Interactive (recommended)
python caption_generator.py

# Command line
python caption_generator.py \
  --platform instagram \
  --type product \
  --description "Red and black handball jerseys for Sherwood Park Sandstorm"
```

Post types: `product`, `spotlight`, `behind-the-scenes`, `motivational`, `announcement`, `repost`

---

## 3. Scheduler — `scheduler.py`

Queue posts to Buffer (which then publishes to Instagram + LinkedIn for you).

```bash
# List your connected profiles (do this first to get profile IDs)
python scheduler.py --list-profiles

# Queue a post now
python scheduler.py --platform instagram --text "Your caption here"

# Schedule for a specific time (AEST)
python scheduler.py \
  --platform instagram \
  --text "Your caption" \
  --scheduled-at "2025-05-20 09:00"

# With an image
python scheduler.py \
  --platform instagram \
  --text "Your caption" \
  --media-url "https://yourdomain.com/image.jpg" \
  --scheduled-at "2025-05-20 09:00"
```

---

## Typical Weekly Workflow

1. **Monday morning** — Run `content_planner.py` to get your 5-post week plan
2. **Take photos / grab images** based on the visual descriptions
3. **Run `caption_generator.py`** for each post to get polished captions
4. **Run `scheduler.py`** to queue them all in Buffer at the right times
5. **Set up ManyChat** (see below) to handle DM auto-replies

---

## Auto-Reply to DMs — ManyChat (No Code)

For Instagram DM automation, use **ManyChat** (free tier available):

1. Go to [manychat.com](https://manychat.com) → Connect your Instagram Business account
2. Create a new **Flow** with a keyword trigger
3. Add keywords: `quote`, `pricing`, `order`, `jersey`, `kit`
4. Set the auto-reply message:

   > "Hey! 👋 Thanks for reaching out to Project Team Wear.
   > For a free custom quote, fill in our form here: www.projectteamwear.com/#quote
   > We'll get back to you within 24 hours. 🧡"

5. Enable the flow — done. Every DM containing those keywords gets an instant reply.

---

## Costs

| Tool | Free tier | Paid |
|------|-----------|------|
| Anthropic (Claude) | Pay-per-use (~$0.01–$0.05 per run) | — |
| Buffer | 3 channels, 10 posts queued | $6/mo for more |
| ManyChat | 1,000 contacts, basic flows | $15/mo for more |
