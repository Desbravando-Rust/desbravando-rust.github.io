# Landing page de vendas — Desbravando Rust

**Data:** 2026-07-02
**Objetivo:** Substituir a home atual (README.md renderizado) por uma landing page de vendas com checkout Kiwify, mantendo o blog em markdown e a hospedagem no GitHub Pages.

## Contexto

- Site hospedado no GitHub Pages com domínio próprio (`desbravandorust.com.br`, via CNAME).
- Hoje não há `_config.yml`: o Jekyll padrão do Pages renderiza `README.md` como home e `posts/NNNN-slug/README.md` com o tema default, dependendo dos plugins habilitados por padrão no Pages (`jekyll-readme-index`, `jekyll-relative-links`, `jekyll-optional-front-matter`, `jekyll-titles-from-headings`, `jekyll-sitemap`).
- A página `obrigado/index.html` define a identidade visual da marca: fundo dark (`#141e30`), laranja Rust (`#f74c00`), cards com glow — alinhada à capa do livro (gradiente vinho→laranja).
- Existe um GitHub Action (`blog-agent`) que gera posts criando pasta + `README.md`; esse fluxo não pode quebrar.

## Decisões

1. **Arquitetura A — Jekyll nativo do GitHub Pages.** Sem build customizado, sem Actions novos, sem dependências. Layout e CSS próprios sobre o Jekyll que o Pages já roda.
2. **Posts continuam markdown puro** em `posts/NNNN-slug/README.md`, sem front matter. O layout da marca é aplicado via `defaults` no `_config.yml`.
3. **Checkout Kiwify:** `https://pay.kiwify.com.br/kDaL3Xq` — preço final **R$ 89,90**. Todo o PIX (QR code, chave copia-e-cola, instruções de comprovante) sai do site.
4. **Sem preço de/por inventado** (risco CDC + público dev fareja âncora falsa). O bloco de preço suporta 3 estados via `_config.yml`:
   - só preço (estado inicial);
   - de/por (se `preco_antigo` for preenchido no futuro);
   - cupom ativo (se `cupom` e `cupom_texto` preenchidos → faixa de destaque no topo do site, pensada para a campanha de engajamento no LinkedIn).
5. **Analytics:** GA4 + Meta Pixel + LinkedIn Insight Tag, IDs no `_config.yml`; cada snippet só é incluído se o ID estiver preenchido. Clique em qualquer CTA de compra dispara evento de conversão antes do redirect ao Kiwify.

## Estrutura de arquivos

```
├── _config.yml              # título, url, link Kiwify, preço, cupom, IDs de analytics, defaults de layout
├── _layouts/
│   ├── default.html         # casca da marca: header fixo + CTA, faixa de cupom, footer, meta/OG, pixels
│   └── post.html            # herda default + banner de compra no fim do post
├── _includes/
│   └── cta.html             # botão "Comprar agora" reutilizável (lê link/preço do _config.yml)
├── assets/css/style.css     # CSS único do site (dark/laranja, responsivo, syntax highlighting Rouge)
├── index.html               # landing page de vendas
├── blog/index.html          # índice completo de posts (gerado por loop Liquid sobre site.pages)
├── amostra/index.md         # página do capítulo gratuito
├── 404.html                 # página 404 com CTA
├── posts/…                  # INTOCADOS: pasta + README.md em markdown
├── obrigado/index.html      # mantém; vira URL de redirect pós-compra do Kiwify; remove bloco de comprovante
└── README.md                # volta a ser README curto de repositório (index.html assume a home)
```

## Landing page (`index.html`) — seções em ordem de funil

Visual: fundo escuro com gradiente vinho→laranja seguindo a capa; laranja `#f74c00` reservado quase exclusivamente aos CTAs.

1. **Hero** — capa com glow + título + subtítulo ("Um guia prático para pythonistas explorarem novos horizontes") + 3 bullets de valor (performance, segurança de memória, sem abandonar o que já sabe) + botão **Comprar agora — R$ 89,90** + link secundário "Ler capítulo gratuito". Acima da dobra em desktop e mobile.
2. **Prova social** — 2–3 depoimentos curtos (nome + cargo; foto opcional). Textos fornecidos pelo autor na implementação; blocos HTML copiáveis para adicionar mais.
3. **Para quem é / o que você vai aprender** — conteúdo atual do README reescrito em cards escaneáveis (Ownership/Borrowing/Lifetimes, tratamento de erros, concorrência, projetos práticos: Axum, TOTP/Lambdas, concatenação de arquivos).
4. **Dentro do livro** — sumário completo em `<details>` expansível + números concretos (páginas, capítulos, projetos). Dados fornecidos pelo autor.
5. **Capítulo gratuito** — CTA secundário para `/amostra` (isca da campanha LinkedIn; reduz risco percebido).
6. **Sobre o autor** — foto redonda, texto enxuto (~3 linhas) focado em autoridade: 22 anos de web, Python → Rust.
7. **Preço + CTA final** — card de compra: capa mini, o que está incluído (PDF + atualizações + nota fiscal), bloco de preço (3 estados), botão Kiwify, selo "compra segura via Kiwify", garantia de 7 dias explícita.
8. **FAQ** — 4–5 `<details>`: quanto de Python preciso? formato e prazo de entrega? garantia? nota fiscal? cupom (quando ativo)?
9. **Últimos posts** — 6 mais recentes em cards + link "ver todos" para `/blog`.

## Blog

- **Header fixo da marca em todas as páginas**: nome à esquerda, botão compacto "Comprar o livro" à direita (visível também no mobile).
- **`_layouts/post.html`**: coluna de leitura ~720px, tipografia confortável, code blocks Rouge estilizados no tema dark, imagens responsivas com `loading="lazy"`.
- **Banner de venda no fim de cada post**: capa mini + chamada + CTA.
- **`/blog`**: índice completo gerado automaticamente — loop Liquid sobre `site.pages` filtrando `path` que começa com `posts/`, ordenado pelo prefixo numérico decrescente. Título vem do primeiro `#` de cada README (`jekyll-titles-from-headings`). Post novo aparece em `/blog` e na home sem edição manual.
- Fluxo de criação de post permanece: criar pasta `posts/NNNN-slug/`, escrever `README.md`, commit. Compatível com o `blog_agent.py` existente.

## SEO e compartilhamento

- **Open Graph/Twitter cards em todas as páginas**: título, descrição e imagem (capa na home; `imgs/cover.png` do post quando existir, capa como fallback). Item crítico para a campanha de repostagens no LinkedIn.
- Meta description e canonical por página; sitemap automático (plugin já ativo).
- **Padrão de UTM para campanhas** (documentação, não código): `https://desbravandorust.com.br/?utm_source=linkedin&utm_medium=social&utm_campaign=<nome-da-campanha>` — o GA4 reporta origem e conversão por campanha.

## Detalhes de implementação

- `exclude` no `_config.yml` para `docs/`, `scripts/`, `temas.md`, `Pipfile*` — nada disso deve ser publicado no site.

## Insumos pendentes do autor (a fornecer durante a implementação)

- Textos dos depoimentos (nome + cargo; foto opcional).
- Sumário completo do livro e números (páginas, capítulos, projetos).
- PDF ou conteúdo do capítulo de amostra.
- IDs de GA4, Meta Pixel e LinkedIn Insight Tag (placeholders vazios até lá — snippets não carregam sem ID).

## Fora de escopo (adicionar depois se necessário)

- Captura de e-mail/newsletter (exige serviço externo).
- Contador regressivo de oferta.
- Chat/WhatsApp flutuante.
- Migração dos posts para outro formato (markdown atende).

## Critérios de sucesso

- Home nova no ar via GitHub Pages sem workflow adicional, responsiva (desktop/mobile).
- CTA leva ao checkout Kiwify e registra evento nos três rastreadores.
- Trocar preço/cupom/link = editar somente `_config.yml`.
- Os 17 posts existentes renderizam com o visual novo sem nenhuma edição neles.
- Post novo (pasta + README.md) aparece automaticamente em `/blog` e na home.
- Compartilhar home ou post no LinkedIn gera card com imagem e título corretos.
