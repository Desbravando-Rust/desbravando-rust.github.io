# Prompts para geração de covers dos posts — Desbravando Rust

Arquivo de entrada para o **D6** do plano de OG images.
Cada entrada abaixo corresponde a um post **sem `imgs/cover.png`** e traz um prompt
assertivo, pronto para ser enviado a um modelo de geração de imagem.

**Como usar (Claude Code):**
1. Para cada post, prepende o bloco **STYLE BASE** ao prompt específico.
2. Gere a imagem em **1200×630 px** (1.91:1), exporte como PNG otimizado (< 300 KB).
3. Salve em `posts/<slug>/imgs/cover.png`.
4. Não deixe o modelo "escrever" o título na arte — o título é sobreposto
   programaticamente no D3 (o prompt já reserva o terço esquerdo como área limpa).

Posts **fora** desta lista: `0011` (tem `cover11.png`, apenas renomear no D6),
`0016` e `0017` (já possuem `imgs/cover.png`).

---

## STYLE BASE (prepend em TODOS os prompts)

```
Wide 1200x630 landscape digital illustration, strict 1.91:1 aspect ratio.
Modern editorial tech-illustration style: flat shapes with subtle depth, soft
gradients, gentle film grain, soft rim light. Dark slate/charcoal background
(#1B1F24 to #2B2F36). Primary accent: Rust orange (#CE422B and #DEA584).
Secondary accent used sparingly: Python blue and yellow (#3776AB / #FFD343) to
signal a Python-to-Rust bridge. Clean geometric composition weighted to the
right; keep the LEFT THIRD calm and mostly empty as negative space for a title
overlay added later. High contrast, crisp, poster-quality, cohesive brand look
across the whole series.
Negative prompt: text, words, letters, captions, numbers, logos, brand marks,
watermark, signature, UI chrome, borders, low-res, blurry, cluttered left third.
```

---

## 0001 — Performance na prática: Axum supera o FastAPI

**Prompt:**
```
Concept: raw backend speed and lower latency. Two abstract server monoliths
racing along parallel tracks; the Rust-orange server streaks ahead leaving bright
light trails while a blue server trails behind. Include a subtle descending
latency curve and a fast-forward/throughput motif. Convey a benchmark victory:
speed, requests per second, low tail latency. Right-weighted composition.
```

## 0002 — Pandas vs Polars: benchmark com 3 milhões de registros

**Prompt:**
```
Concept: crunching a massive dataset at high speed. A towering grid of glowing
data cells representing millions of rows, fed through a sleek orange processing
pipeline that visibly outruns a slower parallel blue pipeline. Emphasize scale
and velocity — enormous volume processed effortlessly. Abstract data shapes, no
animal mascots. Right-weighted composition.
```

## 0003 — Cargo contra rapa (Cargo vs. fadiga de configuração)

**Prompt:**
```
Concept: Rust's tooling bringing order to dependency chaos. Left side, calmer: a
tangled knot of cables and scattered config files dissolving away. Right side:
neat orange shipping-cargo crates stacked and aligned on a smooth conveyor, one
tidy glowing manifest crate front and center. Theme: order emerging from chaos,
tooling that just works out of the box. Right-weighted composition.
```

## 0004 — De Django ORM para SQLx

**Prompt:**
```
Concept: leaving 'magic' abstraction behind for explicit control. On the left, a
soft purple magic orb / ORM cloud dissolving; it transforms toward the right into
precise interlocking orange gears and a clean, explicit query pipeline. Theme:
from hidden magic to honest, explicit SQL and predictable control.
Right-weighted composition.
```

## 0005 — Entendendo Ownership em Rust

**Prompt:**
```
Concept: ownership and borrowing of a value. A single glowing orange key/token is
held by one abstract hand and lent to another, with a clear return arrow forming a
loop. Nearby, memory blocks show exactly one exclusive owner highlighted while
others are dimmed. Theme: exclusivity, move semantics, borrowing and returning.
Right-weighted composition.
```

## 0006 — Gerenciamento de Memória: Rust vs Python

**Prompt:**
```
Concept: memory as a well-planned city. An isometric miniature city built from
memory blocks: the Rust side is precisely zoned and deterministically allocated in
orange; the contrasting blue side is tidied automatically by a small crane
(garbage collector). Theme: deterministic manual allocation versus automatic
cleanup. Right-weighted composition.
```

## 0007 — Dominando Enums em Rust

**Prompt:**
```
Concept: enums as labeled variant compartments (sum types). A sleek orange
selector dial locks into exactly one of several distinct glowing compartments,
each a different geometric shape; only one variant is active at a time while the
rest wait, clearly separated. Theme: exhaustive, mutually exclusive variants.
Right-weighted composition.
```

## 0008 — Tratamento de Erros: Result e Option

**Prompt:**
```
Concept: safe, explicit error handling. A value travels a path that forks into two
clearly separated channels: a bright 'success' lane and a contained 'error' lane
held safely inside a glowing orange box, with a subtle safety net beneath the
whole scene. Theme: errors wrapped in a safe container (Result/Option) instead of
uncaught exceptions flying loose. Right-weighted composition.
```

## 0009 — Desmistificando Traits em Rust

**Prompt:**
```
Concept: composable capabilities snapping onto a type. A central neutral object
gains glowing orange modular facets/badges (traits) that plug in from the sides;
in the background a rigid inheritance tree fades out in blue. Theme: flexible
composition over rigid inheritance. Right-weighted composition.
```

## 0010 — Concorrência e Paralelismo: Threads e Async/Await

**Prompt:**
```
Concept: many tasks running safely in parallel. Multiple glowing orange lanes
(threads) weave forward in parallel without ever colliding; a few loop back on
themselves as async/await cycles; a subtle conductor figure keeps them
synchronized. Theme: fearless concurrency, threads plus async. Right-weighted
composition.
```

## 0012 — Lifetimes em Rust

**Prompt:**
```
Concept: how long a reference is allowed to live. Overlapping translucent
time-bars / hourglasses connected by orange tethers to memory blocks, visually
showing that a reference's span must fit entirely inside its owner's span. Theme:
scopes, spans and borrow durations. Right-weighted composition.
```

## 0013 — Smart Pointers em Rust

**Prompt:**
```
Concept: values held in smart containers with reference counting. Glowing orange
boxes floating on a heap plane, connected by counted arrows; one shared box is
pointed to by several pointers and carries a small counter badge. Theme: ownership
containers (Box/Rc/RefCell) and reference counts. Right-weighted composition.
```

## 0014 — Macros em Rust

**Prompt:**
```
Concept: code that writes code. An orange forge/machine takes a small compact
glyph-seed and, through a chain of gears, emits a much larger expanded lattice of
generated structure. Theme: metaprogramming and code expansion, automation beyond
what Python's decorators allow. Right-weighted composition.
```

## 0015 — Pattern Matching em Rust

**Prompt:**
```
Concept: matching shapes into exactly the right slot. Differently-shaped glowing
tokens are routed through an orange 'match' junction that sorts each token into its
exact corresponding branch/arm; nothing falls through, every case is covered.
Theme: exhaustive destructuring and branching. Right-weighted composition.
```

---

### Resumo da varredura

| Post | Status | Ação |
|------|--------|------|
| 0001–0010 | sem `imgs/cover.png` | **gerar** (prompts acima) |
| 0011 | tem `cover11.png` (nome/local errado) | **renomear** → `imgs/cover.png` (D6, sem gerar) |
| 0012–0015 | sem `imgs/cover.png` | **gerar** (prompts acima) |
| 0016–0017 | já têm `imgs/cover.png` | nenhuma |

**Total a gerar: 14 imagens.**
