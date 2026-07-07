# Validação e re-scrape das imagens de compartilhamento (Open Graph)

Os crawlers das redes sociais **cacheiam** o preview de forma agressiva. Depois de
publicar uma correção de OG (imagem/meta tags), é preciso forçar o re-scrape em
cada plataforma, senão o preview antigo (ou sem imagem) continua aparecendo.

## Pré-requisitos

- A alteração precisa estar **publicada** em `https://desbravandorust.com.br`
  (GitHub Pages já publicou o commit na `main`).
- Confirme que a imagem carrega direto no navegador, ex.:
  `https://desbravandorust.com.br/imgs/og-default.png` (deve abrir a arte 1200×630).

## Re-scrape por plataforma

### LinkedIn — Post Inspector
1. Acesse https://www.linkedin.com/post-inspector/
2. Cole a URL da página (home ou post) e clique **Inspect**.
3. O LinkedIn re-busca a página no ato; a imagem correta deve aparecer no preview.
   Se aparecer erro de imagem, revise `og:image:width/height` (devem ser 1200/630).

### Facebook / WhatsApp — Sharing Debugger
> O WhatsApp usa o mesmo cache do Facebook. Corrigir aqui corrige o WhatsApp.
1. Acesse https://developers.facebook.com/tools/debug/
2. Cole a URL e clique **Debug**.
3. Clique em **Scrape Again** para invalidar o cache.
4. Verifique em "Link Preview" que a imagem 1200×630 aparece e que não há
   warnings de `og:image` faltando.

### X (Twitter)
O antigo Card Validator foi descontinuado. Para validar:
1. Comece a **compor um post** (sem publicar) e cole a URL.
2. Aguarde o card renderizar no editor — deve exibir `summary_large_image`
   com a imagem 1200×630.
3. Se o card não atualizar, o X pode levar alguns minutos para expirar o cache
   da URL; tente novamente mais tarde ou adicione um `?v=2` temporário à URL só
   para conferir a renderização.

## Regenerar / normalizar imagens

Os scripts rodam **localmente** (precisam de `pillow`); os PNGs gerados são
commitados — nada disso vai para o runtime do site.

```bash
pip install pillow
# Gera imgs/og-default.png e normaliza os covers existentes p/ 1200×630 (<300KB)
python3 scripts/gen_og_images.py
```

Para **um novo cover de post**: coloque a arte em `posts/<slug>/imgs/cover.png`
(ou `.jpg`). O layout detecta automaticamente e passa a usá-la no lugar do
`og-default`. Ideal já em 1200×630; se estiver em outro tamanho, adicione o
caminho na lista do `scripts/gen_og_images.py` e rode-o para normalizar.

## Checagem automática (CI)

O workflow `.github/workflows/og-images.yml` builda o site e roda
`scripts/check_og_images.py`, que **falha o build** se qualquer `og:image`/
`twitter:image` apontar para um arquivo inexistente. Para rodar localmente:

```bash
jekyll build -d _site        # ou: bundle exec jekyll build
python3 scripts/check_og_images.py _site
```
