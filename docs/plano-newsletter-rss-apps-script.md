# Plano — Newsletter RSS→e-mail gratuita (Google Apps Script)

Objetivo: script agendado que lê o feed do site, pega o **último post**, e envia
um e-mail estilizado (identidade Desbravando Rust) para uma lista pequena (~10),
com **título, resumo, thumb da capa e link para leitura na íntegra**. Sem custo,
sem Mailchimp. Análogo ao `scripts/autorresposta-capitulo-html.gs`.

## Viabilidade (validada em 2026-07-08)

Tudo resolvido com APIs nativas do Apps Script — nenhuma dependência paga:

| Necessidade | Como | Custo |
|---|---|---|
| Baixar o feed | `UrlFetchApp.fetch()` | grátis |
| Parsear (é **Atom**, não RSS 2.0) | `XmlService` + namespace `http://www.w3.org/2005/Atom` | grátis |
| Não reenviar o mesmo post | `PropertiesService` guarda o `id` do último enviado | grátis |
| Agendar | Gatilho por tempo (diário) | grátis |
| Enviar | `MailApp.sendEmail` (quota 100 dest./dia no Gmail comum) | grátis |

## Fatos do projeto que moldam o design

1. **Feed é Atom** (`/feed.xml`, layout `null`, escrito à mão). Campos por `<entry>`:
   `<title>`, `<link rel="alternate" href="…">`, `<id>`, `<published>`, `<summary>`
   (resumo = 1º parágrafo, truncado em 200 chars). O último post é a **primeira**
   `<entry>` (o feed já vem ordenado desc por path).
2. **A capa NÃO vem no feed.** Convenção fixa do repo: a capa do post é
   `<url-do-post>/imgs/cover.png` (fallback `.jpg`; senão `/imgs/og-default.png`).
   → derivar a thumb a partir do `href` da entry, não do feed.
3. Feed URL: `https://desbravandorust.com.br/feed.xml`. Site: `desbravandorust.com.br`.
4. Identidade visual (reusar do autorresponder): fundo `#0e1524`, card `#1b2740`,
   borda topo laranja `#f74c00`, título `#e8edf5`, texto `#b8c2d0`, marca
   "Desbravando **Rust**" (`#ff7a3d`). Layout em tabelas + estilos inline.

## Lista de e-mails (~10)

Usar uma aba `assinantes` numa planilha (coluna A = e-mails, 1 por linha, a
partir da linha 2). Vantagem: o autor edita sem mexer no código, e sobra espaço
pra colunas futuras (nome, data de inscrição). Enviar **um** e-mail com todos em
**Bcc** (privacidade + simples). 10 destinatários ≪ quota de 100/dia.

> Alternativa mais preguiçosa: array `ASSINANTES = ['a@x.com', ...]` no topo do
> script. Escolher a planilha se o autor for gerenciar a lista sozinho.

## Anti-reenvio

`PropertiesService.getScriptProperties()` guarda `ultimo_post_id`. A cada
execução: pega o `id` da 1ª entry; se for **igual** ao salvo, não faz nada; se
for diferente, envia e atualiza a property. Assim o gatilho pode rodar 1x/dia
tranquilo — só dispara quando sai post novo.

## Thumb da capa (o único ponto não-trivial)

Derivar de `postUrl`:
- `coverPng = postUrl + '/imgs/cover.png'`
- No `<img>`: `width="600"` + `style="max-width:100%;height:auto;border-radius:12px"`
  (a capa é 1200×630; o cliente de e-mail escala).
- Fallback: a maioria dos posts tem `cover.png`. Para robustez, uma checagem
  `UrlFetchApp.fetch(coverPng, {muteHttpExceptions:true}).getResponseCode()`:
  200 → usa png; senão tenta `cover.jpg`; senão `https://desbravandorust.com.br/imgs/og-default.png`.
  <!-- ponytail: se todo post novo sempre tiver cover.png, pular a checagem e
       usar png direto com og-default como único fallback. Adicionar a checagem
       só se aparecer post sem cover.png. -->

## Estrutura do script (`scripts/newsletter-ultimo-post.gs`)

```
// Constantes: FEED_URL, SITE, PLANILHA_ID (ou ASSINANTES[]), REMETENTE, OG_DEFAULT

function enviarUltimoPost() {
  1. resp = UrlFetchApp.fetch(FEED_URL)            // baixa Atom
  2. entry = primeiraEntry(resp.getContentText())  // XmlService + ns Atom
  3. if (entry.id === propriedade('ultimo_post_id')) return   // nada novo
  4. cover = resolverCapa(entry.link)              // png→jpg→og-default
  5. html = montarHtml(entry.title, entry.summary, cover, entry.link)
  6. enviarBcc(listaAssinantes(), 'Novo no Desbravando Rust: ' + entry.title, html)
  7. salvarPropriedade('ultimo_post_id', entry.id)
}

function primeiraEntry(xml) {
  // XmlService.parse → root.getChild('entry', ns)
  // ns = XmlService.getNamespace('http://www.w3.org/2005/Atom')
  // title = getChildText; link = getChild('link',ns).getAttribute('href').getValue()
  // summary = getChildText('summary',ns); id = getChildText('id',ns)
}

function montarHtml(titulo, resumo, coverUrl, postUrl) {
  // reusar tabela/inline-style do autorresposta-capitulo-html.gs:
  //   marca → <img cover> → <h1 titulo> → <p resumo> → botão "Ler na íntegra"
  //   → rodapé com link do site + linha de descadastro
}

function testeNewsletterDryRun() {
  // Logger.log do título/resumo/cover/link do último post, SEM enviar e SEM
  // gravar a property. Rodar 1x antes de ativar o gatilho.
}
```

## Template do e-mail (blocos, na ordem)

Reusar `montarHtml` do `autorresposta-capitulo-html.gs` como base e trocar o miolo:

1. **Marca** — "Desbravando **Rust**".
2. **Capa** — `<img>` da thumb (link clicável para o post).
3. **Título** — `<h1>` = título do post.
4. **Resumo** — `<p>` = `<summary>` do feed.
5. **CTA** — botão laranja `#f74c00` "Ler na íntegra" → `postUrl`.
6. **Rodapé** — link do site + **linha de descadastro** ("Não quer mais receber?
   responda com SAIR" — remoção manual da planilha; suficiente p/ lista pequena).

Incluir também `body` (texto puro) além do `htmlBody`, como no autorresponder.

## Instalação (documentar no topo do .gs)

1. Planilha → Extensões → Apps Script → colar o arquivo.
2. Ajustar constantes (`PLANILHA_ID`/aba `assinantes`, `FEED_URL` já preenchida).
3. Rodar `testeNewsletterDryRun()` uma vez e conferir os logs.
4. Rodar `enviarUltimoPost()` manualmente 1x (autoriza escopos + envia o atual e
   grava `ultimo_post_id`, evitando reenvio retroativo).
5. Criar gatilho de tempo: `enviarUltimoPost`, "Baseado em tempo" → "Dia" (1x/dia).

## Limites / decisões conscientes

- **Quota**: 100 dest./dia (Gmail comum) / 1500 (Workspace). ~10 → sem risco.
  Se a lista crescer muito, é o teto real desta abordagem — aí sim migrar p/
  serviço dedicado.
- **Sem tracking de abertura/clique** (não dá sem pixel/serviço externo). Ok.
- **Descadastro é manual** (apagar linha da planilha). Aceitável em ~10.
- **1 post por execução**: se dois posts saírem entre execuções, só o mais novo
  é enviado. Para o ritmo do blog, irrelevante. Se importar, iterar entries
  até bater no `ultimo_post_id` e enviar as pendentes em ordem.
```
