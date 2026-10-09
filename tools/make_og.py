"""1200x630 sharing images for the Services branch (white card, brand logo,
charcoal title, orange accent). No photos, names or figures."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.join(HERE, "..", "site", "wp-content", "uploads", "2026", "02", "Digicomplish-Logo.png")
FONTS = r"C:\Windows\Fonts"


def _font(names, size):
    for n in names:
        p = os.path.join(FONTS, n)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def _wrap(draw, text, font, width):
    lines, line = [], ""
    for w in text.split():
        t = (line + " " + w).strip()
        if draw.textlength(t, font=font) <= width:
            line = t
        else:
            lines.append(line)
            line = w
    lines.append(line)
    return lines


def render(out, title, line):
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), "#ffffff")
    d = ImageDraw.Draw(img)
    # right-hand charcoal panel with orange gradient edge
    d.rectangle([860, 0, W, H], fill="#36454F")
    for i, c in enumerate(["#FFAF14", "#FA961E", "#F4761D", "#F0541E"]):
        d.rectangle([860 + i * 6, 0, 866 + i * 6, H], fill=c)
    logo = Image.open(LOGO).convert("RGBA")
    logo = logo.resize((int(logo.width * 0.9), int(logo.height * 0.9)))
    img.paste(logo, (72, 70), logo)
    d.rectangle([72, 250, 138, 256], fill="#F4761D")
    tf = _font(["segoeuib.ttf", "arialbd.ttf"], 74)
    lf = _font(["segoeui.ttf", "arial.ttf"], 32)
    y = 282
    for t in _wrap(d, title, tf, 740):
        d.text((72, y), t, font=tf, fill="#141A25")
        y += 86
    y += 14
    for t in _wrap(d, line, lf, 720):
        d.text((72, y), t, font=lf, fill="#4a5157")
        y += 44
    os.makedirs(os.path.dirname(out), exist_ok=True)
    img.save(out, optimize=True)
