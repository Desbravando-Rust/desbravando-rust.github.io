#!/usr/bin/env python3
"""Gera a imagem OG padrão (og-default) e normaliza covers de posts para 1200x630.

Uso:
    python3 scripts/gen_og_images.py

Requer Pillow (pip install pillow). Roda localmente; os PNGs gerados são
commitados no repo — nada disso vai para o build do site.

- og-default.png: card branded landscape (fallback de compartilhamento).
- Normaliza covers existentes (crop 1.91:1 + resize 1200x630 + otimização).
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1200, 630
RATIO = W / H
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MAX_KB = 300

SLATE_TOP = (0x1B, 0x1F, 0x24)
SLATE_BOTTOM = (0x2B, 0x2F, 0x36)
RUST = (0xCE, 0x42, 0x2B)
RUST_LIGHT = (0xDE, 0xA5, 0x84)
PY_BLUE = (0x37, 0x76, 0xAB)
WHITE = (0xF5, 0xF5, 0xF5)


def font(size):
    return ImageFont.truetype(FONT_BOLD, size)


def vgradient(w, h, top, bottom):
    """Gradiente vertical (barato, sem numpy)."""
    base = Image.new("RGB", (1, h))
    px = base.load()
    for y in range(h):
        t = y / (h - 1)
        px[0, y] = tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    return base.resize((w, h))


def crop_to_ratio(img):
    """Center-crop para 1.91:1 e resize para 1200x630."""
    img = img.convert("RGB")
    w, h = img.size
    if w / h > RATIO:
        new_w = round(h * RATIO)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        new_h = round(w / RATIO)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))
    return img.resize((W, H), Image.LANCZOS)


def save_under_limit(img, dst):
    """Salva PNG otimizado; se >300KB, quantiza; se ainda grande, cai para JPEG."""
    img.save(dst, "PNG", optimize=True)
    if os.path.getsize(dst) <= MAX_KB * 1024:
        return dst
    img.convert("RGB").quantize(colors=256, method=Image.FASTOCTREE).save(
        dst, "PNG", optimize=True
    )
    if os.path.getsize(dst) <= MAX_KB * 1024:
        return dst
    # Fallback JPEG (troca a extensão; o layout aceita .png e .jpg).
    jpg = os.path.splitext(dst)[0] + ".jpg"
    img.convert("RGB").save(jpg, "JPEG", quality=85, optimize=True, progressive=True)
    if dst != jpg and os.path.exists(dst):
        os.remove(dst)
    return jpg


def make_og_default():
    img = vgradient(W, H, SLATE_TOP, SLATE_BOTTOM)
    d = ImageDraw.Draw(img)
    # Barra de acento à esquerda (identidade Rust).
    d.rectangle([0, 0, 14, H], fill=RUST)
    # Kicker.
    d.text((80, 150), "RUST PARA PYTHONISTAS", font=font(30), fill=RUST_LIGHT)
    # Título da marca em duas linhas.
    d.text((78, 205), "Desbravando", font=font(104), fill=WHITE)
    d.text((78, 320), "Rust", font=font(104), fill=RUST)
    # Tagline.
    d.text(
        (80, 460),
        "Um guia prático para pythonistas\nexplorarem novos horizontes",
        font=font(30),
        fill=(0xC0, 0xC4, 0xCA),
        spacing=10,
    )
    # Marcador Python->Rust (pequeno detalhe no canto).
    d.rectangle([W - 90, H - 90, W - 40, H - 40], fill=PY_BLUE)
    d.rectangle([W - 70, H - 70, W - 20, H - 20], fill=RUST)
    out = os.path.join(ROOT, "imgs", "og-default.png")
    save_under_limit(img, out)
    print(f"og-default.png -> {os.path.getsize(out)//1024}KB")


def normalize(src, dst):
    if not os.path.exists(src):
        print(f"SKIP (não existe): {src}")
        return
    with Image.open(src) as im:
        out = crop_to_ratio(im)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    final = save_under_limit(out, dst)
    print(f"{os.path.relpath(src, ROOT)} -> {os.path.relpath(final, ROOT)} "
          f"({os.path.getsize(final)//1024}KB)")
    # remove o arquivo original mal-nomeado se foi renomeado
    if os.path.abspath(src) != os.path.abspath(final) and os.path.exists(src) \
            and os.path.basename(src) != "cover.png":
        os.remove(src)
        print(f"  removido original: {os.path.relpath(src, ROOT)}")


def p(*parts):
    return os.path.join(ROOT, *parts)


if __name__ == "__main__":
    make_og_default()
    # 0011: cover11.png (raiz do post) -> imgs/cover.png
    normalize(
        p("posts/0011-iteradores-closures-rust-pythonistas/cover11.png"),
        p("posts/0011-iteradores-closures-rust-pythonistas/imgs/cover.png"),
    )
    # 0016 / 0017: já têm imgs/cover.png (ratio/peso errados) -> normaliza in place
    for slug in ("0016-cnpj-alfanumerico-rust-python-performance",
                 "0017-orm-mentindo-n1-sqlx"):
        normalize(p("posts", slug, "imgs/cover.png"), p("posts", slug, "imgs/cover.png"))
