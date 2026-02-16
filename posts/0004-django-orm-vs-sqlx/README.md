# De Django ORM para SQLx: A Jornada de um backend que desaprendeu a confiar em mágica
###### Por [@zejuniortdr](https://github.com/zejuniortdr/) em Fev 16, 2026

Este artigo é para quem viveu anos no conforto do Django ORM e está cogitando encarar SQLx em Rust. Vamos falar de produtividade, dor, performance e o que você realmente ganha (e perde) ao largar a ‘mágica’.

Passei quase 20 anos confiando que o Django fazia magia com bancos de dados. Eu estava errado - não era magia, era abstração. E abstrações, descobri da pior forma, têm custo.

Durante anos, escrevi código Python elegante que se transformava em SQL sem eu nem pensar nisso. `Produto.objects.filter(preco__gt=100).select_related('categoria')` - boom, query otimizada. Migrations automáticas com `makemigrations`. Admin de graça. CRUD em minutos. Era produtividade pura.

Até o dia em que isso deixou de ser verdade. Um endpoint de relatório começou a demorar 8 segundos. O Django Debug Toolbar mostrou 247 queries. Duzentas e quarenta e sete. Eu tinha acabado de criar o N+1 query mais épico da história da empresa, e o pior: o código Python parecia perfeitamente inocente. Foi quando comecei a questionar se eu realmente entendia o que estava acontecendo embaixo do capô.

E foi assim que acabei conhecendo SQLx. Minha primeira reação? "Mano, eu tenho que escrever SQL na mão?!" Spoiler: sim. E isso mudou completamente como penso sobre bancos de dados.

## O Conforto (e o Preço) da Magia do Django ORM
Vamos ser justos: Django ORM é espetacular para o que foi projetado. Não estou aqui para fazer bashing - usei o Django por décadas e ainda uso em vários projetos. Mas preciso ser honesto sobre seus limites.

### O Que o Django ORM Faz de Genial
A produtividade é absurda. Você define seus modelos como classes Python normais e ganha de graça:

```python
# Django ORM - Elegante, Pythônico, Produtivo
from django.db import models

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

class Produto(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.IntegerField(default=0)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    criado_em = models.DateTimeField(auto_now_add=True)

# Queries elegantes e intuitivas
produtos_caros = Produto.objects.filter(
    preco__gt=100,
    estoque__gt=0
).select_related('categoria')

# Lazy evaluation - não executa até você iterar
for produto in produtos_caros:
    print(f"{produto.nome} - {produto.categoria.nome}")
```

É lindo. É Pythônico. E funciona muito bem para 80% dos casos de uso. O sistema de migrations é quase mágico - você altera o modelo, roda makemigrations, e o Django gera o SQL de migração automaticamente. O admin? Um CRUD completo e funcional sem escrever uma linha de HTML.

Para MVPs, protótipos e aplicações CRUD tradicionais, Django ORM é imbatível em produtividade.


### Onde a Magia Começa a Doer

Mas aí você começa a escalar. Suas queries ficam mais complexas. E começam os problemas:

**1. N+1 Queries Silenciosos**

```python

# Parece inocente, mas...
produtos = Produto.objects.filter(estoque__gt=0)

for produto in produtos:
    print(produto.categoria.nome)  # BOOM! Uma query POR produto
```

Você precisa lembrar de usar `select_related()` ou `prefetch_related()`. Esqueça uma vez em produção e seu banco chora.

**2. Queries Complexas Viram Hieróglifos**

```python
# Django ORM quando fica feio
from django.db.models import Count, Sum, F, Q, Prefetch

relatorio = Categoria.objects.annotate(
    total_produtos=Count('produto'),
    produtos_em_estoque=Count('produto', filter=Q(produto__estoque__gt=0)),
    valor_total_estoque=Sum(
        F('produto__preco') * F('produto__estoque')
    )
).filter(
    total_produtos__gt=5
).select_related(
    'categoria_pai'
).prefetch_related(
    Prefetch(
        'produto_set',
        queryset=Produto.objects.filter(estoque__gt=0).order_by('-preco')
    )
)
```

Olha, eu sei fazer isso. Mas na moral: você consegue ler essa query e saber exatamente qual SQL será gerado? Eu não consigo sem rodar e olhar o log.

**3. Controle Limitado**

Às vezes você sabe a query SQL perfeita. Você testou no psql, otimizou os índices, usou CTEs, tudo lindo. Mas fazer o Django gerar esse SQL específico? Boa sorte. Você acaba usando .raw() ou connection.cursor(), jogando fora todas as vantagens do ORM.

**4. Performance Imprevisível**

O ORM pode gerar SQL subótimo e você só descobre em produção, sob carga. Aquele inocente .filter().count() pode virar um SELECT COUNT(*) numa tabela de 10 milhões de linhas sem índice adequado.


## O Choque Inicial com SQLx

Quando abri meu primeiro projeto Rust com SQLx, quase desliguei o pc e voltei para o conforto do Django.


```rust
// SQLx - Primeira impressão: "Isso é TUDO isso?!"
use sqlx::{PgPool, FromRow};
use serde::Serialize;

#[derive(Debug, FromRow, Serialize)]
struct Produto {
    id: i32,
    nome: String,
    preco: rust_decimal::Decimal,
    estoque: i32,
    categoria_id: i32,
}

async fn listar_produtos_caros(pool: &PgPool) -> Result<Vec<Produto>, sqlx::Error> {
    let produtos = sqlx::query_as::<_, Produto>(
        "SELECT id, nome, preco, estoque, categoria_id
         FROM produtos
         WHERE preco > $1 AND estoque > 0
         ORDER BY preco DESC"
    )
    .bind(100.0)
    .fetch_all(pool)
    .await?;

    Ok(produtos)
}
```

Minha reação: "Pera aí... eu tenho que escrever o SQL inteiro? Listar todos os campos? Não tem .select_related() mágico? E as migrations, onde estão?!"

Era desconfortável. Parecia que eu estava regredindo 15 anos na carreira.


**Mas Aí Veio o Momento "Aha!"**
Depois de alguns dias brigando com o compilador (porque Rust não perdoa), descobri algo incrível:

```rust

// SQLx com compile-time checking
let produtos = sqlx::query!(
    r#"
    SELECT id, nome, preco, estoque, categoria_id
    FROM produtos
    WHERE preco > $1 AND estoque > 0
    "#,
    100.0
)
.fetch_all(pool)
.await?;

// O compilador VALIDA essa query contra seu banco REAL
// Se você escreveu "produtoss" (com S duplo), NÃO COMPILA
// Se você typar "categoria_idd", NÃO COMPILA
// Se a coluna não existir, NÃO COMPILA

// E o melhor: autocomplete perfeito!
let primeiro = &produtos[0];
println!("{}", primeiro.nome);  // ← IDE sabe que existe
// primeiro.campo_inexistente  // ← ERRO DE COMPILAÇÃO
```

Isso mudou tudo.

O SQLx valida suas queries em tempo de compilação contra o schema real do banco de dados. Você não descobre erro de SQL em produção, às 3h da manhã, com o CEO te ligando. Você descobre quando tenta compilar. É impossível deployar SQL quebrado.


## Comparação Técnica: Lado a Lado

| Aspecto               | Django ORM              | SQLx                     | Vencedor |
| --------------------- | ----------------------- | ------------------------ | -------- |
| Curva de Aprendizado  | ⭐⭐⭐⭐⭐ Muito fácil       | ⭐⭐ Requer SQL sólido     | Django   |
| Produtividade Inicial | ⭐⭐⭐⭐⭐ CRUD em minutos   | ⭐⭐⭐ Mais boilerplate     | Django   |
| Controle sobre SQL    | ⭐⭐ Limitado             | ⭐⭐⭐⭐⭐ Total              | SQLx     |
| Type Safety           | ⭐⭐ Runtime (mypy ajuda) | ⭐⭐⭐⭐⭐ Compile-time       | SQLx     |
| Performance           | ⭐⭐⭐ Boa com cuidado     | ⭐⭐⭐⭐⭐ Zero overhead      | SQLx     |
| Debugging             | ⭐⭐ SQL gerado obscuro   | ⭐⭐⭐⭐ Você escreveu       | SQLx     |
| Migrations            | ⭐⭐⭐⭐⭐ Automáticas       | ⭐⭐ Manuais (ferramentas) | Django   |
| Queries Complexas     | ⭐⭐ Fica feio rápido     | ⭐⭐⭐⭐ SQL puro é melhor   | SQLx     |
| Admin/CRUD Grátis     | ⭐⭐⭐⭐⭐ Sim               | ⭐ Não existe             | Django   |
| Validação de Schema   | ⭐⭐ Runtime              | ⭐⭐⭐⭐⭐ Compile-time       | SQLx     |


### Relacionamentos e JOINs

```python
# Automático mas implícito
produtos = Produto.objects.select_related('categoria', 'fornecedor')

# Você não vê qual tipo de JOIN está rolando
# É INNER? É LEFT? Django decide por você
```

```rust
// Explícito - você controla cada JOIN
let produtos = sqlx::query!(
    r#"
    SELECT
        p.id, p.nome, p.preco, p.estoque,
        c.nome as "categoria_nome!",
        f.nome as "fornecedor_nome?"
    FROM produtos p
    INNER JOIN categorias c ON p.categoria_id = c.id
    LEFT JOIN fornecedores f ON p.fornecedor_id = f.id
    WHERE p.preco > $1
    ORDER BY p.preco DESC
    "#,
    100.0
)
.fetch_all(pool)
.await?;
```

**Análise:** Django é mais rápido de escrever. Mas SQLx deixa cristalino o que está acontecendo. Você vê que categoria é INNER (obrigatório) e fornecedor é LEFT (opcional). O ! e ? na query do SQLx indicam tipos não-nuláveis e nuláveis, respectivamente.

### Agregações e Subqueries

**Django:**
```python
# Fica confuso rápido
from django.db.models import Count, Sum, F, Q, OuterRef, Subquery

vendas_por_categoria = Categoria.objects.annotate(
    total_produtos=Count('produto', distinct=True),
    produtos_em_estoque=Count(
        'produto',
        filter=Q(produto__estoque__gt=0)
    ),
    receita_potencial=Sum(
        F('produto__preco') * F('produto__estoque'),
        filter=Q(produto__estoque__gt=0)
    )
).filter(
    receita_potencial__gt=50000
).order_by('-receita_potencial')
```

**Rust com SQLx:**
```rust
// SQL puro - sem surpresas
let vendas = sqlx::query!(
    r#"
    SELECT
        c.id,
        c.nome,
        COUNT(DISTINCT p.id) as "total_produtos!",
        COUNT(p.id) FILTER (WHERE p.estoque > 0) as "produtos_em_estoque!",
        COALESCE(SUM(p.preco * p.estoque) FILTER (WHERE p.estoque > 0), 0) as "receita_potencial!"
    FROM categorias c
    LEFT JOIN produtos p ON c.id = p.categoria_id
    GROUP BY c.id, c.nome
    HAVING COALESCE(SUM(p.preco * p.estoque) FILTER (WHERE p.estoque > 0), 0) > $1
    ORDER BY receita_potencial DESC
    "#,
    50000.0
)
.fetch_all(pool)
.await?;
```


**Análise:** Para queries complexas, SQL puro é infinitamente mais legível. Você não precisa decorar a sintaxe do Django ORM nem adivinhar qual SQL será gerado. E quando roda EXPLAIN ANALYZE, você vê exatamente a query que escreveu.


### Transactions
**Django:**

```python
from django.db import transaction

@transaction.atomic
def transferir_estoque(origem_id, destino_id, quantidade):
    # select_for_update = lock pessimista
    origem = Estoque.objects.select_for_update().get(id=origem_id)
    destino = Estoque.objects.select_for_update().get(id=destino_id)

    if origem.quantidade < quantidade:
        raise ValueError("Estoque insuficiente")

    origem.quantidade -= quantidade
    destino.quantidade += quantidade

    origem.save()
    destino.save()
    # Se qualquer coisa explodir, rollback automático
```

**SQLx:**
```rust
async fn transferir_estoque(
    pool: &PgPool,
    origem_id: i32,
    destino_id: i32,
    quantidade: i32,
) -> Result<(), sqlx::Error> {
    let mut tx = pool.begin().await?;

    // SELECT FOR UPDATE explícito
    let origem = sqlx::query!(
        "SELECT quantidade FROM estoque WHERE id = $1 FOR UPDATE",
        origem_id
    )
    .fetch_one(&mut *tx)
    .await?;

    if origem.quantidade < quantidade {
        return Err(sqlx::Error::RowNotFound); // Rollback implícito
    }

    sqlx::query!(
        "UPDATE estoque SET quantidade = quantidade - $1 WHERE id = $2",
        quantidade, origem_id
    )
    .execute(&mut *tx)
    .await?;

    sqlx::query!(
        "UPDATE estoque SET quantidade = quantidade + $1 WHERE id = $2",
        quantidade, destino_id
    )
    .execute(&mut *tx)
    .await?;

    tx.commit().await?;
    Ok(())
}
```

**Análise:** SQLx é mais verboso, mas você controla cada passo da transação. O `SELECT FOR UPDATE` está explícito. O commit é manual. Se você retornar `Err`, o rollback é automático. Zero mágica, controle total.

## O Que SQLx Me Ensinou Sobre Bancos de Dados

Essa é a parte que eu não esperava: usar SQLx me tornou um desenvolvedor melhor, inclusive quando volto para Django.

**1. Índices Importam (DE VERDADE)**
No Django, você adiciona db_index=True e esquece. No SQLx, quando você escreve WHERE preco > 100 ORDER BY criado_em DESC, você pensa: "Pera, eu tenho um índice em preco? E em criado_em? Devo criar um índice composto?"

Comecei a rodar EXPLAIN ANALYZE em tudo. Descobri que metade dos índices que criava no Django eram inúteis, e faltavam índices críticos em queries reais.

**2. JOINs Têm Custo Diferente**
INNER JOIN é rápido quando há match. LEFT JOIN traz tudo da tabela esquerda mesmo sem match - mais lento e mais dados. RIGHT JOIN quase ninguém usa (e provavelmente você também não deveria).

No Django, select_related esconde essas decisões. No SQLx, você escolhe o JOIN, e isso te força a pensar na semântica dos dados.

**3. Connection Pooling Não É Mágico**
Django gerencia o pool automaticamente. Você nem pensa nisso. No SQLx:

```rust
let pool = PgPoolOptions::new()
    .max_connections(20)
    .min_connections(5)
    .acquire_timeout(Duration::from_secs(3))
    .connect(&database_url)
    .await?;
```

Você configura explicitamente quantas conexões, timeouts, behavior de retry. E quando dá erro de "too many connections", você sabe exatamente por quê.


**4. Tipos do Banco vs Tipos da Linguagem**
Django abstrai: DecimalField vira Decimal em Python. No SQLx, você mapeia explicitamente:

```rust
use rust_decimal::Decimal;  // Para NUMERIC/DECIMAL do PostgreSQL
use chrono::{DateTime, Utc};  // Para TIMESTAMP WITH TIME ZONE
use uuid::Uuid;  // Para UUID

#[derive(FromRow)]
struct Produto {
    id: Uuid,
    preco: Decimal,  // Não é f64! Precisão financeira!
    criado_em: DateTime<Utc>,
}
```

Você aprende que f64 é péssimo para dinheiro (floating point errors). Você entende que timestamps com timezone são diferentes de timestamps ingênuos. Django abstrai isso; SQLx te educa.

**5. Prepared Statements são seus amigos**
SQLx usa prepared statements por padrão:

```rust
sqlx::query!("SELECT * FROM produtos WHERE id = $1", produto_id)
```

Esse $1 não é interpolação de string. É um placeholder. O PostgreSQL prepara a query uma vez, cacheia o plano de execução, e reutiliza. É mais rápido e previne SQL injection automaticamente.

Django também faz isso, mas você nunca vê. Em SQLx, é impossível não usar prepared statements (a menos que você use .query() com raw SQL, mas aí você perde compile-time checking).

### Quando Usar Cada Um?


Quando Usar Cada Um?
Aqui está a verdade: eu não "abandonei" o Django. Uso as duas ferramentas, para coisas diferentes.

#### Use Django ORM quando:
✅ Você precisa de um MVP/protótipo RÁPIDO - Nada bate Django para validar uma ideia em 2 dias

✅ Seu time é predominantemente Python - Curva de aprendizado de Rust é íngreme; às vezes não vale a pena

✅ As queries são simples - CRUD básico, filtros simples, relacionamentos diretos? Django é imbatível

✅ O Django Admin é requisito - Um backoffice completo de graça é difícil de superar

✅ Performance não é gargalo - Se o banco responde em 50ms e isso é OK para seu SLA, otimização prematura é raiz de todo mal

✅ Você quer migrations automáticas - makemigrations é espetacular; em Rust você usa ferramentas como sqlx-cli migrate ou refinery, mas é mais manual

#### Use SQLx quando:
✅ Performance e latência são críticas - APIs públicas de alta carga, microserviços que processam milhões de requests

✅ Você tem queries SQL complexas - CTEs, window functions, LATERAL joins - SQL puro é mais legível

✅ Type safety em compile-time é importante - Zero erros de SQL em produção vale ouro

✅ Você quer controle total - Quando você precisa otimizar cada byte e cada milissegundo

✅ Seu time já sabe SQL bem - Se seu time é forte em SQL, SQLx é produtivo rapidamente

✅ Microserviços de alta performance - Serviços stateless, containerizados, que precisam escalar horizontalmente com eficiência

Use os Dois quando:
✅ Sistema híbrido - Django para backoffice/admin, Rust+SQLx para APIs públicas de alta carga

✅ Migração gradual - Comece com Django, identifique gargalos, reescreva apenas esses endpoints em Rust

✅ Equipe mista - Devs Python no backoffice, devs Rust em serviços críticos


## Lições da Jornada
Depois de meses nessa transição, aqui estão as lições que carrego:

**1. Abstrações São Trade-offs**

Django te dá produtividade; SQLx te dá controle. Não existe almoço grátis. Escolha conscientemente qual trade-off seu projeto precisa.

**2. Saber SQL de Verdade Importa**

SQLx me forçou a ser muito melhor em SQL. E isso é transferível para qualquer stack. Hoje, quando volto para o Django, escrevo queries do ORM muito mais eficientes porque sei o SQL que vai ser gerado.

**3. Type Safety É Viciante**

Depois que você vê query errors em compile-time, é muito difícil voltar para descobrir em produção que você typo categria em vez de categoria.

**4. Curva de Aprendizado Vale a Pena**

Os primeiros dias foram duros. Muito. Mas depois da curva, você codifica mais rápido e com mais confiança. Zero medo de refatorar queries, porque o compilador te protege.

**5. Django Não É "Ruim"**

Sério. O Django é uma ferramenta incrível para o que foi projetado. Rust+SQLx é para cenários diferentes. Use a ferramenta certa para o problema certo.

## Conclusão
Desaprender a confiar em mágica foi doloroso. Teve dias que eu pensei "cara, por que não deixo o Django fazer isso automaticamente?". Mas hoje, olhando para trás, valeu cada minuto de frustração.

Não é que SQLx seja "melhor" que Django ORM. É que eles resolvem problemas diferentes. O Django maximiza produtividade para 80% dos casos. SQLx maximiza performance e controle para os 20% críticos.

No fim das contas, eu não abandonei o Django - eu só aprendi quando não usar ele. E isso, ironicamente, me tornou um desenvolvedor Django melhor também. Hoje, quando vejo um select_related, sei exatamente qual JOIN está rolando. Quando vejo um .annotate(), sei qual SQL será gerado. Quando vejo N+1 queries, identifico na hora.

A magia ainda está lá. Eu só entendo os truques agora.

E você sabe o que descobri? Não precisa escolher um lado. Use o Django para prototipar rápido. Use SQLx para otimizar gargalos. Use os dois no mesmo sistema. A melhor stack é a que resolve o problema do jeito mais eficiente, não a que te dá mais pontos de dogmatismo no Twitter.

Se você está confortável demais com seu ORM, talvez seja hora de se desconfortar um pouco. Escreva SQL na mão por algumas semanas. Veja o que você aprende. Não precisa migrar tudo - mas experimente.

Você pode se surpreender com o que descobre quando a magia desaparece.

## Quer Mergulhar Fundo no Rust e SQLx?
Se este artigo despertou sua curiosidade sobre como Rust e SQLx funcionam por baixo dos panos, ou se você quer dominar essa transição sem passar pelos mesmos perrengues que eu passei, temos algo especial para você.

**"Desbravando Rust"** é o guia definitivo para desenvolvedores backend que querem ir além das abstrações e realmente entender como bancos de dados, performance e type safety funcionam em sistemas modernos.

**O Que Você Vai Aprender:**

**SQLx do zero:** Desde queries simples até transactions complexas e streaming

**Async/Await em Rust:** Como Tokio funciona e por que é tão rápido comparado ao asyncio do Python

**Type Safety na prática:** Compile-time checking que salva seu deploy às 3h da manhã

**Migrations e Schema Management:** Ferramentas do ecossistema como sqlx-cli e como estruturar projetos reais

**Projetos completos:** Construa APIs de produção com Axum + SQLx + PostgreSQL, com testes, observabilidade e deploy



### [Clique aqui e garanta seu exemplar agora!](https://desbravando-rust.github.io/)


<a href="https://desbravando-rust.github.io/" target="_blank"><img src="../../imgs/capa.jpg" alt="Capa do Livro Desbravando Rust" width="120" align="left"></a>
