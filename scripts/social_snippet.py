#!/usr/bin/env python3
"""Gera um rascunho de post de LinkedIn a partir de um post do blog.

Uso: python3 scripts/social_snippet.py posts/0014-macros-em-rust/README.md
"""
import os
import re
import sys

SITE = "https://desbravandorust.com.br"


def slug_from_path(caminho: str) -> str:
    """Nome da pasta do post (ex.: '0014-macros-rust-pythonistas'), robusto a
    caminho relativo, absoluto ou com './'."""
    return os.path.basename(os.path.dirname(os.path.abspath(caminho)))


def parse_post(markdown: str, slug: str) -> dict:
    linhas = markdown.splitlines()
    titulo = ""
    primeiro_paragrafo = ""
    for ln in linhas:
        t = ln.strip()
        if not titulo and t.startswith("# "):
            titulo = t[2:].strip()
            continue
        # primeiro parágrafo: pula título (#), autor (######), imagem (!) e vazios
        if titulo and not primeiro_paragrafo and t and t[0] not in "#!" and not t.startswith("```"):
            primeiro_paragrafo = t
            break
    m = re.search(r"```[a-z]*\n(.*?)```", markdown, re.S)
    codigo = m.group(1).strip() if m else None
    numero = slug.split("-")[0]
    return {
        "titulo": titulo,
        "numero": numero,
        "primeiro_paragrafo": primeiro_paragrafo,
        "codigo": codigo,
        "url": f"{SITE}/posts/{slug}/",
    }


def format_linkedin(parsed: dict) -> str:
    partes = [
        f"🦀 {parsed['titulo']}",
        "",
        parsed["primeiro_paragrafo"],
    ]
    if parsed["codigo"]:
        trecho = "\n".join(parsed["codigo"].splitlines()[:8])
        partes += ["", trecho]
    partes += [
        "",
        "Se você vem do Python, o post traz o comparativo lado a lado.",
        "",
        "#rustlang #python #backend #desenvolvimento",
        "",
        parsed["url"],
    ]
    return "\n".join(partes)


def main() -> int:
    if len(sys.argv) != 2:
        print("Uso: python3 scripts/social_snippet.py posts/NNNN-slug/README.md")
        return 2
    caminho = sys.argv[1]
    slug = slug_from_path(caminho)
    with open(caminho, encoding="utf-8") as f:
        markdown = f.read()
    print(format_linkedin(parse_post(markdown, slug)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
