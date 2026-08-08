# publica_devto.py — Publicação de posts no dev.to

Script para publicar (ou agendar) em lote os posts do blog Jekyll no
[dev.to](https://dev.to), redimensionando a capa e mantendo o `canonical_url`
apontando para o site — assim o SEO fica com o seu domínio.

## O que ele faz

- Lê os posts em Markdown da pasta `posts/` (com o front matter do Jekyll).
- Redimensiona a capa para **1000x400** (padrão do dev.to): reduz pela largura e
  corta a altura alinhada ao topo.
- Publica via API do dev.to com título, corpo, tags, capa e URL canônica.
- Permite selecionar um intervalo de posts, criar rascunhos, publicar direto ou agendar.

## Pré-requisitos

Este projeto usa o [uv](https://docs.astral.sh/uv/) para gerenciar as dependências.

Instale o uv (se ainda não tiver):

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# ou, se já tem pipx: pipx install uv
```

Crie o ambiente e instale as dependências (uma vez):

```bash
uv venv
uv pip install requests python-frontmatter pillow python-dotenv
```

Depois, rode o script sempre com `uv run` (ele usa o ambiente `.venv` criado acima):

```bash
uv run publica_devto.py --posts 1-15
```

> **Alternativa sem instalar nada por venv:** dá para declarar as dependências
> direto no cabeçalho do script (PEP 723) e rodar só com `uv run publica_devto.py`
> — o uv resolve as dependências sozinho. Se preferir esse modo, peça que eu
> adiciono o bloco de metadados ao script.

## Configuração da chave da API

1. Gere sua chave em **dev.to → Settings → Extensions → "DEV Community API Keys"**.
2. Crie um arquivo `.env` na raiz do projeto (use o `.env.example` como base):

   ```bash
   cp .env.example .env
   ```

   E preencha:

   ```
   DEVTO_API_KEY=sua_chave_aqui
   ```

O script lê o `.env` automaticamente. Uma variável já exportada no shell tem
prioridade sobre o `.env`.

> **Importante:** adicione `.env` ao seu `.gitignore` para **não** versionar a chave.

## Sobre a capa (leia antes de publicar)

A API do dev.to aceita a capa apenas como **URL pública**, não como upload de
arquivo. Por isso o script salva a capa redimensionada em
`assets/devto-covers/<slug>.jpg` dentro do repositório e usa a URL pública dela
(no seu GitHub Pages) como cover.

Isso implica um fluxo em **duas etapas**: gerar e publicar as imagens **antes** de
criar os posts, senão o dev.to tenta buscar uma URL que ainda não existe e a capa
sai quebrada.

A capa de origem é lida do campo `cover:` ou `image:` do front matter, aceitando
tanto uma URL quanto um caminho no repositório (ex.: `/assets/img/capa.png`).

## Como usar

### Fluxo recomendado (com capa)

```bash
# 1) Gerar as capas redimensionadas (sem publicar)
uv run publica_devto.py --posts 1-15 --somente-imagens

# 2) Subir as capas para ficarem públicas no GitHub Pages
git add assets/devto-covers && git commit -m "capas devto" && git push

# 3) Publicar (as capas já estão no ar; o dev.to consegue buscá-las)
uv run publica_devto.py --posts 1-15              # cria rascunhos
uv run publica_devto.py --posts 1-15 --publicar   # publica direto
```

### Publicar um único post

```bash
uv run publica_devto.py --posts 7            # rascunho
uv run publica_devto.py --posts 7 --publicar # publicado
```

### Publicar todos os posts

```bash
uv run publica_devto.py            # todos, como rascunho
uv run publica_devto.py --publicar # todos, publicados
```

### Agendar

Agenda a publicação para uma data/hora futura (horário de Brasília, -03:00).
Em lote, espaça os posts **1 por semana** a partir da data informada.

```bash
uv run publica_devto.py --posts 1-4 --agendar "2026-07-15 09:00"
```

> Confira os agendados em `https://dev.to/dashboard` (status **Scheduled**).
> Para cancelar ou remarcar, use o painel do dev.to.

## Parâmetros

| Parâmetro | Descrição |
|---|---|
| `--posts 1-15` | Intervalo pelo prefixo numérico do arquivo (`0001-…` a `0015-…`). Aceita também um único número (`--posts 7`). Sem esse parâmetro, processa **todos** os posts. |
| `--publicar` | Publica direto. Sem ele, cria **rascunho**. |
| `--agendar "AAAA-MM-DD HH:MM"` | Agenda; em lote, espaça 1 por semana. |
| `--somente-imagens` | Só gera as capas redimensionadas (não chama a API). |
| `--dir posts` | Pasta dos posts (padrão: `posts`). |

## Tags

Cada post é publicado com 4 tags: **comunidade** (`braziliandevs`), **`python`**,
**`rust`** e **1 tema**, extraído da primeira tag do front matter que não seja uma
dessas. Para trocar a tag de comunidade (ex.: usar `ptbr`), edite `TAG_COMUNIDADE`
no início do script. Garanta que cada post tenha ao menos uma tag de tema no front
matter, senão ele sai só com 3 tags.

## Modos de publicação (resumo)

| Comando | Resultado |
|---|---|
| *(sem flag)* | Cria **rascunho** (você revisa e publica no dev.to) |
| `--publicar` | Publica imediatamente |
| `--agendar "…"` | Agenda para a data (1 por semana em lote) |
| `--somente-imagens` | Apenas gera as capas, sem publicar |

## Ajustes no código (se necessário)

No início do `publica_devto.py`:

- `SITE_BASE` — URL do seu site (usada no `canonical_url` e na URL das capas).
- `POSTS_DIR` — pasta padrão dos posts.
- `COVERS_DIR` — pasta onde as capas redimensionadas são salvas.
- `TAG_COMUNIDADE` — tag da comunidade.
- `COVER_W`, `COVER_H` — dimensões da capa (padrão 1000x400).
