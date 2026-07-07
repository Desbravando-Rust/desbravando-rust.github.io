# Playbook de distribuição — Desbravando Rust

O SEO amadurece em semanas/meses; o LinkedIn traz tráfego hoje. Este playbook é
o combustível recorrente. Meta: sustentável, não heroico.

## Cadência (2 posts/semana no LinkedIn)
- **Terça — Repurpose:** transforma 1 post do blog em post de LinkedIn (use
  `scripts/social_snippet.py` para o rascunho).
- **Quinta — Bastidor:** 1 aprendizado curto ("hoje o compilador me ensinou X"),
  sempre puxando pro tema do livro sem vender direto.

## Regra de ouro do canal
- Entregue o valor NO corpo do post (código, benchmark, insight). O LinkedIn
  penaliza post que manda embora.
- Link do blog vai no **1º comentário**, não no corpo.
- CTA do livro é sutil e ocasional (1 a cada ~4 posts), nunca em todo post.

## Moldes de repurpose (por tipo de post)

### Benchmark / performance (ex.: Axum × FastAPI, Polars)
```
[GANCHO] Reescrevi <coisa> em Rust e o p99 caiu de X para Y.

[CONTEXTO] 2 linhas: o que era antes, o problema.

[MINI-CÓDIGO/NÚMERO] o trecho ou a tabela que prova.

[APRENDIZADO] a lição que serve pra quem vem do Python.

Escrevi o passo a passo completo (link no comentário). 🦀
```

### Conceito (ex.: ownership, lifetimes, traits)
```
[GANCHO] "Ownership" assustou você em Rust? Veio do Python? Isto é pra você.

[PONTE] o equivalente mental em Python.

[EXPLICAÇÃO] 3–4 linhas, sem jargão.

[MINI-EXEMPLO] 5–8 linhas de código comentado.

Aprofundei com exemplos lado a lado (link no comentário).
```

### Tooling (ex.: Cargo, SQLx)
```
[GANCHO] O que o pip te deixou mal-acostumado e o Cargo resolve.

[LISTA] 3 coisas que "só funcionam".

[CONVITE] link no comentário.
```

## Calendário-semente (8 semanas)
Prioriza os posts de maior apelo primeiro (benchmarks e performance puxam mais).

| Semana | Terça (repurpose) | Quinta (bastidor) |
|--------|-------------------|-------------------|
| 1 | 0001 Axum × FastAPI | Por que comecei a estudar Rust vindo do Python |
| 2 | 0002 Pandas × Polars | O erro de compilação que virou meu melhor professor |
| 3 | 0016 Performance no mundo real | Um benchmark que me surpreendeu |
| 4 | 0005 Ownership | A analogia de Python que finalmente destravou ownership |
| 5 | 0017 Caçando o N+1 com SQLx | Debugar em Rust vs. em Python |
| 6 | 0008 Result/Option | Por que parei de sentir falta de try/except |
| 7 | 0010 Concorrência sem GIL | O dia que o GIL deixou de ser meu problema |
| 8 | 0014 Macros | Metaprogramação: decorator vs. macro |

Depois da semana 8, reciclar os posts restantes (0003, 0004, 0006, 0007, 0009,
0011, 0012, 0013, 0015) e repetir os campeões com novo ângulo.

## Loop de e-mail (1 broadcast/mês)
Para a lista capturada (planilha do Form):
- 1x/mês, envie o post mais forte do mês + um nudge do livro.
- Reuse o template visual de `scripts/autorresposta-capitulo-html.gs`.
- Assunto curto e concreto (ex.: "O benchmark que fez minha API 6x mais rápida").
