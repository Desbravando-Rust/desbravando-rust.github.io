# Insumos de conversão (ação do autor)

Três seções da home só aparecem quando você fornece conteúdo real. Nada aqui
deve ser inventado — público dev fareja prova social falsa.

## 1. Depoimentos (`_data/depoimentos.yml`)
Como coletar 3–4 depoimentos reais:
- Peça a leitores da amostra e colegas que já leram: "Em 1–2 frases, o que o
  livro destravou pra você?"
- Peça permissão para usar nome, cargo e link do LinkedIn (aumenta a credibilidade).
- Descomente o bloco de exemplo no arquivo e preencha um item por depoimento.
A seção "Quem leu, recomenda" passa a renderizar sozinha.

## 2. Previews (`imgs/preview/`)
- Exporte 3–5 páginas reais do PDF como PNG (idealmente páginas com Python e
  Rust lado a lado). Ferramenta: exportar página do PDF ou print em alta.
- Nomeie `01.png`, `02.png`, ... e salve em `imgs/preview/`.
A seção "Veja por dentro" detecta os arquivos e renderiza automaticamente.

## 3. Oferta / urgência honesta (`_config.yml`)
Só ligue com uma oferta REAL por tempo limitado:
- `cupom: "LANCAMENTO10"` e `cupom_texto: "10% de desconto até 20/07"` → mostra a
  faixa no topo e a nota no checkout.
- `preco_antigo: "129,90"` → só se esse preço realmente existiu. Sem âncora falsa.
