"""Draw the front page for Tuesday 24 November 2026 and save it as entry.png.

The picture is a broadsheet front page built only from the day's reporting:
Nvidia reinstating Jensen Huang, NATO's answer to the reported Russian
space weapon, the Gaza strike that killed Hamas's security chief, the
Zaporizhzhia attack, the UN call for AI rules, and the closing markets.
Everything is drawn with PIL so the page is fully deterministic.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PAGE_W = 1024
PAGE_H = 1024
PAPER = (247, 242, 231)
INK = (26, 24, 20)
FADED = (92, 86, 74)
ACCENT = (146, 32, 24)
BAND = (24, 30, 44)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
SERIF_BOLD = str(FONT_DIR / "DejaVuSerif-Bold.ttf")
SERIF = str(FONT_DIR / "DejaVuSerif.ttf")
SANS_BOLD = str(FONT_DIR / "DejaVuSans-Bold.ttf")
SANS = str(FONT_DIR / "DejaVuSans.ttf")


def load(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, font, width):
    """Split text into lines that fit width, word by word."""
    lines = []
    current = ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=font) <= width:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def story(draw, x, y, width, kicker, headline, body, head_size=37):
    """One news block: red kicker, serif headline, then body text."""
    draw.text((x, y), kicker, font=load(SANS_BOLD, 19), fill=ACCENT)
    y += 29
    head_font = load(SERIF_BOLD, head_size)
    for line in wrap(draw, headline, head_font, width):
        draw.text((x, y), line, font=head_font, fill=INK)
        y += head_size + 6
    y += 3
    body_font = load(SERIF, 20)
    for line in wrap(draw, body, body_font, width):
        draw.text((x, y), line, font=body_font, fill=INK)
        y += 27
    return y


def chip_graphic(draw, x, y, size):
    """A simple processor glyph to sit beside the lead story."""
    draw.rounded_rectangle([x, y, x + size, y + size], radius=18,
                           outline=INK, width=5)
    inner = 26
    draw.rounded_rectangle([x + inner, y + inner, x + size - inner,
                            y + size - inner], radius=10, outline=INK, width=3)
    pin = 16
    step = size // 5
    for i in range(1, 5):
        p = x + i * step
        draw.line([p, y - pin, p, y], fill=INK, width=4)
        draw.line([p, y + size, p, y + size + pin], fill=INK, width=4)
        q = y + i * step
        draw.line([x - pin, q, x, q], fill=INK, width=4)
        draw.line([x + size, q, x + size + pin, q], fill=INK, width=4)
    label = load(SANS_BOLD, 44)
    text = "AI"
    w = draw.textlength(text, font=label)
    draw.text((x + (size - w) / 2, y + size / 2 - 26), text,
              font=label, fill=ACCENT)


def build_page():
    page = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    draw = ImageDraw.Draw(page)
    margin = 46
    right = PAGE_W - margin

    # Masthead
    name_font = load(SERIF_BOLD, 64)
    name = "THE WORLD IN ONE PAGE"
    w = draw.textlength(name, font=name_font)
    draw.text(((PAGE_W - w) / 2, 30), name, font=name_font, fill=INK)
    draw.line([margin, 118, right, 118], fill=INK, width=4)
    draw.line([margin, 126, right, 126], fill=INK, width=1)
    date_font = load(SANS, 19)
    date_line = "Tuesday, 24 November 2026  ·  One image, the whole day"
    w = draw.textlength(date_line, font=date_font)
    draw.text(((PAGE_W - w) / 2, 136), date_line, font=date_font, fill=FADED)

    # Lead story, with the chip glyph on its right
    lead_y = 178
    chip_graphic(draw, right - 168, lead_y + 6, 150)
    lead_end = story(
        draw, margin, lead_y, 730,
        "TECHNOLOGY",
        "HUANG RETURNS TO NVIDIA HELM",
        "Nvidia's board reinstated Jensen Huang as chief executive less "
        "than two weeks after his resignation, following intervention by "
        "President Trump. Huang told staff he had made 'some terrible "
        "mistakes'; Taiwan's chip suppliers called him irreplaceable.",
        head_size=44,
    )

    # Two-column rows; each divider sits below the taller column so no
    # story can spill into the next row.
    col_w = 448
    col_r = right - col_w
    rule_y = lead_end + 12
    draw.line([margin, rule_y, right, rule_y], fill=INK, width=2)
    mid_y = rule_y + 18
    mid_left = story(
        draw, margin, mid_y, col_w,
        "SPACE / NATO",
        "ALLIES VOW TO COUNTER SPACE THREAT",
        "NATO chief Mark Rutte said the alliance will defend against any "
        "threat in orbit after reports Russia is preparing a "
        "nuclear-armed satellite launch.",
        head_size=34,
    )
    mid_right = story(
        draw, col_r, mid_y, col_w,
        "MIDDLE EAST",
        "GAZA STRIKE KILLS HAMAS SECURITY CHIEF",
        "Israeli airstrikes killed Naeem Abu Nahal, head of Hamas's "
        "internal security, and two police officers in Gaza City, "
        "despite the year-old ceasefire.",
        head_size=34,
    )

    rule_y = max(mid_left, mid_right) + 12
    draw.line([margin, rule_y, right, rule_y], fill=INK, width=2)
    low_y = rule_y + 18
    low_left = story(
        draw, margin, low_y, col_w,
        "UNITED NATIONS",
        "UN CHIEF: AI RULES WITHIN A YEAR",
        "Secretary-General Antonio Guterres urged member states to "
        "build a shared framework for managing AI risks within the "
        "next year.",
        head_size=31,
    )
    low_right = story(
        draw, col_r, low_y, col_w,
        "UKRAINE",
        "ZAPORIZHZHIA STRIKE KILLS TWO",
        "An overnight Russian strike on an apartment block killed "
        "two and wounded 40, including four children, officials said.",
        head_size=31,
    )
    assert max(low_left, low_right) <= 946, "stories overflow the page"

    # Markets band along the foot of the page
    band_y = 958
    draw.rectangle([0, band_y, PAGE_W, PAGE_H], fill=BAND)
    band_font = load(SANS_BOLD, 20)
    band_text = ("MARKETS  S&P +4.7% · NASDAQ +6.5% · NIKKEI +3.9% · "
                 "FTSE +1.3% · GOLD $3,620")
    w = draw.textlength(band_text, font=band_font)
    draw.text(((PAGE_W - w) / 2, band_y + 10), band_text,
              font=band_font, fill=(240, 236, 224))
    small_font = load(SANS, 16)
    small = ("Also today: M5.6 earthquake in Nepal · 14 nations back ICJ "
             "Rohingya ruling · landmine toll at five-year high")
    w = draw.textlength(small, font=small_font)
    draw.text(((PAGE_W - w) / 2, band_y + 40), small,
              font=small_font, fill=(196, 200, 210))

    out = Path(__file__).with_name("entry.png")
    page.save(out, format="PNG", optimize=True)
    return out


if __name__ == "__main__":
    print(build_page())
