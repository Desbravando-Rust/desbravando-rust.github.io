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
    for _ in 0..100000 {
        counter += 1;  // ERRO: closure pode outlive a variável
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

Em Rust, precisamos usar tipos seguros para compartilhamento:

```rust
// Rust: Compartilhamento seguro com Arc<Mutex<T>>
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    // Arc = Atomic Reference Counter (compartilhamento entre threads)
    // Mutex = MUTual EXclusion (acesso exclusivo)
    let counter = Arc::new(Mutex::new(0));
    let mut handles = vec![];

    for _ in 0..10 {
        let counter = Arc::clone(&counter);
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
- `Send`: Permite que dados sejam movidos entre threads
- `Sync`: Permite que dados sejam compartilhados entre threads por referência

Esses traits são automaticamente implementados quando é seguro fazê-lo, e o compilador valida isso para você.

## ⚡ Seção 2: Async/Await em Rust - Performance sem Bloqueio

### O Paradigma Assíncrono

Assincronicidade em Rust é diferente do Python: não há GIL e as tarefas podem executar verdadeiramente em paralelo quando há múltiplos núcleos disponíveis.

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

Em Rust, async/await é mais sobre concorrência do que paralelismo:

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
    // Executa as tarefas concorrentemente (não necessariamente em paralelo)
    let tarefa1 = tarefa_lenta("Tarefa 1", 2);
    let tarefa2 = tarefa_lenta("Tarefa 2", 1);
    let tarefa3 = tarefa_lenta("Tarefa 3", 3);
    
    // Aguarda todas as tarefas completarem
    futures::join!(tarefa1, tarefa2, tarefa3);
}
```

### Runtime vs Biblioteca

Uma diferença fundamental: Python tem um runtime built-in para async (asyncio), enquanto Rust usa bibliotecas externas (tokio, async-std):

- **Python**: `asyncio` é parte da biblioteca padrão
- **Rust**: Você escolhe seu runtime (tokio é o mais popular)

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

# Usando threads para trabalho CPU-bound (não funciona bem por causa do GIL)
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
    responses = await asyncio.gather(*tasks)
    return len(responses)
```

```rust
// Rust: I/O-bound com async (eficiente)
use reqwest;
use tokio;

async fn fetch(url: &str) -> Result<String, reqwest::Error> {
    reqwest::get(url).await?.text().await
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let urls = vec!["http://httpbin.org/get"; 10];
    let mut tasks = vec![];
    
    for url in urls {
        tasks.push(tokio::spawn(async move {
            fetch(url).await
        }));
    }
    
    let results = futures::future::join_all(tasks).await;
    println!("Total de respostas: {}", results.len());
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
use actix_web::{get, App, HttpServer, HttpResponse};
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

Vamos testar ambos os servidores com requisições concorrentes:

```python
# Python: Teste de carga para os servidores
import requests
import threading
import time

def testar_servidor(porta, url, num_requisicoes):
    inicio = time.time()
    
    def fazer_requisicao(_):
        return requests.get(f"http://localhost:{porta}{url}").status_code
    
    # Usando threads para requests concorrentes
    with ThreadPoolExecutor(max_workers=100) as executor:
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

### 2. Esquecer de .await em Funções Async
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
    // ... resto async
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

## 📚 O Que Aprendemos

- **Threads em Rust** são seguras graças ao sistema de tipos e traits `Send`/`Sync`
- **Async/Await em Rust** é implementado através de bibliotecas como tokio e oferece alta eficiência para I/O
- **O GIL do Python** limita a verdadeira paralelização com threads, enquanto Rust escala linearmente
- **Threads são ideais** para trabalho CPU-bound, enquanto **async é melhor** para I/O-bound
- **Erros comuns** incluem criar threads demais e esquecer await calls

A jornada de aprendizado de concorrência em Rust é recompensadora e transformará como você pensa sobre programação paralela, mesmo quando voltar ao Python.

Quer se aprofundar ainda mais? Confira o livro completo **"Desbravando Rust"** em https://desbravando-rust.github.io para dominar todos esses conceitos com exemplos práticos e exercícios!