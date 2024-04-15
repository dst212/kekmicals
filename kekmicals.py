#!/usr/bin/env python3
import math
import os
import sys
from PIL import Image, ImageFont, ImageDraw
from elements import elements, Element
from typing import Iterable, Union

MAX_SIZE = 512
TTF = "GoogleSans-Regular.ttf"
COLORS = {
    "actinide": "#9C27B0",
    "alkali metal": "#673AB7",
    "alkaline earth metal": "#2196F3",
    "diatomic nonmetal": "#FF9800",
    "lanthanide": "#009688",
    "metalloid": "#FFC107",
    "noble gas": "#F44336",
    "post-transition metal": "#CDDC39",  # "#FFEB3B",
    "polyatomic nonmetal": "#FF5722",
    "transition metal": "#4CAF50",
    "unknown": "#607D8B",
}


def merge(im1, im2):
    w = im1.size[0] + im2.size[0]
    h = max(im1.size[1], im2.size[1])
    im = Image.new("RGBA", (w, h))

    im.paste(im1)
    im.paste(im2, (im1.size[0], 0))

    return im


# Create all of the needed elements
def create(elements_list: Iterable[Element] = None, style: str = "default", force: bool = False) -> dict[str, Image]:
    GAP = 10
    ret = {}
    cache_dir = f"./cache/{style}"
    os.makedirs(cache_dir, exist_ok=True)
    symbol_font = ImageFont.truetype(TTF, 260)
    number_font = ImageFont.truetype(TTF, 110)
    font = ImageFont.truetype(TTF, 60)
    for e in elements_list or elements.values():
        path = f"{cache_dir}/{e.symbol}.png"
        if os.path.exists(path) and not force:
            ret[e.symbol] = Image.open(path)
        else:
            im = Image.new("RGBA", (MAX_SIZE, MAX_SIZE))
            bg = "#fff"
            color = COLORS.get(e.category) or COLORS["unknown"]
            draw = ImageDraw.Draw(im)
            if style == "border":
                draw.rectangle(((GAP, GAP), (MAX_SIZE - GAP, MAX_SIZE - GAP)), fill=bg, outline=color, width=20)
            else:
                if style == "swap":
                    bg, color = color, bg
                draw.rectangle(((GAP, GAP), (MAX_SIZE - GAP, MAX_SIZE - GAP)), fill=bg)

            # Draw the atomic number on the top left corner
            draw.text((40, 30), f"{e.number}", fill=color, font=number_font)

            # Draw the atomic mass on the top right corner
            mass = round(e.mass * 10000) / 10000
            mass = f"{round(mass)}" if round(mass) == mass else f"{mass}"
            draw.text((MAX_SIZE - 40 - font.getlength(mass), 30), mass, fill=color, font=font)

            # Draw symbol in the center of the image
            symbol_padding = (MAX_SIZE - symbol_font.getlength(e.symbol)) / 2
            draw.text((symbol_padding, 92), e.symbol, fill=color, font=symbol_font)

            # Draw element's name at the bottom
            padding = (MAX_SIZE - font.getlength(e.name)) / 2
            draw.text((padding, MAX_SIZE - 110), e.name, fill=color, font=font)

            with open(path, "wb") as f:
                im.save(f, "PNG")
                print(f"Saved {f.name}.")
            ret[e.symbol] = im
    return ret


# Return all of the elements contained in a string
def split(strings: Union[str, Iterable[str]]) -> list[list[Element]]:
    if isinstance(strings, str):
        strings = (strings,)
    ret = []
    for i, s in enumerate(strings):
        if not s:
            continue
        ret.append([])
        symbol = s[0]
        for i in range(1, len(s) + 1):
            c = s[i] if i < len(s) else ""
            if c.islower():
                symbol += c
            else:
                el = elements.get(symbol)
                if not el:
                    raise Exception(f"Element {symbol} doesn't exist.")
                print(f"{el.symbol} ({el.name})")
                ret[-1].append(el)
                symbol = c
        print()
    return ret


# Compose an image displaying the input string written with elements
def compose(strings: Union[str, Iterable[str]], style: str = "border"):
    output = "./output"
    os.makedirs(output, exist_ok=True)
    if isinstance(strings, str):
        strings = (strings,)
    words = split(strings)
    elems = [e for word in words for e in word]
    images = create(set(elems), style=style)
    final = []
    width = 0

    for word in words:
        im = Image.new("RGBA", (MAX_SIZE * len(word), MAX_SIZE))
        for i, e in enumerate(word):
            im.paste(images[e.symbol], (MAX_SIZE * i, 0))
        final.append(im)
        if im.width > width:
            width = im.width

    final_image = Image.new("RGBA", (width, MAX_SIZE * len(words)))
    for i, word in enumerate(final):
        final_image.paste(word, (0, (MAX_SIZE * i)))

    path = f"{output}/{style}-{'-'.join(strings)}.png"
    width, height = (
        (MAX_SIZE, math.floor(MAX_SIZE / final_image.width * final_image.height)) if final_image.width > final_image.height
        else (math.floor(MAX_SIZE / final_image.height * final_image.width), MAX_SIZE)
    )
    with open(path, "wb") as f:
        final_image.resize((width, height)).save(f, "PNG")
        print(f"Saved {path} ({width}x{height}).")


def main():
    if len(sys.argv) > 1:
        skip = 1
        style = "default"
        for i, arg in enumerate(sys.argv):
            if skip:
                skip -= 1
                continue
            match arg:
                case "--create":
                    create(style=sys.argv[i + 1] if len(sys.argv) > i + 1 else None, force=True)
                    break
                case "--test":
                    split(sys.argv[i + 1:])
                    break
                case "--style":
                    if len(sys.argv) > i + 1:
                        style = sys.argv[i + 1]
                        skip = 1
                case _:
                    compose(sys.argv[i:], style=style)
                    break
    else:
        print(
            "Create a picture with elements (saved in output/<elements>.png):\n"
            f"{sys.argv[0]} [--style <default|border|swap>] <elements>\n"
            "\n"
            "Test elements existance:\n"
            f"{sys.argv[0]} --test <elements>\n"
            "\n"
            "Cache all of the elements' pictures:\n"
            f"{sys.argv[0]} --create [default|border|swap]\n"
        )


if __name__ == "__main__":
    main()
