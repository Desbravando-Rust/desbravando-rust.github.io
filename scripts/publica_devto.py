#!/usr/bin/env python3
"""
Publica em lote posts do blog Jekyll no dev.to, com capa redimensionada. Uso MANUAL.

IMPORTANTE (limitação do dev.to): a API aceita a capa (main_image) apenas como URL
pública, não como upload de arquivo. Por isso o script redimensiona a capa e salva
em imgs/devto-covers/<numero>.jpg dentro do repo (numero = prefixo do post, ex.:
0001.jpg), e usa a URL pública dessa imagem (no seu GitHub Pages) como cover.

Cada post é um diretório posts/NNNN-slug/ com um README.md dentro; o título vem do
primeiro "# " e a capa da primeira imagem markdown do corpo. Fluxo recomendado:

    # 1) gerar as capas redimensionadas (sem publicar):
    python publica_devto.py --posts 1-15 --somente-imagens

    # 2) subir as capas para o site ficarem públicas:
    git add imgs/devto-covers && git commit -m "capas devto" && git push

    # 3) publicar (as capas já estão no ar; dev.to consegue buscá-las):
    python publica_devto.py --posts 1-15              # cria rascunhos
    python publica_devto.py --posts 1-15 --publicar   # publica direto

CHAVE DA API: crie um arquivo .env na raiz do projeto com:
    DEVTO_API_KEY=sua_chave_aqui
O script lê o .env automaticamente. Uma variável já exportada no shell tem
prioridade sobre o .env. NÃO versione o .env (adicione ao .gitignore).

Outros parâmetros:
    --posts 1-15   intervalo pelo prefixo numérico do arquivo (0001-..., 0015-...).
                   Também aceita um único número (ex.: --posts 7). Sem esse parâmetro,
                   processa TODOS os posts.
    --agendar "2026-07-15 09:00"   agenda a partir dessa data. Post único cai nela.
    --intervalo-dias 7   em lote, espaça N dias entre posts (post 1 na data, 2 em +N,
                         3 em +2N...). Padrão: 7.
    --tema performance   fallback da 4ª tag p/ posts SEM entrada no _data/devto_temas.yml.
                         O tema por post vem desse yml (indexado pelo número); as 3 base
                         (braziliandevs+python+rust) são sempre fixas.
    --dir posts    pasta dos posts (padrão: posts).

Requisitos (uma vez): pip install requests python-frontmatter pillow
    (opcional, para .env mais robusto: pip install python-dotenv)
Chave da API: dev.to -> Settings -> Extensions -> "DEV Community API Keys".
"""

import os
import re
import sys
import io
from datetime import datetime, timedelta

import requests
import frontmatter
from PIL import Image


def carrega_dotenv(caminho=".env"):
    """
    Carrega variáveis de um arquivo .env para o ambiente.
    Prioridade: variáveis JÁ exportadas no shell não são sobrescritas.
    Usa python-dotenv se disponível; senão, faz um parser mínimo próprio.
    """
    if not os.path.isfile(caminho):
        return
    try:
        from dotenv import load_dotenv  # opcional
        load_dotenv(caminho, override=False)
        return
    except ImportError:
        pass
    # Fallback sem dependência: parser simples de KEY=VALOR
    with open(caminho, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            if linha.lower().startswith("export "):
                linha = linha[len("export "):]
            chave, _, valor = linha.partition("=")
            chave = chave.strip()
            valor = valor.strip().strip('"').strip("'")
            if chave and chave not in os.environ:  # não sobrescreve o que já existe
                os.environ[chave] = valor


carrega_dotenv()  # lê o .env do diretório atual, se existir

SITE_BASE = "https://desbravandorust.com.br"
POSTS_DIR = "../posts"
TEMAS_FILE = "../_data/devto_temas.yml"          # tema (4ª tag) por número de post
COVERS_DIR = "../imgs/devto-covers"              # caminho no disco (script roda de scripts/)
COVERS_URL = SITE_BASE + "/imgs/devto-covers"    # URL pública (sem o ../ do path local)
OFFSET_BRASILIA = "-03:00"

# Tags (req 5): comunidade + python + rust + tema do artigo.
TAG_COMUNIDADE = "braziliandevs"
TAGS_BASE = [TAG_COMUNIDADE, "python", "rust"]
COVER_W, COVER_H = 1000, 400


# ----------------------------- posts / seleção ------------------------------

def prefixo_num(nome: str):
    m = re.match(r"^(\d+)-", os.path.basename(nome))
    return int(m.group(1)) if m else None


def slug_do_arquivo(caminho: str) -> str:
    nome = re.sub(r"\.md$", "", os.path.basename(caminho))
    return re.sub(r"^\d+-", "", nome)


def readme_de(post_dir: str) -> str:
    return os.path.join(post_dir, "README.md")


def numero_prefixo(post_dir: str) -> str:
    """Prefixo numérico com zeros à esquerda do post (ex.: '0001'). Nome da capa."""
    m = re.match(r"^(\d+)-", os.path.basename(post_dir))
    return m.group(1) if m else slug_do_arquivo(post_dir)


def extrair_titulo(texto: str) -> str:
    for linha in texto.splitlines():
        m = re.match(r"^#\s+(.*\S)\s*$", linha)
        if m:
            return m.group(1).strip()
    return "Sem título"


def listar_posts(pasta: str):
    """Cada post é um diretório posts/NNNN-slug/ com um README.md dentro."""
    dirs = [
        os.path.join(pasta, d)
        for d in os.listdir(pasta)
        if os.path.isdir(os.path.join(pasta, d))
        and os.path.isfile(os.path.join(pasta, d, "README.md"))
    ]
    dirs.sort(key=lambda p: (prefixo_num(p) is None, prefixo_num(p) or 0, p))
    return dirs


def parse_intervalo(valor: str):
    valor = valor.strip().lower()
    if valor in ("", "all", "todos"):
        return None
    if "-" in valor:
        a, b = valor.split("-", 1)
        return (int(a), int(b))
    n = int(valor)
    return (n, n)


def filtrar(posts, intervalo):
    if intervalo is None:
        return posts
    lo, hi = intervalo
    sel = []
    for p in posts:
        n = prefixo_num(p)
        if n is not None and lo <= n <= hi:
            sel.append(p)
    return sel


# --------------------------------- tags -------------------------------------

def normaliza_tag(t: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(t).lower())


def carrega_temas(repo_root: str) -> dict:
    """Lê _data/devto_temas.yml -> {'0001': 'performance', ...}. yaml vem junto do
    python-frontmatter, sem dep nova. Arquivo ausente = dict vazio (sai só as 3 base)."""
    caminho = os.path.join(repo_root, TEMAS_FILE)
    if not os.path.isfile(caminho):
        return {}
    import yaml
    with open(caminho, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return {str(k): v for k, v in data.items()}


def montar_tags(post, tema_cli=None) -> list:
    """comunidade + python + rust + 1 tema.
    Tema vem do front matter `tags:` (se houver) ou do flag --tema. Sem isso,
    saem só as 3 base — os posts do repo não têm front matter, então na prática
    o tema vem do --tema."""
    brutas = post.get("tags")
    if isinstance(brutas, str):
        brutas = [t.strip() for t in brutas.split(",")]
    elif brutas is None:
        brutas = []
    excluir = {"braziliandevs", "python", "rust", "ptbr"}
    tema = None
    for t in brutas:
        nt = normaliza_tag(t)
        if nt and nt not in excluir:
            tema = nt
            break
    if not tema and tema_cli:
        tema = normaliza_tag(tema_cli)
    tags = list(TAGS_BASE)
    if tema:
        tags.append(tema)
    return tags[:4]


# --------------------------------- imagem -----------------------------------

def carregar_imagem(cover_valor: str, repo_root: str) -> bytes:
    """Lê os bytes da imagem de origem: URL (baixa) ou caminho no repo (lê do disco)."""
    v = str(cover_valor).strip()
    if v.startswith("http://") or v.startswith("https://"):
        r = requests.get(v, timeout=30)
        r.raise_for_status()
        return r.content
    caminho = os.path.join(repo_root, v.lstrip("/"))
    with open(caminho, "rb") as f:
        return f.read()


def redimensiona_cover(img_bytes: bytes) -> bytes:
    """
    Redimensiona para 1000x400: resize pela LARGURA (para 1000), depois corta a
    ALTURA para 400 alinhado ao topo (descarta a parte de baixo).
    Ex.: 2000x1000 -> 1000x500 -> corta topo -> 1000x400.
    Fallback: se, após ajustar a largura, a altura ficar < 400 (imagem muito baixa),
    ajusta pela altura e corta a largura no centro, garantindo 1000x400.
    """
    im = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    w, h = im.size

    novo_h = max(1, round(h * COVER_W / w))
    im = im.resize((COVER_W, novo_h), Image.LANCZOS)

    if novo_h >= COVER_H:
        im = im.crop((0, 0, COVER_W, COVER_H))          # alinhado ao topo
    else:
        # imagem larga e baixa: ajusta pela altura e corta largura no centro
        im = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        novo_w = max(COVER_W, round(w * COVER_H / h))
        im = im.resize((novo_w, COVER_H), Image.LANCZOS)
        esq = (novo_w - COVER_W) // 2
        im = im.crop((esq, 0, esq + COVER_W, COVER_H))

    out = io.BytesIO()
    im.save(out, format="JPEG", quality=88, optimize=True)
    return out.getvalue()


def remove_liquid_raw(corpo: str) -> str:
    """Tira os guardas {% raw %}/{% endraw %} — são um workaround do Jekyll pra
    proteger {{ }} em código. No dev.to (Forem) o código cercado já é literal, e
    esses tags fora do bloco viram Liquid e quebram ('Unknown tag endraw')."""
    return re.sub(r"\{%-?\s*(?:end)?raw\s*-?%\}[ \t]*\n?", "", corpo)


def remove_titulo_e_capa(corpo: str, remover_capa: bool) -> str:
    """Tira do corpo o 1º H1 (título) e a 1ª imagem (capa). O dev.to já renderiza
    title e cover_image por conta própria; sem isso ambos aparecem duplicados no
    topo do artigo. ponytail: assume capa = 1ª imagem do corpo (verdade quando não
    há cover no front matter, que é o caso de todos os posts do repo)."""
    titulo_feito = False
    capa_feita = not remover_capa
    out = []
    for ln in corpo.splitlines():
        if not titulo_feito and re.match(r"^#\s+\S", ln):
            titulo_feito = True
            continue
        if not capa_feita and re.match(r"^\s*!\[[^\]]*\]\(", ln):
            capa_feita = True
            continue
        out.append(ln)
    return "\n".join(out)


def absolutiza_imagens(corpo: str, post_base: str) -> str:
    """Converte caminhos de imagem relativos do corpo em URLs absolutas do site.
    dev.to NÃO reescreve caminhos relativos; sem isso o proxy de imagem busca
    'imgs/x.png' relativo a nada e a imagem quebra. Só reescreve o token da URL,
    preservando alt e um eventual título. ponytail: cobre markdown ![](); <img>
    HTML no corpo ficaria de fora, mas os posts usam só a forma markdown."""
    def sub(m):
        pre, url = m.group(1), m.group(2)
        if url.startswith(("http://", "https://", "data:", "#")):
            return m.group(0)
        novo = SITE_BASE + url if url.startswith("/") else post_base + url
        return pre + novo
    return re.sub(r"(!\[[^\]]*\]\(\s*)([^)\s]+)", sub, corpo)


def extrair_cover(post, post_dir: str, repo_root: str):
    """Descobre a capa: campo cover:/image: do front matter (se houver), ou a
    primeira imagem markdown do corpo. Devolve uma URL http(s) ou um caminho
    relativo à raiz do repo (ambos aceitos por carregar_imagem)."""
    v = post.get("cover") or post.get("image")
    if not v:
        m = re.search(r"!\[[^\]]*\]\(\s*([^)\s]+)", post.content)
        if not m:
            return None
        v = m.group(1)
    v = str(v).strip()
    if v.startswith("http://") or v.startswith("https://"):
        return v
    if v.startswith("/"):
        return v.lstrip("/")                          # já relativo à raiz do repo
    caminho_abs = os.path.normpath(os.path.join(post_dir, v))  # relativo ao post
    return os.path.relpath(caminho_abs, repo_root)


def gera_cover(post, post_dir: str, repo_root: str):
    """Gera a capa redimensionada no repo e devolve (url_publica, caminho_local).
    O arquivo é nomeado pelo número do post (ex.: 0001.jpg)."""
    cover_valor = extrair_cover(post, post_dir, repo_root)
    if not cover_valor:
        return None, None
    origem = carregar_imagem(cover_valor, repo_root)
    redimensionada = redimensiona_cover(origem)

    destino_dir = os.path.join(repo_root, COVERS_DIR)
    os.makedirs(destino_dir, exist_ok=True)
    nome = numero_prefixo(post_dir) + ".jpg"
    caminho_local = os.path.join(destino_dir, nome)
    with open(caminho_local, "wb") as f:
        f.write(redimensionada)

    url = COVERS_URL + "/" + nome
    return url, caminho_local


# --------------------------------- publicação -------------------------------

def parse_agendamento(valor: str) -> datetime:
    try:
        dt = datetime.strptime(valor, "%Y-%m-%d %H:%M")
    except ValueError:
        print('ERRO: use --agendar "YYYY-MM-DD HH:MM" (ex.: 2026-07-15 09:00)')
        sys.exit(1)
    if dt <= datetime.now():
        print("ERRO: a data de agendamento precisa estar no futuro.")
        sys.exit(1)
    return dt


def iso_brasilia(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:00") + OFFSET_BRASILIA


def monta_front_matter(titulo, tags, canonical, cover_url, published_at_iso):
    titulo_seguro = str(titulo).replace('"', "'")
    linhas = ["---", 'title: "' + titulo_seguro + '"', "published: true"]
    # aspas: sem elas o YAML do Forem lê como objeto Time e rejeita
    # ("Tried to load unspecified class: Time"), zerando o front matter.
    linhas.append('published_at: "' + published_at_iso + '"')
    linhas.append("tags: " + ", ".join(tags))
    linhas.append("canonical_url: " + canonical)
    if cover_url:
        linhas.append("cover_image: " + cover_url)
    linhas.append("---")
    return "\n".join(linhas)


def publica_um(post_dir, api_key, repo_root, publicar, agendar_dt, temas=None, tema_cli=None):
    post = frontmatter.load(readme_de(post_dir))
    titulo = post.get("title") or extrair_titulo(post.content)
    # tema por post: front matter (dentro de montar_tags) > devto_temas.yml > --tema
    tema = (temas or {}).get(numero_prefixo(post_dir)) or tema_cli
    tags = montar_tags(post, tema)
    # O site serve o post na pasta COM o prefixo numérico (/posts/0001-slug/),
    # não no slug sem número — usar o basename do diretório. Vale p/ canonical e imagens.
    canonical = SITE_BASE + "/posts/" + os.path.basename(post_dir)

    cover_url, _ = gera_cover(post, post_dir, repo_root)

    corpo = remove_titulo_e_capa(post.content, bool(cover_url))
    corpo = absolutiza_imagens(remove_liquid_raw(corpo), canonical + "/")

    headers = {
        "api-key": api_key,
        "Accept": "application/vnd.forem.api-v1+json",
        "Content-Type": "application/json",
        "User-Agent": "desbravando-rust-publisher/1.0",
    }

    if agendar_dt is not None:
        fm = monta_front_matter(titulo, tags, canonical, cover_url, iso_brasilia(agendar_dt))
        payload = {"article": {"body_markdown": fm + "\n\n" + corpo}}
    else:
        art = {
            "title": titulo,
            "body_markdown": corpo,
            "published": publicar,
            "canonical_url": canonical,
            "tags": tags,
        }
        if cover_url:
            art["main_image"] = cover_url
        payload = {"article": art}

    resp = requests.post("https://dev.to/api/articles", json=payload, headers=headers, timeout=30)
    if resp.status_code in (200, 201):
        dados = resp.json()
        if agendar_dt is not None:
            estado = "AGENDADO " + iso_brasilia(agendar_dt)
        else:
            estado = "PUBLICADO" if publicar else "RASCUNHO"
        print("  OK [%s] %s | tags: %s" % (estado, titulo, ", ".join(tags)))
        print("     cover: %s" % (cover_url or "(sem capa)"))
        print("     url:   %s" % dados.get("url"))
        return True
    else:
        print("  ERRO %s em %s: %s" % (resp.status_code, post_dir, resp.text[:200]))
        return False


# ----------------------------------- main -----------------------------------

def get_flag_valor(flag):
    if flag in sys.argv:
        i = sys.argv.index(flag)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return None


def main():
    repo_root = os.getcwd()
    pasta = get_flag_valor("--dir") or POSTS_DIR
    pasta_abs = os.path.join(repo_root, pasta)
    if not os.path.isdir(pasta_abs):
        print("ERRO: pasta de posts não encontrada: " + pasta_abs)
        sys.exit(1)

    intervalo = None
    if get_flag_valor("--posts"):
        intervalo = parse_intervalo(get_flag_valor("--posts"))

    somente_imagens = "--somente-imagens" in sys.argv
    publicar = "--publicar" in sys.argv
    tema = get_flag_valor("--tema")   # fallback p/ posts sem entrada no devto_temas.yml
    temas = carrega_temas(repo_root)  # tema por post (4ª tag)
    agendar_base = None
    if get_flag_valor("--agendar"):
        agendar_base = parse_agendamento(get_flag_valor("--agendar"))
    intervalo_dias = int(get_flag_valor("--intervalo-dias") or 7)

    posts = filtrar(listar_posts(pasta_abs), intervalo)
    if not posts:
        print("Nenhum post encontrado para o filtro informado.")
        sys.exit(0)

    print("Posts selecionados (%d):" % len(posts))
    for p in posts:
        print("  - " + os.path.basename(p))
    print()

    # Modo 1: só gerar as capas (sem API)
    if somente_imagens:
        print("Gerando capas redimensionadas (1000x400)...")
        for p in posts:
            post = frontmatter.load(readme_de(p))
            _, local = gera_cover(post, p, repo_root)
            if local:
                print("  OK %s -> %s" % (os.path.basename(p), os.path.relpath(local, repo_root)))
            else:
                print("  (sem capa) %s" % os.path.basename(p))
        print("\nAgora faça: git add %s && git commit && git push" % COVERS_DIR)
        print("Depois rode de novo sem --somente-imagens para publicar.")
        return

    # Modo 2: publicar (precisa da chave)
    api_key = os.environ.get("DEVTO_API_KEY")
    if not api_key:
        print("ERRO: defina DEVTO_API_KEY (ou use --somente-imagens para só gerar as capas).")
        sys.exit(1)

    ok = 0
    for idx, p in enumerate(posts):
        dt = None
        if agendar_base is not None:
            dt = agendar_base + timedelta(days=intervalo_dias * idx)
        print("[%d/%d] %s" % (idx + 1, len(posts), os.path.basename(p)))
        if publica_um(p, api_key, repo_root, publicar, dt, temas, tema):
            ok += 1
    print("\nConcluído: %d de %d." % (ok, len(posts)))
    if agendar_base is not None:
        print("Confira os agendados em https://dev.to/dashboard (status 'Scheduled').")


if __name__ == "__main__":
    main()