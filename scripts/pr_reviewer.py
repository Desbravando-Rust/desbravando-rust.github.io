#!/usr/bin/env python3
"""
PR Reviewer — Revisa automaticamente posts gerados pelo blog agent
e publica o feedback como comentário no PR.
"""

import os, re
from github import Github
from huggingface_hub import InferenceClient

GITHUB_TOKEN       = os.environ.get("GH_PAT") or os.environ["GITHUB_TOKEN"]
HF_TOKEN           = os.environ["HF_TOKEN"]
REPO_NAME          = os.environ["GITHUB_REPOSITORY"]
PR_NUMBER          = int(os.environ["PR_NUMBER"])
MODEL_ID           = os.environ.get("MODEL_ID") or "deepseek-ai/DeepSeek-V3-0324"  # mesmo do agente

try:
    CONTENT_MAX_TOKENS = int(os.environ.get("CONTENT_MAX_TOKENS")) or 8192
except ValueError:
    CONTENT_MAX_TOKENS = 8192

REVIEW_PROMPT = """
Você é um revisor técnico especializado em Rust e Python.
Revise o post abaixo destinado ao blog 'Desbravando Rust', voltado para
programadores Python que estão aprendendo Rust.

## Post para revisar:
{content}

## O que avaliar e corrigir:

### ✅ Precisão Técnica
- Os exemplos de código Rust estão corretos e compilariam sem erros?
- Os conceitos de Rust estão explicados corretamente?
- As comparações com Python são precisas e justas?

### 📖 Didática e Clareza
- A progressão do conteúdo é lógica para um iniciante em Rust?
- Algum conceito foi introduzido sem explicação adequada?
- As analogias e exemplos ajudam a entender?

### 🇧🇷 Linguagem
- O PT-BR está correto e natural?
- O tom é acessível (não muito técnico, não muito básico)?

### 🔧 Sugestões de Melhoria
- Quais seções poderiam ser expandidas?
- Algum exemplo de código importante está faltando?
- Há algo que confundiria especialmente quem vem do Python?

## Formato da revisão:
Estruture sua resposta em seções com os títulos acima.
Para cada problema encontrado, cite o trecho específico e sugira a correção.
Seja objetivo e construtivo. Ao final, dê uma nota geral de 1 a 10.
"""


def get_post_content(repo, pr) -> tuple[str, str]:
    """Retorna (caminho do arquivo, conteúdo do post) a partir do PR."""
    files = pr.get_files()
    for f in files:
        if f.filename.startswith("posts/") and f.filename.endswith("README.md"):
            content_file = repo.get_contents(f.filename, ref=pr.head.sha)
            return f.filename, content_file.decoded_content.decode("utf-8")
    return "", ""


def post_review_comment(pr, filepath: str, review: str):
    """Publica o review como comentário no PR."""
    comment = f"""## 🤖 Revisão Automática do Post

**Arquivo:** `{filepath}`

---

{review}

---
*Revisão gerada automaticamente. Aceite ou ignore as sugestões conforme seu julgamento.*
"""
    pr.create_issue_comment(comment)


def main():
    print("🔍 PR Reviewer iniciando...\n")

    g    = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    pr   = repo.get_pull(PR_NUMBER)
    print(f"✅ PR #{PR_NUMBER}: {pr.title}\n")

    # 1. Ler o conteúdo do post
    print("📄 Lendo conteúdo do post...")
    filepath, content = get_post_content(repo, pr)
    if not content:
        print("⚠️  Nenhum README.md encontrado no PR. Abortando.")
        return
    print(f"   ✅ {len(content)} caracteres lidos\n")

    # 2. Enviar para o LLM revisar
    print("🤔 Enviando para revisão pelo LLM...")
    client = InferenceClient(api_key=HF_TOKEN)
    resp = client.chat.completions.create(
        model=MODEL_ID,
        messages=[{
            "role": "user",
            "content": REVIEW_PROMPT.format(content=content[:12000])
        }],
        max_tokens=8192,
        temperature=0.3,  # baixo para revisão mais objetiva
    )
    review = resp.choices[0].message.content.strip()
    print(f"   ✅ {len(review)} caracteres de revisão gerados\n")

    # 3. Publicar como comentário no PR
    print("💬 Publicando comentário no PR...")
    post_review_comment(pr, filepath, review)
    print(f"\n🎉 Revisão publicada no PR #{PR_NUMBER}!")


if __name__ == "__main__":
    main()
