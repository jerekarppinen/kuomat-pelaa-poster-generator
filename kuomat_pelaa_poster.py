from PIL import Image, ImageDraw, ImageFont, ImageFilter
import argparse
from pathlib import Path

W, H = 1080, 1350

IMAGE_AREA_H = 860

# Kahden kuvan tilassa kuvien väliin jätetään tumma rako + hohtava jakoviiva.
GAP_H = 18
DIVIDER_H = 4
DIVIDER_COLOR = (92, 238, 238)

TOP_H = (IMAGE_AREA_H - GAP_H) // 2
BOTTOM_H = IMAGE_AREA_H - GAP_H - TOP_H

CARD_X = 40
CARD_Y = 910
CARD_W = 1000
CARD_H = 300
RADIUS = 18

TEXT_PADDING_X = 52
TEXT_PADDING_Y = 38

MAX_FONT_SIZE = 52
MIN_FONT_SIZE = 24

def cover_crop(img, target_w, target_h):
    """Scale image to cover target area, then crop center."""
    img = img.convert("RGB")
    scale = max(target_w / img.width, target_h / img.height)
    new_w = round(img.width * scale)
    new_h = round(img.height * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)

    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))

def contain_fit(img, target_w, target_h):
    """Scale image to fit fully inside target area (no cropping)."""
    img = img.convert("RGB")
    scale = min(target_w / img.width, target_h / img.height)
    new_w = round(img.width * scale)
    new_h = round(img.height * scale)
    return img.resize((new_w, new_h), Image.LANCZOS)

def get_font(size):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    line = ""

    for word in words:
        test = (line + " " + word).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        width = bbox[2] - bbox[0]

        if width <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word

    if line:
        lines.append(line)

    return lines

def text_block_size(draw, lines, font, line_spacing):
    if not lines:
        return 0, 0

    widths = []
    heights = []

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        widths.append(bbox[2] - bbox[0])
        heights.append(bbox[3] - bbox[1])

    total_h = sum(heights) + line_spacing * (len(lines) - 1)
    return max(widths), total_h

def fit_text_to_box(draw, text, max_width, max_height):
    """
    Finds the largest font size where wrapped text fits inside the box.
    Uses both width and height, then returns font, lines and spacing.
    """
    best = None

    for size in range(MAX_FONT_SIZE, MIN_FONT_SIZE - 1, -1):
        font = get_font(size)
        line_spacing = max(6, round(size * 0.28))
        lines = wrap_text(draw, text, font, max_width)
        block_w, block_h = text_block_size(draw, lines, font, line_spacing)

        if block_w <= max_width and block_h <= max_height:
            best = (font, lines, line_spacing, block_w, block_h)
            break

    if best:
        return best

    # If even minimum font does not fit, use minimum and truncate with ellipsis.
    font = get_font(MIN_FONT_SIZE)
    line_spacing = max(6, round(MIN_FONT_SIZE * 0.28))
    lines = wrap_text(draw, text, font, max_width)

    fitted = []
    for line in lines:
        test_lines = fitted + [line]
        _, block_h = text_block_size(draw, test_lines, font, line_spacing)
        if block_h <= max_height:
            fitted.append(line)
        else:
            break

    if fitted:
        last = fitted[-1]
        while last and draw.textbbox((0, 0), last + "…", font=font)[2] > max_width:
            last = last[:-1].rstrip()
        fitted[-1] = last + "…"

    block_w, block_h = text_block_size(draw, fitted, font, line_spacing)
    return font, fitted, line_spacing, block_w, block_h

def add_bottom_gradient(canvas, y, height, max_opacity=230):
    gradient = Image.new("RGBA", (W, height), (0, 0, 0, 0))
    pixels = gradient.load()

    for yy in range(height):
        alpha = int(max_opacity * (yy / max(1, height - 1)))
        for x in range(W):
            pixels[x, yy] = (0, 0, 0, alpha)

    canvas.alpha_composite(gradient, (0, y))

def add_divider(canvas, gap_y, gap_h):
    """Tumma rako kuvien välissä + hohtava aksenttiviiva keskellä."""
    band = Image.new("RGBA", (W, gap_h), (7, 15, 20, 255))
    canvas.paste(band, (0, gap_y))

    cy = gap_y + gap_h / 2

    # Pehmeä hohde viivan ympärille
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.rectangle((0, cy - DIVIDER_H, W, cy + DIVIDER_H),
                 fill=DIVIDER_COLOR + (150,))
    canvas.alpha_composite(glow.filter(ImageFilter.GaussianBlur(11)))

    # Terävä viiva päälle
    d = ImageDraw.Draw(canvas)
    d.rectangle((0, cy - DIVIDER_H / 2, W, cy + DIVIDER_H / 2),
                fill=DIVIDER_COLOR + (240,))


def rounded_rect_layer(x, y, w, h, radius, fill, outline=None, outline_width=1):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(
        (x, y, x + w, y + h),
        radius=radius,
        fill=fill,
        outline=outline,
        width=outline_width
    )
    return layer

def make_poster(top_image, bottom_image, body, output):
    canvas = Image.new("RGBA", (W, H), (7, 15, 20, 255))

    if bottom_image:
        # Kaksi peliä: kaksi kuvaa päällekkäin.
        top = cover_crop(Image.open(top_image), W, TOP_H)
        bottom = cover_crop(Image.open(bottom_image), W, BOTTOM_H)
        canvas.paste(top, (0, 0))
        canvas.paste(bottom, (0, TOP_H + GAP_H))
        add_divider(canvas, TOP_H, GAP_H)
    else:
        # Yksi peli: koko pelikuva näkyviin (fit), reunat täytetään
        # saman kuvan sumennetulla versiolla, ettei mikään leikkaudu pois.
        src = Image.open(top_image)

        bg = cover_crop(src, W, IMAGE_AREA_H).filter(ImageFilter.GaussianBlur(30))
        bg = Image.blend(bg, Image.new("RGB", (W, IMAGE_AREA_H), (7, 15, 20)), 0.4)
        canvas.paste(bg, (0, 0))

        fitted = contain_fit(src, W, IMAGE_AREA_H)
        ox = (W - fitted.width) // 2
        oy = (IMAGE_AREA_H - fitted.height) // 2
        canvas.paste(fitted, (ox, oy))

    # Longer fade helps blend the image(s) into the text area.
    add_bottom_gradient(canvas, IMAGE_AREA_H - 230, 270, 235)

    draw = ImageDraw.Draw(canvas)

    # Dark lower background
    draw.rectangle((0, IMAGE_AREA_H, W, H), fill=(7, 18, 24, 255))

    # Card shadow
    shadow = rounded_rect_layer(
        CARD_X, CARD_Y + 12, CARD_W, CARD_H,
        RADIUS,
        fill=(0, 0, 0, 160)
    ).filter(ImageFilter.GaussianBlur(18))
    canvas.alpha_composite(shadow)

    # Card background
    card = rounded_rect_layer(
        CARD_X, CARD_Y, CARD_W, CARD_H,
        RADIUS,
        fill=(12, 36, 44, 238),
        outline=(92, 238, 238, 230),
        outline_width=2
    )
    canvas.alpha_composite(card)

    draw = ImageDraw.Draw(canvas)

    text_x = CARD_X + TEXT_PADDING_X
    text_w = CARD_W - TEXT_PADDING_X * 2
    text_h = CARD_H - TEXT_PADDING_Y * 2

    font, lines, line_spacing, block_w, block_h = fit_text_to_box(
        draw,
        body,
        text_w,
        text_h
    )

    # Vertically centered text
    y = CARD_Y + (CARD_H - block_h) // 2

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_h = bbox[3] - bbox[1]

        # Text shadow
        draw.text((text_x + 2, y + 2), line, font=font, fill=(0, 0, 0, 125))
        draw.text((text_x, y), line, font=font, fill=(242, 247, 248, 255))

        y += line_h + line_spacing

    canvas.convert("RGB").save(output, quality=95)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Tee 1080x1350 podcast-/somekuva yhdestä tai kahdesta kuvasta ja automaattisesti sovitetusta leipätekstistä."
    )
    parser.add_argument("images", nargs="+", help="Yksi kuva (yksi peli) tai kaksi kuvaa (kaksi peliä)")
    parser.add_argument("--body", required=True, help="Kuvaan tuleva leipäteksti")
    parser.add_argument("-o", "--output", default="jakso.png", help="Tulostiedosto, esim. jakso.png")
    args = parser.parse_args()

    if len(args.images) > 2:
        parser.error("Anna korkeintaan kaksi kuvaa.")

    top = args.images[0]
    bottom = args.images[1] if len(args.images) > 1 else None
    make_poster(top, bottom, args.body, args.output)
