"""
generate_post.py
-----------------
Picks today's quote (cycling through quotes.json with no repeats until
the whole bank has been used, then reshuffles) and renders a clean,
dark-theme 1080x1080 motivational quote image into posts/.

Run directly: python3 scripts/generate_post.py
Prints the output filename on the last line so other scripts/workflow
steps can pick it up.
"""

import json
import os
import random
import sys
import textwrap
from datetime import date

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def pick_quote(quotes, state):
    """Cycle through all quotes in a shuffled order before any repeat."""
    order = state.get("quote_order") or []
    pointer = state.get("quote_pointer", 0)

    if not order or pointer >= len(order):
        order = list(range(len(quotes)))
        random.shuffle(order)
        pointer = 0

    idx = order[pointer]
    pointer += 1

    state["quote_order"] = order
    state["quote_pointer"] = pointer
    return quotes[idx]


def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        for fallback in config.FALLBACK_FONTS:
            try:
                return ImageFont.truetype(fallback, size)
            except Exception:
                continue
        return ImageFont.load_default()


def vertical_gradient(size, top_color, bottom_color):
    w, h = size
    img = Image.new("RGB", size, top_color)
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return img


def wrap_to_fit(draw, text, font, max_width):
    """Word-wrap text so every line fits within max_width for the given font."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = (current + " " + word).strip()
        if draw.textbbox((0, 0), trial, font=font)[2] <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fit_quote_block(draw, quote, max_width, max_height, start_size=84, min_size=40):
    """Shrink font size until the wrapped quote fits inside the box."""
    size = start_size
    while size >= min_size:
        font = load_font(config.QUOTE_FONT_PATH, size)
        lines = wrap_to_fit(draw, quote, font, max_width)
        line_height = draw.textbbox((0, 0), "Ag", font=font)[3] + 14
        total_height = line_height * len(lines)
        if total_height <= max_height:
            return font, lines, line_height
        size -= 4
    font = load_font(config.QUOTE_FONT_PATH, min_size)
    lines = wrap_to_fit(draw, quote, font, max_width)
    line_height = draw.textbbox((0, 0), "Ag", font=font)[3] + 14
    return font, lines, line_height


def generate(quote: str, out_path: str):
    W, H = config.IMG_SIZE
    img = vertical_gradient((W, H), config.BG_TOP_COLOR, config.BG_BOTTOM_COLOR)
    draw = ImageDraw.Draw(img)

    margin_x = 110

    # Top accent line + small tag
    tag_font = load_font(config.TAG_FONT_PATH, 28)
    tag_text = config.TAG_TEXT
    tag_w = draw.textbbox((0, 0), tag_text, font=tag_font)[2]
    tag_y = 150
    draw.text(((W - tag_w) / 2, tag_y), tag_text, font=tag_font, fill=config.ACCENT_COLOR)

    line_y = tag_y + 56
    line_half = 46
    draw.line([(W / 2 - line_half, line_y), (W / 2 + line_half, line_y)],
              fill=config.ACCENT_COLOR, width=3)

    # Quote block, vertically centered in the remaining space
    box_top = line_y + 70
    box_bottom = H - 190
    font, lines, line_height = fit_quote_block(
        draw, quote, max_width=W - 2 * margin_x, max_height=box_bottom - box_top
    )
    total_text_height = line_height * len(lines)
    y = box_top + (box_bottom - box_top - total_text_height) / 2

    for line in lines:
        line_w = draw.textbbox((0, 0), line, font=font)[2]
        draw.text(((W - line_w) / 2, y), line, font=font, fill=config.TEXT_COLOR)
        y += line_height

    # Bottom accent line + handle
    foot_line_y = H - 140
    draw.line([(W / 2 - line_half, foot_line_y), (W / 2 + line_half, foot_line_y)],
              fill=config.ACCENT_COLOR, width=3)

    footer_font = load_font(config.FOOTER_FONT_PATH, 30)
    footer_text = config.HANDLE_TEXT
    footer_w = draw.textbbox((0, 0), footer_text, font=footer_font)[2]
    draw.text(((W - footer_w) / 2, foot_line_y + 26), footer_text,
               font=footer_font, fill=config.FOOTER_COLOR)

    img.save(out_path, "PNG")


def main():
    quotes = load_json(config.QUOTES_FILE)
    state = load_json(config.STATE_FILE)

    quote = pick_quote(quotes, state)
    save_json(config.STATE_FILE, state)

    os.makedirs(config.POSTS_DIR, exist_ok=True)
    filename = f"post_{date.today().isoformat()}.png"
    out_path = os.path.join(config.POSTS_DIR, filename)
    generate(quote, out_path)

    # Save the quote text alongside so post_to_instagram.py can build the caption
    with open(os.path.join(config.POSTS_DIR, "latest_quote.txt"), "w", encoding="utf-8") as f:
        f.write(quote)

    print(out_path)


if __name__ == "__main__":
    main()
