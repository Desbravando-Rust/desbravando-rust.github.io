---
name: escrever-post-blog
description: Use ao escrever um novo post para o blog Desbravando Rust (repositório desbravandorust.github.io) a partir de um tema. Cobre estrutura, tom, comparações Python↔Rust, referências cruzadas entre posts, SEO e os arquivos de marketing (cta_posts.yml) que geram leads para a venda do livro.
---

# Escrever post do blog Desbravando Rust

## Objetivo
Gerar um post novo idêntico em estrutura, tom e apelo comercial aos 17 posts
existentes, com um único fim: converter leitor pythonista em comprador do livro
**Desbravando Rust** (https://desbravandorust.com.br).

Todo post é **material de apoio do livro** — o conteúdo entrega valor real e
termina levando à compra.

## Passo a passo (checklist — crie um todo por item)

1. Escolher o **arquétipo** do tema (ver tabela abaixo).
2. Escolher o próximo número: `NNNN` = maior número em `posts/` + 1, com 4 dígitos.
3. Criar `posts/NNNN-slug-descritivo/README.md` (slug em kebab-case, com palavras-chave de SEO; posts de conceito terminam em `-pythonistas`).
4. Escrever o corpo seguindo a **Anatomia** e o tom (use `template-post.md` como esqueleto).
5. Adicionar **1–2 referências cruzadas** a posts relacionados (ver Referências cruzadas).
6. Adicionar a linha de CTA contextual em `_data/cta_posts.yml` na chave `"NNNN"`.
7. Se houver imagens, colocá-las em `posts/NNNN-slug/imgs/` e referenciar como `imgs/arquivo.png`.
8. Verificar: `index.html` e `/blog/` **atualizam sozinhos** — só confira que `NNNN` é o maior número (aparece primeiro na home, que lista os 6 mais recentes).

## Mecânica do Jekyll (o que é automático vs manual)

| Elemento | Como funciona |
|---|---|
| Título da página | Vem do `# H1` (plugin `titles-from-headings`). **Sem YAML front matter.** |
| Data no blog | Extraída da linha `###### Por [@zejuniortdr](...) em <data>`. O formato **exato** importa. |
| Home "Últimos posts" + página `/blog/` | **Automáticas** — ordenam por path invertido, limit 6 na home. Número maior = topo. Não edite manualmente. |
| Botões de compartilhar (LinkedIn/X/WhatsApp/Telegram/copiar) | Injetados automaticamente por `_layouts/post.html`. **Não coloque no corpo.** |
| Card final "Gostou deste conteúdo?" com capa + botão comprar | Injetado automaticamente pelo layout. |
| CTA contextual dentro desse card | Puxada de `_data/cta_posts.yml[NNNN]`. **Este arquivo você edita.** |

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
| **Conceito para Pythonistas** | Ensinar um recurso de Rust (ownership, traits, enums, closures…) | 0005, 0008, 0009, 0011, 0015 | Bloco Rust seguido do equivalente Python; "Erros comuns de Pythonistas"; tabelas comparativas; "O que aprendemos". Slug termina em `-pythonistas`. |
| **Benchmark / Comparação** | Provar performance com números reais | 0001, 0002, 0016 | Ambiente de execução detalhado, tabela de métricas, gráfico em `imgs/`, análise, "quando usar cada um". |
| **Opinião / Caso real** | Tese provocativa + prova prática | 0004, 0016, 0017 | Abertura incômoda ("Seu ORM está mentindo"), caso concreto, checklist acionável, muitas vezes série (Parte II). |

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
10. **"O que aprendemos? 📚"** — resumo em bullets.
11. **"Próximos passos"** — provoca o próximo post da jornada.
12. **CTA do livro** — parágrafo final levando a `https://desbravandorust.com.br` (ver Lead-gen).

## Tom e voz

- PT-BR, segunda pessoa ("você"), acolhedor e encorajador ("Calma, você não está sozinho nessa jornada").
- Rust **sempre traduzido a partir do que o pythonista já sabe** — Python é a ponte, nunca pré-requisito acadêmico.
- Chama o leitor de "pythonista"/"desbravador". Emojis com parcimônia (🦀 📚 🚀 👋 💡).
- Honesto: mostra trade-offs de Rust e reconhece onde Python ganha (ex.: 0001 reteste com 8 workers). Isso gera credibilidade — e credibilidade vende.
- Código **completo e executável**, não pseudocódigo.

## Referências cruzadas (obrigatório: 1–2 por post)

Linke posts relacionados para segurar o leitor no site e reforçar a jornada.
Use **link relativo** ao diretório do post:

```markdown
No [post sobre Django ORM vs SQLx](../0004-django-orm-vs-sqlx) eu defendi que...
```

Para linkar uma seção específica, use a URL absoluta com âncora
(`https://desbravandorust.com.br/posts/0001-performance-na-pratica/#ambiente-do-execu%C3%A7%C3%A3o`).
Mapa rápido de temas → post para escolher a referência:

- Ownership/memória → 0005, 0006 · Erros → 0008 · Enums/pattern matching → 0007, 0015
- Traits → 0009 · Concorrência → 0010 · Iteradores/closures → 0011 · Lifetimes → 0012
- Smart pointers → 0013 · Macros → 0014 · Performance/API → 0001 · Dados → 0002
- ORM/SQLx → 0004, 0017 · Rust+Python (PyO3) → 0016 · Cargo → 0003

## SEO

- Slug em kebab-case com as palavras-chave do tema (o slug vira a URL).
- Título com o termo que o leitor buscaria + "Rust"/"Python".
- Sem front matter: o título vem do `#` e a descrição global já está no `_config.yml`.

## Lead-gen — foco na venda do livro (não pule)

1. **`_data/cta_posts.yml`**: adicione a chave `"NNNN"` com uma frase que amarra o tema do post ao livro. Padrão observado: pergunta sobre o que a pessoa acabou de curtir + o que o livro entrega. Ex.: `"0018": "Curtiu entender <tema>? O livro tem um capítulo dedicado a <benefício>."`
2. **CTA final no corpo**: parágrafo levando a `https://desbravandorust.com.br`, enquadrando o post como material de apoio do livro. Varie a frase (veja fim dos posts existentes), mas sempre com o link.
3. Confie no layout para o resto (share + card de compra com capa).

## Erros a evitar

- ❌ Adicionar YAML front matter, botões de share ou card de compra manualmente (o layout já faz).
- ❌ Editar `index.html`/`blog/index.html` para listar o post (é automático).
- ❌ Esquecer a linha de CTA em `cta_posts.yml` (cai no genérico e perde conversão).
- ❌ Data fora do formato `Mês DD, YYYY` em PT-BR (quebra a data no blog).
- ❌ Número de post que não seja o maior (fica fora dos "6 mais recentes" da home).
- ❌ Código só em Rust sem o par em Python (o diferencial do blog é a comparação).
