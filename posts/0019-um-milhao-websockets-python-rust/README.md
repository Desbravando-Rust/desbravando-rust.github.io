# 1 milhão de conexões WebSocket: o teto do Python e o chão do Rust
###### Por [@zejuniortdr](https://github.com/zejuniortdr/) em Jul 20, 2026

![Cover](imgs/cover.png)


No [primeiro post deste blog](../0001-performance-na-pratica) eu mostrei o Axum superando o FastAPI numa rota HTTP. A reação mais comum foi: "ok, mas a diferença em request/response não muda minha vida". Justo. Então hoje eu vou para o terreno onde a diferença deixa de ser conforto e vira **teto**: conexões persistentes.

Chat, notificações em tempo real, dashboards ao vivo, feeds de cotação, presença online — tudo isso são WebSockets que ficam **abertos**. E o problema de manter conexões abertas é radicalmente diferente do problema de responder requisições. É aqui que o Python encontra uma parede e o Rust ainda está confortável.

## O problema real

O custo de uma conexão WebSocket não está em processá-la — está em **mantê-la viva** enquanto ela não faz nada. Cada conexão ociosa custa memória. E o problema clássico de servidores, o "C10k" (10 mil conexões simultâneas), virou "C1M" — um milhão — em aplicações realtime modernas.

O gargalo aparece em duas frentes:

1. **Memória por conexão:** cada conexão carrega buffers e estado. Multiplique por um milhão.
2. **Modelo de concorrência:** segurar um milhão de conexões exige que "esperar" seja barato. Em Python, cada conexão no event loop carrega o overhead de uma coroutine pesada; em Rust, é uma `task` de poucos KB.

## O servidor de eco em cada linguagem

Vamos comparar o exemplo mínimo e honesto: um echo server WebSocket.

### Python — FastAPI + uvicorn

```python
# app.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            msg = await websocket.receive_text()
            await websocket.send_text(msg)
    except WebSocketDisconnect:
        pass
```

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

Código limpo, idiomático, funciona lindamente — até a carga crescer.

### Rust — Axum + tokio

```rust
use axum::{
    extract::ws::{Message, WebSocket, WebSocketUpgrade},
    response::Response,
    routing::get,
    Router,
};

#[tokio::main]
async fn main() {
    let app = Router::new().route("/ws", get(handler));
    let listener = tokio::net::TcpListener::bind("0.0.0.0:8000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

async fn handler(ws: WebSocketUpgrade) -> Response {
    ws.on_upgrade(eco)
}

async fn eco(mut socket: WebSocket) {
    // Cada conexão é uma task tokio de poucos KB. Um milhão delas cabe na RAM.
    while let Some(Ok(msg)) = socket.recv().await {
        if let Message::Text(texto) = msg {
            if socket.send(Message::Text(texto)).await.is_err() {
                break;
            }
        }
    }
}
```

A diferença não está na clareza do código — os dois são legíveis. Está no que acontece quando você abre a centésima milésima conexão.

## O teste de carga

Subimos cada servidor numa máquina com 8GB de RAM e abrimos conexões WebSocket ociosas (apenas mantidas vivas com ping periódico), medindo até a degradação. Depois, com 50k conexões ativas, disparamos um broadcast e medimos a latência P99.

**Conexões ociosas até saturar 8GB**

| Servidor | Conexões antes de degradar | RAM por conexão (aprox.) |
| --- | ---: | ---: |
| FastAPI + uvicorn | ~48.000 | ~46KB |
| Axum + tokio | **~1.000.000+** | **~2,4KB** |

![Conexões simultâneas e memória por conexão: FastAPI vs Axum](imgs/benchmark.png)

**Latência de broadcast com 50k conexões ativas**

| Servidor | P50 | P99 |
| --- | ---: | ---: |
| FastAPI + uvicorn | 180ms | 1.240ms |
| Axum + tokio | **9ms** | **38ms** |

Os números variam com kernel, limites de file descriptor (`ulimit -n`), tamanho de buffer e o que cada conexão realmente faz. Mas a ordem de grandeza é estrutural: **~20x mais conexões por GB** e latência de broadcast uma ordem de grandeza menor sob a mesma carga.

> Importante: o FastAPI não está "quebrado". Ele foi feito para um modelo onde conexões são curtas. WebSocket em altíssima escala simplesmente não é o jogo para o qual o stack Python foi otimizado.

## Por que o Rust segura isso

1. **Tasks são baratíssimas.** Uma task tokio ociosa custa poucos KB; uma coroutine Python esperando num event loop custa muito mais, e o interpretador soma overhead por cima.
2. **Sem GIL no caminho.** O agendamento das conexões distribui por várias threads do SO sem disputa de lock global.
3. **Memória previsível.** Sem garbage collector pausando o mundo, a latência de broadcast não tem picos misteriosos sob pressão de memória.

## A arquitetura que eu recomendo de verdade

A lição **não** é "reescreva seu chat inteiro em Rust". É colocar o Rust na **borda de tempo real**, onde a escala dói, e deixar o Python cuidar do que ele faz bem: a regra de negócio.

```
                      ┌────────────────────┐
   1M clientes  ───►  │  Gateway realtime  │  ◄── Axum/tokio
   (WebSocket)        │   (Rust)           │      segura as conexões
                      └─────────┬──────────┘
                                │ HTTP/eventos só quando precisa
                      ┌─────────▼──────────┐
                      │   Django / FastAPI │  ◄── regra de negócio,
                      │   (Python)         │      auth, persistência
                      └────────────────────┘
```

O gateway Rust mantém o milhão de conexões e faz fan-out de mensagens. O Python continua sendo o cérebro do produto, chamado só quando há trabalho real a fazer. Cada linguagem na função em que é imbatível.

## Contraponto honesto

1. Se a sua aplicação tem 500 conexões simultâneas, **nada disso importa** — fique no Python e seja feliz.
2. O ecossistema Python de WebSocket (Django Channels, Socket.IO) entrega produtividade e integração que um gateway Rust caseiro não tem de graça.
3. Operar um serviço Rust adicional é custo de complexidade real. Só vale quando a escala justifica.

O ponto não é que o Python é ruim. É que existe um teto — e quando você bate nele, jogar mais réplica Python no problema fica caro rápido, enquanto o chão do Rust ainda está muito abaixo dos seus pés.

## Checklist para um gateway realtime em produção

1. Ajuste limites do SO: `ulimit -n` (file descriptors) e parâmetros de `tcp` do kernel.
2. Defina protocolo de heartbeat/ping para detectar conexões mortas sem custo alto.
3. Faça backpressure: cliente lento não pode segurar memória do servidor indefinidamente.
4. Meça memória por conexão com carga real, não com echo trivial.
5. Tenha um plano de reconexão no cliente — em escala, conexões caem o tempo todo.

## O que esse caso ensina

Throughput de request/response é uma conversa. Conexões persistentes em escala é outra completamente diferente — e é onde a arquitetura de concorrência do Rust deixa de ser "mais rápida" e passa a ser "possível". O Python te leva longe; o Rust te leva até onde o Python não alcança.

No próximo e último post desta sequência, eu fecho com a ideia mais ambiciosa de todas: escrever uma regra de negócio **uma única vez** e rodá-la igual no navegador e no seu back-end Python. Mesma lógica, dois mundos.

---

Quer se aprofundar em Rust de forma prática, aplicada ao mundo real e com foco em performance? Conheça o livro em [desbravandorust.com.br](https://desbravandorust.com.br).
