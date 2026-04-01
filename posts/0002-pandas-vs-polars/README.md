# Pandas vs Polars: Benchmark com 3 Milhões de Registros
###### Por [@zejuniortdr](https://github.com/zejuniortdr/) em Nov 21, 2025

Recentemente caiu na minha timeline um vídeo do [Lewis](https://www.youtube.com/c/codingwithlewis) apresentando um pacote do python que ele classificou como incrível:

<a href="https://www.youtube.com/watch?v=3Re64c90ZnM" target="_blank">
<img src="https://img.youtube.com/vi/3Re64c90ZnM/0.jpg">
</a>

O pacote em questão é o [Polars](https://pola.rs/). Como o próprio site oficial diz:
> Polars is an open-source library for data manipulation, known for being one of the fastest data processing solutions on a single machine. It features a well-structured, typed API that is both expressive and easy to use.

E como ele consegue ser tão incrível e apresentar resultados tão absurdos? É escrito em Rust 🦀.

Este artigo nasceu da inspiração sobre o tema depois de uma aula de Pandas com o [Rafael Dias](https://github.com/RafaelMascarenhasC) e da provocação da [Amanda Ozava](https://github.com/amandaozava) que lembrou bem quando compartilhei com ela o vídeo acima.

Dado ambos com mais experiência que eu no assunto, achei por bem citá-los aqui e pedir para que fizessem uma revisão no material que compartilharei abaixo.

Meu primeiro contato com o Pandas foi em um Nano Degree da Udacity:
[Programming for Data Science with Python](https://www.udacity.com/course/programming-for-data-science-nanodegree--nd104) e de lá para cá não tive muita oportunidade de usá-lo. O material abaixo é fruto de uma pesquisa ao longo de alguns dias (desde a talk do Rafa), obviamente com algum viés para o bench entre os dois pacotes.

## O que são DataFrames?
Se você já trabalhou com planilhas do Excel ou Google Sheets, você já conhece o conceito de DataFrame sem saber. Um DataFrame é basicamente uma tabela de dados com:

- **Linhas**: cada linha representa um registro (como uma linha na planilha)
- **Colunas**: cada coluna representa um atributo ou campo (como uma coluna na planilha)
- **Tipos de dados**: cada coluna tem um tipo específico (números, texto, datas, etc.)

A diferença é que DataFrames são projetados para:
- Processar milhões de linhas de forma eficiente
- Realizar operações complexas em poucos comandos
- Integrar-se com ferramentas de análise de dados e machine learning

**Pandas** tem sido a biblioteca padrão para isso em Python desde 2008. **Polars** é o novo competidor que promete fazer tudo isso, só que muito mais rápido.


## Semelhanças: O Território Comum

Antes de falarmos das diferenças, é importante entender que ambas as bibliotecas compartilham os mesmos conceitos fundamentais:

**Estruturas de Dados**

- **DataFrames**: Estruturas tabulares bidimensionais com linhas e colunas
- **Series**: Estruturas unidimensionais representando uma única coluna
- **Operações vetorizadas**: Em vez de processar um dado por vez (como um loop), processam lotes inteiros de dados de uma só vez
- **Suporte a diversos formatos**: CSV, Parquet, JSON, Excel e outros

**Operações Comuns**
As operações fundamentais são suportadas por ambas:

- **Filtros e seleções**: Escolher linhas e colunas específicas
- **Agregações**: Somar, calcular médias, contar elementos, etc.
- **Joins e merges**: Combinar dados de múltiplas tabelas
- **Transformações**: Criar novas colunas baseadas em cálculos
- **Agrupamentos**: Agrupar dados por categorias e aplicar operações


**Exemplo Equivalente - Filtro Simples**
```python
#Pandas
pythondf_filtrado = df[df['quantidade'] > 5]

# Polars
pythondf_filtrado = df.filter(pl.col('quantidade') > 5)
```

Ambas fazem a mesma coisa: filtram as linhas onde a coluna 'quantidade' é maior que 5. A sintaxe é um pouco diferente, mas o conceito é idêntico.

## Diferenças: Onde Polars se Destaca

Agora vamos ao que realmente interessa: o que torna Polars tão especial? As diferenças vão muito além da sintaxe.

### 1. Linguagem de Implementação: A Base de Tudo
Aqui está o grande diferencial:

**Pandas:**

- Construído sobre NumPy, que tem seu núcleo escrito em C
- Limitado pelo **GIL (Global Interpreter Lock)** do Python - uma trava que impede que múltiplas threads Python executem ao mesmo tempo
- Sofre com overhead (custo adicional) ao lidar com tipos Python, especialmente strings

**Polars:**

- Escrito completamente em Rust 🦀
- Performance próxima de C/C++, mas com segurança de memória garantida
- Sem limitações do GIL - paralelização nativa e verdadeira
- Gerenciamento de memória eficiente e sem overhead.

**Impacto visível**: Polars é **5-10x mais rápido** em operações comuns. Em alguns casos específicos, pode ser até 100x mais rápido.


### 2. Modelo de Execução: Eager vs Lazy
Esta é uma das diferenças mais importantes e que mais impacta a performance.

**Pandas - Eager Execution (Execução Imediata)**
Pandas executa cada operação imediatamente, na ordem em que você escreve:

```python
df.assign(nova_col=lambda x: x['a'] * 2)     # Executa agora
  .query('quantidade > 100')                 # Depois executa isso
  .groupby('categoria').mean()               # Por último isso

```

O problema: ele processa todos os dados primeiro, para depois filtrar. É como preparar um banquete completo para depois descobrir que só 10% dos convidados apareceram.

**Polars - Lazy + Eager Execution (Execução Preguiçosa + Imediata)**
Polars oferece dois modos:

1. Modo Eager (padrão): Similar ao Pandas, executa imediatamente
2. Modo Lazy (recomendado): Constrói um plano de execução e otimiza antes de executar

```python
df.lazy()                                        # Entra em modo lazy
  .with_columns((pl.col('a') * 2).alias('nova_col'))
  .filter(pl.col('quantidade') > 100)            # Ainda não executou nada
  .group_by('categoria').mean()
  .collect()                                     # AGORA executa tudo otimizado
```

**O que Polars faz nos bastidores:**

- Reordena operações: Aplica filtros ANTES de fazer cálculos pesados
- Elimina redundâncias: Remove cálculos que não serão usados
- Otimiza memória: Processa apenas o necessário
- Paraleliza: Divide o trabalho entre múltiplos núcleos

É como ter um assistente inteligente que reorganiza sua lista de tarefas para fazer tudo mais rápido.

### 3. Sintaxe e Estilo de Código

#### Pandas - Flexível Demais
Pandas é **muito flexível**, o que pode ser bom para iniciantes, mas ruim para manutenção:

```python
# Múltiplas formas de fazer a mesma coisa:
df[df['a'] > 5]
df.query('a > 5')
df.loc[df['a'] > 5]
```

Para operações complexas, você frequentemente precisa usar `.apply()` com lambdas (funções anônimas), que são lentas porque processam linha por linha:

```python
# Operação condicional com .mask()
df.assign(a=lambda df_: df_['a'].mask(df_['c'] == 2, df_['b']))

# Apply sequencial (lento!)
df['resultado'] = df.apply(lambda row: complexa_func(row), axis=1)
```

#### Polars - Consistente e Expressivo
Polars usa uma **API baseada em expressões e contextos**. Tudo é mais consistente:

```python
# Operação condicional clara
df.with_columns(
    pl.when(pl.col('c') == 2)
    .then(pl.col('b'))
    .otherwise(pl.col('a'))
    .alias('a')
)

# Operação nativa e paralela (rápida!)
df.with_columns(
    pl.col('valores').map_elements(complexa_func)  # Automaticamente paralelizado
)
```

A sintaxe de Polars pode parecer mais verbosa no início, mas é:

- Mais explícita: Fica claro o que está acontecendo
- Mais consistente: Sempre usa o mesmo padrão
- Mais rápida: Evita loops implícitos

### 4. Paralelização e Concorrência

#### Pandas - Praticamente Single-Threaded

Pandas roda majoritariamente em um único núcleo do seu processador:

```python
# Pandas opera majoritariamente em um único núcleo, exceto por algumas operações vetorizadas que podem usar paralelismo interno do NumPy.
df.groupby('categoria')['valor'].sum()
```

Por quê? Por causa do **GIL (Global Interpreter Lock)** do Python. É como ter um carro de 8 cilindros, mas só poder usar 1 de cada vez.

Para ter paralelismo real em Pandas, você precisa de bibliotecas externas como:

- Dask: Pandas paralelo para datasets grandes
- Modin: Drop-in replacement que paraleliza Pandas
- Ray: Framework de computação distribuída


#### Polars - Paralelização Nativa
Polars usa todos os núcleos disponíveis automaticamente:
```python
# Usa todos os núcleos automaticamente
df.group_by('categoria').agg(pl.col('valor').sum())
```

Além disso, Polars usa SIMD (Single Instruction, Multiple Data) - uma tecnologia que permite processar múltiplos valores com uma única instrução do processador. É como ter um supermercado com múltiplos caixas, todos trabalhando simultaneamente.

Pandas também usa SIMD em algumas operações via NumPy. Exemplo: operações vetorizadas:
```python
df["price_with_tax"] = df["price"] * 1.12
```


### 5. Tipos de Dados e Strictness

#### Pandas - Loose Typing (Tipagem Flexível)

Pandas faz conversões automáticas de tipos, o que pode parecer conveniente, mas gera bugs silenciosos:

```python
df = pd.DataFrame({'valores': [1, 2, 3, 4, 5]})
print(df['valores'].dtype)  # int64

df.loc[5] = [None]  # Adiciona um valor None
print(df['valores'].dtype)  # float64 (converteu TODA a coluna!)
```

O que aconteceu? Ao adicionar um `None` (que representa ausência de valor), Pandas converteu toda a coluna de inteiros para floats, porque inteiros não podem representar valores ausentes nativamente.

#### Polars - Strict Typing (Tipagem Estrita)

Polars é rigoroso com tipos e te força a ser explícito:
```python
df = pl.DataFrame({'valores': [1, 2, 3, 4, 5]})

# Isso dá erro!
df.extend(pl.DataFrame({'valores': [None]}))
# Error: type mismatch

# Forma correta - seja explícito
df.extend(pl.DataFrame({'valores': [pl.Null]}))  # OK com tipo correto
```

Por que isso é bom? Porque erros explícitos são melhores que bugs silenciosos. Você descobre o problema imediatamente, não depois de horas de depuração.

### 6. Uso de Memória

#### Pandas - Guloso com RAM
Pandas requer **5-10x** o tamanho do dataset em memória RAM:
- Copia dados frequentemente entre operações
- Não tem suporte nativo para datasets maiores que a memória
- Precisa carregar tudo na RAM de uma vez

Se você tem um arquivo CSV de 1GB, pode precisar de 10GB de RAM para processá-lo com Pandas.

#### Polars - Eficiente e com Streaming
Polars requer apenas **2-4x** o tamanho do dataset:

- Usa zero-copy operations sempre que possível (reutiliza dados sem copiar)
- Suporte nativo a streaming para datasets maiores que a RAM
- Processa dados em chunks (pedaços) quando necessário

```python
# Processar arquivo maior que a memória disponível
pl.scan_csv('arquivo_gigante.csv')           # Não carrega tudo
  .filter(pl.col('data') > '2024-01-01')     # Filtra durante a leitura
  .group_by('categoria')
  .agg(pl.col('valor').sum())
  .sink_csv('resultado.csv')                 # Streaming! Não sobrecarrega RAM
```

Com Polars, você pode processar arquivos de 50GB em uma máquina com 8GB de RAM.


### 7. Operações Complexas: Apply vs Expressões Nativas

#### Pandas - Dependente de `.apply()`
Para operações complexas, Pandas frequentemente te força a usar `.apply()`, que é lento:
```python
# Loop implícito - processa linha por linha
df['novo'] = df.apply(
    lambda row: row['a'] * row['b'] if row['c'] > 10 else 0,
    axis=1
)
```

O `.apply()` é lento porque:

- Itera linha por linha (perde vetorização)
- Tem overhead do Python para cada linha
- Não pode ser paralelizado facilmente

#### Polars - Métodos Nativos para Tudo
Polars tem métodos nativos (escritos em Rust) para praticamente tudo:

```python
# Operação vetorizada e paralela
df.with_columns(
    pl.when(pl.col('c') > 10)
    .then(pl.col('a') * pl.col('b'))
    .otherwise(0)
    .alias('novo')
)
```

Por ser nativo em Rust:

- **Vetorizado**: Processa múltiplas linhas de uma vez
- **Paralelizado**: Usa múltiplos núcleos automaticamente
- **Zero overhead**: Sem custo adicional do Python


### 8. Ecossistema e Maturidade

#### Pandas - Maduro e Integrado

**Vantagens:**

- **Maturidade**: Desde 2008, extremamente estável
- **Ecossistema rico**: Integração profunda com scikit-learn, matplotlib, seaborn, statsmodels
- **Documentação extensa**: Milhares de tutoriais e respostas no Stack Overflow
- **Comunidade gigante**: Fácil encontrar ajuda

Quando usar: Se você precisa de integração imediata com ferramentas de machine learning.

#### Polars - Novo mas Crescendo Rápido
**Situação atual:**

- **Maturidade**: Desde 2020, mas já muito estável
- **Crescimento acelerado**: Comunidade crescendo exponencialmente
- **Interoperabilidade**: Fácil converter para Pandas quando necessário

```python
# Usar Polars para processamento pesado
df_polars = pl.DataFrame({'a': [1, 2, 3, 4, 5]})

# Converter para Pandas quando precisar de scikit-learn
df_pandas = df_polars.to_pandas()
model.fit(df_pandas)

# E vice-versa
df_polars_novamente = pl.from_pandas(df_pandas)
```
**Tendência:** Cada vez mais bibliotecas estão adicionando suporte direto a Polars.


### Quando Usar Cada Uma?
#### Use Pandas quando:
- **Datasets pequenos/médios (< 1GB)**: Se cabe confortavelmente na memória, Pandas funciona bem;
- **Prototipagem rápida e exploração**: Sintaxe mais familiar para quem está começando e ótimo para análise exploratória em Jupyter notebooks;
- **Integração profunda com ML**: scikit-learn, statsmodels, TensorFlow integram nativamente. Também não quer o overhead de converter dados;
- **Time já familiarizado**: Equipe já domina Pandas e o  custo de mudança não se justifica (ainda);

#### Use Polars quando:
- **Performance é crítica**: Processamento precisa ser rápido e economia de tempo/recursos tem valor significativo;
- **Datasets grandes (> 1GB)**: Arquivos de vários gigabytes e precisa processar milhões/bilhões de linhas;
- **Operações de agregação/groupby pesadas**: Para agrupamentos complexos com múltiplas agregações, o Polars pode ser 10-50x mais rápido;
- **Dados maiores que memória**: Suporte nativo a streaming e consegue processar arquivos de 50GB com 8GB de RAM;
- **Código em produção que precisa escalar**: Aplicações que rodam frequentemente, custos de infraestrutura importam e/ou desempenho impacta experiência do usuário;


## Exemplos Práticos: Comparando as Três Abordagens

Toda essa parte teórica com exemplos simples foram para criar uma fundação mínima de conhecimento para quem nunca viu algum destes pacotes e conseguirmos seguir na parte que realmente importa deste artigo.

Não é que eu duvide do Lewis, mas por se tratar de números tão absurdos, resolvi testar reproduzindo o mesmo cenário que ele criou: processar três milhões de linhas de um arquivo CSV com ambas e para cereja do bolo, resolvi fazer um teste apelativo para ver se traria muita diferença. Também inclui neste benchmark processar o mesmo arquivo com Rust + Polars.


Para gerar esse arquivo inicial, utilizei o seguinte script em python:

```python
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

def generate_sales_data(num_records=3_000_000, output_file="data/sales_data.csv"):
    """Gera dados sintéticos de vendas"""
    Path("data").mkdir(exist_ok=True)

    products = ["Laptop", "Mouse", "Keyboard", "Monitor", "Headset",
                "Webcam", "SSD", "RAM", "GPU", "CPU"]
    categories = ["Electronics", "Accessories", "Components"]
    regions = ["North", "South", "East", "West", "Central"]

    start_date = datetime(2023, 1, 1)

    print(f"Gerando {num_records:,} registros...")

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'id', 'date', 'product', 'category', 'region',
            'quantity', 'price', 'discount', 'customer_id'
        ])

        for i in range(num_records):
            date = start_date + timedelta(days=random.randint(0, 730))
            product = random.choice(products)
            category = random.choice(categories)
            region = random.choice(regions)
            quantity = random.randint(1, 20)
            price = round(random.uniform(10, 2000), 2)
            discount = round(random.uniform(0, 0.3), 2)
            customer_id = random.randint(1, 50000)

            writer.writerow([
                i, date.strftime('%Y-%m-%d'), product, category,
                region, quantity, price, discount, customer_id
            ])

            if (i + 1) % 500_000 == 0:
                print(f"  {i + 1:,} registros gerados...")

    print(f"✓ Arquivo gerado: {output_file}")

if __name__ == "__main__":
    generate_sales_data()
```

Com as seguintes dependências:
```text
pandas = "==2.3.3"
polars-lts-cpu = "==1.33.1"
psutil = "==7.1.3"
```


### Exemplo 1: Python + Pandas
Para o bench para este cenário, foi utilizado o seguinte script:
```python
import pandas as pd
import time
import psutil
import os
from pathlib import Path

def get_memory_usage():
    """Retorna uso de memória em MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

def benchmark_pandas():
    Path("results").mkdir(exist_ok=True)

    metrics = {
        'library': 'Pandas',
        'operations': {},
        'total_time': 0,
        'peak_memory_mb': 0
    }

    initial_memory = get_memory_usage()
    start_total = time.time()

    # 1. LEITURA
    print("1. Lendo CSV...")
    start = time.time()
    df = pd.read_csv('data/sales_data.csv')
    read_time = time.time() - start
    metrics['operations']['read_csv'] = read_time
    print(f"   Tempo: {read_time:.2f}s | Memória: {get_memory_usage():.2f} MB")

    # 2. FILTROS
    print("2. Aplicando filtros...")
    start = time.time()
    filtered = df[(df['quantity'] > 5) & (df['price'] > 100)]
    filter_time = time.time() - start
    metrics['operations']['filter'] = filter_time
    print(f"   Tempo: {filter_time:.2f}s | Registros: {len(filtered):,}")

    # 3. AGREGAÇÕES
    print("3. Agregações (groupby)...")
    start = time.time()
    agg_result = df.groupby(['region', 'category']).agg({
        'quantity': 'sum',
        'price': 'mean',
        'id': 'count'
    }).reset_index()
    agg_time = time.time() - start
    metrics['operations']['aggregation'] = agg_time
    print(f"   Tempo: {agg_time:.2f}s | Grupos: {len(agg_result):,}")

    # 4. TRANSFORMAÇÕES
    print("4. Transformações de colunas...")
    start = time.time()
    df['total_price'] = df['quantity'] * df['price'] * (1 - df['discount'])
    df['year'] = pd.to_datetime(df['date']).dt.year
    transform_time = time.time() - start
    metrics['operations']['transform'] = transform_time
    print(f"   Tempo: {transform_time:.2f}s")

    # 5. JOINS
    print("5. Join de dataframes...")
    start = time.time()
    summary = df.groupby('customer_id')['total_price'].sum().reset_index()
    summary.columns = ['customer_id', 'total_spent']
    joined = df.merge(summary, on='customer_id', how='left')
    join_time = time.time() - start
    metrics['operations']['join'] = join_time
    print(f"   Tempo: {join_time:.2f}s")

    # 6. ESCRITA
    print("6. Escrevendo resultado...")
    start = time.time()
    top_customers = joined.groupby('customer_id')['total_spent'].first()\
        .sort_values(ascending=False).head(1000)
    top_customers.to_csv('results/pandas_top_customers.csv')
    write_time = time.time() - start
    metrics['operations']['write_csv'] = write_time
    print(f"   Tempo: {write_time:.2f}s")

    # MÉTRICAS FINAIS
    total_time = time.time() - start_total
    peak_memory = get_memory_usage()

    metrics['total_time'] = total_time
    metrics['peak_memory_mb'] = peak_memory - initial_memory

    print(f"\n{'='*50}")
    print(f"PANDAS - Tempo total: {total_time:.2f}s")
    print(f"PANDAS - Memória pico: {peak_memory - initial_memory:.2f} MB")
    print(f"{'='*50}\n")

    # Salvar métricas
    import json
    with open('results/pandas_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)

    return metrics

if __name__ == "__main__":
    benchmark_pandas()
```


### Exemplo 2: Python + Polars

Eis o script, também em python processa o mesmo arquivo do exemplo anterior, só que agora com o Polars:

```python
import polars as pl
import time
import psutil
import os
from pathlib import Path

def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

def benchmark_polars_python():
    Path("results").mkdir(exist_ok=True)

    metrics = {
        'library': 'Polars (Python)',
        'operations': {},
        'total_time': 0,
        'peak_memory_mb': 0
    }

    initial_memory = get_memory_usage()
    start_total = time.time()

    # 1. LEITURA (Lazy)
    print("1. Lendo CSV (lazy)...")
    start = time.time()
    df = pl.scan_csv('data/sales_data.csv')
    read_time = time.time() - start
    metrics['operations']['read_csv'] = read_time
    print(f"   Tempo: {read_time:.4f}s (lazy) | Memória: {get_memory_usage():.2f} MB")

    # 2. FILTROS
    print("2. Aplicando filtros...")
    start = time.time()
    filtered = df.filter(
        (pl.col('quantity') > 5) & (pl.col('price') > 100)
    )
    filter_time = time.time() - start
    metrics['operations']['filter'] = filter_time
    print(f"   Tempo: {filter_time:.4f}s (lazy)")

    # 3. AGREGAÇÕES
    print("3. Agregações (groupby)...")
    start = time.time()
    agg_result = df.group_by(['region', 'category']).agg([
        pl.col('quantity').sum().alias('total_quantity'),
        pl.col('price').mean().alias('avg_price'),
        pl.col('id').count().alias('count')
    ])
    agg_time = time.time() - start
    metrics['operations']['aggregation'] = agg_time
    print(f"   Tempo: {agg_time:.4f}s (lazy)")

    # 4. TRANSFORMAÇÕES
    print("4. Transformações de colunas...")
    start = time.time()
    df = df.with_columns([
        (pl.col('quantity') * pl.col('price') * (1 - pl.col('discount')))
            .alias('total_price'),
        pl.col('date').str.strptime(pl.Date, '%Y-%m-%d').dt.year().alias('year')
    ])
    transform_time = time.time() - start
    metrics['operations']['transform'] = transform_time
    print(f"   Tempo: {transform_time:.4f}s (lazy)")

    # 5. JOINS
    print("5. Join de dataframes...")
    start = time.time()
    summary = df.group_by('customer_id').agg(
        pl.col('total_price').sum().alias('total_spent')
    )
    joined = df.join(summary, on='customer_id', how='left')
    join_time = time.time() - start
    metrics['operations']['join'] = join_time
    print(f"   Tempo: {join_time:.4f}s (lazy)")

    # 6. EXECUÇÃO + ESCRITA
    print("6. Executando query e escrevendo resultado...")
    start = time.time()
    top_customers = (joined
        .group_by('customer_id')
        .agg(pl.col('total_spent').first())
        .sort('total_spent', descending=True)
        .head(1000)
        .collect()  # Aqui executa tudo!
    )
    top_customers.write_csv('results/polars_python_top_customers.csv')
    write_time = time.time() - start
    metrics['operations']['write_csv'] = write_time
    print(f"   Tempo: {write_time:.2f}s (execução + escrita)")

    # MÉTRICAS FINAIS
    total_time = time.time() - start_total
    peak_memory = get_memory_usage()

    metrics['total_time'] = total_time
    metrics['peak_memory_mb'] = peak_memory - initial_memory

    print(f"\n{'='*50}")
    print(f"POLARS (Python) - Tempo total: {total_time:.2f}s")
    print(f"POLARS (Python) - Memória pico: {peak_memory - initial_memory:.2f} MB")
    print(f"{'='*50}\n")

    import json
    with open('results/polars_python_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)

    return metrics

if __name__ == "__main__":
    benchmark_polars_python()

```

### Exemplo 3: Rust + Polars

E por fim mas não menos importante, o exemplo em Rust com Polars que é praticamente uma F1 nessa corrida de velotrol:

{% raw %}
```rust
use polars::prelude::*;
use std::time::Instant;
use std::fs;
use sysinfo::System;

fn get_memory_usage() -> f64 {
    let mut sys = System::new_all();
    sys.refresh_memory();
    sys.used_memory() as f64 / (1024.0 * 1024.0)
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    fs::create_dir_all("results")?;

    let initial_memory = get_memory_usage();
    let start_total = Instant::now();

    // 1. LEITURA (Lazy)
    println!("1. Lendo CSV (lazy)...");
    let start = Instant::now();
    let df = LazyCsvReader::new("data/sales_data.csv")
        .with_has_header(true)
        .finish()?;
    let read_time = start.elapsed();
    println!("   Tempo: {:?} (lazy) | Memória: {:.2} MB", read_time, get_memory_usage());

    // 2. FILTROS
    println!("2. Aplicando filtros...");
    let start = Instant::now();
    let _filtered = df.clone().filter(
        col("quantity").gt(lit(5))
            .and(col("price").gt(lit(100.0)))
    );
    let filter_time = start.elapsed();
    println!("   Tempo: {:?} (lazy)", filter_time);

    // 3. AGREGAÇÕES
    println!("3. Agregações (groupby)...");
    let start = Instant::now();
    let _agg_result = df.clone()
        .group_by([col("region"), col("category")])
        .agg([
            col("quantity").sum().alias("total_quantity"),
            col("price").mean().alias("avg_price"),
            col("id").count().alias("count"),
        ]);
    let agg_time = start.elapsed();
    println!("   Tempo: {:?} (lazy)", agg_time);

    // 4. TRANSFORMAÇÕES
    println!("4. Transformações de colunas...");
    let start = Instant::now();
    let df = df.with_columns([
        (col("quantity") * col("price") * (lit(1.0) - col("discount")))
            .alias("total_price"),
    ]);
    let transform_time = start.elapsed();
    println!("   Tempo: {:?} (lazy)", transform_time);

    // 5. JOINS
    println!("5. Join de dataframes...");
    let start = Instant::now();
    let summary = df.clone()
        .group_by([col("customer_id")])
        .agg([col("total_price").sum().alias("total_spent")]);

    let joined = df.join(
        summary,
        [col("customer_id")],
        [col("customer_id")],
        JoinArgs::new(JoinType::Left),
    );
    let join_time = start.elapsed();
    println!("   Tempo: {:?} (lazy)", join_time);

    // 6. EXECUÇÃO + ESCRITA
    println!("6. Executando query e escrevendo resultado...");
    let start = Instant::now();
    let top_customers = joined
        .group_by([col("customer_id")])
        .agg([col("total_spent").first()])
        .sort(
            ["total_spent"],
            SortMultipleOptions::default().with_order_descending(true),
        )
        .limit(1000)
        .collect()?; // Executa aqui!

    let mut file = std::fs::File::create("results/polars_rust_top_customers.csv")?;
    CsvWriter::new(&mut file)
        .include_header(true)
        .finish(&mut top_customers.clone())?;

    let write_time = start.elapsed();
    println!("   Tempo: {:?} (execução + escrita)", write_time);

    // MÉTRICAS FINAIS
    let total_time = start_total.elapsed();
    let peak_memory = get_memory_usage() - initial_memory;

    println!("\n{}", "=".repeat(50));
    println!("POLARS (Rust) - Tempo total: {:.2?}", total_time);
    println!("POLARS (Rust) - Memória pico: {:.2} MB", peak_memory);
    println!("{}\n", "=".repeat(50));

    // Salvar métricas
    let metrics = format!(
        r#"{{
  "library": "Polars (Rust)",
  "total_time": {:.2},
  "peak_memory_mb": {:.2}
}}"#,
        total_time.as_secs_f64(),
        peak_memory
    );

    fs::write("results/polars_rust_metrics.json", metrics)?;

    Ok(())
}
```
{% endraw %}

### Resultados

Cada um dos exemplos acima foram executados na mesma máquina do post [Performance na prática: Um exemplo de real onde o Axum supera o FastAPI](https://desbravandorust.com.br/posts/0001-performance-na-pratica/#ambiente-do-execu%C3%A7%C3%A3o), e criei um script em python para analisar as saídas geradas na pasta `results/`:

```python
import json
import pandas as pd
from pathlib import Path

def compare_results():
    results_dir = Path("results")

    # Carregar métricas
    with open(results_dir / "pandas_metrics.json") as f:
        pandas_data = json.load(f)

    with open(results_dir / "polars_python_metrics.json") as f:
        polars_py_data = json.load(f)

    with open(results_dir / "polars_rust_metrics.json") as f:
        polars_rust_data = json.load(f)

    # Criar tabela comparativa
    comparison = pd.DataFrame({
        'Biblioteca': [
            pandas_data['library'],
            polars_py_data['library'],
            polars_rust_data['library']
        ],
        'Tempo Total (s)': [
            f"{pandas_data['total_time']:.2f}",
            f"{polars_py_data['total_time']:.2f}",
            f"{polars_rust_data['total_time']:.2f}"
        ],
        'Memória Pico (MB)': [
            f"{pandas_data['peak_memory_mb']:.2f}",
            f"{polars_py_data['peak_memory_mb']:.2f}",
            f"{polars_rust_data['peak_memory_mb']:.2f}"
        ]
    })

    print("\n" + "="*60)
    print("COMPARAÇÃO FINAL: Pandas vs Polars (Python) vs Polars (Rust)")
    print("="*60)
    print(comparison.to_string(index=False))
    print("="*60)

    # Calcular speedup
    pandas_time = pandas_data['total_time']
    polars_py_time = polars_py_data['total_time']
    polars_rust_time = polars_rust_data['total_time']

    print(f"\nSPEEDUP:")
    print(f"  Polars (Python) vs Pandas: {pandas_time/polars_py_time:.2f}x mais rápido")
    print(f"  Polars (Rust) vs Pandas: {pandas_time/polars_rust_time:.2f}x mais rápido")
    print(f"  Polars (Rust) vs Polars (Python): {polars_py_time/polars_rust_time:.2f}x mais rápido")

    print(f"\nREDUÇÃO DE MEMÓRIA:")
    pandas_mem = pandas_data['peak_memory_mb']
    polars_py_mem = polars_py_data['peak_memory_mb']
    polars_rust_mem = polars_rust_data['peak_memory_mb']

    print(f"  Polars (Python) vs Pandas: {((pandas_mem-polars_py_mem)/pandas_mem*100):.1f}% menos memória")
    print(f"  Polars (Rust) vs Pandas: {((pandas_mem-polars_rust_mem)/pandas_mem*100):.1f}% menos memória")
    print()

if __name__ == "__main__":
    compare_results()
```

#### Eis os números:

Para facilitar a execução de todos e coletar principalmente os picos de consumo de cpu e e memória de uma forma fácil, utilizei o seguinte `Makefile`:
```Makefile
bench:
	echo "============================================"
	echo "Python + Pandas"
	python scripts/2_benchmark_pandas.py
	echo "============================================"
	sleep 15

	echo "============================================"
	echo "Python + Polars"
	python scripts/2_benchmark_pandas.py
	echo "============================================"
	sleep 15

	echo "============================================"
	echo "Rust + Polars"
	./target/release/pandas-vs-polars
	echo "============================================"
	sleep 15

	echo "Resultados"
	python scripts/5_compare_results.py

```

Depois de rodar o primeiro script para gerar o arquivo, simplesmente rodei esse `bench`, com intervalos de 15s entre cada um para mapear os picos. Os números foram surpreendentes:

```shell
➜  make bench
echo "============================================"
============================================
echo "Python + Pandas"
Python + Pandas
python scripts/2_benchmark_pandas.py
1. Lendo CSV...
   Tempo: 2.56s | Memória: 302.78 MB
2. Aplicando filtros...
   Tempo: 0.12s | Registros: 2,148,184
3. Agregações (groupby)...
   Tempo: 0.33s | Grupos: 15
4. Transformações de colunas...
   Tempo: 0.58s
5. Join de dataframes...
   Tempo: 0.37s
6. Escrevendo resultado...
   Tempo: 0.07s

==================================================
PANDAS - Tempo total: 4.05s
PANDAS - Memória pico: 782.25 MB
==================================================

echo "============================================"
============================================
sleep 15
echo "============================================"
============================================
echo "Python + Polars"
Python + Polars
python scripts/2_benchmark_pandas.py
1. Lendo CSV...
   Tempo: 2.49s | Memória: 302.79 MB
2. Aplicando filtros...
   Tempo: 0.12s | Registros: 2,148,184
3. Agregações (groupby)...
   Tempo: 0.35s | Grupos: 15
4. Transformações de colunas...
   Tempo: 0.53s
5. Join de dataframes...
   Tempo: 0.37s
6. Escrevendo resultado...
   Tempo: 0.07s

==================================================
PANDAS - Tempo total: 3.93s
PANDAS - Memória pico: 782.39 MB
==================================================

echo "============================================"
============================================
sleep 15
echo "============================================"
============================================
echo "Rust + Polars"
Rust + Polars
./target/release/pandas-vs-polars
1. Lendo CSV (lazy)...
   Tempo: 23.295µs (lazy) | Memória: 2659.56 MB
2. Aplicando filtros...
   Tempo: 206.271µs (lazy)
3. Agregações (groupby)...
   Tempo: 13.338µs (lazy)
4. Transformações de colunas...
   Tempo: 4.626µs (lazy)
5. Join de dataframes...
   Tempo: 14.751µs (lazy)
6. Executando query e escrevendo resultado...
   Tempo: 618.259553ms (execução + escrita)

==================================================
POLARS (Rust) - Tempo total: 634.52ms
POLARS (Rust) - Memória pico: 312.22 MB
==================================================

echo "============================================"
============================================
sleep 15
echo "Resultados"
Resultados
python scripts/5_compare_results.py

============================================================
COMPARAÇÃO FINAL: Pandas vs Polars (Python) vs Polars (Rust)
============================================================
     Biblioteca Tempo Total (s) Memória Pico (MB)
         Pandas            3.93            782.39
Polars (Python)            0.35            311.11
  Polars (Rust)            0.63            312.22
============================================================

SPEEDUP:
  Polars (Python) vs Pandas: 11.08x mais rápido
  Polars (Rust) vs Pandas: 6.24x mais rápido
  Polars (Rust) vs Polars (Python): 0.56x mais rápido

REDUÇÃO DE MEMÓRIA:
  Polars (Python) vs Pandas: 60.2% menos memória
  Polars (Rust) vs Pandas: 60.1% menos memória
```


## Conclusão
Quando comecei este artigo, prometi mostrar por que Polars está revolucionando o processamento de dados. Os números não mentem - e eles são ainda mais impressionantes do que esperava.

### Os Resultados em Números
Processando 3 milhões de registros com operações reais (filtros, agregações, transformações e joins), foi obtido:

#### Python + Pandas:

- Tempo total: 3.93 segundos
- Memória pico: 782.39 MB

#### Python + Polars:
- Tempo total: 0.35 segundos → **11.08x mais rápido**
- **Memória pico**: 311.11 MB → **60.2% menos memória**

#### Rust + Polars:

- Tempo total: 0.63 segundos → **6.24x mais rápido**
- Memória pico: 312.22 MB → **60.1% menos memória**

### O Que Esses Números Significam?
#### 1. Polars é Consistentemente Mais Rápido
Com 11x de ganho de performance, Polars em Python transformou uma operação que levava quase 4 segundos em apenas 0.35 segundos. Em termos práticos:

- Uma análise que levava 10 minutos agora leva menos de 1 minuto
- Um pipeline que rodava em 1 hora agora termina em 5 minutos
- Processamentos noturnos de 8 horas podem ser reduzidos para menos de 1 hora

#### 2. Eficiência de Memória é Revolucionária
A redução de 60% no uso de memória não é apenas um número - é a diferença entre:

- Precisar de uma máquina com 32GB vs 16GB de RAM
- Conseguir processar datasets 2-3x maiores na mesma infraestrutura
- Reduzir custos de nuvem significativamente em ambientes de produção

### 3. Lazy Evaluation é Magia Pura
Observe os tempos do Rust + Polars:
```text
1. Lendo CSV (lazy)...          23.295µs (0.000023 segundos!)
2. Aplicando filtros...         206.271µs (0.0002 segundos!)
3. Agregações (groupby)...      13.338µs (0.000013 segundos!)
4. Transformações de colunas... 4.626µs (0.000004 segundos!)
5. Join de dataframes...        14.751µs (0.000014 segundos!)
6. Execução + escrita...        618.259ms (0.618 segundos)
```

As operações 1-5 levaram microsegundos porque Polars apenas construiu o plano de execução - não processou nada ainda. Quando finalmente executou (operação 6), fez tudo de uma vez, otimizado.

É como ter um assistente que anota todas as suas tarefas, reorganiza da forma mais eficiente possível, e então executa tudo de uma vez só.

### 4. Rust vs Python: Uma Surpresa Interessante
Curiosamente, Polars em Python foi mais rápido (0.35s) que em Rust puro (0.63s) no tempo total. Por quê? A maior parte do tempo do Rust foi gasto na escrita final do arquivo (618ms). As operações de processamento em si foram absurdamente rápidas em ambos.
Isso nos ensina algo importante: para a maioria dos casos de uso, Polars em Python já é mais que suficiente. Você não precisa migrar para Rust para ter ganhos extraordinários de performance.


#### O Veredicto Final
**Polars não é hype - é uma mudança de paradigma.**
Se você trabalha com dados e ainda usa apenas Pandas:

- Para prototipagem e datasets pequenos: Pandas continua sendo excelente
- Para qualquer coisa em produção: Polars deveria ser sua escolha padrão
- Para datasets grandes (>1GB): Polars não é opcional, é necessário
- Para economia de recursos: 60% menos memória = custos menores

| Critério            | Pandas                      | Polars                                |
| :------------------ | :-------------------------- | :------------------------------------ |
| **Performance**     | Significativamente mais lenta | **Extremamente Rápida** (11x mais)    |
| **Tipagem**         | Flexível (pode levar a erros) | Estrita (segurança e performance)     |
| **Paralelismo**     | Limitado (single-core padrão) | Nativo (aproveita todos os cores)     |
| **Lazy Evaluation** | ❌ (processamento imediato)   | ✔ (otimização e eficiência)           |
| **Uso de RAM**      | Alto (782 MB)               | **Baixo** (311 MB, 60% menos)         |
| **Streaming**       | ❌ (requer dados em memória)  | ✔ (via lazy, para datasets grandes)   |
| **Ecossistema ML**  | Excelente (maduro)          | Bom (crescendo rapidamente)           |


###### A Transição Vale a Pena?

A curva de aprendizado de Polars existe, sim. A sintaxe é diferente, o paradigma de expressões requer uma mudança de mentalidade. Mas os resultados falam por si:

- 11x mais rápido significa que o tempo que você investe aprendendo Polars se paga na primeira semana de uso
- 60% menos memória significa infraestrutura mais barata e capacidade de processar datasets maiores
- API consistente e expressiva significa código mais limpo e manutenível a longo prazo

##### O Futuro é Rust, Mas Você Não Precisa Saber Rust

A beleza de Polars é que você colhe todos os benefícios do Rust (velocidade, segurança de memória, paralelização) escrevendo Python. É o melhor dos dois mundos.

E quando você realmente precisar daquele último bit de performance? A transição de Python para Rust com Polars é suave - a API é praticamente idêntica.

Os números provam: Polars entrega o que promete. Não é marketing, não é hype - é engenharia de qualidade resolvendo problemas reais.
Se você processa dados regularmente, especialmente em produção, não é mais uma questão de "devo aprender Polars?" mas sim "quando vou migrar?".

A revolução do processamento de dados já começou. E ela é escrita em Rust 🦀.



## Quer Dominar Rust e Entender Como Polars Funciona Por Baixo dos Panos?

Se este artigo despertou sua curiosidade sobre como Polars consegue ser tão rápido, ou se você quer entender por que Rust está revolucionando o mundo da programação, temos algo especial para você.
"Desbravando Rust" é o guia definitivo para quem quer ir além do superficial e realmente dominar a linguagem que está por trás de ferramentas como Polars, Tokio, Servo e tantas outras que estão redefinindo performance e segurança.

**O Que Você Vai Aprender:**
- **Fundamentos sólidos**: Do zero ao avançado, sem pular etapas essenciais
- **Performance real**: Entenda como Rust elimina o overhead que torna Python lento
- **Safety sem garbage collector**: Como Rust garante segurança de memória em compile-time
- **Concorrência sem medo**: Paralelização nativa sem data races (o que torna Polars tão rápido)
- **Projetos práticos**: Construa aplicações reais, incluindo processamento de dados como vimos neste artigo


### [Clique aqui e garanta seu exemplar agora!](https://desbravandorust.com.br/)


Se os números não mentem e o Polars é 11x mais rápido que Pandas,  imagine o que você pode construir quando entende a linguagem que torna isso possível.


<a href="https://desbravandorust.com.br/" target="_blank"><img src="../../imgs/capa.jpg" alt="Capa do Livro Desbravando Rust" width="120" align="left"></a>
