# Plano de desenvolvimento — Preview de imagem nas redes sociais (Open Graph)

**Repo:** `Desbravando-Rust/desbravando-rust.github.io`
**Objetivo:** fazer com que todo link compartilhado (home e posts) exiba a imagem
correta no LinkedIn, WhatsApp/Facebook e X (Twitter).
**Entregável de apoio:** `post-cover-prompts.md` (prompts de geração das artes).

---

## Diagnóstico (causa raiz)

O `head` em `_layouts/default.html` monta as meta tags Open Graph, mas:

1. A imagem OG padrão é a capa do livro `imgs/capa.jpg` — **1631×2480 px (retrato),
   ~782 KB**. Cards `summary_large_image` esperam **paisagem ~1200×630 (1.91:1)**;
   uma imagem alta e pesada é rejeitada/cortada e o WhatsApp costuma nem buscá-la.
2. Apenas **2 de 17 posts** (0016, 0017) têm `imgs/cover.png`; os outros caem no
   fallback inadequado. O `0011` tem `cover11.png` (nome/local errados) e é ignorado.
3. Faltam `og:image:width`, `og:image:height`, `og:image:type`, `og:image:alt`,
   `og:image:secure_url` — sem dimensões declaradas, LinkedIn/WhatsApp costumam não renderizar.
4. `og:type` está fixo em `website`; posts deveriam ser `article`.
5. A imagem precisa carregar publicamente no domínio custom e o cache dos crawlers
   é agressivo — exige re-scrape após a correção.

---

## Entregáveis

### D1 — Imagem OG padrão em formato correto
- Criar `imgs/og-default.png` em **1200×630 px**, PNG otimizado **< 300 KB**
  (composição paisagem com identidade do livro; usar STYLE BASE de `post-cover-prompts.md`).
- Em `_layouts/default.html`, trocar o fallback de `/imgs/capa.jpg` para `/imgs/og-default.png`.
- **Aceite:** compartilhar qualquer página sem cover próprio exibe a imagem paisagem.

### D2 — Meta tags OG/Twitter completas + `og:type` dinâmico
- No `head`, após definir `og_image`, adicionar:
  `og:image:secure_url`, `og:image:type` (`image/png`), `og:image:width` (1200),
  `og:image:height` (630) e `og:image:alt` (usar `page.title | default: site.title`).
- Tornar `og:type` = `article` quando `page.dir contains "posts/"`, senão `website`.
- **Aceite:** o `view-source` de um post exibe todas as tags `og:image:*` e `twitter:*`;
  os validadores não acusam campos ausentes.

### D3 — Normalização de covers + overlay de título
- Padronizar todos os `imgs/cover.png` para **1200×630 px**.
- Implementar overlay programático do título do post sobre a arte base (para não
  depender do modelo de imagem escrever texto). Manter o terço esquerdo livre.
- **Aceite:** os 17 posts resolvem para um `cover.png` landscape 1200×630 com o
  título legível e consistente.

### D4 — Robustez do lookup + verificação no build (CI)
- Endurecer a lógica de cover em `default.html`: garantir barra final em `page.dir`
  e aceitar `.png`/`.jpg`.
- Adicionar passo no GitHub Actions que **falha o build** se o `og:image` de
  qualquer página apontar para arquivo inexistente.
- **Aceite:** CI acusa erro se algum post ficar sem imagem válida.

### D5 — Validação e re-scrape nas plataformas
- Documentar (em `docs/` ou README) o procedimento de validação/re-scrape:
  LinkedIn Post Inspector, Facebook Sharing Debugger (cobre WhatsApp) e X Card Validator.
- **Aceite:** cada plataforma exibe a imagem correta; procedimento documentado no repo.

### D6 — Varredura de posts sem cover e geração das artes
- Executar a varredura de posts **sem `imgs/cover.png`** (referência: tabela em
  `post-cover-prompts.md`). Resultado atual: **14 posts a gerar** (0001–0010, 0012–0015).
- Para cada post da lista, enviar `STYLE BASE + prompt específico` a um modelo de
  imagem, exportar **1200×630 / PNG < 300 KB** e salvar em `posts/<slug>/imgs/cover.png`.
- **Caso especial `0011`:** apenas **renomear/mover** `cover11.png` →
  `posts/0011-.../imgs/cover.png` (não gerar nova imagem); se não estiver em 1200×630,
  ajustar no D3.
- As artes geradas alimentam o D3 (normalização + overlay de título).
- **Aceite:** todos os 14 posts possuem `imgs/cover.png` novo; o 0011 renomeado;
  nenhum post cai mais no fallback padrão.

---

## Ordem de execução sugerida
`D1 → D2` (base de tags funciona já com o fallback) → `D6` (gerar artes) →
`D3` (normalizar + overlay) → `D4` (blindar no CI) → `D5` (validar e re-scrape).

## Arquivos afetados
- `_layouts/default.html` — D1, D2, D4
- `imgs/og-default.png` — D1 (novo)
- `posts/*/imgs/cover.png` — D3, D6
- `posts/0011-iteradores-closures-rust-pythonistas/` — D6 (rename)
- `.github/workflows/*` — D4
- `scripts/` — D3 (overlay), D4 (checagem), D6 (batch de geração)
- `docs/` ou `README.md` — D5
- `post-cover-prompts.md` — entrada do D6
