# desbravandorust.com.br

Site de vendas + blog do livro **Desbravando Rust**, hospedado no GitHub Pages
(Jekyll nativo, sem build customizado).

## Como editar as coisas do dia a dia

| O que | Onde |
|---|---|
| Preço, link Kiwify, cupom, IDs de analytics | `_config.yml` (seções comentadas no topo) |
| Depoimentos de leitores | `_data/depoimentos.yml` |
| Sumário do livro | `_data/sumario.yml` |
| Capítulo de amostra (PDF) | salvar como `assets/desbravando-rust-amostra.pdf` |
| Textos da home | `index.html` (HTML simples, seções marcadas com comentários) |

## Como publicar um post novo

1. Crie a pasta `posts/NNNN-slug-do-post/` (numeração sequencial).
2. Escreva o `README.md` em markdown, começando com `# Título do post`.
3. Imagens do post em `posts/NNNN-slug/imgs/` (use `imgs/cover.png` para a
   imagem de compartilhamento no LinkedIn).
4. Commit + push. O post aparece automaticamente na home e em `/blog`.

## Campanhas (LinkedIn)

- Ative o cupom preenchendo `cupom` e `cupom_texto` no `_config.yml` — uma faixa
  aparece no topo de todas as páginas.
- Use UTM nos links divulgados:
  `https://desbravandorust.com.br/?utm_source=linkedin&utm_medium=social&utm_campaign=NOME`

## Rodar localmente

```bash
gem install jekyll jekyll-optional-front-matter jekyll-readme-index \
  jekyll-relative-links jekyll-titles-from-headings jekyll-sitemap
jekyll serve
```

## Estrutura

- `_layouts/` — casca da marca (`default.html`) e layout dos posts (`post.html`)
- `_includes/` — botão de compra (`cta.html`) e rastreadores (`analytics.html`)
- `assets/css/style.css` — todo o CSS do site
- `obrigado/` — página de redirect pós-compra configurada no Kiwify
