# Roadmap — iniciativas para enriquecer o site e potencializar vendas

Backlog priorizado (ordenado por alavancagem sobre vendas) de coisas **ainda não
feitas** no site. Cada item traz o *porquê vende* e um *ponto de partida no
projeto*, pra servir de prompt de implementação no futuro.

> Contexto: já existem hero + CTA (Kiwify), seção "Veja por dentro" com lightbox,
> blog (17 posts) com cross-post no dev.to, feed RSS/Atom (`/feed.xml`), JSON-LD
> `Book`/`Offer`/`FAQPage` na home e captura de e-mail via Google Form.
> Depoimentos ficam de fora (aguardando retorno).

---

## 1. Automação de newsletter (RSS → e-mail)
**Por que vende:** transforma o tráfego do blog em audiência própria (lista de
e-mail), o ativo que mais converte num funil de livro. O feed que já existe é a
metade do caminho.
**Ponto de partida:** ligar `/feed.xml` a um serviço RSS-to-email
(Buttondown/Mailchimp/Beehiiv) que dispara um e-mail a cada post novo. Zero
manutenção recorrente depois de configurado.

## 2. Entrega automática do capítulo grátis + sequência de nutrição
**Por que vende:** hoje o "Receba um capítulo grátis" (`_includes/lead-capture.html`)
aponta pra um Google Form cru — sem entrega automática nem follow-up. Um
autoresponder que entrega o capítulo na hora e emenda um drip educacional
(3–5 e-mails Python→Rust) fecha a venda com quem já demonstrou interesse.
**Ponto de partida:** trocar o `forms.gle` por um form do provedor de e-mail com
double opt-in + automação de boas-vindas; reaproveitar trechos dos posts no drip.

## 3. Ativar remarketing (Meta Pixel + LinkedIn Insight)
**Por que vende:** a maioria não compra na 1ª visita. Retargetar quem leu o blog
ou visitou a página de compra e não converteu é o anúncio de melhor ROI.
**Ponto de partida:** `meta_pixel_id` e `linkedin_partner_id` já existem em
`_config.yml` (vazios) e o `_includes/analytics.html` já injeta os scripts quando
preenchidos — basta criar as contas de ads, preencher os IDs e montar as campanhas.

## 4. Ancoragem de preço + urgência real
**Por que vende:** "de R$ X por R$ Y" e um cupom com prazo aumentam conversão por
ancoragem e escassez — sem baixar a percepção de valor.
**Ponto de partida:** `preco_antigo`, `cupom` e `cupom_texto` já estão previstos
em `_config.yml` (vazios) e renderizados no `index.html`. Definir uma janela real
(ex.: campanha de lançamento) pra a urgência ser honesta, não permanente.

## 5. Lead magnet: cheat sheet Python→Rust (PDF)
**Por que vende:** um brinde de alto valor percebido e baixo atrito ("cola" de
equivalências Python↔Rust) capta e-mail muito melhor que "assine a newsletter", e
alimenta os itens 1 e 2.
**Ponto de partida:** gerar 1 PDF a partir das tabelas comparativas já espalhadas
nos posts; oferecer como content upgrade nos posts de maior tráfego e na home.

## 6. CTA no meio do post + barra de compra fixa no blog
**Por que vende:** hoje a oferta só aparece no card final (`_layouts/post.html`).
Quem abandona no meio nunca vê o CTA. Um CTA contextual no meio do conteúdo e/ou
uma barra fixa discreta capturam a intenção no pico do interesse.
**Ponto de partida:** injetar um bloco de CTA após a primeira seção `##` no
layout de post (reaproveitando `cta_posts.yml`), e uma sticky bar responsiva.

## 7. Otimização de imagens (WebP/AVIF + `srcset`)
**Por que vende:** capas, `og-default` e os prints do "Veja por dentro" são PNG/JPG
pesados. Imagem mais leve = LCP melhor = melhor ranqueamento no Google e menos
abandono no mobile (onde vem a maior parte do tráfego social).
**Ponto de partida:** converter as imagens de `imgs/` e `posts/*/imgs/` para
WebP/AVIF com fallback e `srcset` responsivo; medir com PageSpeed/Lighthouse antes/depois.

## 8. Funil de conversão mensurável no GA4
**Por que vende:** sem medir onde o comprador desiste, otimização vira chute. Hoje
o `analytics.html` rastreia clique de compra e lead soltos, mas não há funil.
**Ponto de partida:** disparar eventos padronizados (`view_item`,
`begin_checkout`, `purchase`) e marcá-los como conversões no GA4; cruzar com o
checkout da Kiwify pra enxergar o drop-off real.

## 9. Página `/obrigado` como motor de pós-venda
**Por que vende:** o momento pós-compra é o de maior engajamento e o mais
desperdiçado. Um order-bump/upsell e um pedido de indicação ("dê de presente a um
colega pythonista") extraem receita e boca-a-boca extras de graça.
**Ponto de partida:** a pasta `obrigado/` já existe — adicionar oferta
complementar (ex.: mentoria/pacote) e um bloco de compartilhamento/indicação.

## 10. Busca + tags/categorias no blog
**Por que vende:** 17 posts sem taxonomia nem busca deixam SEO de cauda longa e
navegação na mesa. Mais tráfego qualificado no topo do funil = mais vendas embaixo.
**Ponto de partida:** derivar tags a partir dos clusters de `relacionados.yml`,
gerar páginas de tag e uma busca client-side simples (índice JSON estático, sem
dependência externa).

---

_Ordenado por alavancagem: 1–4 mexem direto na conversão/audiência com baixo
esforço; 5–7 são ganhos médios de captação e SEO; 8–10 são estruturais e de
médio prazo._
