# Publicando posts e entendendo o build

Guia dos dois fluxos mais comuns do site: **escrever um post novo** e **aproveitar PRs de posts que já estão abertos**.

---

## Como o site é construído (o essencial)

- O site roda no **GitHub Pages clássico** (opção "Deploy from a branch" → `main`).
- Quando algo entra na `main`, o **GitHub Pages roda o Jekyll automaticamente** e publica `https://desbravandorust.com.br`. Não existe workflow de deploy para manter — é automático.
- Você escreve **sempre em Markdown**, nunca em HTML. O visual (tema escuro, header com botão de compra, banner de venda no fim, syntax highlighting) vem dos arquivos `_layouts/` e `_config.yml` e é aplicado **sozinho** a qualquer post.

### A pasta `_site/` — não mexa nela

`_site/` é o **resultado** do build (o HTML final que o Jekyll gera). Ela está no `.gitignore` e é recriada a cada build. Você **nunca** edita, commita ou escreve nada dentro de `_site/`. Se quiser ver o site formatado localmente antes de publicar, rode `jekyll serve` e o Jekyll gera o `_site/` para você.

---

## 1. Escrevendo um post novo

### Onde escrever

Crie uma pasta com numeração sequencial e um `README.md` dentro dela:

```
posts/
  0022-titulo-curto-do-post/
    README.md          ← o conteúdo, em Markdown
    imgs/
      cover.png        ← imagem de capa (usada no card do LinkedIn)
```

**Não** escreva em `_site/posts/` — aquilo é gerado. O arquivo-fonte é sempre `posts/NNNN-slug/README.md`.

### Regras de formatação do arquivo

Siga o mesmo padrão dos posts existentes (ex.: `posts/0017-orm-mentindo-n1-sqlx/README.md`):

1. **A primeira linha tem que ser o título com um `#`:**
   ```markdown
   # Título do post que aparece no blog e na aba do navegador
   ```
   O título dos cards do `/blog` e da home é extraído dessa linha automaticamente (plugin `jekyll-titles-from-headings`). Se a primeira linha não for um `# ...`, o card sai **sem título**.

2. **Não envolva o arquivo inteiro em cerca de código.** Um arquivo que começa com ` ```markdown ` e termina com ` ``` ` faz o post inteiro virar um bloco de código e quebra a extração do título. (Foi o bug que o post 0015 tinha.) Cercas de código são só para trechos de código dentro do texto.

3. **Coloque a imagem de capa em `imgs/cover.png`** dentro da pasta do post. Ela é usada como imagem de compartilhamento (Open Graph) — é o que aparece quando você posta o link no LinkedIn. Se não houver `cover.png`, o site usa a capa do livro como fallback.

### Publicando

1. Crie a pasta e o `README.md` (numa branch, ex.: `feat/post-22`).
2. Commit + abra um PR.
3. **Ao dar merge do PR em `main`, o GitHub Pages reconstrói o site sozinho** — exatamente como acontece hoje com os posts em Markdown. Em 1–2 minutos o post está no ar, já com o layout da marca, aparecendo automaticamente na home (6 mais recentes) e em `/blog` (todos).

Você não precisa editar nenhuma lista de posts à mão: home e `/blog` varrem a pasta `posts/` sozinhas.

---

## 2. PRs de posts que já estão abertos (posts agendados)

As branches `feat/post-18` … `feat/post-21` já trazem posts prontos, e **o conteúdo delas já está no formato certo** (Markdown, primeira linha `# Título`, capa em `imgs/cover.png`). **Você não precisa reformatar o conteúdo desses posts.**

O que dá o visual novo a eles são os `_layouts/` e o `_config.yml` — que vivem na `main`, não nos posts. Então o único ponto de atenção é a **ordem** e o **rebase**, porque essas branches foram criadas de uma `main` antiga, anterior ao redesenho da landing page.

### Passo a passo recomendado

1. **Primeiro, coloque a landing page nova na `main`** (merge da branch `feat/landing-page-vendas`). A partir daí, `main` tem os `_layouts/`, o `_config.yml` e o CSS.

2. **Para cada PR de post, atualize a branch com a `main` nova** antes de mergear. Duas formas:
   - **Rebase** (histórico mais limpo):
     ```bash
     git checkout feat/post-18
     git rebase main
     git push --force-with-lease
     ```
   - **Merge da main na branch** (mais simples, sem force-push):
     ```bash
     git checkout feat/post-18
     git merge main
     git push
     ```
   Os arquivos do post (`posts/0018-.../`) **não conflitam** com as mudanças da landing, então a atualização é tranquila. Se o Git acusar conflito, será só em arquivos como `README.md` da raiz ou `obrigado/index.html` — nesses casos, **fique com a versão da `main`** (a nova), porque a versão da branch de post é a antiga.

3. **Antes de mergear cada post, confira o formato** (checklist rápido):
   - [ ] Primeira linha do `README.md` é `# Título`
   - [ ] O arquivo **não** está inteiro dentro de uma cerca ` ```markdown `
   - [ ] Existe `imgs/cover.png` na pasta do post

4. **Merge do PR → GitHub Pages reconstrói e publica**, já com o layout novo.

### Por que não precisa "converter" os posts

O layout não está escrito dentro do arquivo do post — ele é aplicado por fora, pelo `_config.yml` (que manda todo post em `posts/**` usar o `_layouts/post.html`). Então "formatar no mesmo padrão" acontece de graça no build, desde que o Markdown siga as 3 regras acima. Não há passo de conversão manual.

---

## Testar localmente antes de publicar (opcional)

```bash
gem install jekyll jekyll-optional-front-matter jekyll-readme-index \
  jekyll-relative-links jekyll-titles-from-headings jekyll-sitemap
jekyll serve
```

Abra `http://localhost:4000` e navegue até o post. É o mesmo HTML que o GitHub Pages vai gerar.
