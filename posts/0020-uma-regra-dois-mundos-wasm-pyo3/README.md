# Uma regra, dois mundos: a mesma lógica no front-end e no Python via Rust + WASM
###### Por [@zejuniortdr](https://github.com/zejuniortdr/) em Jul 27, 2026

![Cover](imgs/cover.png)


Escreva uma regra de negócio **uma única vez** em Rust e rode-a idêntica no navegador do usuário (via WASM) e no seu back-end Python (via PyO3): a mesma validação de CPF, o mesmo cálculo de desconto, sem reimplementar a lógica em duas linguagens.

Esta é a última parada de uma jornada que começou [acelerando um endpoint](../0001-performance-na-pratica), passou por [trocar o worker de tarefas por Rust](../0018-apaguei-meu-celery-worker-rust-django) e chegou a [segurar um milhão de conexões](../0019-um-milhao-websockets-python-rust). Agora vamos ao truque mais ambicioso de todos — e talvez o mais subestimado.

Sem duplicação. Sem "validou no front mas o back recusou". Uma fonte da verdade, dois destinos de compilação.

## O problema real

Toda aplicação web séria reimplementa a mesma regra duas vezes. A validação de um CPF, o cálculo de um desconto, a regra de elegibilidade de um pedido — escritas em JavaScript para dar feedback rápido no front, e **de novo** em Python para garantir no back-end.

E aí mora o bug mais frustrante que existe:

1. O front valida com uma regra.
2. O back valida com outra (que deveria ser igual, mas divergiu numa atualização).
3. O usuário preenche tudo certo segundo o front, clica em enviar, e leva um `422` do back-end.

São **duas implementações da mesma regra que inevitavelmente derivam** uma da outra com o tempo. Cada correção precisa ser feita em dois lugares, em duas linguagens, por (às vezes) dois times.

```python
# back-end (Python) — uma versão da regra
def desconto_valido(valor: float, cupom: str) -> bool:
    return valor >= 50.0 and cupom.startswith("PROMO")
```

```javascript
// front-end (JS) — a "mesma" regra, escrita de novo... e já divergindo
function descontoValido(valor, cupom) {
  return valor > 50 && cupom.startsWith("PROMO"); // > em vez de >= — bug sutil!
}
```

Achou o bug? `>=` virou `>`. Em produção isso é um chamado de suporte que ninguém consegue reproduzir.

## A ideia: escreva uma vez, compile para dois alvos

Rust compila tanto para **WebAssembly** (que roda no navegador) quanto para uma **extensão nativa de Python** (via PyO3, como nos posts anteriores). Então escrevemos a regra **uma vez**, num crate puro, e geramos os dois artefatos a partir dela.

```
                  ┌────────────────────────┐
                  │   regra de negócio      │
                  │   (crate Rust puro)     │
                  └───────────┬─────────────┘
                  wasm-pack    │    maturin
              ┌────────────────┴────────────────┐
              ▼                                  ▼
   ┌────────────────────┐            ┌────────────────────┐
   │  WASM no navegador │            │  wheel no Python   │
   │  (front-end)       │            │  (back-end)        │
   └────────────────────┘            └────────────────────┘
```

### 1. O núcleo: a regra, escrita uma vez

```rust
// src/lib.rs — lógica pura, sem dependência de navegador nem de Python
pub fn desconto_valido(valor: f64, cupom: &str) -> bool {
    valor >= 50.0 && cupom.starts_with("PROMO")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn regra_de_desconto() {
        assert!(desconto_valido(50.0, "PROMO10"));   // limite exato
        assert!(!desconto_valido(49.99, "PROMO10")); // abaixo do mínimo
        assert!(!desconto_valido(80.0, "DESCONTO")); // cupom errado
    }
}
```

Os testes rodam uma vez e cobrem **os dois mundos**. Se a regra está certa aqui, está certa no front e no back — porque é literalmente o mesmo código compilado.

### 2. Alvo navegador: expor para WASM

```rust
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn desconto_valido_js(valor: f64, cupom: &str) -> bool {
    crate::desconto_valido(valor, cupom)
}
```

```bash
wasm-pack build --target web
```

```javascript
// front-end — agora chama a MESMA regra do back-end
import init, { desconto_valido_js } from "./pkg/regras.js";

await init();
if (desconto_valido_js(valor, cupom)) {
  habilitarBotao();
}
```

### 3. Alvo Python: expor para PyO3

```rust
use pyo3::prelude::*;

#[pyfunction]
fn desconto_valido_py(valor: f64, cupom: &str) -> bool {
    crate::desconto_valido(valor, cupom)
}

#[pymodule]
fn regras(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(desconto_valido_py, m)?)?;
    Ok(())
}
```

```bash
maturin develop --release
```

```python
# back-end — a MESMA regra, byte por byte
from regras import desconto_valido_py

if not desconto_valido_py(valor, cupom):
    raise HTTPException(status_code=422, detail="Desconto inválido")
```

Agora aquele bug do `>` vs `>=` é **impossível por construção**. Não existem duas implementações para divergir — existe uma só, em dois invólucros finos.

## O que você ganha

| Antes (duas implementações) | Depois (uma regra, Rust) |
| --- | --- |
| Regra escrita em JS e em Python | Escrita uma vez em Rust |
| Divergência silenciosa com o tempo | Impossível divergir: mesmo binário lógico |
| Bug corrigido em 2 lugares | Corrigido em 1 lugar |
| Testada (talvez) nos 2 lados | Um conjunto de testes cobre os 2 alvos |
| Front em ms, back validando de novo | Front em WASM nativo, back em extensão C |

![Uma fonte de verdade alimentando front e back](imgs/benchmark.png)

E como bônus de performance: no navegador, WASM roda perto da velocidade nativa (muito mais rápido que validar regra complexa em JS interpretado); no back, é uma extensão compilada, sem o overhead do Python puro — exatamente a tese dos posts anteriores.

## Custos de tamanho e build

Honestidade sobre os números reais:

| Métrica | Valor típico |
| --- | ---: |
| Bundle WASM (regra simples, otimizado + gzip) | ~25–60KB |
| Tempo de build dos dois alvos | poucos segundos |
| Runtime extra no Python | wheel pré-compilado, zero Rust no cliente |

Os valores variam com o tamanho da regra e dependências, mas para lógica de negócio (validações, cálculos, elegibilidade) o WASM gerado é pequeno o bastante para não pesar no carregamento da página.

## Quando isso vale — e quando é overkill

**Vale muito quando:**

1. A regra é **crítica e compartilhada** (fiscal, financeira, de elegibilidade) e divergência custa caro.
2. A regra é **complexa o suficiente** para que reimplementá-la em duas linguagens seja arriscado.
3. Você já tem afinidade com Rust no time (os posts anteriores ajudaram nisso 😉).

**É overkill quando:**

1. A regra é um `if` trivial que nunca muda — duplicar custa menos que o setup.
2. O time não tem nenhum contato com Rust e a regra é simples.
3. O front e o back já compartilham linguagem (ex.: um BFF em Python) — aí o problema nem existe.

A complexidade do build (dois pipelines, dois empacotadores) é real. Você troca "duas implementações de regra" por "um pipeline de build a mais". Para regras críticas, é uma troca excelente. Para um `valor > 0`, não.

## Checklist de adoção

1. Comece por **uma** regra de alto valor e alto risco de divergência.
2. Escreva os testes no crate Rust — eles passam a ser a especificação executável da regra.
3. Automatize os dois builds (`wasm-pack` e `maturin`) no CI, publicando os dois artefatos juntos.
4. Versione o pacote: front e back devem consumir a **mesma versão** da regra.
5. Meça o tamanho do bundle WASM no front e trate como orçamento de performance.

## O fim da jornada

Ao longo desta sequência, o Rust apareceu em quatro papéis diferentes na sua stack Python: como **lente** que revela o custo escondido do ORM, como **motor** que substitui o worker de tarefas, como **borda** que segura escala impossível, e agora como **fonte única de verdade** que atravessa a fronteira entre navegador e servidor.

O fio condutor sempre foi o mesmo: você não precisa abandonar o Python para colher o que o Rust oferece. Precisa saber **onde** ele entra. Da regra fiscal ao milhão de conexões, da fila de tarefas à lógica compartilhada — o padrão é colocar Rust exatamente no ponto onde a sua stack mais dói, e deixar o Python brilhar em todo o resto.

E é exatamente esse mapa — onde, como e por que — que eu detalho com calma, do zero, no livro.

---

Quer se aprofundar em Rust de forma prática, aplicada ao mundo real e com foco em performance? Conheça o livro em [desbravandorust.com.br](https://desbravandorust.com.br).
