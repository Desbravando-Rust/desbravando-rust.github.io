# Potencializar Vendas — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Aumentar vendas atacando o gargalo de tráfego orgânico (SEO + captura de lead + nutrição) e tapar os vazamentos de conversão, sem verba de anúncio.

**Architecture:** Site Jekyll estático no GitHub Pages. Toda a Fase 1 são includes Liquid, JSON-LD, JS de medição e um script Apps Script; a Fase 2 são docs de playbook + um script Python de apoio. O blog (17 posts) é o motor de descoberta; cada post vira porta de captura de e-mail.

**Tech Stack:** Jekyll 4.4.1, Liquid, HTML/CSS/JS vanilla, Google Apps Script (autoresponder), Python 3 (script de apoio), GA4.

## Global Constraints

- **Build/verify:** `jekyll build` gera `_site/`. Verificação de tarefas de site = build + `grep` no HTML gerado em `_site/`. Servir local: `make serve` (porta 8000; checar se ocupada antes).
- **Não quebrar o `blog_agent`:** posts continuam markdown puro em `posts/NNNN-slug/README.md` sem front-matter obrigatório (`scripts/blog_agent.py` gera posts). Nada pode exigir front-matter para renderizar.
- **Preço:** `R$ {{ site.preco }}` = R$ 89,90. Nunca inventar âncora de preço (sem `preco_antigo` falso) — decisão herdada do spec 2026-07-02.
- **Integridade:** não fabricar depoimentos nem afirmações factuais. Prova social e previews só entram com insumo real do autor.
- **Identidade visual:** dark `#141e30`, laranja Rust `#f74c00` / `#ff7a3d`, texto `#e8edf5` / muted `#b8c2d0`. Reusar classes de `_includes/style.scss`.
- **Commits:** local apenas, sem push. O autor tem regra de não commitar sem pedido explícito — cada "Commit" abaixo significa *deixar staged/pronto*; o commit real só quando o autor aprovar (pode ser em lote ao fim de cada fase).

---

# FASE 1 — Motor de tráfego + tapar buracos

## File Structure (Fase 1)

- `_includes/analytics.html` — **modificar**: eventos `view_price`, `select_content`, `generate_lead`.
- `_includes/schema-home.html` — **criar**: JSON-LD `Book`+`Offer` e `FAQPage`.
- `_includes/schema-post.html` — **criar**: JSON-LD `BlogPosting`+`BreadcrumbList`.
- `_includes/meta-description.html` — **criar**: description única por post (extrai 1º parágrafo).
- `_data/faq.yml` — **criar**: fonte única do FAQ (render visível + schema).
- `_data/relacionados.yml` — **criar**: mapa de clusters de links internos.
- `_includes/lead-capture.html` — **criar**: bloco de captura de e-mail nos posts.
- `_layouts/default.html` — **modificar**: usar `meta-description.html`; incluir `schema-home.html` na home; renderizar FAQ de `_data/faq.yml`.
- `index.html` — **modificar**: FAQ passa a vir de `_data/faq.yml`.
- `_layouts/post.html` — **modificar**: incluir `schema-post.html`, `relacionados`, `lead-capture.html`.
- `scripts/sequencia-nutricao.gs` — **criar**: sequência de e-mails (Apps Script).
- `_data/depoimentos.yml`, `imgs/preview/`, docs — **conversão** (Task 7).

---

### Task 1: Medição do funil (eventos GA4)

**Files:**
- Modify: `_includes/analytics.html` (acrescentar bloco antes do `</...>` final, junto do listener `js-buy` existente)

**Interfaces:**
- Consumes: `window.gtag` (já inicializado no mesmo arquivo), `window.fbq` (se pixel ativo).
- Produces: eventos GA4 `view_price`, `select_content` (`content_type: 'amostra'`), `generate_lead` (`method: 'amostra_form'`).

- [ ] **Step 1: Escrever a verificação (falha primeiro)**

Build atual e confirme que os eventos ainda não existem:

Run: `jekyll build && grep -c "view_price" _site/index.html`
Expected: `0`

- [ ] **Step 2: Adicionar o bloco de medição**

Em `_includes/analytics.html`, logo após o listener de clique `.js-buy` (o `<script>` final), acrescente:

```html
<script>
  (function () {
    // view_price: usuário chegou ao bloco de compra
    var priceEl = document.getElementById('comprar');
    if (priceEl && 'IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting) {
          if (window.gtag) gtag('event', 'view_price');
          io.disconnect();
        }
      }, { threshold: 0.4 });
      io.observe(priceEl);
    }
    // Cliques de interesse na amostra e de lead (link do Google Form)
    document.addEventListener('click', function (e) {
      if (!e.target.closest) return;
      var lead = e.target.closest('a[href^="https://forms.gle/"], a.js-lead');
      if (lead) {
        if (window.gtag) gtag('event', 'generate_lead', { method: 'amostra_form' });
        if (window.fbq) fbq('track', 'Lead');
        return;
      }
      var amostra = e.target.closest('a[href="/amostra/"]');
      if (amostra && window.gtag) gtag('event', 'select_content', { content_type: 'amostra' });
    });
  })();
</script>
```

- [ ] **Step 3: Verificar que passa**

Run: `jekyll build && grep -c "view_price" _site/index.html && grep -c "generate_lead" _site/index.html`
Expected: `1` e `1`

- [ ] **Step 4: Fumaça no navegador (manual)**

Run: `make serve` → abrir `http://localhost:8000`, abrir DevTools → Console, rolar até o bloco de preço e clicar em "Ler capítulo gratuito". Confirmar no painel Network/DebugView do GA4 (ou `dataLayer`) que os eventos disparam. Parar com Ctrl+C.

- [ ] **Step 5: Commit (staged, conforme Global Constraints)**

```bash
git add _includes/analytics.html
git commit -m "feat: eventos GA4 de funil (view_price, select_content, generate_lead)"
```

---

### Task 2: Dados estruturados (JSON-LD) + FAQ como fonte única

**Files:**
- Create: `_data/faq.yml`
- Create: `_includes/schema-home.html`
- Modify: `index.html:198-217` (seção FAQ → renderizar de `_data/faq.yml`)
- Modify: `_layouts/default.html` (incluir `schema-home.html` só na home)

**Interfaces:**
- Consumes: `site.data.faq` (lista de `{q, a}`), `site.preco`, `site.paginas`, `site.author`, `site.kiwify_url`.
- Produces: `_includes/schema-home.html` (renderiza `Book`, `Offer`, `FAQPage`); FAQ visível a partir de `_data/faq.yml`.

- [ ] **Step 1: Criar `_data/faq.yml` (fonte única — texto atual da home)**

```yaml
# Perguntas frequentes — renderiza a seção visível E o JSON-LD FAQPage.
- q: "Preciso ser avançado em Python?"
  a: "Não. Se você já escreve Python no dia a dia — funções, classes, pip/venv — tem toda a base necessária. O livro usa seu conhecimento de Python como ponte, não como pré-requisito acadêmico."
- q: "Como e quando recebo o livro?"
  a: "A compra é processada pela Kiwify. Assim que o pagamento é confirmado, o acesso ao PDF é liberado imediatamente na sua área de membros — sem espera."
- q: "Recebo nota fiscal?"
  a: "Sim, a nota fiscal é emitida e enviada para o seu e-mail."
- q: "Quais formas de pagamento?"
  a: "Cartão de crédito, PIX e boleto — tudo pelo checkout seguro da Kiwify."
```

- [ ] **Step 2: Substituir a FAQ hardcoded por render de dados**

Em `index.html`, trocar o conteúdo da `<section class="faq">` (linhas ~199-216) por:

```html
<section class="faq">
  <div class="container">
    <h2>Perguntas frequentes</h2>
    {% for item in site.data.faq %}
    <details><summary>{{ item.q }}</summary>
      <p>{{ item.a }}</p>
    </details>
    {% endfor %}
  </div>
</section>
```

- [ ] **Step 3: Criar `_includes/schema-home.html`**

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Book",
      "name": "Desbravando Rust",
      "author": { "@type": "Person", "name": "{{ site.author }}" },
      "inLanguage": "pt-BR",
      "bookFormat": "https://schema.org/EBook",
      {% if site.paginas != "" %}"numberOfPages": {{ site.paginas }},{% endif %}
      "url": "{{ '/' | absolute_url }}",
      "image": "{{ '/imgs/capa.jpg' | absolute_url }}",
      "offers": {
        "@type": "Offer",
        "price": "{{ site.preco | remove: '.' | replace: ',', '.' }}",
        "priceCurrency": "BRL",
        "availability": "https://schema.org/InStock",
        "url": "{{ site.kiwify_url }}"
      }
    },
    {
      "@type": "FAQPage",
      "mainEntity": [
        {% for item in site.data.faq %}
        {
          "@type": "Question",
          "name": {{ item.q | jsonify }},
          "acceptedAnswer": { "@type": "Answer", "text": {{ item.a | jsonify }} }
        }{% unless forloop.last %},{% endunless %}
        {% endfor %}
      ]
    }
  ]
}
</script>
```

- [ ] **Step 4: Incluir só na home, no `<head>` de `_layouts/default.html`**

Antes de `</head>` (após o bloco `<style>`), adicionar:

```html
  {% if page.url == "/" %}{% include schema-home.html %}{% endif %}
```

- [ ] **Step 5: Build e validar JSON-LD**

Run: `jekyll build && grep -c '"@type": "Book"' _site/index.html && grep -c '"@type": "FAQPage"' _site/index.html`
Expected: `1` e `1`

Run: `python3 -c "import json,re,sys; h=open('_site/index.html').read(); m=re.findall(r'<script type=\"application/ld\+json\">(.*?)</script>', h, re.S); [json.loads(x) for x in m]; print('JSON-LD ok:', len(m))"`
Expected: `JSON-LD ok: 1` (sem exceção — prova que o JSON é válido)

- [ ] **Step 6: Confirmar que a FAQ visível continua idêntica**

Run: `grep -c "Preciso ser avançado em Python?" _site/index.html`
Expected: `1`

- [ ] **Step 7: Commit**

```bash
git add _data/faq.yml _includes/schema-home.html index.html _layouts/default.html
git commit -m "feat: JSON-LD Book/Offer/FAQPage e FAQ a partir de _data/faq.yml"
```

---

### Task 3: Meta description única por post

**Files:**
- Create: `_includes/meta-description.html`
- Modify: `_layouts/default.html:7` (a tag `<meta name="description">`)

**Interfaces:**
- Consumes: `page.description` (override opcional via front-matter), `page.content`, `page.path`, `site.description`.
- Produces: `_includes/meta-description.html` imprime a string de description (≤160 chars).

- [ ] **Step 1: Verificação (falha) — hoje todos os posts herdam a description do site**

Run: `jekyll build && grep -o '<meta name="description"[^>]*' _site/posts/*/index.html | sort -u | wc -l`
Expected: `1` (todas iguais — o bug)

- [ ] **Step 2: Criar `_includes/meta-description.html`**

Extrai o primeiro parágrafo real do markdown (pula H1, linha de autor `######` e a imagem de capa `!`):

```liquid
{%- if page.description -%}
{{- page.description | strip_newlines | strip | truncate: 160 -}}
{%- elsif page.path contains 'posts/' -%}
{%- assign desc = '' -%}
{%- assign lines = page.content | newline_to_br | split: '<br />' -%}
{%- for line in lines -%}
  {%- assign t = line | strip -%}
  {%- assign c = t | slice: 0, 1 -%}
  {%- if desc == '' and t != '' and c != '#' and c != '!' -%}
    {%- assign desc = t | markdownify | strip_html | strip_newlines | strip | truncate: 160 -%}
  {%- endif -%}
{%- endfor -%}
{{- desc -}}
{%- else -%}
{{- site.description | strip_newlines | strip -}}
{%- endif -%}
```

- [ ] **Step 3: Usar o include em `_layouts/default.html`**

Trocar a linha 7:

```html
  <meta name="description" content="{{ page.description | default: site.description | strip_newlines | strip }}">
```

por:

```html
  <meta name="description" content="{% include meta-description.html %}">
```

- [ ] **Step 4: Verificar que passa (descriptions agora distintas)**

Run: `jekyll build && grep -o '<meta name="description"[^>]*' _site/posts/*/index.html | sort -u | wc -l`
Expected: número > `1` (≈ 17 — cada post com a sua)

Run: `grep -o '<meta name="description"[^>]*' _site/posts/0014-*/index.html`
Expected: contém "Metaprogramação é a arte de escrever" (1º parágrafo do post de macros)

- [ ] **Step 5: Confirmar que a home não regrediu**

Run: `grep -o '<meta name="description"[^>]*' _site/index.html`
Expected: a description da home (do front-matter do `index.html`), inalterada.

- [ ] **Step 6: Commit**

```bash
git add _includes/meta-description.html _layouts/default.html
git commit -m "feat: meta description única por post (extrai 1º parágrafo)"
```

---

### Task 4: Schema de post + clusters de links internos

**Files:**
- Create: `_includes/schema-post.html`
- Create: `_data/relacionados.yml`
- Modify: `_layouts/post.html` (incluir schema e bloco "Leia também")

**Interfaces:**
- Consumes: `page.title`, `page.url`, `site.author`, `site.data.relacionados[post_num]`, `post_num` (já calculado em `post.html`).
- Produces: JSON-LD `BlogPosting`+`BreadcrumbList` por post; bloco `<aside class="related">`.

- [ ] **Step 1: Criar `_data/relacionados.yml` (clusters por tópico)**

Números conforme `_data/cta_posts.yml`. Cada post aponta para 3 relacionados:

```yaml
# Clusters de tópico para links internos (sinal de autoridade p/ SEO).
"0001": ["0003", "0016", "0004"]   # Axum ↔ Cargo, performance, SQLx
"0002": ["0016", "0004", "0017"]   # Polars ↔ performance, SQLx, N+1
"0003": ["0001", "0016", "0014"]   # Cargo ↔ Axum, performance, macros
"0004": ["0017", "0002", "0016"]   # SQLx ↔ N+1, Polars, performance
"0005": ["0006", "0012", "0013"]   # Ownership ↔ memória, lifetimes, smart pointers
"0006": ["0005", "0012", "0013"]   # Memória ↔ ownership, lifetimes, smart pointers
"0007": ["0008", "0015", "0009"]   # Enums ↔ Result/Option, pattern matching, traits
"0008": ["0007", "0015", "0005"]   # Result/Option ↔ enums, pattern matching, ownership
"0009": ["0011", "0007", "0014"]   # Traits ↔ iteradores, enums, macros
"0010": ["0016", "0001", "0011"]   # Concorrência ↔ performance, Axum, iteradores
"0011": ["0009", "0014", "0010"]   # Iteradores ↔ traits, macros, concorrência
"0012": ["0005", "0006", "0013"]   # Lifetimes ↔ ownership, memória, smart pointers
"0013": ["0006", "0012", "0005"]   # Smart pointers ↔ memória, lifetimes, ownership
"0014": ["0009", "0011", "0015"]   # Macros ↔ traits, iteradores, pattern matching
"0015": ["0007", "0008", "0014"]   # Pattern matching ↔ enums, Result/Option, macros
"0016": ["0010", "0002", "0001"]   # Performance ↔ concorrência, Polars, Axum
"0017": ["0004", "0002", "0016"]   # N+1 ↔ SQLx, Polars, performance
```

- [ ] **Step 2: Criar `_includes/schema-post.html`**

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "BlogPosting",
      "headline": {{ page.title | jsonify }},
      "author": { "@type": "Person", "name": "{{ site.author }}" },
      "publisher": { "@type": "Organization", "name": "Desbravando Rust" },
      "inLanguage": "pt-BR",
      "image": "{{ '/imgs/og-default.png' | absolute_url }}",
      "mainEntityOfPage": "{{ page.url | absolute_url }}"
    },
    {
      "@type": "BreadcrumbList",
      "itemListElement": [
        { "@type": "ListItem", "position": 1, "name": "Início", "item": "{{ '/' | absolute_url }}" },
        { "@type": "ListItem", "position": 2, "name": "Blog", "item": "{{ '/blog/' | absolute_url }}" },
        { "@type": "ListItem", "position": 3, "name": {{ page.title | jsonify }}, "item": "{{ page.url | absolute_url }}" }
      ]
    }
  ]
}
</script>
```

(Nota: `datePublished` é omitido de propósito — a data no corpo do post está em pt-BR não-ISO ("Mai 12, 2026") e não vale fabricar. `BlogPosting` continua válido sem ela.)

- [ ] **Step 3: Adicionar schema + "Leia também" em `_layouts/post.html`**

Após o bloco `<aside class="post-cta">` existente (fim do arquivo), adicionar. `post_num` já é calculado acima no arquivo:

```html
{% include schema-post.html %}

{% assign related = site.data.relacionados[post_num] %}
{% if related %}
<aside class="related">
  <h2>Leia também</h2>
  <ul>
    {% assign blog_posts = site.pages | where_exp: "p", "p.path contains 'posts/'" %}
    {% for p in blog_posts %}
      {% assign pp = p.path | split: "/" %}
      {% assign pnum = pp[1] | split: "-" | first %}
      {% if related contains pnum %}
      <li><a href="{{ p.url }}">{{ p.title }}</a></li>
      {% endif %}
    {% endfor %}
  </ul>
</aside>
{% endif %}
```

- [ ] **Step 4: Estilo do bloco "Leia também"**

Em `_includes/style.scss`, adicionar (reusa paleta existente):

```scss
.related { margin: 40px 0; padding: 24px; background: var(--bg-card); border-radius: 12px; }
.related h2 { font-size: 1.2rem; margin-bottom: 12px; }
.related ul { list-style: none; padding: 0; display: grid; gap: 8px; }
.related a { color: var(--rust-orange-soft); text-decoration: none; }
.related a:hover { text-decoration: underline; }
```

- [ ] **Step 5: Build e verificar**

Run: `jekyll build && grep -c '"@type": "BlogPosting"' _site/posts/0014-*/index.html`
Expected: `1`

Run: `grep -c 'class="related"' _site/posts/0014-*/index.html`
Expected: `1`

Run: `grep -A6 'class="related"' _site/posts/0014-*/index.html | grep -c '<li>'`
Expected: `3` (três posts relacionados renderizados)

- [ ] **Step 6: Commit**

```bash
git add _data/relacionados.yml _includes/schema-post.html _layouts/post.html _includes/style.scss
git commit -m "feat: JSON-LD de post e clusters de links internos (Leia também)"
```

---

### Task 5: Captura de e-mail nos posts

**Files:**
- Create: `_includes/lead-capture.html`
- Modify: `_layouts/post.html` (incluir após o `post-cta`)
- Modify: `_includes/style.scss` (estilo do bloco)

**Interfaces:**
- Consumes: link do Google Form (o mesmo de `/amostra/`: `https://forms.gle/RPPhXWYM1UEkBz4y6`).
- Produces: `<aside class="lead-capture">` com `a.js-lead` (dispara `generate_lead` via listener da Task 1).

- [ ] **Step 1: Criar `_includes/lead-capture.html`**

```html
<aside class="lead-capture">
  <h2>Receba um capítulo grátis</h2>
  <p>Sinta o estilo do livro: Rust sempre comparado com o Python que você já domina — direto no seu e-mail.</p>
  <a class="btn btn-buy js-lead" href="https://forms.gle/RPPhXWYM1UEkBz4y6" target="_blank" rel="noopener">Quero o capítulo grátis</a>
</aside>
```

- [ ] **Step 2: Incluir em `_layouts/post.html`**

Logo após o `{% include schema-post.html %}` da Task 4 (antes do bloco `related` ou depois — ordem indiferente), adicionar:

```html
{% include lead-capture.html %}
```

- [ ] **Step 3: Estilo em `_includes/style.scss`**

```scss
.lead-capture { margin: 40px 0; padding: 28px 24px; text-align: center; background: rgba(247, 76, 0, 0.08); border: 1px solid rgba(247, 76, 0, 0.35); border-radius: 12px; }
.lead-capture h2 { font-size: 1.3rem; margin-bottom: 8px; }
.lead-capture p { color: var(--text-muted); margin-bottom: 16px; }
```

- [ ] **Step 4: Build e verificar**

Run: `jekyll build && grep -c 'class="lead-capture"' _site/posts/0014-*/index.html`
Expected: `1`

Run: `grep -c 'js-lead' _site/posts/0014-*/index.html`
Expected: `1`

- [ ] **Step 5: Verificar que o clique dispara `generate_lead` (integração com Task 1)**

Run: `make serve` → abrir um post, DevTools aberto, clicar "Quero o capítulo grátis" → confirmar evento `generate_lead` no dataLayer/DebugView. Ctrl+C.

- [ ] **Step 6: Commit**

```bash
git add _includes/lead-capture.html _layouts/post.html _includes/style.scss
git commit -m "feat: bloco de captura de e-mail ao fim de cada post"
```

---

### Task 6: Sequência de nutrição de e-mail (Apps Script)

**Files:**
- Create: `scripts/sequencia-nutricao.gs`

**Interfaces:**
- Consumes: planilha de respostas do Google Form (colunas: timestamp, e-mail, nome). Adiciona coluna de controle `seq_stage`.
- Produces: função `enviarSequencia()` acionada por gatilho de tempo (diário); função `testeSequenciaDryRun()` para QA manual.

**Nota:** Apps Script roda no Google, não no build do site — não há teste automatizado no repo. A verificação é manual via `testeSequenciaDryRun()` (loga o que enviaria sem enviar). O e-mail #1 (capítulo) continua no `autorresposta-capitulo-html.gs` existente; esta sequência cuida dos e-mails #2–#4.

- [ ] **Step 1: Criar `scripts/sequencia-nutricao.gs`**

```javascript
/**
 * Sequência de nutrição — Desbravando Rust
 *
 * Complementa o autorresponder do capítulo (autorresposta-capitulo-html.gs).
 * Envia e-mails #2, #3 e #4 em D+2, D+5 e D+9 após a captura do lead.
 *
 * Instalação:
 *  1. Abrir a planilha de respostas do Form → Extensões → Apps Script.
 *  2. Colar este arquivo.
 *  3. Ajustar as constantes (SHEET_NAME, colunas, links).
 *  4. Criar gatilho de tempo: enviarSequencia, "Baseado em tempo" → "Dia" (1x/dia).
 *  5. Rodar testeSequenciaDryRun() uma vez para conferir os logs antes de ativar.
 */

const SHEET_NAME = 'Respostas ao formulário 1'; // ajuste ao nome real da aba
const COL_TIMESTAMP = 1;   // A
const COL_EMAIL = 2;       // ajuste: coluna do e-mail
const COL_NOME = 3;        // ajuste: coluna do nome (ou 0 se não houver)
const STAGE_HEADER = 'seq_stage';
const REMETENTE = 'José Luis — Desbravando Rust';
const KIWIFY_URL = 'https://pay.kiwify.com.br/18ZoOt1';
const SITE = 'https://desbravandorust.com.br';

// E-mails da sequência: dias após captura + assunto + corpo (HTML simples inline).
const SEQUENCIA = [
  { dia: 2, assunto: 'O que mais tem dentro do Desbravando Rust',
    html: function (nome) { return corpo(nome,
      'Já deu uma olhada no capítulo? Ele é só a ponta. O livro tem 30 capítulos e 3 projetos completos — API REST com Axum, TOTP com Lambdas e uma CLI de arquivos.',
      'Ver o blog com benchmarks reais', SITE + '/blog/'); } },
  { dia: 5, assunto: 'Por que ownership deixa de assustar',
    html: function (nome) { return corpo(nome,
      'A parte que mais trava quem vem do Python é ownership. O livro dedica capítulos inteiros a ownership, borrowing e lifetimes — com o equivalente em Python lado a lado. Depois disso, o resto flui.',
      'Ler um post sobre ownership', SITE + '/posts/0005-'); } },
  { dia: 9, assunto: 'Sua jornada do Python ao Rust — R$ 89,90',
    html: function (nome) { return corpo(nome,
      'Se o capítulo fez sentido, o livro completo é o caminho mais direto do Python ao Rust: claro, prático e sem recomeçar do zero. Garantia incondicional de 7 dias.',
      'Garantir meu exemplar', KIWIFY_URL); } },
];

function enviarSequencia() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  const data = sheet.getDataRange().getValues();
  const header = data[0];
  let stageCol = header.indexOf(STAGE_HEADER);
  if (stageCol === -1) { stageCol = header.length; sheet.getRange(1, stageCol + 1).setValue(STAGE_HEADER); }

  const agora = new Date();
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    const email = row[COL_EMAIL - 1];
    if (!email) continue;
    const capturado = new Date(row[COL_TIMESTAMP - 1]);
    const diasPassados = Math.floor((agora - capturado) / 86400000);
    const stage = Number(row[stageCol] || 0);
    if (stage >= SEQUENCIA.length) continue;

    const proximo = SEQUENCIA[stage];
    if (diasPassados >= proximo.dia) {
      const nome = COL_NOME ? String(row[COL_NOME - 1] || 'Leitor(a)').split(' ')[0] : 'Leitor(a)';
      enviar_(email, proximo.assunto, proximo.html(nome));
      sheet.getRange(i + 1, stageCol + 1).setValue(stage + 1);
    }
  }
}

function enviar_(email, assunto, html) {
  MailApp.sendEmail({ to: email, subject: assunto, htmlBody: html, name: REMETENTE });
}

function corpo(nome, texto, ctaLabel, ctaUrl) {
  return '<div style="font-family:Arial,sans-serif;max-width:600px;color:#1b2740;">' +
    '<p>Olá, ' + nome + '!</p><p>' + texto + '</p>' +
    '<p><a href="' + ctaUrl + '" style="display:inline-block;background:#f74c00;color:#fff;' +
    'padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:bold;">' + ctaLabel + '</a></p>' +
    '<p style="color:#7d8aa0;font-size:13px;">José Luis · Desbravando Rust · ' +
    '<a href="' + SITE + '">desbravandorust.com.br</a></p></div>';
}

/** QA: loga o que seria enviado hoje, sem enviar nada. */
function testeSequenciaDryRun() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  const data = sheet.getDataRange().getValues();
  const header = data[0];
  const stageCol = header.indexOf(STAGE_HEADER);
  const agora = new Date();
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    const email = row[COL_EMAIL - 1];
    if (!email) continue;
    const dias = Math.floor((agora - new Date(row[COL_TIMESTAMP - 1])) / 86400000);
    const stage = stageCol === -1 ? 0 : Number(row[stageCol] || 0);
    if (stage < SEQUENCIA.length && dias >= SEQUENCIA[stage].dia) {
      Logger.log('ENVIARIA e-mail #' + (stage + 2) + ' para ' + email + ' (D+' + dias + ')');
    }
  }
}
```

- [ ] **Step 2: QA manual (dry-run)**

No editor de Apps Script (após colar e ajustar as constantes à planilha real): rodar `testeSequenciaDryRun` → conferir em "Execuções/Logs" que os leads certos apareceriam nos estágios certos. Nenhum e-mail é enviado.

- [ ] **Step 3: Ativar em produção (autor)**

Criar o gatilho de tempo diário para `enviarSequencia`. Enviar 1 e-mail de teste real para a própria caixa do autor antes de deixar rodando.

- [ ] **Step 4: Commit**

```bash
git add scripts/sequencia-nutricao.gs
git commit -m "feat: sequência de nutrição de e-mail (Apps Script, D+2/D+5/D+9)"
```

---

### Task 7: Tapar buracos de conversão (habilitar + insumo do autor)

**Files:**
- Modify: `_data/depoimentos.yml` (exemplo preenchido comentado)
- Create: `imgs/preview/.gitkeep`
- Create: `docs/conversao-insumos.md` (roteiro de depoimentos, exportação de previews, como ligar cupom/oferta)

**Interfaces:**
- Consumes: nada no build (seções já são condicionais: só renderizam com dados).
- Produces: caminho claro para o autor preencher prova social, previews e oferta.

- [ ] **Step 1: Enriquecer `_data/depoimentos.yml` com exemplo real-formatado (comentado)**

Acrescentar ao arquivo (mantendo tudo comentado até ter depoimento real):

```yaml
# EXEMPLO de formato (descomente e substitua por depoimentos REAIS — nunca invente):
# - nome: "Maria Silva"
#   cargo: "Backend Engineer @ Empresa"
#   texto: "Vim do Python travado em ownership. Em duas semanas com o livro eu estava escrevendo Rust sem lutar com o compilador."
#   linkedin: "https://www.linkedin.com/in/maria-silva/"
```

- [ ] **Step 2: Criar `imgs/preview/.gitkeep`** (garante o diretório no git)

```bash
mkdir -p imgs/preview && touch imgs/preview/.gitkeep
```

- [ ] **Step 3: Criar `docs/conversao-insumos.md`**

```markdown
# Insumos de conversão (ação do autor)

Três seções da home só aparecem quando você fornece conteúdo real. Nada aqui
deve ser inventado — público dev fareja prova social falsa.

## 1. Depoimentos (`_data/depoimentos.yml`)
Como coletar 3–4 depoimentos reais:
- Peça a leitores da amostra e colegas que já leram: "Em 1–2 frases, o que o
  livro destravou pra você?"
- Peça permissão para usar nome, cargo e link do LinkedIn (aumenta a credibilidade).
- Descomente o bloco de exemplo no arquivo e preencha um item por depoimento.
A seção "Quem leu, recomenda" passa a renderizar sozinha.

## 2. Previews (`imgs/preview/`)
- Exporte 3–5 páginas reais do PDF como PNG (idealmente páginas com Python e
  Rust lado a lado). Ferramenta: exportar página do PDF ou print em alta.
- Nomeie `01.png`, `02.png`, ... e salve em `imgs/preview/`.
A seção "Veja por dentro" detecta os arquivos e renderiza automaticamente.

## 3. Oferta / urgência honesta (`_config.yml`)
Só ligue com uma oferta REAL por tempo limitado:
- `cupom: "LANCAMENTO10"` e `cupom_texto: "10% de desconto até 20/07"` → mostra a
  faixa no topo e a nota no checkout.
- `preco_antigo: "129,90"` → só se esse preço realmente existiu. Sem âncora falsa.
```

- [ ] **Step 4: Build e verificar que nada quebrou (seções continuam ocultas até ter dados)**

Run: `jekyll build && grep -c 'class="social-proof"' _site/index.html`
Expected: `0` (sem depoimentos ainda — correto)

Run: `test -d _site/imgs/preview && echo "dir ok"`
Expected: `dir ok`

- [ ] **Step 5: Commit**

```bash
git add _data/depoimentos.yml imgs/preview/.gitkeep docs/conversao-insumos.md
git commit -m "docs: insumos de conversão (depoimentos, previews, oferta)"
```

---

# FASE 2 — Playbook de distribuição contínua

## File Structure (Fase 2)

- `docs/playbook-distribuicao.md` — **criar**: cadência, regras de canal, moldes de repurpose, calendário-semente de 8 semanas, loop de broadcast mensal.
- `scripts/social_snippet.py` — **criar**: gera rascunho de post de LinkedIn a partir de um post do blog.
- `scripts/test_social_snippet.py` — **criar**: testes (assert puro, roda com `python3`).

---

### Task 8: Playbook de distribuição

**Files:**
- Create: `docs/playbook-distribuicao.md`

**Interfaces:** documento; sem código.

- [ ] **Step 1: Criar `docs/playbook-distribuicao.md`**

````markdown
# Playbook de distribuição — Desbravando Rust

O SEO amadurece em semanas/meses; o LinkedIn traz tráfego hoje. Este playbook é
o combustível recorrente. Meta: sustentável, não heroico.

## Cadência (2 posts/semana no LinkedIn)
- **Terça — Repurpose:** transforma 1 post do blog em post de LinkedIn (use
  `scripts/social_snippet.py` para o rascunho).
- **Quinta — Bastidor:** 1 aprendizado curto ("hoje o compilador me ensinou X"),
  sempre puxando pro tema do livro sem vender direto.

## Regra de ouro do canal
- Entregue o valor NO corpo do post (código, benchmark, insight). O LinkedIn
  penaliza post que manda embora.
- Link do blog vai no **1º comentário**, não no corpo.
- CTA do livro é sutil e ocasional (1 a cada ~4 posts), nunca em todo post.

## Moldes de repurpose (por tipo de post)

### Benchmark / performance (ex.: Axum × FastAPI, Polars)
```
[GANCHO] Reescrevi <coisa> em Rust e o p99 caiu de X para Y.

[CONTEXTO] 2 linhas: o que era antes, o problema.

[MINI-CÓDIGO/NÚMERO] o trecho ou a tabela que prova.

[APRENDIZADO] a lição que serve pra quem vem do Python.

Escrevi o passo a passo completo (link no comentário). 🦀
```

### Conceito (ex.: ownership, lifetimes, traits)
```
[GANCHO] "Ownership" assustou você em Rust? Veio do Python? Isto é pra você.

[PONTE] o equivalente mental em Python.

[EXPLICAÇÃO] 3–4 linhas, sem jargão.

[MINI-EXEMPLO] 5–8 linhas de código comentado.

Aprofundei com exemplos lado a lado (link no comentário).
```

### Tooling (ex.: Cargo, SQLx)
```
[GANCHO] O que o pip te deixou mal-acostumado e o Cargo resolve.

[LISTA] 3 coisas que "só funcionam".

[CONVITE] link no comentário.
```

## Calendário-semente (8 semanas)
Prioriza os posts de maior apelo primeiro (benchmarks e performance puxam mais).

| Semana | Terça (repurpose) | Quinta (bastidor) |
|--------|-------------------|-------------------|
| 1 | 0001 Axum × FastAPI | Por que comecei a estudar Rust vindo do Python |
| 2 | 0002 Pandas × Polars | O erro de compilação que virou meu melhor professor |
| 3 | 0016 Performance no mundo real | Um benchmark que me surpreendeu |
| 4 | 0005 Ownership | A analogia de Python que finalmente destravou ownership |
| 5 | 0017 Caçando o N+1 com SQLx | Debugar em Rust vs. em Python |
| 6 | 0008 Result/Option | Por que parei de sentir falta de try/except |
| 7 | 0010 Concorrência sem GIL | O dia que o GIL deixou de ser meu problema |
| 8 | 0014 Macros | Metaprogramação: decorator vs. macro |

Depois da semana 8, reciclar os posts restantes (0003, 0004, 0006, 0007, 0009,
0011, 0012, 0013, 0015) e repetir os campeões com novo ângulo.

## Loop de e-mail (1 broadcast/mês)
Para a lista capturada (planilha do Form):
- 1x/mês, envie o post mais forte do mês + um nudge do livro.
- Reuse o template visual de `scripts/autorresposta-capitulo-html.gs`.
- Assunto curto e concreto (ex.: "O benchmark que fez minha API 6x mais rápida").
````

- [ ] **Step 2: Verificar**

Run: `test -f docs/playbook-distribuicao.md && grep -c "Calendário-semente" docs/playbook-distribuicao.md`
Expected: `1`

- [ ] **Step 3: Commit**

```bash
git add docs/playbook-distribuicao.md
git commit -m "docs: playbook de distribuição (cadência, moldes, calendário, broadcast)"
```

---

### Task 9: Script de repurpose (`social_snippet.py`)

**Files:**
- Create: `scripts/social_snippet.py`
- Create: `scripts/test_social_snippet.py`

**Interfaces:**
- Consumes: caminho de um post (`posts/NNNN-slug/README.md`).
- Produces:
  - `parse_post(markdown: str, slug: str) -> dict` com chaves `titulo` (str), `numero` (str), `primeiro_paragrafo` (str), `codigo` (str|None), `url` (str).
  - `format_linkedin(parsed: dict) -> str` — rascunho pronto pra colar.
  - CLI: `python3 scripts/social_snippet.py posts/0014-macros-em-rust/README.md`.

- [ ] **Step 1: Escrever os testes (falham primeiro)**

`scripts/test_social_snippet.py`:

```python
from social_snippet import parse_post, format_linkedin

SAMPLE = """# Macros em Rust: Automatizando Código
###### Por [@zejuniortdr](https://github.com/zejuniortdr/) em Mai 12, 2026

![Macros em Rust](imgs/cover.png)

Metaprogramação é a arte de escrever código que gera outro código.

## Seção

```rust
macro_rules! diga {
    () => { println!("oi"); };
}
```
"""

def test_parse_extrai_titulo_numero_e_paragrafo():
    p = parse_post(SAMPLE, "0014-macros-em-rust")
    assert p["titulo"] == "Macros em Rust: Automatizando Código"
    assert p["numero"] == "0014"
    assert p["primeiro_paragrafo"].startswith("Metaprogramação é a arte")
    assert "###### Por" not in p["primeiro_paragrafo"]
    assert p["url"] == "https://desbravandorust.com.br/posts/0014-macros-em-rust/"

def test_parse_captura_primeiro_bloco_de_codigo():
    p = parse_post(SAMPLE, "0014-macros-em-rust")
    assert "macro_rules!" in p["codigo"]

def test_parse_sem_codigo_retorna_none():
    md = "# T\n###### Por x em Y\n\n![a](imgs/cover.png)\n\nParágrafo só.\n"
    p = parse_post(md, "0001-x")
    assert p["codigo"] is None

def test_format_linkedin_inclui_gancho_e_link_no_fim():
    p = parse_post(SAMPLE, "0014-macros-em-rust")
    out = format_linkedin(p)
    assert "Macros em Rust" in out
    assert out.rstrip().endswith("https://desbravandorust.com.br/posts/0014-macros-em-rust/")
    assert "#rustlang" in out

if __name__ == "__main__":
    import sys
    n = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn(); n += 1; print("ok:", name)
    print(f"\n{n} testes passaram")
    sys.exit(0)
```

- [ ] **Step 2: Rodar os testes e confirmar que falham**

Run: `cd scripts && python3 test_social_snippet.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'social_snippet'`

- [ ] **Step 3: Implementar `scripts/social_snippet.py`**

```python
#!/usr/bin/env python3
"""Gera um rascunho de post de LinkedIn a partir de um post do blog.

Uso: python3 scripts/social_snippet.py posts/0014-macros-em-rust/README.md
"""
import re
import sys

SITE = "https://desbravandorust.com.br"


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
    slug = caminho.replace("\\", "/").split("/posts/")[-1].split("/")[0]
    with open(caminho, encoding="utf-8") as f:
        markdown = f.read()
    print(format_linkedin(parse_post(markdown, slug)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Rodar os testes e confirmar que passam**

Run: `cd scripts && python3 test_social_snippet.py`
Expected: `4 testes passaram`

- [ ] **Step 5: Fumaça na CLI com um post real**

Run: `python3 scripts/social_snippet.py posts/0014-macros-em-rust/README.md`
Expected: rascunho de LinkedIn no stdout, terminando com a URL do post.

- [ ] **Step 6: Commit**

```bash
git add scripts/social_snippet.py scripts/test_social_snippet.py
git commit -m "feat: script de repurpose de post para LinkedIn + testes"
```

---

## Self-Review (feita)

- **Cobertura do spec:** medição (T1), SEO técnico — description (T3), JSON-LD (T2, T4), links internos (T4) —, captura de e-mail nos posts (T5), sequência de nutrição (T6), buracos de conversão (T7), playbook + calendário + broadcast (T8), script de repurpose (T9). Todas as frentes do spec têm tarefa.
- **Sem placeholders:** todo passo traz código/comando reais e output esperado.
- **Consistência de tipos:** `parse_post`/`format_linkedin` e suas chaves (`titulo`, `numero`, `primeiro_paragrafo`, `codigo`, `url`) batem entre teste, implementação e bloco Interfaces. `js-lead`/`forms.gle` e `#comprar` consistentes entre T1, T5. `post_num` reutiliza o cálculo já existente em `post.html`.
- **Dependências do autor** isoladas em T7 (não bloqueiam T1–T6, T8–T9).
```
