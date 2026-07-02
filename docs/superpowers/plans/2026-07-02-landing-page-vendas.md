# Landing Page de Vendas — Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Substituir a home (README renderizado) por uma landing page de vendas com checkout Kiwify, aplicando a identidade da marca a todos os posts, sobre o Jekyll nativo do GitHub Pages.

**Architecture:** Jekyll nativo do GitHub Pages (sem Actions/build custom). Um layout base (`default.html`) carrega marca, SEO/OG e analytics; um layout de post herda dele. Posts continuam `posts/NNNN-slug/README.md` em markdown puro — os plugins padrão do Pages (`jekyll-readme-index`, `jekyll-titles-from-headings`, etc.) fazem o resto. Tudo que é "de venda" (link Kiwify, preço, cupom, IDs de analytics) vive no `_config.yml`.

**Tech Stack:** Jekyll (GitHub Pages), Liquid, HTML/CSS puro (zero framework JS), plugins whitelisted do Pages.

## Global Constraints

- Checkout: `https://pay.kiwify.com.br/kDaL3Xq` — preço final `R$ 89,90` (sem preço âncora inventado).
- Posts em `posts/NNNN-slug/README.md` **não podem ser editados** — o visual vem 100% de layout/defaults.
- Hospedagem: GitHub Pages com Jekyll padrão (só plugins whitelisted; GH Pages roda Jekyll 3.10 — usar apenas Liquid compatível).
- Responsivo desktop/mobile; sem dependência JS externa além dos snippets de analytics.
- Todo texto do site em pt-BR.
- Trocar preço/cupom/link/IDs = editar apenas `_config.yml`.
- Verificação local: `jekyll build --trace` (Jekyll 4.4.1 instalado com os plugins). Se falhar com `cannot load ... jekyll-readme-index`, prefixar comandos com `GEM_PATH="$(ruby -e 'print Gem.user_dir')"`.
- Commits locais a cada task; **não fazer push** (regra do usuário: push só quando pedido).

---

### Task 1: `_config.yml` — configuração central

**Files:**
- Create: `_config.yml`

**Interfaces:**
- Produces: variáveis Liquid usadas por todas as tasks seguintes: `site.kiwify_url`, `site.preco`, `site.preco_antigo`, `site.cupom`, `site.cupom_texto`, `site.paginas`, `site.capitulos`, `site.ga4_id`, `site.meta_pixel_id`, `site.linkedin_partner_id`, `site.tagline`, `site.email`. Defaults aplicam `layout: default` a todas as páginas e `layout: post` a `posts/**`.

- [ ] **Step 1: Criar `_config.yml`**

```yaml
title: Desbravando Rust
tagline: Um guia prático para pythonistas explorarem novos horizontes
description: >-
  Guia técnico para desenvolvedores Python que querem dominar Rust:
  ownership, tratamento de erros, concorrência e projetos práticos.
url: "https://desbravandorust.com.br"
lang: pt-BR
author: José Luis da Cruz Junior
email: desbravandorust@gmail.com

# ================= VENDA — edite aqui =================
kiwify_url: "https://pay.kiwify.com.br/kDaL3Xq"
preco: "89,90"
preco_antigo: ""   # preencha (ex: "129,90") para exibir "de R$ 129,90 por R$ 89,90"
cupom: ""          # preencha (ex: "LINKEDIN10") para exibir a faixa de cupom no topo do site
cupom_texto: ""    # ex: "10% de desconto para a comunidade do LinkedIn"

# Números do livro (aparecem na seção "Dentro do livro" quando preenchidos)
paginas: ""        # ex: "320"
capitulos: ""      # ex: "18"

# ================= ANALYTICS — edite aqui =================
ga4_id: ""              # ex: "G-XXXXXXXXXX"
meta_pixel_id: ""       # ex: "1234567890"
linkedin_partner_id: "" # ex: "123456"

plugins:
  - jekyll-optional-front-matter
  - jekyll-readme-index
  - jekyll-relative-links
  - jekyll-titles-from-headings
  - jekyll-sitemap

relative_links:
  enabled: true
  collections: false

titles_from_headings:
  enabled: true
  strip_title: false
  collections: false

defaults:
  - scope:
      path: ""
    values:
      layout: default
  - scope:
      path: "posts"
    values:
      layout: post

exclude:
  - docs
  - scripts
  - temas.md
  - Pipfile
  - Pipfile.lock
  - README.md
  - Gemfile
  - Gemfile.lock
  - vendor
```

- [ ] **Step 2: Rodar o build e verificar plugins/exclude**

Run:
```bash
jekyll build --trace && ls _site/posts/0017-orm-mentindo-n1-sqlx/index.html && ls _site/docs 2>&1; ls _site/temas.html _site/temas.md 2>&1
```
Expected: build OK (warnings "Layout 'post'/'default' requested ... does not exist" são esperados nesta task); `_site/posts/0017-orm-mentindo-n1-sqlx/index.html` existe (readme-index funcionando); `_site/docs` e `_site/temas.*` → "No such file or directory" (exclude funcionando).

- [ ] **Step 3: Verificar título extraído do heading**

Run: `grep -o "<title>[^<]*" _site/posts/0017-orm-mentindo-n1-sqlx/index.html || grep -o "Seu ORM está mentindo" _site/posts/0017-orm-mentindo-n1-sqlx/index.html | head -1`
Expected: conteúdo do post presente (sem layout ainda, o `<title>` pode não existir; o grep do texto do h1 deve retornar `Seu ORM está mentindo`).

- [ ] **Step 4: Garantir que `_site` está no `.gitignore`**

`.gitignore` atual tem 14 bytes; conferir com `cat .gitignore`. Se `_site` não estiver listado, adicionar as linhas:
```
_site/
.jekyll-cache/
```

- [ ] **Step 5: Commit**

```bash
git add _config.yml .gitignore
git commit -m "feat: _config.yml central (venda, analytics, defaults de layout)"
```

---

### Task 2: Casca da marca — layout base, CTA, analytics e CSS base

**Files:**
- Create: `_layouts/default.html`
- Create: `_includes/cta.html`
- Create: `_includes/analytics.html`
- Create: `assets/css/style.css`

**Interfaces:**
- Consumes: variáveis do `_config.yml` (Task 1).
- Produces: layout `default` (header fixo + faixa de cupom + footer + SEO/OG + analytics) que envolve `{{ content }}`; include `cta.html` (aceita `include.label` opcional; classes `.btn .btn-buy .js-buy`); include `analytics.html` (snippets condicionais + listener de clique em `.js-buy` disparando `begin_checkout`/`InitiateCheckout`); classes CSS base: `.container`, `.btn`, `.btn-buy`, `.btn-ghost`, `.coupon-bar`, `.site-header`, `.site-footer`.

- [ ] **Step 1: Criar `_includes/cta.html`**

```html
{% if include.label %}{% assign cta_label = include.label %}{% else %}{% assign cta_label = "Comprar agora — R$ " | append: site.preco %}{% endif %}
<a class="btn btn-buy js-buy" href="{{ site.kiwify_url }}" rel="noopener">{{ cta_label }}</a>
```

- [ ] **Step 2: Criar `_includes/analytics.html`**

```html
{% if site.ga4_id != "" %}
<script async src="https://www.googletagmanager.com/gtag/js?id={{ site.ga4_id }}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', '{{ site.ga4_id }}');
</script>
{% endif %}
{% if site.meta_pixel_id != "" %}
<script>
  !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
  n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
  n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
  t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
  document,'script','https://connect.facebook.net/en_US/fbevents.js');
  fbq('init', '{{ site.meta_pixel_id }}');
  fbq('track', 'PageView');
</script>
{% endif %}
{% if site.linkedin_partner_id != "" %}
<script>
  _linkedin_partner_id = "{{ site.linkedin_partner_id }}";
  window._linkedin_data_partner_ids = window._linkedin_data_partner_ids || [];
  window._linkedin_data_partner_ids.push(_linkedin_partner_id);
  (function(l){if(!l){window.lintrk=function(a,b){window.lintrk.q.push([a,b])};window.lintrk.q=[]}
  var s=document.getElementsByTagName("script")[0];var b=document.createElement("script");
  b.type="text/javascript";b.async=true;b.src="https://snap.licdn.com/li.lms-analytics/insight.min.js";
  s.parentNode.insertBefore(b,s)})(window.lintrk);
</script>
{% endif %}
<script>
  document.addEventListener('click', function (e) {
    var a = e.target.closest ? e.target.closest('.js-buy') : null;
    if (!a) return;
    if (window.gtag) gtag('event', 'begin_checkout', { currency: 'BRL', value: {{ site.preco | replace: ",", "." }} });
    if (window.fbq) fbq('track', 'InitiateCheckout');
  });
</script>
```

- [ ] **Step 3: Criar `_layouts/default.html`**

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  {% if page.title %}<title>{{ page.title }} — {{ site.title }}</title>{% else %}<title>{{ site.title }} — {{ site.tagline }}</title>{% endif %}
  <meta name="description" content="{{ page.description | default: site.description | strip_newlines | strip }}">
  <link rel="canonical" href="{{ page.url | absolute_url }}">
  {% assign og_image = "/imgs/capa.jpg" %}
  {% assign cover_candidate = page.dir | append: "imgs/cover.png" %}
  {% assign cover = site.static_files | where: "path", cover_candidate | first %}
  {% if cover %}{% assign og_image = cover_candidate %}{% endif %}
  <meta property="og:type" content="website">
  <meta property="og:locale" content="pt_BR">
  <meta property="og:site_name" content="{{ site.title }}">
  <meta property="og:title" content="{{ page.title | default: site.title }}">
  <meta property="og:description" content="{{ page.description | default: site.description | strip_newlines | strip }}">
  <meta property="og:url" content="{{ page.url | absolute_url }}">
  <meta property="og:image" content="{{ og_image | absolute_url }}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{{ page.title | default: site.title }}">
  <meta name="twitter:image" content="{{ og_image | absolute_url }}">
  <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
  {% if site.cupom != "" %}
  <div class="coupon-bar">🎟️ {{ site.cupom_texto }} — use o cupom <b>{{ site.cupom }}</b> no checkout</div>
  {% endif %}
  <header class="site-header">
    <div class="container header-inner">
      <a class="brand" href="/">Desbravando <span>Rust</span></a>
      {% include cta.html label="Comprar o livro" %}
    </div>
  </header>
  <main>
    {{ content }}
  </main>
  <footer class="site-footer">
    <div class="container">
      <nav class="footer-links">
        <a href="/">Início</a>
        <a href="/blog/">Blog</a>
        <a href="/amostra/">Capítulo gratuito</a>
      </nav>
      <p>Dúvidas? <a href="mailto:{{ site.email }}">{{ site.email }}</a></p>
      <p class="copy">© {{ site.time | date: "%Y" }} {{ site.author }} — {{ site.title }}</p>
    </div>
  </footer>
  {% include analytics.html %}
</body>
</html>
```

- [ ] **Step 4: Criar `assets/css/style.css` (base)**

```css
/* ===== Desbravando Rust — tema (paleta da capa/obrigado) ===== */
:root {
  --bg: #141e30;
  --bg-deep: #0e1524;
  --bg-card: #1b2740;
  --border: #2a3850;
  --rust-orange: #f74c00;
  --rust-orange-soft: #ff7a3d;
  --text: #e8edf5;
  --text-muted: #b8c2d0;
  --accent-glow: rgba(247, 76, 0, 0.35);
  --green: #7ed957;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

html { background: var(--bg); scroll-behavior: smooth; }

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background: radial-gradient(ellipse at top, #1d2b47 0%, var(--bg) 55%);
  color: var(--text);
  line-height: 1.6;
}

img { max-width: 100%; height: auto; }

a { color: var(--rust-orange-soft); }

.container { max-width: 1080px; margin: 0 auto; padding: 0 24px; }

/* ===== Botões ===== */
.btn {
  display: inline-block;
  padding: 14px 28px;
  border-radius: 8px;
  font-weight: 700;
  text-decoration: none;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.btn:hover { transform: translateY(-2px); }

.btn-buy {
  background: var(--rust-orange);
  color: #fff;
  box-shadow: 0 6px 18px var(--accent-glow);
}

.btn-ghost {
  border: 1px solid #3a4a68;
  color: var(--text-muted);
}

.btn-ghost:hover { color: var(--text); border-color: var(--rust-orange-soft); }

/* ===== Faixa de cupom ===== */
.coupon-bar {
  background: var(--rust-orange);
  color: #fff;
  text-align: center;
  padding: 10px 16px;
  font-size: 0.95rem;
}

/* ===== Header ===== */
.site-header {
  position: sticky;
  top: 0;
  z-index: 10;
  background: rgba(14, 21, 36, 0.92);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--border);
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 12px;
  padding-bottom: 12px;
}

.brand {
  font-weight: 800;
  font-size: 1.15rem;
  color: var(--text);
  text-decoration: none;
}

.brand span { color: var(--rust-orange-soft); }

.site-header .btn { padding: 9px 18px; font-size: 0.9rem; }

/* ===== Footer ===== */
.site-footer {
  margin-top: 80px;
  border-top: 1px solid var(--border);
  background: var(--bg-deep);
  padding: 32px 0;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.footer-links { display: flex; gap: 20px; justify-content: center; margin-bottom: 12px; }

.footer-links a { color: var(--text-muted); text-decoration: none; }

.footer-links a:hover { color: var(--rust-orange-soft); }

.site-footer .copy { margin-top: 8px; color: #7d8aa0; }

@media (max-width: 720px) {
  .site-header .btn { padding: 8px 12px; font-size: 0.8rem; }
}
```

- [ ] **Step 5: Build e verificar arquivos copiados**

Nesta task nenhuma página usa o layout `default` ainda (o `index.html` só nasce na Task 4 e os posts usam `post`, criado na Task 3) — a validação aqui é o build passar e os assets saírem no `_site`. A validação renderizada do layout acontece na Task 3.

Run:
```bash
jekyll build --trace && ls _site/assets/css/style.css
```
Expected: build OK (warning "Layout 'post' requested ... does not exist" ainda esperado até a Task 3) e `_site/assets/css/style.css` presente.

- [ ] **Step 6: Commit**

```bash
git add _layouts/default.html _includes/cta.html _includes/analytics.html assets/css/style.css
git commit -m "feat: layout base da marca (header CTA, SEO/OG, analytics, CSS base)"
```

---

### Task 3: Layout de post — coluna de leitura, Rouge dark, banner de venda

**Files:**
- Create: `_layouts/post.html`
- Modify: `assets/css/style.css` (append ao final)

**Interfaces:**
- Consumes: layout `default`, include `cta.html`, classes `.btn`, `.container` (Task 2).
- Produces: layout `post` aplicado automaticamente a `posts/**` (defaults da Task 1); classes `.post`, `.post-cta`.

- [ ] **Step 1: Criar `_layouts/post.html`**

```html
---
layout: default
---
<article class="post">
  {{ content }}
</article>
<aside class="post-cta">
  <img src="/imgs/capa.jpg" alt="Capa do livro Desbravando Rust" loading="lazy">
  <div>
    <h2>Gostou deste conteúdo?</h2>
    <p>O livro <b>Desbravando Rust</b> aprofunda tudo isso: ownership, erros, concorrência e projetos
      práticos — escrito para quem vem do Python.</p>
    {% include cta.html %}
  </div>
</aside>
```

- [ ] **Step 2: Append no `assets/css/style.css`**

```css
/* ===== Post (coluna de leitura) ===== */
.post {
  max-width: 760px;
  margin: 48px auto 0;
  padding: 0 24px;
}

.post h1 { font-size: 2rem; line-height: 1.25; margin-bottom: 8px; }

.post h2, .post h3 { margin: 32px 0 12px; }

.post h6 { color: #7d8aa0; font-weight: 500; margin-bottom: 24px; }

.post p, .post li { color: var(--text-muted); margin-bottom: 14px; }

.post li { margin-left: 24px; margin-bottom: 6px; }

.post strong, .post b { color: var(--text); }

.post img { border-radius: 8px; margin: 16px 0; }

.post blockquote {
  border-left: 3px solid var(--rust-orange);
  background: rgba(247, 76, 0, 0.08);
  padding: 12px 20px;
  border-radius: 0 8px 8px 0;
  margin: 16px 0;
}

.post table { border-collapse: collapse; margin: 16px 0; width: 100%; display: block; overflow-x: auto; }

.post th, .post td { border: 1px solid var(--border); padding: 8px 12px; color: var(--text-muted); }

.post th { color: var(--text); background: var(--bg-card); }

.post code {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
  font-size: 0.9em;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 1px 6px;
  color: var(--rust-orange-soft);
}

.post pre {
  background: var(--bg-deep);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px;
  overflow-x: auto;
  margin: 16px 0;
}

.post pre code { background: none; border: none; padding: 0; color: var(--text); }

/* ===== Rouge (syntax highlighting dark) ===== */
.highlight .c, .highlight .c1, .highlight .cm { color: #6a7891; font-style: italic; }
.highlight .k, .highlight .kd, .highlight .kn, .highlight .kr { color: #ff7a3d; }
.highlight .kt, .highlight .kc { color: #e5c07b; }
.highlight .s, .highlight .s1, .highlight .s2, .highlight .sb { color: #98c379; }
.highlight .mi, .highlight .mf, .highlight .mh { color: #d19a66; }
.highlight .nf, .highlight .fm { color: #61afef; }
.highlight .nc, .highlight .nn { color: #e5c07b; }
.highlight .n, .highlight .nx { color: #e8edf5; }
.highlight .o, .highlight .p { color: #b8c2d0; }
.highlight .nb, .highlight .bp { color: #56b6c2; }
.highlight .na, .highlight .nd { color: #d19a66; }
.highlight .err { color: #e8edf5; background: transparent; }

/* ===== Banner de venda no fim do post ===== */
.post-cta {
  max-width: 760px;
  margin: 56px auto 0;
  padding: 28px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-top: 4px solid var(--rust-orange);
  border-radius: 12px;
  display: flex;
  gap: 24px;
  align-items: center;
}

.post-cta img {
  width: 110px;
  flex-shrink: 0;
  border-radius: 6px;
  box-shadow: 0 0 20px var(--accent-glow);
  margin: 0;
}

.post-cta h2 { margin-bottom: 8px; font-size: 1.3rem; }

.post-cta p { color: var(--text-muted); margin-bottom: 16px; }

@media (max-width: 720px) {
  .post-cta { flex-direction: column; text-align: center; margin-left: 24px; margin-right: 24px; }
}
```

- [ ] **Step 3: Build e verificar post completo**

Run:
```bash
jekyll build --trace && grep -c "post-cta" _site/posts/0017-orm-mentindo-n1-sqlx/index.html && grep -c "class=\"highlight\"" _site/posts/0017-orm-mentindo-n1-sqlx/index.html && grep -o "<title>[^<]*</title>" _site/posts/0017-orm-mentindo-n1-sqlx/index.html && grep -o "og:image\" content=\"[^\"]*" _site/posts/0017-orm-mentindo-n1-sqlx/index.html
```
Expected: build sem warnings de layout; `post-cta` ≥ 1; `highlight` ≥ 1 (code blocks); `<title>Seu ORM está mentindo para você (Parte II): o N+1 que o SQLx te obriga a enxergar — Desbravando Rust</title>`; og:image apontando para `https://desbravandorust.com.br/posts/0017-orm-mentindo-n1-sqlx/imgs/cover.png` (o post tem cover; fallback capa é validado na Task 4 com a home).

- [ ] **Step 4: Verificar visualmente 2 posts no navegador (spot check)**

Run: `jekyll serve --port 4001 &` e abrir `http://localhost:4001/posts/0017-orm-mentindo-n1-sqlx/` e `http://localhost:4001/posts/0002-pandas-vs-polars/`. Conferir: header com CTA, código legível no dark, tabelas/imagens ok, banner no fim, mobile (devtools). Encerrar o serve depois.

- [ ] **Step 5: Commit**

```bash
git add _layouts/post.html assets/css/style.css
git commit -m "feat: layout de post (leitura, rouge dark, banner de venda)"
```

---

### Task 4: Landing page (`index.html`) + dados editáveis

**Files:**
- Create: `index.html`
- Create: `_data/depoimentos.yml`
- Create: `_data/sumario.yml`
- Modify: `assets/css/style.css` (append ao final)

**Interfaces:**
- Consumes: layout `default`, include `cta.html`, variáveis do config (Tasks 1–2).
- Produces: home de vendas; classes `.post-card`/`.post-grid` (reutilizadas pela Task 5); seções ocultas automaticamente quando `_data/*.yml` estiver vazio.

- [ ] **Step 1: Criar `_data/depoimentos.yml`**

```yaml
# Depoimentos de leitores — a seção só aparece na home quando houver ao menos um.
# Formato (remova o "#" para ativar):
# - nome: "Fulano de Tal"
#   cargo: "Backend Engineer"
#   texto: "Uma frase curta sobre o que o livro destravou para você."
```

- [ ] **Step 2: Criar `_data/sumario.yml`**

```yaml
# Sumário do livro — a seção "Dentro do livro" só lista capítulos quando houver ao menos um.
# Formato (remova o "#" para ativar):
# - "1. Do zen do Python ao rigor do Rust"
# - "2. Sintaxe e estruturas de dados"
```

- [ ] **Step 3: Criar `index.html`**

```html
---
layout: default
description: >-
  Desbravando Rust — guia prático para desenvolvedores Python dominarem Rust:
  ownership, tratamento de erros, concorrência e projetos reais. Compre o livro digital.
---
<!-- ============ HERO ============ -->
<section class="hero">
  <div class="container hero-inner">
    <div class="hero-copy">
      <h1>Desbravando <span>Rust</span></h1>
      <p class="hero-tagline">{{ site.tagline }}</p>
      <ul class="hero-bullets">
        <li>Conceitos lado a lado: cada tema de Rust comparado com o Python que você já domina</li>
        <li>Ownership, Borrowing e Lifetimes explicados sem sofrimento</li>
        <li>Projetos reais: API REST com Axum, TOTP com Lambdas, CLI de arquivos</li>
      </ul>
      <div class="hero-actions">
        {% include cta.html %}
        <a class="btn btn-ghost" href="/amostra/">Ler capítulo gratuito</a>
      </div>
    </div>
    <div class="hero-cover">
      <img src="/imgs/capa.jpg" alt="Capa do livro Desbravando Rust">
    </div>
  </div>
</section>

<!-- ============ DEPOIMENTOS ============ -->
{% if site.data.depoimentos and site.data.depoimentos.size > 0 %}
<section class="social-proof">
  <div class="container">
    <h2>Quem leu, recomenda</h2>
    <div class="quotes">
      {% for d in site.data.depoimentos %}
      <blockquote class="quote">
        <p>“{{ d.texto }}”</p>
        <footer><b>{{ d.nome }}</b>{% if d.cargo %} — {{ d.cargo }}{% endif %}</footer>
      </blockquote>
      {% endfor %}
    </div>
  </div>
</section>
{% endif %}

<!-- ============ O QUE VOCÊ VAI APRENDER ============ -->
<section class="learn">
  <div class="container">
    <h2>Feito para quem vem do Python</h2>
    <p class="section-sub">Você não vai recomeçar do zero — vai traduzir o que já sabe para uma
      linguagem com performance de C e segurança de memória garantida em compilação.</p>
    <div class="learn-grid">
      <div class="learn-card">
        <h3>🧭 Sintaxe e estruturas</h3>
        <p>As particularidades de Rust sempre comparadas com o equivalente em Python.</p>
      </div>
      <div class="learn-card">
        <h3>🧠 Gerenciamento de memória</h3>
        <p>Ownership, Borrowing e Lifetimes — o coração da segurança de Rust, desmistificado.</p>
      </div>
      <div class="learn-card">
        <h3>🛡️ Tratamento de erros</h3>
        <p>Result e Option no lugar de exceções: erros robustos e idiomáticos.</p>
      </div>
      <div class="learn-card">
        <h3>⚡ Concorrência e paralelismo</h3>
        <p>Threads e async/await sem GIL e sem data races.</p>
      </div>
      <div class="learn-card">
        <h3>🔨 Projetos práticos</h3>
        <p>API REST de agendamento com Axum, TOTP com Lambdas, concatenação de arquivos.</p>
      </div>
      <div class="learn-card">
        <h3>🚀 Do zero ao deploy</h3>
        <p>Cargo, tooling e as melhores práticas do ecossistema desde o primeiro capítulo.</p>
      </div>
    </div>
  </div>
</section>

<!-- ============ DENTRO DO LIVRO ============ -->
<section class="inside">
  <div class="container">
    <h2>Dentro do livro</h2>
    {% if site.paginas != "" or site.capitulos != "" %}
    <div class="stats">
      {% if site.paginas != "" %}<div class="stat"><b>{{ site.paginas }}</b><span>páginas</span></div>{% endif %}
      {% if site.capitulos != "" %}<div class="stat"><b>{{ site.capitulos }}</b><span>capítulos</span></div>{% endif %}
      <div class="stat"><b>3</b><span>projetos completos</span></div>
    </div>
    {% endif %}
    {% if site.data.sumario and site.data.sumario.size > 0 %}
    <details class="toc">
      <summary>Ver o sumário completo</summary>
      <ol>
        {% for cap in site.data.sumario %}
        <li>{{ cap }}</li>
        {% endfor %}
      </ol>
    </details>
    {% endif %}
    <p class="sample-nudge">Quer sentir o estilo antes de comprar?
      <a href="/amostra/">Leia um capítulo gratuito →</a></p>
  </div>
</section>

<!-- ============ AUTOR ============ -->
<section class="author">
  <div class="container author-inner">
    <img src="/imgs/profile1.jpg" alt="Foto de José Luis da Cruz Junior" loading="lazy">
    <div>
      <h2>Quem escreveu</h2>
      <p><b>José Luis da Cruz Junior</b> — mais de 22 anos de desenvolvimento web, carreira sólida
        construída em Python e hoje dedicado a explorar o poder de Rust.</p>
      <p>Este livro é o caminho que ele gostaria de ter tido: claro, prático e sem exigir que você
        abandone o que já sabe.</p>
    </div>
  </div>
</section>

<!-- ============ PREÇO + CTA FINAL ============ -->
<section class="buy" id="comprar">
  <div class="container">
    <div class="buy-card">
      <img src="/imgs/capa.jpg" alt="Capa do livro Desbravando Rust" loading="lazy">
      <div class="buy-info">
        <h2>Garanta seu exemplar</h2>
        <ul class="buy-includes">
          <li>✔ Livro digital em PDF</li>
          <li>✔ Entrega imediata por e-mail após a confirmação do pagamento</li>
          <li>✔ Nota fiscal inclusa</li>
          <li>✔ Garantia incondicional de 7 dias</li>
        </ul>
        <div class="price-block">
          {% if site.preco_antigo != "" %}<span class="price-old">R$ {{ site.preco_antigo }}</span>{% endif %}
          <span class="price">R$ {{ site.preco }}</span>
        </div>
        {% if site.cupom != "" %}
        <p class="coupon-note">🎟️ {{ site.cupom_texto }} — use o cupom <b>{{ site.cupom }}</b> no checkout</p>
        {% endif %}
        {% include cta.html %}
        <p class="secure">🔒 Compra processada com segurança pela Kiwify · cartão, PIX ou boleto</p>
      </div>
    </div>
  </div>
</section>

<!-- ============ FAQ ============ -->
<section class="faq">
  <div class="container">
    <h2>Perguntas frequentes</h2>
    <details><summary>Preciso ser avançado em Python?</summary>
      <p>Não. Se você já escreve Python no dia a dia — funções, classes, pip/venv — tem toda a base
        necessária. O livro usa seu conhecimento de Python como ponte, não como pré-requisito acadêmico.</p>
    </details>
    <details><summary>Como e quando recebo o livro?</summary>
      <p>A compra é processada pela Kiwify. Assim que o pagamento é confirmado, você recebe por e-mail
        o acesso ao PDF — sem espera.</p>
    </details>
    <details><summary>E se eu não gostar?</summary>
      <p>Você tem 7 dias de garantia incondicional: pediu reembolso dentro do prazo, recebeu de volta.
        Sem perguntas.</p>
    </details>
    <details><summary>Recebo nota fiscal?</summary>
      <p>Sim, a nota fiscal é emitida e enviada para o seu e-mail.</p>
    </details>
    <details><summary>Quais formas de pagamento?</summary>
      <p>Cartão de crédito, PIX e boleto — tudo pelo checkout seguro da Kiwify.</p>
    </details>
  </div>
</section>

<!-- ============ ÚLTIMOS POSTS ============ -->
<section class="recent-posts" id="blog">
  <div class="container">
    <h2>Do blog</h2>
    <p class="section-sub">Benchmarks reais, Rust acelerando Python e muito código para reproduzir.</p>
    {% assign blog_posts = site.pages | where_exp: "p", "p.path contains 'posts/'" | sort: "path" | reverse %}
    <div class="post-grid">
      {% for p in blog_posts limit: 6 %}
      {% assign post_num = p.dir | split: "/" | last | split: "-" | first %}
      <a class="post-card" href="{{ p.url }}">
        <span class="post-num">#{{ post_num }}</span>
        <h3>{{ p.title }}</h3>
      </a>
      {% endfor %}
    </div>
    <p class="all-posts"><a href="/blog/">Ver todos os posts →</a></p>
  </div>
</section>
```

- [ ] **Step 4: Append no `assets/css/style.css`**

```css
/* ===== Landing: hero ===== */
.hero { padding: 72px 0 56px; }

.hero-inner { display: flex; align-items: center; gap: 56px; }

.hero-copy { flex: 1; min-width: 0; }

.hero h1 { font-size: 3rem; font-weight: 800; line-height: 1.1; }

.hero h1 span { color: var(--rust-orange-soft); }

.hero-tagline { font-size: 1.25rem; color: var(--text-muted); margin: 12px 0 20px; }

.hero-bullets { list-style: none; margin-bottom: 28px; }

.hero-bullets li {
  color: var(--text-muted);
  margin-bottom: 10px;
  padding-left: 28px;
  position: relative;
}

.hero-bullets li::before { content: "🦀"; position: absolute; left: 0; }

.hero-actions { display: flex; gap: 14px; flex-wrap: wrap; align-items: center; }

.hero-cover { flex-shrink: 0; }

.hero-cover img {
  width: 300px;
  border-radius: 10px;
  box-shadow: 0 0 40px var(--accent-glow), 0 16px 40px rgba(0, 0, 0, 0.6);
  transform: rotate(2deg);
}

/* ===== Landing: seções genéricas ===== */
.hero, .social-proof, .learn, .inside, .author, .buy, .faq, .recent-posts { padding-top: 56px; }

section > .container > h2 { font-size: 1.9rem; margin-bottom: 8px; }

.section-sub { color: var(--text-muted); margin-bottom: 28px; max-width: 640px; }

/* ===== Depoimentos ===== */
.quotes { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 20px; margin-top: 20px; }

.quote {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-left: 3px solid var(--rust-orange);
  border-radius: 0 10px 10px 0;
  padding: 20px 24px;
}

.quote p { color: var(--text-muted); margin-bottom: 12px; font-style: italic; }

.quote footer { color: var(--text); font-size: 0.9rem; }

/* ===== Cards "o que vai aprender" ===== */
.learn-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-top: 24px; }

.learn-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 24px;
}

.learn-card h3 { margin-bottom: 8px; font-size: 1.05rem; }

.learn-card p { color: var(--text-muted); font-size: 0.95rem; }

/* ===== Dentro do livro ===== */
.stats { display: flex; gap: 40px; margin: 24px 0; flex-wrap: wrap; }

.stat b { font-size: 2.2rem; color: var(--rust-orange-soft); display: block; line-height: 1; }

.stat span { color: var(--text-muted); font-size: 0.9rem; }

.toc {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 18px 24px;
  margin: 20px 0;
}

.toc summary { cursor: pointer; font-weight: 700; }

.toc ol { margin: 16px 0 0 24px; color: var(--text-muted); }

.toc li { margin-bottom: 6px; }

.sample-nudge { color: var(--text-muted); }

/* ===== Autor ===== */
.author-inner { display: flex; gap: 32px; align-items: center; }

.author img {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  border: 3px solid var(--rust-orange);
  object-fit: cover;
  filter: drop-shadow(0 0 10px var(--accent-glow));
  flex-shrink: 0;
}

.author p { color: var(--text-muted); margin-bottom: 10px; max-width: 640px; }

.author b { color: var(--text); }

/* ===== Card de compra ===== */
.buy-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-top: 4px solid var(--rust-orange);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  padding: 40px;
  display: flex;
  gap: 40px;
  align-items: center;
}

.buy-card > img {
  width: 220px;
  flex-shrink: 0;
  border-radius: 8px;
  box-shadow: 0 0 30px var(--accent-glow);
  transform: rotate(-2deg);
}

.buy-includes { list-style: none; margin: 16px 0 20px; }

.buy-includes li { color: var(--text-muted); margin-bottom: 8px; }

.price-block { display: flex; align-items: baseline; gap: 14px; margin-bottom: 8px; }

.price { font-size: 2.4rem; font-weight: 800; color: var(--text); }

.price-old {
  font-size: 1.3rem;
  color: #7d8aa0;
  text-decoration: line-through;
}

.coupon-note { color: var(--green); margin-bottom: 12px; }

.buy .btn-buy { margin-top: 8px; }

.secure { color: #7d8aa0; font-size: 0.85rem; margin-top: 14px; }

/* ===== FAQ ===== */
.faq details {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px 22px;
  margin-top: 12px;
}

.faq summary { cursor: pointer; font-weight: 700; }

.faq details p { color: var(--text-muted); margin-top: 10px; }

/* ===== Cards de posts ===== */
.post-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 24px; }

.post-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 22px;
  text-decoration: none;
  display: block;
  transition: transform 0.15s ease, border-color 0.15s ease;
}

.post-card:hover { transform: translateY(-3px); border-color: var(--rust-orange-soft); }

.post-num { color: var(--rust-orange-soft); font-size: 0.8rem; font-weight: 700; }

.post-card h3 { color: var(--text); font-size: 1.05rem; margin-top: 6px; line-height: 1.4; }

.all-posts { margin-top: 24px; }

/* ===== Responsivo (landing) ===== */
@media (max-width: 860px) {
  .hero-inner { flex-direction: column-reverse; text-align: center; }
  .hero h1 { font-size: 2.2rem; }
  .hero-bullets { text-align: left; }
  .hero-actions { justify-content: center; }
  .hero-cover img { width: 220px; }
  .author-inner { flex-direction: column; text-align: center; }
  .buy-card { flex-direction: column; padding: 28px 20px; text-align: center; }
  .buy-includes { text-align: left; }
  .price-block { justify-content: center; }
}
```

- [ ] **Step 5: Build e verificar a home**

Run:
```bash
jekyll build --trace && grep -c "pay.kiwify.com.br/kDaL3Xq" _site/index.html && grep -c "R$ 89,90" _site/index.html && grep -c "post-card" _site/index.html && grep -o "og:image\" content=\"[^\"]*" _site/index.html && grep -c "price-old" _site/index.html; grep -c "coupon-bar" _site/index.html
```
Expected: kiwify_url ≥ 2 (hero + card de compra + header = 3); `R$ 89,90` ≥ 2; `post-card` = 6; og:image = `https://desbravandorust.com.br/imgs/capa.jpg` (fallback da capa, pois a home não tem `imgs/cover.png` no dir); `price-old` = 0 e `coupon-bar` = 0 (estados desligados com config vazio).

- [ ] **Step 6: Testar os 3 estados do bloco de preço**

Editar temporariamente `_config.yml`: `preco_antigo: "129,90"`, `cupom: "TESTE10"`, `cupom_texto: "10% off de teste"`. Rodar `jekyll build` e verificar:
```bash
grep -c "price-old" _site/index.html && grep -c "coupon-bar" _site/index.html && grep -c "TESTE10" _site/index.html
```
Expected: `price-old` = 1; `coupon-bar` = 1; `TESTE10` ≥ 2 (faixa + nota no card). **Reverter o `_config.yml` para os valores vazios** e rebuildar.

- [ ] **Step 7: Spot check visual da home**

`jekyll serve --port 4001` → conferir hero acima da dobra (desktop e mobile via devtools), CTA visível, seções de depoimentos/sumário ocultas (dados vazios), FAQ abrindo/fechando.

- [ ] **Step 8: Commit**

```bash
git add index.html _data/depoimentos.yml _data/sumario.yml assets/css/style.css
git commit -m "feat: landing page de vendas com CTA Kiwify e estados de preço/cupom"
```

---

### Task 5: Índice completo do blog (`/blog`)

**Files:**
- Create: `blog/index.html`

**Interfaces:**
- Consumes: classes `.post-grid`/`.post-card`/`.post-num` (Task 4), layout `default`.
- Produces: página `/blog/` com todos os posts, ordenados do mais novo para o mais antigo, sem manutenção manual.

- [ ] **Step 1: Criar `blog/index.html`**

```html
---
title: Blog
description: >-
  Artigos técnicos sobre Rust para pythonistas: benchmarks, comparações
  Python vs Rust e projetos práticos com código para reproduzir.
---
<section class="blog-index">
  <div class="container">
    <h1>Blog</h1>
    <p class="section-sub">Benchmarks reais, Rust acelerando Python e muito código para reproduzir.
      Post novo? Ele aparece aqui automaticamente.</p>
    {% assign blog_posts = site.pages | where_exp: "p", "p.path contains 'posts/'" | sort: "path" | reverse %}
    <div class="post-grid">
      {% for p in blog_posts %}
      {% assign post_num = p.dir | split: "/" | last | split: "-" | first %}
      <a class="post-card" href="{{ p.url }}">
        <span class="post-num">#{{ post_num }}</span>
        <h3>{{ p.title }}</h3>
      </a>
      {% endfor %}
    </div>
  </div>
</section>
```

- [ ] **Step 2: Append no `assets/css/style.css`**

```css
/* ===== Página /blog ===== */
.blog-index { padding-top: 56px; }

.blog-index h1 { font-size: 2.2rem; margin-bottom: 8px; }
```

- [ ] **Step 3: Build e verificar índice**

Run:
```bash
jekyll build --trace && grep -c "post-card" _site/blog/index.html && grep -o "href=\"/posts/0017-orm-mentindo-n1-sqlx/\"" _site/blog/index.html && grep -o "#0001" _site/blog/index.html
```
Expected: `post-card` = 17 (todos os posts atuais); link do 0017 presente; `#0001` presente (mais antigo também listado). Conferir também que o primeiro card do HTML é o 0017 (ordem decrescente): `grep -o "#00[0-9][0-9]" _site/blog/index.html | head -1` → `#0017`.

- [ ] **Step 4: Commit**

```bash
git add blog/index.html assets/css/style.css
git commit -m "feat: índice do blog gerado automaticamente"
```

---

### Task 6: Página de amostra gratuito e 404

**Files:**
- Create: `amostra/index.md`
- Create: `404.html`

**Interfaces:**
- Consumes: layout `default`, include `cta.html`, classes `.btn`, `.container`.
- Produces: `/amostra/` (isca de campanha; botão de download aponta para `assets/desbravando-rust-amostra.pdf` — o autor deve colocar o PDF nesse caminho) e `/404.html` com CTA.

- [ ] **Step 1: Criar `amostra/index.md`**

```markdown
---
title: Capítulo gratuito
description: >-
  Baixe gratuitamente um capítulo do livro Desbravando Rust e sinta o estilo
  antes de comprar — comparações diretas entre Python e Rust.
---

<section class="post">

# Leia um capítulo gratuito

Antes de decidir, sinta o estilo do livro: direto, prático e sempre comparando
Rust com o Python que você já domina.

<a class="btn btn-buy" href="/assets/desbravando-rust-amostra.pdf" download>Baixar capítulo em PDF</a>

Gostou do que leu? O livro completo aprofunda ownership, tratamento de erros,
concorrência e três projetos completos.

<a class="btn btn-ghost js-buy" href="{{ site.kiwify_url }}" rel="noopener">Comprar o livro — R$ {{ site.preco }}</a>

</section>
```

- [ ] **Step 2: Criar `404.html`**

```html
---
title: Página não encontrada
permalink: /404.html
sitemap: false
---
<section class="post" style="text-align: center; padding-top: 64px;">
  <h1>404 — trilha não mapeada 🦀</h1>
  <p>Essa página não existe (ou o borrow checker a moveu). Mas a jornada continua:</p>
  <p style="margin-top: 24px;">
    <a class="btn btn-buy js-buy" href="{{ site.kiwify_url }}" rel="noopener">Conhecer o livro — R$ {{ site.preco }}</a>
    <a class="btn btn-ghost" href="/blog/">Ver os posts</a>
  </p>
</section>
```

- [ ] **Step 3: Build e verificar**

Run:
```bash
jekyll build --trace && grep -c "desbravando-rust-amostra.pdf" _site/amostra/index.html && grep -c "kDaL3Xq" _site/amostra/index.html && grep -c "kDaL3Xq" _site/404.html
```
Expected: todos ≥ 1. Nota: o PDF em si ainda não existe — registrado como insumo pendente do autor (colocar em `assets/desbravando-rust-amostra.pdf`).

- [ ] **Step 4: Commit**

```bash
git add amostra/index.md 404.html
git commit -m "feat: página de capítulo gratuito e 404 com CTA"
```

---

### Task 7: Atualizar `/obrigado` e reescrever `README.md`

**Files:**
- Modify: `obrigado/index.html`
- Modify: `README.md` (reescrita completa; já excluído do site na Task 1)

**Interfaces:**
- Consumes: include `analytics.html` (Task 2), `site.preco`/`site.kiwify_url` (Task 1).
- Produces: `/obrigado/` como página de redirect pós-compra do Kiwify, com evento de `purchase` nos rastreadores; README de manutenção do repositório.

- [ ] **Step 1: Adicionar front matter Liquid ao `obrigado/index.html`**

No topo do arquivo, antes de `<!DOCTYPE html>`, adicionar:

```
---
layout: none
sitemap: false
---
```

(`layout: none` mantém o HTML standalone — o design de card centralizado é próprio; o front matter só habilita Liquid.)

- [ ] **Step 2: Remover o bloco comentado do PIX/comprovante**

Deletar do `obrigado/index.html` o bloco entre `<!--` e `-->` que contém "Próximos passos", "comprovante de pagamento" e "2 dias úteis" (linhas 160–167 do arquivo atual).

- [ ] **Step 3: Adicionar analytics + evento de compra antes de `</body>`**

```html
  {% include analytics.html %}
  <script>
    if (window.gtag) gtag('event', 'purchase', { currency: 'BRL', value: {{ site.preco | replace: ",", "." }} });
    if (window.fbq) fbq('track', 'Purchase', { currency: 'BRL', value: {{ site.preco | replace: ",", "." }} });
  </script>
```

- [ ] **Step 4: Trocar links absolutos por relativos no `obrigado/index.html`**

- `href="https://desbravandorust.com.br/#últimos-posts"` → `href="/blog/"` (a âncora antiga deixa de existir)
- `href="https://desbravandorust.com.br"` → `href="/"`

- [ ] **Step 5: Reescrever `README.md` como guia de manutenção do repositório**

```markdown
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
```

- [ ] **Step 6: Build e verificar**

Run:
```bash
jekyll build --trace && grep -c "purchase" _site/obrigado/index.html && grep -c "Próximos passos" _site/obrigado/index.html; grep -c "site-header" _site/obrigado/index.html; ls _site/README.html 2>&1
```
Expected: `purchase` ≥ 1; "Próximos passos" = 0 (bloco removido); `site-header` = 0 (layout none preservou o design standalone); `_site/README.html` → "No such file" (README excluído do site).

- [ ] **Step 7: Commit**

```bash
git add obrigado/index.html README.md
git commit -m "feat: obrigado como redirect pós-compra Kiwify + README de manutenção"
```

---

### Task 8: Verificação final de ponta a ponta

**Files:**
- Nenhum novo (correções pontuais se a verificação falhar).

- [ ] **Step 1: Build limpo completo**

Run: `rm -rf _site .jekyll-cache && jekyll build --trace`
Expected: build sem erros e sem warnings de layout.

- [ ] **Step 2: Checklist automatizado**

Run:
```bash
test -f _site/index.html && \
test -f _site/blog/index.html && \
test -f _site/amostra/index.html && \
test -f _site/404.html && \
test -f _site/obrigado/index.html && \
test -f _site/sitemap.xml && \
test -f _site/posts/0001-performance-na-pratica/index.html && \
test ! -e _site/docs && \
test ! -e _site/README.html && \
echo "TUDO OK"
```
Expected: `TUDO OK`.

- [ ] **Step 3: Conferir links internos dos posts**

Run: `grep -o 'href="../0004-django-orm-vs-sqlx[^"]*"' _site/posts/0017-orm-mentindo-n1-sqlx/index.html`
Expected: link relativo presente e navegável (aponta para o diretório do post 0004, que tem `index.html`).

- [ ] **Step 4: Revisão visual final com o usuário**

`jekyll serve --port 4001` e pedir ao usuário para revisar: home (desktop + mobile), um post, `/blog`, `/amostra`, `/obrigado`. Lembrá-lo dos insumos pendentes: depoimentos (`_data/depoimentos.yml`), sumário (`_data/sumario.yml`), números do livro e IDs de analytics (`_config.yml`), PDF da amostra (`assets/`), e de configurar a URL `https://desbravandorust.com.br/obrigado/` como página de entrega/obrigado no painel do Kiwify.

- [ ] **Step 5: Commit final (se houve correções) — sem push**

```bash
git status
git add -A && git commit -m "chore: ajustes finais da landing page" || echo "nada a commitar"
```
