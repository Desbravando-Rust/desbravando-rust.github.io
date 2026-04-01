# Concorrência e Paralelismo em Rust: Desvendando Threads e Async/Await para Pythonistas

Desenvolvedores Python que estão migrando para Rust frequentemente encontram desafios interessantes quando o assunto é concorrência e paralelismo. Enquanto Python tem seu próprio conjunto de ferramentas (threads, multiprocessing, asyncio), Rust oferece uma abordagem única que combina segurança de memória com alto desempenho.

Neste artigo, vamos explorar como Rust aborda essas questões fundamentais da programação moderna, sempre comparando com os conceitos que você já conhece do Python.

## 🧵 Introdução: O Desafio da Programação Concorrente

A programação concorrente é como coordenar vários cozinheiros em uma mesma cozinha:
- **Python**: Os cozinheiros precisam revezar o uso das facas (GIL)
- **Rust**: Cada cozinheiro tem suas próprias facas (ownership system)

A grande diferença é que Rust garante em tempo de compilação que não haverá conflitos, enquanto Python precisa confiar no desenvolvedor para evitar race conditions.

```python
# Python: Race condition comum
counter = 0

def increment():
    global counter
    for _ in range(100000):
        counter += 1

import threading
threads = [threading.Thread(target=increment) for _ in range(10)]

for t in threads:
    t.start()
for t in threads:
    t.join()

print(counter)  # Resultado imprevisível - não será 1.000.000!
```

Rust previne esse problema em tempo de compilação:

```rust
// Rust: Tentativa ingênua que não compila
let mut counter = 0;

let handle = std::thread::spawn(|| {
    // ERRO: `closure may outlive the current function, but it borrows
    // `counter`, which is owned by the current function`
    for _ in 0..100000 {
        counter += 1;
    }
});

handle.join().unwrap();
println!("{}", counter);
```

O compilador Rust nos impede de cometer erros comuns de concorrência! 🛡️

## 🔒 Seção 1: Threads em Rust - Safety Garantido pelo Sistema de Tipos

### Threads Seguras por Padrão

Enquanto em Python threads podem compartilhar estado livremente (com riscos), Rust exige que você pense cuidadosamente sobre o compartilhamento de dados.

```python
# Python: Compartilhamento "fácil" mas perigoso
import threading

shared_data = {"counter": 0}

def worker():
    for _ in range(1000):
        shared_data["counter"] += 1

threads = []
for _ in range(10):
    t = threading.Thread(target=worker)
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print(shared_data["counter"])  # Resultado inconsistente
```

Para compartilhar dados entre threads com segurança em Rust, precisamos de dois conceitos:

- **`Mutex<T>`** (MUTual EXclusion): funciona como o `threading.Lock()` do Python. O `Mutex` garante que apenas **um owner por vez** possa acessar e modificar o dado interno.
- **`Arc<T>`** (Atomic Reference Counter): é como um `Rc` (contador de referências) seguro para threads — ele permite que **múltiplos owners** compartilhem a posse do mesmo valor. Não tem equivalente direto simples em Python, pois o GIL faz isso implicitamente.

Juntos, `Arc<Mutex<T>>` é o padrão clássico para compartilhar estado mutável entre threads de forma segura: o `Arc` *compartilha a propriedade* e o `Mutex` *protege o acesso* ao dado interno.

```rust
// Rust: Compartilhamento seguro com Arc<Mutex<T>>
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let counter = Arc::new(Mutex::new(0));
    let mut handles = vec![];

    for _ in 0..10 {
        let counter = Arc::clone(&counter);
        // O `move` força o closure a *tomar posse* (ownership) da variável `counter`
        // (que é uma `Arc<Mutex<...>>`, já clonada para esta iteração).
        // Isso é necessário porque as threads podem durar mais que a função atual —
        // o sistema de ownership garante que os dados clonados vivam enquanto a thread precisar deles.
        let handle = thread::spawn(move || {
            for _ in 0..1000 {
                let mut num = counter.lock().unwrap();
                *num += 1;
            }
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    println!("Resultado: {}", *counter.lock().unwrap()); // Sempre 10000
}
```

### O Sistema de Ownership como Guardião

O segredo da segurança das threads em Rust está no sistema de tipos:
- `Send`: Permite que a **propriedade** de dados seja movida entre threads.
- `Sync`: Permite que dados sejam **acessados** por múltiplas threads simultaneamente através de referências imutáveis (`&T`). Um tipo `T` é `Sync` se `&T` é `Send`.

Isso contrasta diretamente com o GIL do Python: enquanto o GIL protege *tudo* de forma global (limitando o paralelismo), os traits `Send`/`Sync` permitem proteção *granular* — você usa `Mutex` apenas nos dados que realmente precisam de exclusão mútua, o que é mais eficiente e explícito.

Esses traits são automaticamente implementados quando é seguro fazê-lo, e o compilador valida isso para você.

## ⚡ Seção 2: Async/Await em Rust - Performance sem Bloqueio

### O Paradigma Assíncrono

A assincronia em Rust é diferente do Python: não há GIL e as tarefas podem executar verdadeiramente em paralelo quando há múltiplos núcleos disponíveis.

```python
# Python: asyncio com GIL
import asyncio

async def tarefa_lenta(nome, segundos):
    print(f"{nome} iniciou")
    await asyncio.sleep(segundos)
    print(f"{nome} terminou")

async def main():
    await asyncio.gather(
        tarefa_lenta("Tarefa 1", 2),
        tarefa_lenta("Tarefa 2", 1),
        tarefa_lenta("Tarefa 3", 3)
    )

asyncio.run(main())
```

Em Rust, async/await é mais sobre concorrência do que paralelismo — isso significa que uma única thread pode gerenciar milhares de operações de I/O concorrentes (como esperar respostas de rede) de forma eficiente, alternando entre elas. O paralelismo real (múltiplos núcleos trabalhando ao mesmo tempo) ainda é alcançado pelo *runtime* async (como o Tokio) ao distribuir essas tarefas por uma *pool* de threads de trabalho.

```rust
// Rust: async/await com tokio
use tokio::time::{sleep, Duration};

async fn tarefa_lenta(nome: &str, segundos: u64) {
    println!("{} iniciou", nome);
    sleep(Duration::from_secs(segundos)).await;
    println!("{} terminou", nome);
}

#[tokio::main]
async fn main() {
    let tarefa1 = tarefa_lenta("Tarefa 1", 2);
    let tarefa2 = tarefa_lenta("Tarefa 2", 1);
    let tarefa3 = tarefa_lenta("Tarefa 3", 3);

    // `tokio::join!` aguarda todas as tarefas completarem (sem dependências extras)
    tokio::join!(tarefa1, tarefa2, tarefa3);
}
```

### Runtime vs Biblioteca

Uma diferença fundamental: Python tem um runtime built-in para async (asyncio), enquanto Rust usa bibliotecas externas (tokio, async-std):

- **Python**: `asyncio` é parte da biblioteca padrão — solução oficial e única
- **Rust**: Você escolhe seu runtime conforme a necessidade

Esta abordagem dá mais flexibilidade ao programador Rust. Você pode escolher `tokio` para alta performance e um ecossistema rico de bibliotecas async, ou `async-std` para uma API mais próxima da stdlib. Em contraste, Python oferece o `asyncio` como solução única na biblioteca padrão.

## 🐍 Seção 3: Comparação com Python - GIL, Threads e Asyncio

### A Maldição do GIL (Global Interpreter Lock)

O GIL do Python é provavelmente o maior contraste com Rust:
- **Python**: Apenas uma thread executa código Python por vez (com exceções)
- **Rust**: Threads podem executar verdadeiramente em paralelo

```python
# Python: CPU-bound com threads (não escala)
import threading
import time

def trabalho_pesado():
    n = 0
    for i in range(10000000):
        n += i
    return n

# Threads para trabalho CPU-bound não escalam por causa do GIL
inicio = time.time()
threads = []
for _ in range(4):
    t = threading.Thread(target=trabalho_pesado)
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print(f"Threads Python: {time.time() - inicio:.2f}s")
```

Para trabalho CPU-bound em Python, você precisaria usar `multiprocessing`:

```python
# Python: CPU-bound com multiprocessing
from multiprocessing import Pool
import time

def trabalho_pesado(_):
    n = 0
    for i in range(10000000):
        n += i
    return n

inicio = time.time()
with Pool(4) as p:
    p.map(trabalho_pesado, range(4))
print(f"Multiprocessing Python: {time.time() - inicio:.2f}s")
```

Em Rust, threads escalam perfeitamente para trabalho CPU-bound:

```rust
// Rust: CPU-bound com threads (escala linearmente)
use std::thread;
use std::time::Instant;

fn trabalho_pesado() -> i64 {
    let mut n = 0;
    for i in 0..10000000 {
        n += i as i64;
    }
    n
}

fn main() {
    let inicio = Instant::now();

    let mut handles = vec![];
    for _ in 0..4 {
        handles.push(thread::spawn(|| {
            trabalho_pesado();
        }));
    }

    for handle in handles {
        handle.join().unwrap();
    }

    println!("Threads Rust: {:.2?}", inicio.elapsed());
}
```

### IO-bound: Async vs Threads

Para operações de I/O (arquivos, rede, banco de dados), ambas as linguagens têm boas soluções:

```python
# Python: I/O-bound com asyncio (eficiente)
import aiohttp
import asyncio

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

async def main():
    urls = ["http://httpbin.org/get"] * 10
    tasks = [fetch(url) for url in urls]
    # asyncio.gather aceita uma lista dinâmica de tarefas com sintaxe concisa
    responses = await asyncio.gather(*tasks)
    return len(responses)
```

```rust
// Rust: I/O-bound com async (eficiente)
// Cargo.toml: reqwest = { version = "0.12", features = ["json"] }
use reqwest;
use tokio::task::JoinSet;

async fn fetch(url: &str) -> Result<String, reqwest::Error> {
    reqwest::get(url).await?.text().await
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let urls = vec!["http://httpbin.org/get"; 10];

    // JoinSet gerencia um conjunto dinâmico de tarefas — sem dependências extras
    let mut set = JoinSet::new();
    for url in urls {
        set.spawn(async move { fetch(url).await });
    }

    let mut count = 0;
    while let Some(result) = set.join_next().await {
        result??;
        count += 1;
    }
    // Nota: Python's asyncio.gather(*tasks) é mais conciso para listas dinâmicas.
    // Em Rust, JoinSet (tokio) ou futures::future::join_all (crate `futures`) são as alternativas,
    // contrabalançadas pela performance e pelo controle fino que Rust oferece.
    println!("Total de respostas: {}", count);
    Ok(())
}
```

## 🚀 Seção 4: Exemplo Prático - Servidor Web Concorrente

Vamos implementar um servidor HTTP simples que pode lidar com múltiplas requisições concorrentemente.

### Versão Python com Flask + Threading

```python
# Python: Servidor simples com Flask
from flask import Flask
import time
import threading

app = Flask(__name__)

@app.route('/lenta/<int:segundos>')
def rota_lenta(segundos):
    time.sleep(segundos)  # Simula trabalho bloqueante
    return f"Dormi {segundos}s no thread {threading.get_ident()}"

if __name__ == '__main__':
    # Flask usa threads por padrão para lidar com concorrência
    app.run(threaded=True, port=8000)
```

Este servidor pode lidar com múltiplas requisições usando threads, mas cada thread consome recursos significativos do sistema.

### Versão Rust com Actix Web (Async)

```rust
// Rust: Servidor async com Actix Web
use actix_web::{get, web, App, HttpServer, HttpResponse};
use std::time::Duration;
use tokio::time::sleep;

#[get("/lenta/{segundos}")]
async fn rota_lenta(segundos: web::Path<u64>) -> HttpResponse {
    sleep(Duration::from_secs(*segundos)).await; // Não bloqueia o thread
    HttpResponse::Ok().body(format!("Dormi {}s", segundos))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new().service(rota_lenta)
    })
    .bind("127.0.0.1:8080")?
    .workers(4)  // Número de threads de trabalho
    .run()
    .await
}
```

A versão Rust é muito mais eficiente em termos de recursos porque:
- Usa um número fixo de threads (workers)
- As tarefas async não bloqueiam os threads
- Pode lidar com milhares de conexões concorrentes com poucos threads

### Teste de Carga Simples

```python
# Python: Teste de carga para os servidores
import requests
import time
from concurrent.futures import ThreadPoolExecutor  # necessário para ThreadPoolExecutor

def testar_servidor(porta, url, num_requisicoes):
    inicio = time.time()

    # O parâmetro `_` recebe cada número do range mas é ignorado —
    # o importante é disparar `num_requisicoes` chamadas concorrentes.
    def fazer_requisicao(_):
        return requests.get(f"http://localhost:{porta}{url}").status_code

    with ThreadPoolExecutor(max_workers=100) as executor:
        # Executa a função 'fazer_requisicao' para cada elemento no range
        resultados = list(executor.map(fazer_requisicao, range(num_requisicoes)))

    tempo_total = time.time() - inicio
    print(f"Porta {porta}: {num_requisicoes} reqs em {tempo_total:.2f}s")

# Testar ambos
testar_servidor(8000, "/lenta/1", 100)  # Flask com threads
testar_servidor(8080, "/lenta/1", 100)  # Actix com async
```

## 🤔 Quando Usar Threads vs Async/Await em Rust

### Threads São Ideais Para:
- **Trabalho CPU-bound** que pode ser paralelizado
- **Operações bloqueantes** que não têm suporte async
- **Código simples** onde o overhead do async não se justifica

### Async/Await É Ideal Para:
- **Operações I/O-bound** (rede, arquivos, banco de dados)
- **Servidores** que precisam lidar com muitas conexões
- **Operações não-bloqueantes** onde a eficiência é crítica

### Paralelismo de Dados com `rayon`

Para trabalho CPU-bound que envolve processar coleções e iteradores, a crate [`rayon`](https://crates.io/crates/rayon) é uma ferramenta fantástica e muito popular. Ela oferece paralelismo quase automático — basta trocar `.iter()` por `.par_iter()`:

```rust
// Cargo.toml: rayon = "1"
use rayon::prelude::*;

fn main() {
    let data = vec!;[1][2]

    // Processa cada elemento em paralelo entre todos os núcleos disponíveis!
    let resultados: Vec<_> = data.par_iter().map(|x| x * x).collect();
    println!("{:?}", resultados); //[1]
}
```

Para Pythonistas, isso é comparável a usar `multiprocessing.Pool` com `map`, mas com uma API muito mais ergonômica e sem o overhead de processos separados.

### Comparação de Performance

| Cenário | Python (Threads) | Python (Async) | Rust (Threads) | Rust (Async) |
|---------|------------------|----------------|----------------|--------------|
| CPU-bound | ⚠️ Com multiprocessing | ❌ Não aplicável | ⭐⭐ Excelente | ❌ Não aplicável |
| I/O-bound (1000 conexões) | ⚠️ Consome muitos recursos | ⭐ Bom | ⭐⭐ Excelente | ⭐⭐⭐ Excelente+ |
| Simplicidade | ⭐⭐ Fácil | ⚠️ Complexo | ⭐⭐ Moderado | ⚠️ Complexo |

## ⚠️ Erros Comuns de Pythonistas em Rust

### 1. Tentar Usar Threads para Tudo Como no Python

```rust
// ❌ Errado: Criar threads demais como faria em Python
for _ in 0..1000 {
    thread::spawn(|| { /* ... */ }); // Consome muitos recursos
}

// ✅ Correto: Usar async para I/O ou thread pool para CPU
let pool = ThreadPool::new(4); // Pool com número fixo de threads
for _ in 0..1000 {
    pool.execute(|| { /* ... */ });
}
```

### 2. Esquecer de `.await` em Funções Async

```rust
// ❌ Errado: Esquecer o .await
async fn processar_dados() {
    buscar_dados(); // Esqueceu .await - não executa!
}

// ✅ Correto: Usar .await
async fn processar_dados() {
    buscar_dados().await; // Executa corretamente
}
```

### 3. Bloquear Threads de Execução com Operações CPU-intensivas

```rust
// ❌ Errado: Trabalho CPU-intensive em contexto async
async fn rota_lenta() {
    trabalho_pesado_cpu(); // Bloqueia o executor!
}

// ✅ Correto: Mover trabalho CPU-intensive para thread dedicado
async fn rota_lenta() {
    let resultado = tokio::task::spawn_blocking(|| {
        trabalho_pesado_cpu() // Executa em thread separado
    }).await.unwrap();
    // ... resto async
}
```

## 🎯 Conclusão: Por Que Rust Brilha em Concorrência

Rust oferece o melhor dos dois mundos: a segurança de memória que previne erros concorrentes comuns e o desempenho que permite tirar máximo proveito do hardware moderno.

Para Pythonistas, aprender Rust significa:
- Entender como a concorrência pode ser segura por padrão
- Aprender a pensar em termos de ownership e borrowing
- Descobrir que async/await pode ser mais eficiente que threads tradicionais
- Ganhar habilidades para escrever sistemas concorrentes mais robustos

Em termos filosóficos, as duas linguagens representam trade-offs conscientes: Rust exige mais *upfront* — tipos explícitos, gerenciamento de ownership e um compilador rigoroso — para garantir segurança máxima e performance previsível. Python oferece mais facilidade inicial com tipagem dinâmica e o GIL como rede de segurança, mas esses atalhos têm um custo em performance e em race conditions que só aparecem em produção. Conhecer Rust muda a forma como você programa em qualquer linguagem.

## 📚 O Que Aprendemos

- **Threads em Rust** são seguras graças ao sistema de tipos e traits `Send`/`Sync`
- **Async/Await em Rust** é implementado através de bibliotecas como tokio e oferece alta eficiência para I/O
- **O GIL do Python** limita a verdadeira paralelização com threads, enquanto Rust escala linearmente
- **Threads são ideais** para trabalho CPU-bound, enquanto **async é melhor** para I/O-bound
- **`rayon`** é a ferramenta certa para paralelismo de dados em coleções com mínima mudança de código
- **Erros comuns** incluem criar threads demais, esquecer await calls e bloquear o executor com código CPU-intensivo

A jornada de aprendizado de concorrência em Rust é recompensadora e transformará como você pensa sobre programação paralela, mesmo quando voltar ao Python.

Quer se aprofundar ainda mais? Confira o livro completo **"Desbravando Rust"** em https://desbravandorust.com.br para dominar todos esses conceitos com exemplos práticos e exercícios!
