#!/usr/bin/env python3
"""Falha se algum og:image/twitter:image do site apontar para arquivo inexistente.

Roda depois do `jekyll build`, contra o diretório gerado (padrão: ./_site).

    python3 scripts/check_og_images.py [_site]

Só valida imagens do próprio domínio (ignora URLs externas).
"""
import glob
import os
import re
import sys
from urllib.parse import urlparse

SITE_DIR = sys.argv[1] if len(sys.argv) > 1 else "_site"
OWN_HOSTS = {"", "desbravandorust.com.br", "www.desbravandorust.com.br"}
META_RE = re.compile(
    r'<meta[^>]+(?:property|name)=["\'](?:og:image|og:image:secure_url|twitter:image)["\']'
    r'[^>]+content=["\']([^"\']+)["\']',
    re.IGNORECASE,
)


def local_path(url):
    """URL -> caminho dentro de SITE_DIR, ou None se for externa."""
    p = urlparse(url)
    if p.netloc not in OWN_HOSTS:
        return None
    return os.path.join(SITE_DIR, p.path.lstrip("/"))


def main():
    if not os.path.isdir(SITE_DIR):
        sys.exit(f"ERRO: diretório '{SITE_DIR}' não existe — rode o build antes.")
    missing = []
    checked = 0
    for html in glob.glob(os.path.join(SITE_DIR, "**", "*.html"), recursive=True):
        with open(html, encoding="utf-8") as f:
            content = f.read()
        for url in set(META_RE.findall(content)):
            path = local_path(url)
            if path is None:
                continue
            checked += 1
            if not os.path.isfile(path):
                missing.append((os.path.relpath(html, SITE_DIR), url))
    if missing:
        print(f"❌ {len(missing)} referência(s) de imagem OG quebrada(s):")
        for page, url in sorted(missing):
            print(f"  - {page} -> {url}")
        sys.exit(1)
    print(f"✅ {checked} referência(s) de imagem OG válidas.")


if __name__ == "__main__":
    main()
