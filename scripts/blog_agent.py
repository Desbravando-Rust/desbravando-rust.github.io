#!/usr/bin/env python3
"""
Blog Agent - Gerador automático de posts para o blog Desbravando Rust
"""

import os, re, sys, json, yaml
from datetime import datetime
from github import Github, GithubException
from huggingface_hub import InferenceClient

# ─────────────────────────────────────────────────────────────
# CONFIGURAÇÕES — ajuste conforme seu repositório
# ─────────────────────────────────────────────────────────────
GITHUB_TOKEN  = os.environ["GITHUB_TOKEN"]
HF_TOKEN      = os.environ["HF_TOKEN"]
REPO_NAME     = os.environ["GITHUB_REPOSITORY"]  # ex: "jose/jose.github.io"
POSTS_DIR     = "posts"
MAIN_BRANCH   = "main"   # ou "master" se for o caso
# MODEL_ID      = "meta-llama/Meta-Llama-3.1-8B-Instruct"
MODEL_ID      = "mistralai/Mistral-7B-Instruct-v0.3"
POST_FILENAME = "README.md"   # padrão do repositório

BLOG_CONTEXT = """
Você é um escritor técnico especializado em Rust e Python.
O blog 'Desbravando Rust' é voltado para programadores brasileiros,
especialmente aqueles com background em Python que querem aprender Rust.
O blog serve como material de apoio para o livro 'Desbravando Rust'.
Escreva SEMPRE em PT-BR, com linguagem acessível e didática.
"""

# ─────────────────────────────────────────────────────────────
# 1. ABSORVER CONTEXTO EXISTENTE
# ─────────────────────────────────────────────────────────────

def parse_frontmatter(content: str) -> dict:
    """Extrai o frontmatter YAML do arquivo markdown."""
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}


def get_existing_posts(repo) -> list:
    """Lê todos os posts existentes e retorna lista de metadados."""
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
            fm = parse_frontmatter(f.decoded_content.decode("utf-8"))
            posts.append({
                "dirname":     item.name,
                "title":       fm.get("title", item.name),
                "tags":        fm.get("tags", []),
                "categories":  fm.get("categories", []),
                "description": fm.get("description", ""),
            })
        except GithubException:
            pass  # ignora diretórios sem index.md

    return posts


def get_next_number(posts: list) -> int:
    """Determina o número sequencial do próximo post."""
    numbers = []
    for p in posts:
        m = re.match(r"^(\d+)", p["dirname"])
        if m:
            numbers.append(int(m.group(1)))
    return max(numbers, default=0) + 1


# ─────────────────────────────────────────────────────────────
# 2. DECIDIR O PRÓXIMO TEMA
# ─────────────────────────────────────────────────────────────

def choose_next_topic(posts: list, client: InferenceClient) -> dict:
    """Usa o LLM para sugerir o próximo tema ainda não publicado."""
    topics_list = "\n".join(
        f"- [{p['dirname']}] {p['title']}  | tags: {', '.join(p['tags'])}"
        for p in posts
    ) or "Nenhum post publicado ainda."

    prompt = f"""
{BLOG_CONTEXT}

## Posts já publicados:
{topics_list}

## Sua tarefa:
Sugira o PRÓXIMO post. O tema deve:
- NÃO repetir nenhum dos temas acima
- Ter progressão lógica de aprendizado de Rust para quem vem do Python
- Ser específico o suficiente para um post focado

Responda SOMENTE com JSON válido, sem blocos de código markdown:
{{
  "title": "Título do post em PT-BR",
  "slug": "slug-curto-kebab-case",
  "description": "Uma frase descrevendo o post",
  "tags": ["tag1", "tag2", "tag3"],
  "categories": ["rust"],
  "outline": [
    "Introdução: ...",
    "Seção 1: ...",
    "Seção 2: ...",
    "Comparação com Python: ...",
    "Conclusão: ..."
  ]
}}
"""
    resp = client.chat_completion(
        model=MODEL_ID,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600,
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
    """Gera o arquivo .md completo com frontmatter."""
    today = datetime.now().strftime("%Y-%m-%d")
    recent_titles = "\n".join(f"- {p['title']}" for p in posts[-5:])
    outline = "\n".join(f"  - {s}" for s in topic.get("outline", []))

    prompt = f"""
{BLOG_CONTEXT}

## Contexto (últimos posts publicados):
{recent_titles or "Nenhum ainda."}

## Post a ser escrito:
Título: {topic['title']}
Slug: {topic['slug']}
Descrição: {topic['description']}
Tags: {', '.join(topic['tags'])}

Outline sugerido:
{outline}

## Regras de escrita:
1. Linguagem acessível para quem tem pouco contexto em Rust
2. Inclua blocos ```rust com comentários em PT-BR explicando cada parte
3. Compare com Python (```python) sempre que facilitar o entendimento
4. Use subtítulos (##, ###) para organizar o post
5. Inclua uma introdução cativante e uma conclusão com resumo dos aprendizados
6. Use emojis com moderação para deixar mais amigável
7. O post deve ter profundidade suficiente para ser útil, sem ser excessivamente longo

## Formato de saída:
Gere APENAS o conteúdo markdown, começando obrigatoriamente com o frontmatter:

---
title: "{topic['title']}"
date: {today}
slug: {topic['slug']}
tags: {json.dumps(topic['tags'], ensure_ascii=False)}
categories: {json.dumps(topic.get('categories', ['rust']), ensure_ascii=False)}
description: "{topic['description']}"
draft: false
---

Escreva o post completo abaixo do frontmatter.
"""
    resp = client.chat_completion(
        model=MODEL_ID,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096,
        temperature=0.75,
    )
    return resp.choices[0].message.content.strip()


# ─────────────────────────────────────────────────────────────
# 4. CRIAR BRANCH + ARQUIVO + PULL REQUEST
# ─────────────────────────────────────────────────────────────

def create_pull_request(repo, post_number: int, topic: dict, content: str) -> str:
    """Cria branch, commita o arquivo e abre o PR. Retorna URL do PR."""
    dirname    = f"{post_number:04d}-{topic['slug']}"
    file_path  = f"{POSTS_DIR}/{dirname}/{POST_FILENAME}"
    branch     = f"agent/post-{datetime.now().strftime('%Y%m%d')}-{topic['slug']}"
    today_br   = datetime.now().strftime("%d/%m/%Y")

    # SHA do commit mais recente da branch principal
    base_sha = repo.get_branch(MAIN_BRANCH).commit.sha

    # 1. Cria a nova branch
    repo.create_git_ref(ref=f"refs/heads/{branch}", sha=base_sha)
    print(f"  🌿 Branch criada: {branch}")

    # 2. Cria o arquivo index.md na nova branch
    repo.create_file(
        path=file_path,
        message=f"feat(blog): add post {dirname}",
        content=content,
        branch=branch,
    )
    print(f"  📄 Arquivo criado: {file_path}")

    # 3. Abre o Pull Request
    pr_body = f"""
## 🤖 Post gerado automaticamente pelo Blog Agent

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
> - [ ] Frontmatter correto (tags, slug, data)
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

    client = InferenceClient(
        provider="hf-inference",
        api_key=HF_TOKEN,
    )
    print(f"✅ HF Inference API: {MODEL_ID}\n")

    # Passo 1: Absorver contexto
    print("📚 Lendo posts existentes...")
    posts = get_existing_posts(repo)
    print(f"   {len(posts)} post(s) encontrado(s)\n")

    # Passo 2: Decidir tema
    print("🤔 Escolhendo próximo tema...")
    topic = choose_next_topic(posts, client)
    print(f"   ✅ Tema: {topic['title']}\n")

    # Passo 3: Gerar conteúdo
    print("✍️  Gerando conteúdo do post...")
    content = generate_post_content(topic, posts, client)
    print(f"   ✅ {len(content)} caracteres gerados\n")

    # Passo 4: Criar PR
    number = get_next_number(posts)
    print(f"📬 Criando PR para o post #{number:04d}...")
    pr_url = create_pull_request(repo, number, topic, content)

    print(f"\n🎉 Concluído! PR disponível em:\n   {pr_url}")


if __name__ == "__main__":
    main()
