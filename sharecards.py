"""Share images (link previews) for NothingDown.com.

Draws a 1200x630 PNG for every page: offer pages show the deal's price and
category color; listing and guide pages show the page headline.
Uses Pillow and the Inter fonts bundled in fonts/. If Pillow is missing,
build.py falls back to the single static og-image.png.
"""
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(ROOT, "fonts")
W, H = 1200, 630
SCALE = 2  # draw at 2x, then downsample for crisp edges

BG = (251, 248, 245)
INK = (17, 26, 34)
MUTED = (96, 108, 118)
LINE = (230, 224, 218)
CORAL = (255, 107, 61)
CORAL_INK = (29, 17, 8)
MONEY = (21, 128, 61)
MONEY_SOFT = (220, 245, 227)
CAT_COLORS = {
    "Car lease": (37, 99, 235),
    "Car financing": (14, 116, 144),
    "Home loan": (21, 128, 61),
    "Phone": (147, 51, 234),
    "Home improvement": (180, 83, 9),
}
CAT_LABELS = {
    "Car lease": "Car lease",
    "Car financing": "Car loan",
    "Home loan": "Home loan",
    "Phone": "Phone deal",
    "Home improvement": "Solar & home",
}

_font_cache = {}


def font(name, size):
    key = (name, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(os.path.join(FONTS, name + ".otf"), size * SCALE)
    return _font_cache[key]


def S(v):
    return int(round(v * SCALE))


def soft(rgb, amount=0.12):
    return tuple(int(255 - (255 - c) * amount) for c in rgb)


def text_w(d, txt, f):
    return d.textlength(txt, font=f) / SCALE


def fit_lines(d, txt, fname, sizes, max_w, max_lines):
    """Pick the largest size where the text wraps into max_lines within max_w."""
    for size in sizes:
        f = font(fname, size)
        words, lines, cur = txt.split(), [], ""
        for w in words:
            trial = (cur + " " + w).strip()
            if text_w(d, trial, f) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        if len(lines) <= max_lines:
            return f, size, lines
    f = font(fname, sizes[-1])
    lines = textwrap.wrap(txt, 40)[:max_lines]
    lines[-1] = lines[-1].rstrip(".,") + "…"
    return f, sizes[-1], lines


def base(updated):
    im = Image.new("RGB", (S(W), S(H)), BG)
    d = ImageDraw.Draw(im)
    # Logo
    d.rounded_rectangle([S(64), S(56), S(64 + 52), S(56 + 52)], radius=S(12), fill=CORAL)
    f = font("Inter-Bold", 22)
    tw = text_w(d, "$0", f)
    d.text((S(64 + 26 - tw / 2), S(56 + 12)), "$0", font=f, fill=CORAL_INK)
    d.text((S(132), S(64)), "NothingDown.com", font=font("InterDisplay-SemiBold", 30), fill=INK)
    # Updated date, right aligned
    f = font("Inter-Medium", 22)
    label = f"Updated {updated}"
    tw = text_w(d, label, f)
    x = W - 64 - tw
    d.ellipse([S(x - 22), S(76), S(x - 10), S(88)], fill=MONEY)
    d.text((S(x), S(68)), label, font=f, fill=MUTED)
    return im, d


def pill(d, x, y, label, rgb, size=20, filled=False):
    f = font("Inter-SemiBold", size)
    tw = text_w(d, label, f)
    h = size + 22
    w = tw + 48
    d.rounded_rectangle([S(x), S(y), S(x + w), S(y + h)], radius=S(h / 2), fill=rgb if filled else soft(rgb, 0.14))
    d.ellipse([S(x + 16), S(y + h / 2 - 5), S(x + 26), S(y + h / 2 + 5)], fill=(255, 255, 255) if filled else rgb)
    d.text((S(x + 34), S(y + 10)), label, font=f, fill=(255, 255, 255) if filled else rgb)
    return w


def footer(d, colors):
    d.line([S(64), S(H - 78), S(W - 64), S(H - 78)], fill=LINE, width=S(2))
    d.text((S(64), S(H - 58)), "Every $0-down deal, updated daily", font=font("Inter-Medium", 22), fill=MUTED)
    # Category color key, right aligned
    x = W - 64
    for rgb in reversed(colors):
        d.rounded_rectangle([S(x - 44), S(H - 52), S(x), S(H - 40)], radius=S(6), fill=rgb)
        x -= 54


def save(im, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    im = im.resize((W, H), Image.LANCZOS)
    im.save(out_path, optimize=True)


def _layout_lines(d, txt, sizes, max_lines):
    return fit_lines(d, txt, "InterDisplay-Bold", sizes, W - 128, max_lines)


def offer_card(out_path, o, price_big, price_unit, due, total_line, updated, due_is_money=True):
    cat = o.get("category")
    rgb = CAT_COLORS.get(cat, CORAL)
    im, d = base(updated)
    d.rectangle([0, 0, S(12), S(H)], fill=rgb)
    f, size, lines = _layout_lines(d, o.get("title", ""), [64, 58, 52, 46], 2)
    big_size = 104 if len(price_big) <= 6 else 80 if len(price_big) <= 10 else 64
    unit_w = (text_w(d, price_unit, font("InterDisplay-SemiBold", 42)) + 12) if price_unit else 0
    while big_size > 36 and text_w(d, price_big, font("InterDisplay-Bold", big_size)) + unit_w > W - 128:
        big_size -= 2
    fb = font("InterDisplay-Bold", big_size)
    fu = font("InterDisplay-SemiBold", 42)
    fd = font("Inter-SemiBold", 28)
    price_w = text_w(d, price_big, fb) + (text_w(d, price_unit, fu) + 12 if price_unit else 0)
    dw = text_w(d, due, fd) + 44
    side = 64 + price_w + 36 + dw <= W - 64
    title_h = len(lines) * size * 1.12
    price_h = big_size * 1.05 + (0 if side else 74) + (40 if total_line and not side else 0)
    block = 44 + 26 + title_h + 18 + price_h
    y = 132 + max(0, (H - 96 - 132 - block) / 2)
    pill(d, 64, y, f"{CAT_LABELS.get(cat, cat)} · {o.get('provider')}", rgb)
    y += 44 + 26
    for ln in lines:
        d.text((S(64), S(y)), ln, font=f, fill=INK)
        y += size * 1.12
    y += 18
    d.text((S(64), S(y)), price_big, font=fb, fill=INK)
    x = 64 + text_w(d, price_big, fb) + 12
    if price_unit:
        d.text((S(x), S(y + big_size * 0.48)), price_unit, font=fu, fill=MUTED)
    if side:
        bx, by = 64 + price_w + 36, y + big_size * 0.5 - 28
    else:
        bx, by = 64, y + big_size * 1.05 + 14
    d.rounded_rectangle([S(bx), S(by), S(bx + dw), S(by + 54)], radius=S(14), fill=MONEY_SOFT if due_is_money else soft(MUTED, 0.14))
    d.text((S(bx + 22), S(by + 11)), due, font=fd, fill=MONEY if due_is_money else INK)
    if total_line:
        d.text((S(bx + 2), S(by + 66)), total_line, font=font("Inter-Medium", 23), fill=MUTED)
    footer(d, [rgb])
    save(im, out_path)


def page_card(out_path, eyebrow, headline, sub, colors, updated, accent=None):
    im, d = base(updated)
    rgb = accent or (194, 65, 12)
    if accent:
        d.rectangle([0, 0, S(12), S(H)], fill=accent)
    f, size, lines = _layout_lines(d, headline, [84, 76, 68, 60, 54], 3)
    block = 44 + 28 + len(lines) * size * 1.08 + (52 if sub else 0)
    y = 132 + max(0, (H - 96 - 132 - block) / 2)
    pill(d, 64, y, eyebrow, rgb)
    y += 44 + 28
    for ln in lines:
        d.text((S(64), S(y)), ln, font=f, fill=INK)
        y += size * 1.08
    if sub:
        d.text((S(64), S(y + 14)), sub, font=font("Inter-Medium", 29), fill=MUTED)
    footer(d, colors)
    save(im, out_path)
