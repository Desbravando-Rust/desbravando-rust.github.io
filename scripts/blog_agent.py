#!/usr/bin/env python3
"""
Blog Agent - Gerador automático de posts para o blog Desbravando Rust
"""

import os, re, json
from datetime import datetime
from github import Github, GithubException
from huggingface_hub import InferenceClient

# ─────────────────────────────────────────────────────────────
# CONFIGURAÇÕES
# ─────────────────────────────────────────────────────────────
GITHUB_TOKEN        = os.environ.get("GH_PAT") or os.environ["GITHUB_TOKEN"]
HF_TOKEN            = os.environ["HF_TOKEN"]
REPO_NAME           = os.environ["GITHUB_REPOSITORY"]
POSTS_DIR           = "posts"
README_PATH         = "README.md"
POSTS_SECTION       = "## Últimos posts:"
MAIN_BRANCH         = "main"
POST_FILENAME       = "README.md"
MODEL_ID            = os.environ.get("MODEL_ID") or "deepseek-ai/DeepSeek-V3-0324"

# FIX: int(None) lança TypeError, não ValueError — helper dedicado
def _parse_int_env(key: str, default: int) -> int:
    try:
        return int(os.environ[key])
    except (KeyError, ValueError, TypeError):
        return default

THEME_MAX_TOKENS   = _parse_int_env("THEME_MAX_TOKENS", 1024)
CONTENT_MAX_TOKENS = _parse_int_env("CONTENT_MAX_TOKENS", 8192)

BLOG_CONTEXT = """
Você é um escritor técnico especializado em Rust e Python.
O blog 'Desbravando Rust' é voltado para programadores brasileiros,
especialmente aqueles com background em Python que querem aprender Rust.
O blog serve como material de apoio para o livro 'Desbravando Rust'.
Escreva SEMPRE em PT-BR, com linguagem acessível e didática.
""".strip()


# ─────────────────────────────────────────────────────────────
# 1. ABSORVER CONTEXTO EXISTENTE
# ─────────────────────────────────────────────────────────────

# FIX: posts não têm frontmatter — extrai título do primeiro # Heading
def extract_title(content: str, fallback: str) -> str:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return fallback


def get_existing_posts(repo) -> list:
    posts = []
    try:
        items = repo.get_contents(POSTS_DIR)
    except GithubException:
        print(f"  ⚠️  Diretório '{POSTS_DIR}' não encontrado. Iniciando do zero.")
        return posts

    for item in sorted(items, key=lambda x: x.name):
        if item.type != "dir":
            continue
        try:
            f = repo.get_contents(f"{POSTS_DIR}/{item.name}/{POST_FILENAME}")
            raw = f.decoded_content.decode("utf-8")
            posts.append({
                "dirname": item.name,
                "title":   extract_title(raw, item.name),
            })
        except GithubException:
            pass

    return posts


def get_next_number(posts: list) -> int:
    numbers = [
        int(m.group(1))
        for p in posts
        if (m := re.match(r"^(\d+)", p["dirname"]))
    ]
    return max(numbers, default=0) + 1


# ─────────────────────────────────────────────────────────────
# 2. DECIDIR O PRÓXIMO TEMA
# ─────────────────────────────────────────────────────────────

def choose_next_topic(posts: list, client: InferenceClient) -> dict:
    topics_list = "\n".join(
        f"- [{p['dirname']}] {p['title']}"
        for p in posts
    ) or "Nenhum post publicado ainda."

    # FIX: ']' estava faltando para fechar o array "outline"
    prompt = f"""{BLOG_CONTEXT}

## Posts já publicados:
{topics_list}

## Tarefa:
Sugira o PRÓXIMO post com progressão lógica de aprendizado de Rust para quem vem do Python.
NÃO repita temas acima. Seja específico.

Responda SOMENTE com JSON válido (sem blocos de código markdown):
{{
  "title": "Título do post em PT-BR",
  "slug": "slug-curto-kebab-case",
  "description": "Uma frase descrevendo o post",
  "tags": ["tag1", "tag2", "tag3"],
  "outline": [
    "Introdução: ...",
    "Seção 1: ...",
    "Seção 2: ...",
    "Comparação com Python: ...",
    "Conclusão: ..."
  ]
}}"""

    resp = client.chat.completions.create(
        model=MODEL_ID,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=THEME_MAX_TOKENS,
        temperature=0.7,
    )
    raw = resp.choices[0].message.content.strip()
    raw = re.sub(r"^```(?:json)?\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)
    return json.loads(raw)


# ─────────────────────────────────────────────────────────────
# 3. GERAR O CONTEÚDO DO POST
# ─────────────────────────────────────────────────────────────

def generate_post_content(topic: dict, posts: list, client: InferenceClient) -> str:
    recent_titles = "\n".join(f"- {p['title']}" for p in posts[-5:]) or "Nenhum ainda."
    outline = "\n".join(f"  - {s}" for s in topic.get("outline", []))

    # FIX: removida regra #12 (pedir ao LLM para atualizar README — impossível)
    prompt = f"""{BLOG_CONTEXT}

## Contexto (últimos posts publicados):
{recent_titles}

## Post a ser escrito:
Título: {topic['title']}
Slug: {topic['slug']}
Descrição: {topic['description']}
Tags: {', '.join(topic['tags'])}

Outline:
{outline}

## Regras de escrita:
1. Mínimo de 1500 palavras — prefira mais
2. Linguagem acessível para iniciantes em Rust com background Python
3. Introduza cada conceito com analogia ou contexto antes do código
4. Blocos ```rust extensos, comentados linha a linha em PT-BR
5. Compare SEMPRE com Python (```python) — mesmo problema nas duas linguagens
6. Use subtítulos (##, ###) para organizar bem o conteúdo
7. Seção "## O que aprendemos" ao final com bullet points dos conceitos
8. Ao menos um exemplo prático completo e funcional, não apenas fragmentos
9. Emojis com moderação nos títulos para deixar mais amigável
10. Explique os erros mais comuns de quem vem do Python nesse tema
11. Finalize com chamada para compra do livro com link já em markdowon [desbravandorust.com.br
](https://desbravandorust.com.br)

## Formato de saída:
Markdown puro, iniciando diretamente com o título:

# {topic['title']}

Sem frontmatter, sem `---`, sem bloco de metadados."""

    # FIX: era client.chat_completion() — API antiga e removida
    resp = client.chat.completions.create(
        model=MODEL_ID,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=CONTENT_MAX_TOKENS,
        temperature=0.75,
    )
    return resp.choices[0].message.content.strip()


# ─────────────────────────────────────────────────────────────
# 4. ATUALIZAR ÍNDICE NO README DA RAIZ  ← NOVO
# ─────────────────────────────────────────────────────────────

def update_readme_index(repo, branch: str, dirname: str, topic: dict, post_number: int):
    """Insere o novo post no topo da seção '## Últimos posts:' do README.md."""
    readme_file = repo.get_contents(README_PATH, ref=branch)
    current = readme_file.decoded_content.decode("utf-8")

    new_entry  = f"- [{post_number:04d} - {topic['title']}](./posts/{dirname})\n"
    # Busca a seção seguida de linha em branco (padrão atual do README)
    marker     = f"{POSTS_SECTION}\n\n"

    if marker in current:
        # Insere no topo da lista, mantendo a linha em branco após o título da seção
        updated = current.replace(marker, f"{marker}{new_entry}", 1)
    else:
        # Fallback: seção não existe, cria ao final
        updated = current.rstrip() + f"\n\n{POSTS_SECTION}\n\n{new_entry}"

    repo.update_file(
        path=README_PATH,
        message=f"docs(index): add link to post {dirname}",
        content=updated,
        sha=readme_file.sha,
        branch=branch,
    )
    print(f"  📋 README.md atualizado com link para {dirname}")


# ─────────────────────────────────────────────────────────────
# 5. CRIAR BRANCH + ARQUIVOS + PULL REQUEST
# ─────────────────────────────────────────────────────────────

def create_pull_request(repo, post_number: int, topic: dict, content: str) -> str:
    dirname   = f"{post_number:04d}-{topic['slug']}"
    file_path = f"{POSTS_DIR}/{dirname}/{POST_FILENAME}"
    branch    = f"agent/post-{datetime.now().strftime('%Y%m%d')}-{topic['slug']}"
    today_br  = datetime.now().strftime("%d/%m/%Y")

    base_sha = repo.get_branch(MAIN_BRANCH).commit.sha
    repo.create_git_ref(ref=f"refs/heads/{branch}", sha=base_sha)
    print(f"  🌿 Branch criada: {branch}")

    # Commit 1: arquivo do novo post
    repo.create_file(
        path=file_path,
        message=f"feat(blog): add post {dirname}",
        content=content,
        branch=branch,
    )
    print(f"  📄 Arquivo criado: {file_path}")

    # Commit 2: atualização do índice no README da raiz
    update_readme_index(repo, branch, dirname, topic, post_number)

    pr_body = f"""## 🤖 Post gerado automaticamente pelo Blog Agent

| Campo | Valor |
|-------|-------|
| **Título** | {topic['title']} |
| **Arquivo** | `{file_path}` |
| **Tags** | {', '.join(f'`{t}`' for t in topic['tags'])} |
| **Gerado em** | {today_br} |

### 📝 Descrição
{topic['description']}

---
> ⚠️ **Revisão obrigatória antes do merge:**
> - [ ] Precisão técnica do conteúdo Rust
> - [ ] Exemplos de código compilam corretamente
> - [ ] Linguagem adequada ao público-alvo
> - [ ] Link no README.md está correto e no topo da lista
"""

    pr = repo.create_pull(
        base=MAIN_BRANCH,
        head=branch,
        title=f"[Blog Agent] {topic['title']}",
        body=pr_body,
        draft=False,
    )
    return pr.html_url


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    print("🚀 Blog Agent iniciando...\n")

    g    = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    print(f"✅ GitHub: {repo.full_name}")

    client = InferenceClient(api_key=HF_TOKEN)
    print(f"✅ HF Inference API: {MODEL_ID}\n")

    print("📚 Lendo posts existentes...")
    posts = get_existing_posts(repo)
    print(f"   {len(posts)} post(s) encontrado(s)\n")

    print("🤔 Escolhendo próximo tema...")
    topic = choose_next_topic(posts, client)
    print(f"   ✅ Tema: {topic['title']}\n")

    print("✍️  Gerando conteúdo do post...")
    content = generate_post_content(topic, posts, client)
    print(f"   ✅ {len(content)} caracteres gerados\n")

    number = get_next_number(posts)
    print(f"📬 Criando PR para o post #{number:04d}...")
    pr_url = create_pull_request(repo, number, topic, content)

    print(f"\n🎉 Concluído! PR disponível em:\n   {pr_url}")


if __name__ == "__main__":
    main()
