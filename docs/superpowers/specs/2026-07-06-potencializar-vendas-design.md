# Potencializar vendas — Desbravando Rust

**Data:** 2026-07-06
**Objetivo:** Aumentar as vendas do livro atacando o gargalo real diagnosticado — **tráfego baixo** — por canais orgânicos (SEO, LinkedIn/redes, lista de e-mail), sem verba de anúncio. Aproveitar os ativos que já existem (17 posts de blog, funil de amostra, presença no LinkedIn do autor) e tapar os vazamentos de conversão que hoje desperdiçam cada visita escassa.

## Diagnóstico

Confirmado com o autor: o problema **não** é conversão de checkout nem página fraca — é **pouco tráfego chegando ao site**. Portanto tráfego lidera o plano; correções de conversão entram em paralelo por serem baratas e amplificarem cada visita.

Canais escolhidos pelo autor: **SEO orgânico + LinkedIn/redes + lista de e-mail**. Explicitamente **sem tráfego pago**.

Tipo de entrega escolhido: **os dois, faseado** — sprint técnico no repositório primeiro, depois playbook de distribuição contínua.

## Estado atual (o que já existe)

- **Home** (`index.html`): hero, depoimentos, "o que vai aprender", "dentro do livro" (stats + sumário), "veja por dentro", autor, preço/CTA, FAQ, últimos posts.
- **Blog**: 17 posts em `posts/NNNN-slug/README.md` (markdown puro, sem front-matter), cada um com CTA contextual (`_data/cta_posts.yml`) e capa OG gerada por workflow.
- **Amostra** (`/amostra/`): captura e-mail via Google Form (`forms.gle/...`) → Apps Script (`scripts/autorresposta-capitulo-html.gs`) manda **um** e-mail com o capítulo.
- **Checkout**: Kiwify, R$ 89,90.
- **Obrigado** (`/obrigado/`): dispara `purchase` (GA4 + Meta Pixel).
- **Analytics**: só GA4 ativo (`G-XL3S6FDENZ`). Meta Pixel e LinkedIn vazios no `_config.yml`.

## Buracos identificados (linha de base)

1. 🔴 **Seção de prova social não renderiza** — `_data/depoimentos.yml` está vazio.
2. 🔴 **Seção "Veja por dentro" não renderiza** — não existe `imgs/preview/`.
3. 🔴 **Captura de e-mail só na `/amostra/`** — os 17 posts (a porta de entrada orgânica) não capturam nada.
4. 🔴 **Autoresponder de tiro único** — leads ficam parados na planilha do Form; nenhum follow-up oferece o livro.
5. 🟡 **Zero dados estruturados (JSON-LD)** — sem elegibilidade a rich results (preço, FAQ, artigo).
6. 🟡 **Meta description compartilhada** — os 17 posts herdam a mesma description do site; só o título é único (`titles_from_headings`).
7. 🟡 **Funil cego** — GA4 mede só `begin_checkout` e `purchase`; lead, scroll até preço e clique na amostra são invisíveis.

## Guardrails de integridade (dependências do autor)

Itens que **não** serão fabricados e precisam de insumo real do autor:

1. **Depoimentos reais** — preencher `_data/depoimentos.yml` com depoimentos verídicos. Fabricar prova social é fraude e destrói confiança de público dev. Entregável do design: estrutura pronta + roteiro de como pedir a leitores/colegas.
2. **Imagens de preview** — prints reais de páginas do livro em `imgs/preview/`. Entregável: slot + instruções de exportação.
3. **Link do PDF da amostra no Drive** e qualquer afirmação factual em e-mails — confirmados pelo autor.

## Decisão de estratégia

**Abordagem A — Motor de tráfego primeiro, funil em paralelo.** O blog é o motor de descoberta; tudo que aumenta entrada de gente e captura de lead vem primeiro. Correções de conversão (baratas) entram junto porque cada visita escassa vale muito. Rejeitadas: (B) funil primeiro — polir página que ninguém vê rende ~0; (C) flywheel de e-mail isolado — é sub-componente de A, não substituto.

---

## Fase 1 — Motor de tráfego + tapar buracos (implementação no repositório)

Ordem de entrada:

### 1.1 Medição (pré-requisito)
Novos eventos GA4, para tornar o funil visível ponta a ponta:
- `generate_lead` — envio do Google Form da amostra (via retorno/redirect ou evento no clique de submit).
- `view_price` — scroll até o bloco `#comprar` (IntersectionObserver).
- `select_content` — clique em "Ler capítulo gratuito".

Funil resultante: visita → lead → view_price → begin_checkout → purchase.

### 1.2 SEO técnico (maior alavancador de tráfego orgânico)
- **Meta description por post.** Cada post recebe description própria (front-matter mínimo ou extração do 1º parágrafo via Liquid em `_layouts/post.html`/`default.html`). Não pode quebrar o fluxo do `blog_agent` que gera posts.
- **JSON-LD:**
  - `Book` + `Offer` (preço, moeda BRL, disponibilidade) na home.
  - `FAQPage` na seção de FAQ da home.
  - `BlogPosting` + `BreadcrumbList` em cada post.
- **Clusters de links internos.** Cross-linkar posts relacionados por tópico (ex.: ownership ↔ lifetimes ↔ smart pointers; benchmarks entre si). Fonte: os 17 posts existentes. Mecanismo a definir no plano (mapa em `_data/` ou bloco "leia também").

### 1.3 Captura de e-mail nos posts (balde furado #3)
Bloco "Receba o capítulo grátis" ao fim de cada post (em `_layouts/post.html`, junto do `post-cta`), reaproveitando o Google Form existente. Cada visitante orgânico vira lead em potencial. Dispara `generate_lead`.

### 1.4 Sequência de nutrição de e-mail (balde furado #4)
Evoluir o autoresponder de 1 tiro para sequência curta via time-triggers do Apps Script (sem ESP pago):
1. Capítulo (já existe).
2. "O que mais tem no livro" + post relevante do blog.
3. Prova/autoridade (rsfn4py, trajetória, bastidor).
4. Oferta com CTA de compra (cupom real se houver).

Requer estado por lead (planilha do Form já é a fonte) e triggers agendados. Detalhe de implementação no plano.

### 1.5 Buracos de conversão (baratos, amplificam cada visita)
- Preencher `_data/depoimentos.yml` (autor fornece depoimentos reais).
- Popular `imgs/preview/` (autor fornece prints).
- Urgência honesta: usar `cupom`/`cupom_texto`/`preco_antigo` que já existem no `_config.yml` para uma oferta real por tempo limitado — **sem âncora falsa** (mantém a decisão do spec de 2026-07-02).

---

## Fase 2 — Playbook de distribuição contínua (execução do autor, moldes no repo)

O SEO amadurece em semanas/meses; o LinkedIn traz tráfego imediato. A Fase 2 é o combustível recorrente. Execução é do autor; o repo entrega os moldes que reduzem o atrito.

Entregáveis in-repo:

1. **`docs/playbook-distribuicao.md`** — cadência realista (2 posts LinkedIn/semana: 1 reaproveitando post do blog, 1 bastidor/aprendizado); regra de canal (valor no corpo, link no 1º comentário, CTA sutil do livro).
2. **Moldes de repurpose** — esqueleto de post de LinkedIn por tipo de conteúdo: gancho → insight → mini-código/benchmark → convite pro blog.
3. **`scripts/social_snippet.py`** — lê um post do blog e gera rascunho de post social (gancho + trechos-chave + hashtags + link), reaproveitando a capa OG já gerada. Objetivo: editar em ~5 min em vez de partir do zero.
4. **Calendário-semente (8 semanas)** — mapeia qual dos 17 posts vira conteúdo em qual semana, priorizando benchmarks e "Rust acelerando Python".
5. **Loop de lista de e-mail** — playbook de 1 broadcast mensal para a lista (novo post + nudge do livro), fechando tráfego → lead → venda.

Fica com o autor: escrever/postar (com os moldes), prints de preview, coletar depoimentos reais.

## Fora de escopo (YAGNI)

Tráfego pago; ESP pago (Mailchimp/ConvertKit); agendador automático de posts; vídeo/YouTube. Se necessário no futuro, cada um vira sub-projeto próprio com spec.

## Critérios de sucesso

- Funil mensurável ponta a ponta no GA4 (lead, view_price, checkout, purchase).
- Todo post captura e-mail; leads entram numa sequência que oferece o livro.
- Rich results elegíveis (Book/Offer, FAQ) e description única por post.
- Prova social e previews visíveis na home (após insumo do autor).
- Playbook + moldes de distribuição prontos para execução semanal sustentável.
- Métrica-guia: crescimento de sessões orgânicas + de LinkedIn, e de leads capturados/mês.
