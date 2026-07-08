---
name: escrever-post-blog
description: Use ao escrever um novo post para o blog Desbravando Rust (repositório desbravandorust.github.io) a partir de um tema. Cobre estrutura, tom, comparações Python↔Rust, referências cruzadas entre posts, SEO, o cross-post no dev.to (tags/tema em devto_temas.yml) e os arquivos de marketing (cta_posts.yml) que geram leads para a venda do livro.
---

# Escrever post do blog Desbravando Rust

## Objetivo
Gerar um post novo idêntico em estrutura, tom e apelo comercial aos posts
existentes (0001–0022), com um único fim: converter leitor pythonista em comprador
do livro **Desbravando Rust** (https://desbravandorust.com.br).

Todo post é **material de apoio do livro** — o conteúdo entrega valor real e
termina levando à compra.

## Passo a passo (checklist — crie um todo por item)

1. Escolher o **arquétipo** do tema (ver tabela abaixo).
2. Escolher o próximo número: `NNNN` = maior número em `posts/` + 1, com 4 dígitos.
3. Criar `posts/NNNN-slug-descritivo/README.md` (slug em kebab-case, com palavras-chave de SEO; posts de conceito terminam em `-pythonistas`).
4. Escrever o corpo seguindo a **Anatomia** e o tom (use `template-post.md` como esqueleto).
5. **Primeiro parágrafo = meta description**: garanta que a primeira linha de prosa (depois do título/autor/capa) funcione sozinha como resumo de SEO (ver seção dedicada abaixo).
6. Adicionar **1–2 referências cruzadas inline** a posts relacionados (ver Referências cruzadas).
7. Adicionar a entrada em `_data/relacionados.yml` (chave `"NNNN"` com 3 posts do mesmo cluster) **e** incluir `NNNN` na lista dos posts relacionados que fazem par (ver Referências cruzadas).
8. Adicionar a linha de CTA contextual em `_data/cta_posts.yml` na chave `"NNNN"`.
9. Adicionar o **tema do dev.to** em `_data/devto_temas.yml` na chave `"NNNN"` (1 palavra, sem espaço — vira a 4ª tag no dev.to). **Sem isso o post é publicado só com as 3 tags fixas** (ver "Publicar no dev.to").
10. Se houver imagens, colocá-las em `posts/NNNN-slug/imgs/` e referenciar como `imgs/arquivo.png` (relativo — nunca URL absoluta).
11. Verificar: `index.html` e `/blog/` **atualizam sozinhos** — só confira que `NNNN` é o maior número (aparece primeiro na home, que lista os 6 mais recentes).

## Mecânica do Jekyll (o que é automático vs manual)

| Elemento | Como funciona |
|---|---|
| Título da página | Vem do `# H1` (plugin `titles-from-headings`). **Sem YAML front matter.** |
| Data no blog | Extraída da linha `###### Por [@zejuniortdr](...) em <data>`. O formato **exato** importa. |
| Home "Últimos posts" + página `/blog/` | **Automáticas** — ordenam por path invertido, limit 6 na home. Número maior = topo. Não edite manualmente. |
| Botões de compartilhar (LinkedIn/X/WhatsApp/Telegram/copiar) | Injetados automaticamente por `_layouts/post.html`. **Não coloque no corpo.** |
| Card final "Gostou deste conteúdo?" com capa + botão comprar | Injetado automaticamente pelo layout. |
| CTA contextual dentro desse card | Puxada de `_data/cta_posts.yml[NNNN]`. **Este arquivo você edita.** |
| Bloco "Receba um capítulo grátis" (captura de e-mail) | Injetado automaticamente por `_layouts/post.html` (`lead-capture.html`). **Não coloque formulário/captura no corpo.** |
| JSON-LD (`BlogPosting` + `BreadcrumbList`) | Gerado automaticamente por `schema-post.html`. Nada a fazer no corpo. |
| **Meta description** (`<meta description>` + `og:`/`twitter:`) | **Extraída automaticamente do 1º parágrafo do post** (`_includes/meta-description.html`). O que você escreve na 1ª linha de prosa vira o snippet no Google e nos cards de compartilhamento. **Você controla isso pelo texto** — ver seção abaixo. |
| Bloco "Leia também" (links internos estruturados) | Renderizado a partir de `_data/relacionados.yml[NNNN]`. **Este arquivo você edita** (além dos links inline no corpo). |

As duas primeiras linhas do README **têm formato fixo**:

```markdown
# Título do Post: subtítulo cativante para Pythonistas
###### Por [@zejuniortdr](https://github.com/zejuniortdr/) em Mês DD, YYYY
```

Mês abreviado em PT-BR: `Jan Fev Mar Abr Mai Jun Jul Ago Set Out Nov Dez`
(ex.: `Jul 04, 2026`). Use a data de hoje.

## Arquétipos de post (escolha 1)

| Arquétipo | Quando | Exemplos | Marca registrada |
|---|---|---|---|
| **Conceito para Pythonistas** | Ensinar um recurso de Rust (ownership, traits, enums, closures, strings…) | 0005, 0008, 0009, 0011, 0015, 0022 | Bloco Rust seguido do equivalente Python; "Erros comuns de Pythonistas"; tabelas comparativas; "O que aprendemos". Slug termina em `-pythonistas`. |
| **Benchmark / Comparação** | Provar performance com números reais | 0001, 0002, 0016, 0019, 0021 | Ambiente de execução detalhado, tabela de métricas, gráfico em `imgs/`, análise, "quando usar cada um". |
| **Opinião / Caso real** | Tese provocativa + prova prática | 0004, 0017, 0018, 0020 | Abertura incômoda ("Seu ORM está mentindo", "Eu apaguei meu Celery"), caso concreto, checklist acionável, "O que esse caso ensina", muitas vezes série. |

## Anatomia do corpo

1. **Título** (`#`) — descritivo, com palavra-chave. Conceito: `X em Rust: <gancho> para Pythonistas`. Benchmark: `A vs B: <resultado>`. Opinião: frase provocativa.
2. **Linha de autor/data** (formato fixo acima).
3. **(Opcional) capa**: `![Cover](imgs/cover.png)` — comum nos posts recentes.
4. **Gancho de abertura** (1–3 parágrafos): cenário identificável do pythonista ("Se você vem do Python e já viu o erro `value moved here`…"), analogia (ownership = anfitrião da festa), anedota de timeline, ou tese provocativa. Aqui entra a **referência cruzada** quando o tema puxa um post anterior.
5. **Seções `##`** de desenvolvimento: para cada ideia, **bloco de código Rust imediatamente seguido do equivalente Python** com "Compare com Python:". Comentários no código explicam o *porquê*.
6. **"Erros comuns de Pythonistas em Rust"** (posts de conceito): erro → **Solução:** com código corrigido.
7. **Tabelas comparativas** `| Característica | Python | Rust |`.
8. **Exemplo prático completo** — versão Rust e versão Python lado a lado.
9. **(Opcional) Exercício** com dica.
10. **Fecho de aprendizado** — "O que aprendemos? 📚" (conceito) ou "O que esse caso ensina" (benchmark/opinião): resumo do que fica.
11. **Gancho para o próximo passo** — provoca o próximo post da jornada; se citar um post existente, **linke-o** (não só mencione).
12. **CTA do livro** — parágrafo final levando a `https://desbravandorust.com.br` (ver Lead-gen).

## O primeiro parágrafo é a sua meta description (regra nova, crítica)

O layout **extrai automaticamente a 1ª linha de prosa do post** e a usa como
`<meta name="description">`, `og:description` e `twitter:description` — ou seja,
é o texto que aparece no Google e nos cards de LinkedIn/WhatsApp. A extração é
**baseada em linha** (pega a primeira linha não vazia que não começa com `#` nem
`!`), corta em **160 caracteres**. Consequências práticas ao escrever o gancho:

- **Escreva o 1º parágrafo como UMA linha física** (sem quebra manual no meio).
  Se você quebrar o parágrafo em várias linhas, só a 1ª linha vira a description.
- **Faça a 1ª frase valer sozinha como resumo**: clara, com a palavra-chave do
  tema, atraente fora de contexto. Os ~155 primeiros caracteres são o que o
  leitor vê no Google — não desperdice com "Esta é a última parada de uma jornada…".
- **Não comece o corpo com lista, citação (`>`), tabela (`|`) ou um link
  `[texto](url)`** — a description sairia truncada ou sem sentido. Comece com
  prosa. (Referência cruzada inline pode vir logo na sequência, não como 1ª linha.)
- A capa `![Cover](imgs/cover.png)` e a linha de autor são puladas
  automaticamente — pode mantê-las antes do parágrafo normalmente.

## Tom e voz

- PT-BR, segunda pessoa ("você"), acolhedor e encorajador ("Calma, você não está sozinho nessa jornada").
- Rust **sempre traduzido a partir do que o pythonista já sabe** — Python é a ponte, nunca pré-requisito acadêmico.
- Chama o leitor de "pythonista"/"desbravador". Emojis com parcimônia (🦀 📚 🚀 👋 💡).
- Honesto: mostra trade-offs de Rust e reconhece onde Python ganha (ex.: 0001 reteste com 8 workers). Isso gera credibilidade — e credibilidade vende.
- Código **completo e executável**, não pseudocódigo.

## Referências cruzadas (dois mecanismos — faça os dois)

Existem **dois** caminhos de link interno, e cada post novo deve usar ambos:

**1. Links inline no corpo (obrigatório: 1–2 por post).** Linke posts
relacionados dentro do texto para segurar o leitor e reforçar a jornada. Use
**link relativo** ao diretório do post:

```markdown
No [post sobre Django ORM vs SQLx](../0004-django-orm-vs-sqlx) eu defendi que...
```

Para linkar uma seção específica, use a URL absoluta com âncora
(`https://desbravandorust.com.br/posts/0001-performance-na-pratica/#ambiente-do-execu%C3%A7%C3%A3o`).

> ⚠️ Se o corpo narra uma "jornada" citando outros posts ("mostrei o Axum
> superar o FastAPI", "troquei o worker"), **transforme cada citação em um
> link** — mencionar sem linkar desperdiça o reforço de SEO e de navegação.

**2. Cluster estruturado em `_data/relacionados.yml` (obrigatório).** Alimenta o
bloco automático "Leia também" no fim do post. Adicione a chave do post novo com
3 números do mesmo cluster temático, **e** insira o número do post novo nas
listas dos posts com que ele faz par (o mapa é aproximadamente mútuo):

```yaml
"0022": ["0005", "0006", "0012"]   # strings ↔ ownership, memória, lifetimes
```

Mapa rápido de temas → post (use para escolher tanto os links inline quanto o cluster):

- Ownership/memória → 0005, 0006 · Erros → 0008 · Enums/pattern matching → 0007, 0015
- Traits → 0009 · Concorrência → 0010, 0021 · Iteradores/closures → 0011 · Lifetimes → 0012
- Smart pointers → 0013 · Macros → 0014 · Strings (String/&str) → 0022
- Performance/API → 0001, 0019 · Dados → 0002 · ORM/SQLx → 0004, 0017 · Cargo → 0003
- Rust+Python (PyO3/WASM) → 0016, 0020 · Rust no stack Python (fila/worker) → 0018
- GIL / free-threading / paralelismo → 0021, 0010

## SEO

- Slug em kebab-case com as palavras-chave do tema (o slug vira a URL).
- Título com o termo que o leitor buscaria + "Rust"/"Python".
- Sem front matter: o título vem do `#`; a **description sai do 1º parágrafo**
  (ver seção "O primeiro parágrafo é a sua meta description") — não é mais a
  global do `_config.yml` para posts.
- JSON-LD (`BlogPosting`/`BreadcrumbList`) e o cluster "Leia também" são gerados
  automaticamente — o seu trabalho de SEO é o 1º parágrafo, o slug, o título e a
  entrada em `_data/relacionados.yml`.

## Depois de publicar: distribuição (opcional, mas recomendado)

O tráfego orgânico do blog é o motor de vendas. Para transformar o post em
alcance imediato:

- `python3 scripts/social_snippet.py posts/NNNN-slug/README.md` gera um rascunho
  de post de LinkedIn (gancho + trecho de código + hashtags + link) a partir do post.
- `docs/playbook-distribuicao.md` traz a cadência, os moldes por arquétipo e o
  calendário de distribuição. Regra de ouro: valor no corpo do post social, link
  no 1º comentário.

## Publicar no dev.to (cross-post canônico)

`scripts/publica_devto.py` republica o post no dev.to com `canonical_url`
apontando de volta pro blog. Ele **já resolve sozinho** os problemas que davam
retrabalho — **não ajuste o corpo por causa deles**:

| O script faz automaticamente | Problema que evita |
|---|---|
| Remove o 1º `# H1` (título) e a 1ª imagem (capa) do corpo antes de enviar | o dev.to já renderiza `title` e `cover_image` no topo — sem isso saíam **título e capa duplicados** |
| Absolutiza imagens: `imgs/x.png` → `https://desbravandorust.com.br/posts/NNNN-slug/imgs/x.png` (com o prefixo numérico!) | o dev.to não reescreve caminho relativo — **imagem quebrada** no proxy |
| Remove `{% raw %}` / `{% endraw %}` | são guardas do Jekyll; no dev.to viram Liquid inválido (**"Unknown tag endraw"**) |
| `published_at` sempre entre aspas no front matter de agendamento | sem aspas o YAML do Forem lê como `Time` e rejeita (**422 "Title can't be blank"**) |
| Monta as tags `braziliandevs, python, rust` + o tema do post | — |

**O ÚNICO passo manual ao criar um post novo é adicionar o tema em
`_data/devto_temas.yml`** (checklist item 9), chave `"NNNN"`, 1 palavra sem
espaço (ex.: `"0023": ownership`). **Sem essa entrada o post publica só com as 3
tags fixas** — foi o que mais gerou retrabalho.

Para o auto-tratamento acima funcionar, o corpo (a Anatomia já garante) precisa:
- **Título como 1º `# H1`** e **capa como 1ª imagem markdown** (`![Cover](imgs/cover.png)`) — é assim que o script os identifica pra remover a duplicata.
- **Imagens sempre relativas** (`imgs/arquivo.png`), nunca URL absoluta escrita à mão.

Obs.: a API do dev.to faz **POST** (cria artigo novo) a cada execução — não
atualiza o anterior. Ao republicar após corrigir algo, **apague o rascunho/preview
antigo** pra não duplicar o artigo.

## Lead-gen — foco na venda do livro (não pule)

1. **`_data/cta_posts.yml`**: adicione a chave `"NNNN"` com uma frase que amarra o tema do post ao livro. Padrão observado: pergunta sobre o que a pessoa acabou de curtir + o que o livro entrega. Ex.: `"0018": "Curtiu entender <tema>? O livro tem um capítulo dedicado a <benefício>."`
2. **CTA final no corpo**: parágrafo levando a `https://desbravandorust.com.br`, enquadrando o post como material de apoio do livro. Varie a frase (veja fim dos posts existentes), mas sempre com o link.
3. Confie no layout para o resto (share + card de compra com capa).

## Erros a evitar

- ❌ Adicionar YAML front matter, botões de share, card de compra **ou bloco de captura de e-mail** manualmente (o layout já injeta tudo isso).
- ❌ Editar `index.html`/`blog/index.html` para listar o post (é automático).
- ❌ Esquecer a linha de CTA em `cta_posts.yml` (cai no genérico e perde conversão).
- ❌ Esquecer a entrada em `_data/relacionados.yml` (o bloco "Leia também" fica vazio e o post perde link interno estruturado).
- ❌ **Esquecer o tema em `_data/devto_temas.yml`** (o post é cross-postado no dev.to só com as 3 tags fixas, sem a 4ª tag do tema).
- ❌ **1º parágrafo fraco, multi-linha, ou começando com lista/citação/tabela/link** — ele vira a meta description do Google e dos cards sociais; escreva-o como uma única linha de prosa que valha sozinha.
- ❌ Narrar a "jornada" citando outros posts **sem linká-los** (referência sem link é SEO desperdiçado).
- ❌ Data fora do formato `Mês DD, YYYY` em PT-BR (quebra a data no blog).
- ❌ Número de post que não seja o maior (fica fora dos "6 mais recentes" da home).
- ❌ Código só em Rust sem o par em Python (o diferencial do blog é a comparação).
