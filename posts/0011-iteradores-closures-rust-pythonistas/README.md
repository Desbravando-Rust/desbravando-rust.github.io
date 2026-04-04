# Desvendando Iteradores e Closures em Rust: A Potência Funcional para Pythonistas

Se você vem do Python e está começando sua jornada em Rust, provavelmente já percebeu que ambas as linguagens possuem recursos poderosos para programação funcional. No entanto, as semelhanças superficiais escondem diferenças profundas que são cruciais para entender como Rust oferece segurança de memória e desempenho superior.

Neste artigo, vamos explorar como closures e iteradores funcionam em Rust, comparando constantemente com as abordagens do Python. Você descobrirá como Rust implementa esses conceitos de forma única, proporcionando tanto flexibilidade quanto segurança em tempo de compilação.

## 🧠 Por Que Closures e Iteradores São Fundamentais?

Tanto em Python quanto em Rust, closures e iteradores são pilares da programação funcional. Eles permitem:
- Escrever código mais conciso e expressivo
- Manipular coleções de dados de forma elegante
- Criar abstrações poderosas com pouco código

Mas enquanto Python prioriza flexibilidade e legibilidade, Rust adiciona uma camada de segurança e eficiência que previne erros comuns em tempo de compilação.

Vamos começar nossa jornada entendendo as closures, uma das construções mais interessantes em Rust!

## 🔗 Seção 1: Entendendo Closures em Rust

### O Que São Closures?

Closures são funções anônimas que podem capturar variáveis do seu ambiente circundante. Se você já usou `lambda` em Python, já trabalhou com closures!

**Python:**
```python
# Closure simples em Python
def multiplicador_por(n):
    def multiplicador(x):
        return x * n
    return multiplicador

dobro = multiplicador_por(2)
print(dobro(5))  # Output: 10
```

**Rust:**
```rust
// Closure simples em Rust
fn main() {
    let multiplicador_por = |n| {
        move |x| x * n
    };
    
    let dobro = multiplicador_por(2);
    println!("{}", dobro(5));  // Output: 10
}
```

Note a palavra-chave `move` no exemplo Rust. Ela indica que a closure vai "tomar posse" (ownership) da variável `n`. Essa é uma das diferenças fundamentais entre as duas linguagens!

### Os Três Traits de Closures: Fn, FnMut e FnOnce

Em Rust, closures são classificadas em três tipos baseados em como capturam variáveis:

1. **Fn**: Apenas empresta variáveis (read-only)
2. **FnMut**: Empresta variáveis mutavelmente (pode modificá-las)
3. **FnOnce**: Toma posse das variáveis (pode usá-las apenas uma vez)

Vamos ver exemplos práticos:

```rust
fn main() {
    let valor = 10;
    
    // Fn: apenas empresta 'valor'
    let closure_fn = || println!("Valor: {}", valor);
    closure_fn();
    closure_fn();  // Pode ser chamada múltiplas vezes
    
    // FnMut: empresta 'valor' mutavelmente
    let mut valor_mut = 10;
    let mut closure_fnmut = || {
        valor_mut += 1;
        println!("Valor mut: {}", valor_mut);
    };
    closure_fnmut();
    closure_fnmut();
    
    // FnOnce: toma posse de 'valor'
    let valor_once = String::from("Hello");
    let closure_fnonce = || {
        println!("Valor: {}", valor_once);
        // valor_once é consumido aqui
    };
    closure_fnonce();
    // closure_fnonce();  // Erro! Não pode ser chamada novamente
}
```

### Captura de Variáveis: As Diferenças Cruciais

Aqui está onde Rust brilha em comparação com Python. Enquanto Python usa referências e garbage collection, Rust exige que você seja explícito sobre como as variáveis são capturadas.

**Python (com comportamento potencialmente problemático):**
```python
def criar_closures():
    closures = []
    for i in range(3):
        closures.append(lambda: print(f"Valor: {i}"))
    return closures

# Todas as closures imprimem "Valor: 2"!
for closure in criar_closures():
    closure()
```

**Rust (comportamento correto por padrão):**
```rust
fn criar_closures() -> Vec<Box<dyn Fn()>> {
    let mut closures = Vec::new();
    for i in 0..3 {
        closures.push(Box::new(move || println!("Valor: {}", i)));
    }
    closures
}

fn main() {
    // Cada closure tem sua própria cópia de i
    for closure in criar_closures() {
        closure();  // Imprime 0, 1, 2
    }
}
```

Rust força você a pensar sobre ownership desde o início, prevenindo erros sutis que são comuns em Python!

## 🔄 Seção 2: Dominando Iteradores em Rust

### FromIterator e IntoIterator: A Magia Por Trás dos Iteradores

Em Rust, iteradores são lazy por padrão - eles não fazem nada até que você os consuma. Isso é diferente do Python, onde muitas operações são eager (executadas imediatamente).

Os dois traits mais importantes são:
- **IntoIterator**: Converte algo em um iterador
- **FromIterator**: Constrói uma coleção a partir de um iterador

Vamos ver como isso funciona na prática:

```rust
fn main() {
    let numeros = vec![1, 2, 3, 4, 5];
    
    // IntoIterator: converte Vec em iterador
    let iterador = numeros.into_iter();
    
    // FromIterator: converte iterador de volta para Vec
    let novos_numeros: Vec<_> = iterador.collect();
    println!("{:?}", novos_numeros);
}
```

### As Poderosas Adaptações: map, filter, collect

Aqui está onde a programação funcional realmente brilha em Rust! Vamos comparar com Python:

**Python (eager evaluation):**
```python
# Python: operações são aplicadas imediatamente
numeros = [1, 2, 3, 4, 5]
resultado = [x * 2 for x in numeros if x % 2 == 0]
print(resultado)  # [4, 8]
```

**Rust (lazy evaluation):**
```rust
fn main() {
    let numeros = vec![1, 2, 3, 4, 5];
    
    // Rust: operações são lazy, só executam quando consumidas
    let resultado: Vec<_> = numeros
        .into_iter()
        .filter(|x| x % 2 == 0)
        .map(|x| x * 2)
        .collect();
    
    println!("{:?}", resultado);  // [4, 8]
}
```

A beleza da abordagem Rust é que o compilador pode otimizar toda a cadeia de operações sem alocações intermediárias desnecessárias!

### Exemplo Prático: Processando Dados de Sensor

Vamos criar um exemplo mais complexo e realista:

```rust
struct LeituraSensor {
    valor: f64,
    timestamp: i64,
    valida: bool,
}

fn processar_leitura(leituras: Vec<LeituraSensor>) -> Vec<(i64, f64)> {
    leituras
        .into_iter()
        .filter(|leitura| leitura.valida)  // Filtra leituras válidas
        .filter(|leitura| leitura.valor >= 0.0)  // Valores não-negativos
        .map(|leitura| (leitura.timestamp, leitura.valor * 1.5))  // Transforma
        .filter(|(_, valor)| *valor <= 100.0)  // Remove valores excessivos
        .collect()  // Coleta em Vec
}

fn main() {
    let leituras = vec![
        LeituraSensor { valor: 25.5, timestamp: 1000, valida: true },
        LeituraSensor { valor: -5.0, timestamp: 1001, valida: true },
        LeituraSensor { valor: 75.0, timestamp: 1002, valida: false },
        LeituraSensor { valor: 150.0, timestamp: 1003, valida: true },
    ];
    
    let resultado = processar_leitura(leituras);
    println!("{:?}", resultado);  // [(1000, 38.25)]
}
```

Este exemplo mostra como Rust permite criar pipelines de processamento de dados claros, seguros e eficientes!

## ⚡ Seção 3: Lazy Evaluation vs Eager Evaluation

### A Filosofia de Cada Linguagem

**Python (Eager):**
- Operações são executadas imediatamente
- Mais fácil de depurar (você vê resultados intermediários)
- Pode consumir mais memória (cria listas intermediárias)

**Rust (Lazy):**
- Operações só acontecem quando os resultados são realmente necessários
- Permite otimizações poderosas (fusão de iteradores, eliminação de alocações)
- Mais eficiente em termos de memória e desempenho

### Exemplo de Performance

Vamos comparar o processamento de grandes conjuntos de dados:

**Python (com list comprehensions):**
```python
# Python: cria 3 listas intermediárias na memória
import time

dados = list(range(1_000_000))

inicio = time.time()
resultado = [x * 2 for x in dados if x % 3 == 0]
fim = time.time()

print(f"Tempo: {(fim - inicio):.4f}s")
print(f"Tamanho do resultado: {len(resultado)}")
```

**Rust (com iteradores lazy):**
```rust
// Rust: não cria coleções intermediárias
use std::time::Instant;

fn main() {
    let dados: Vec<_> = (1..1_000_000).collect();
    
    let inicio = Instant::now();
    let resultado: Vec<_> = dados
        .into_iter()
        .filter(|x| x % 3 == 0)
        .map(|x| x * 2)
        .collect();
    let duracao = inicio.elapsed();
    
    println!("Tempo: {:.4?}s", duracao);
    println!("Tamanho do resultado: {}", resultado.len());
}
```

Em benchmarks, a versão Rust geralmente é 2-3x mais rápida e consome significativamente menos memória!

## 🐍 Comparação com Python: Quando Cada Abordagem Brilha

### List Comprehensions vs Iteradores Rust

**Python (list/dict/set comprehensions):**
```python
# Python é excelente para expressões concisas
quadrados_pares = [x**2 for x in range(10) if x % 2 == 0]
dicionario = {x: x**2 for x in range(5)}
conjunto = {x for x in "abracadabra" if x not in "abc"}
```

**Rust (iteradores):**
```rust
// Rust é mais explícito mas igualmente poderoso
let quadrados_pares: Vec<_> = (0..10)
    .filter(|x| x % 2 == 0)
    .map(|x| x.pow(2))
    .collect();

let dicionario: std::collections::HashMap<_, _> = (0..5)
    .map(|x| (x, x.pow(2)))
    .collect();

let conjunto: std::collections::HashSet<_> = "abracadabra"
    .chars()
    .filter(|c| !"abc".contains(*c))
    .collect();
```

### Generators Python vs Iteradores Rust

**Python (generators):**
```python
# Generator expression (lazy)
quadrados = (x**2 for x in range(1000000))
soma = sum(quadrados)  # Consome o generator
```

**Rust (iteradores):**
```rust
// Iteradores Rust são sempre lazy
let quadrados = (0..1_000_000).map(|x| x.pow(2));
let soma: i64 = quadrados.sum();  // Consome o iterador
```

### Erros Comuns de Pythonistas em Rust

1. **Esquecer o `collect()`:**
```rust
// ERRO: Iteradores são lazy, então isso não faz nada!
let resultado = vec![1, 2, 3].iter().map(|x| x * 2);
// CORRETO: 
let resultado: Vec<_> = vec![1, 2, 3].iter().map(|x| x * 2).collect();
```

2. **Problemas de ownership em closures:**
```rust
// ERRO: Tentar usar variável após mover para closure
let dados = vec![1, 2, 3];
let closure = move || println!("{:?}", dados);
println!("{:?}", dados);  // Erro! dados foi movido
```

3. **Confusão entre `iter()`, `into_iter()`, `iter_mut()`:**
```rust
let mut numeros = vec![1, 2, 3];

// iter(): empréstimo imutável
for n in numeros.iter() { /* pode ler n */ }

// iter_mut(): empréstimo mutável  
for n in numeros.iter_mut() { /* pode modificar n */ }

// into_iter(): posse (consome o vetor)
for n in numeros.into_iter() { /* n é dono do valor */ }
```

## 🚀 Conclusão: Por Que Rust Vale a Pena para Programação Funcional

Rust oferece o melhor dos dois mundos: a expressividade da programação funcional combinada com o desempenho e segurança de sistemas. 

**Use Rust quando:**
- Você precisa de máximo desempenho e eficiência de memória
- A segurança contra erros é crítica (sistemas concorrentes, código de longa duração)
- Você está trabalhando com grandes volumes de dados

**Use Python quando:**
- A velocidade de desenvolvimento é prioridade
- Você está prototipando ou explorando dados
- O código não é performance-critical

## 🎯 O Que Aprendemos

- **Closures Rust** são mais poderosas e seguras que as do Python, com sistema explícito de ownership
- **Iteradores Rust** são lazy por padrão, permitindo otimizações poderosas
- **Traits Fn, FnMut, FnOnce** definem como closures capturam variáveis
- **Lazy evaluation** em Rust é mais eficiente que eager evaluation do Python
- **Erros comuns** de Pythonistas podem ser evitados entendendo ownership

Iteradores e closures são apenas parte do que torna Rust especial. Se você quer dominar completamente a linguagem e desbloquear todo seu potencial, o livro "Desbravando Rust" tem muito mais a oferecer!

📚 [Adquira já seu exemplar de "Desbravando Rust" para se tornar um expert!](https://desbravandorust.com.br)

Nos próximos artigos, continuaremos explorando recursos avançados de Rust. Até lá, continue praticando e compartilhando suas descobertas! 🦀