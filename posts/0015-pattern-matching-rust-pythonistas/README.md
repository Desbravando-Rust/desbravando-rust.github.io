# Desvendando Pattern Matching em Rust: Um Guia Prático para Pythonistas
###### Por [@zejuniortdr](https://github.com/zejuniortdr/) em Mai 16, 2026

![Desvendando Pattern Matching em Rust: Um Guia Prático para Pythonistas](imgs/cover.png)

Se você vem do Python, está acostumado com estruturas condicionais como `if-elif-else` para controlar o fluxo do programa. Mas e se eu te disser que Rust possui uma ferramenta muito mais poderosa chamada **pattern matching**? Vamos explorar como essa funcionalidade revolucionária pode transformar sua maneira de escrever código.

## Introdução: O Que é Pattern Matching?

Em Python, quando precisamos verificar múltiplas condições, geralmente escrevemos uma cadeia de `if-elif-else`. Funciona, mas pode ficar verboso e difícil de manter. Rust oferece o `match`, uma estrutura que permite comparar um valor contra uma série de padrões de forma limpa e expressiva.

```python
# Python - abordagem tradicional
status = 404
if status == 200:
    print("OK")
elif status == 404:
    print("Não encontrado")
else:
    print("Erro desconhecido")
```

```rust
// Rust - pattern matching
let status = 404;
match status {
    200 => println!("OK"),
    404 => println!("Não encontrado"),
    _ => println!("Erro desconhecido"),
}
```

Note como o `match` do Rust é mais declarativo e menos propenso a erros do que a cadeia de `if-elif-else` do Python.

## Seção 1: `match` vs `if-elif-else` - Comparação Lado a Lado

### Exemplo Prático: Classificação de Números

Vamos resolver o mesmo problema nas duas linguagens: classificar um número como positivo, negativo ou zero.

```python
# Python
numero = 5
if numero > 0:
    print("Positivo")
elif numero < 0:
    print("Negativo")
else:
    print("Zero")
```

```rust
// Rust
let numero = 5;
match numero.cmp(&0) {
    std::cmp::Ordering::Greater => println!("Positivo"),
    std::cmp::Ordering::Less => println!("Negativo"),
    std::cmp::Ordering::Equal => println!("Zero"),
}
```

**Vantagem do Rust:** O compilador garante que todos os casos possíveis são tratados. Se esquecermos o `Ordering::Equal`, o Rust não compila!

## Seção 2: Destruturação de Enums e Structs - Poder Além do Python

Enums em Rust são muito mais poderosos que em Python. Combinados com pattern matching, tornam-se uma ferramenta incrível.

```rust
// Definindo um enum
enum Forma {
    Circulo(f64),
    Retangulo(f64, f64),
    Quadrado(f64),
}

// Pattern matching com destruturação
fn area(forma: Forma) -> f64 {
    match forma {
        Forma::Circulo(raio) => 3.14159 * raio * raio,
        Forma::Retangulo(largura, altura) => largura * altura,
        Forma::Quadrado(lado) => lado * lado,
    }
}
```

Em Python, precisaríamos usar classes e verificações de tipo, que são menos seguras e mais verbosas.

## Seção 3: Pattern Matching com Guards - Condições Avançadas

Guards permitem adicionar condições extras aos padrões:

```rust
let numero = Some(42);
match numero {
    Some(x) if x > 50 => println!("Maior que 50"),
    Some(x) if x < 10 => println!("Menor que 10"),
    Some(x) => println!("Entre 10 e 50: {}", x),
    None => println!("Nenhum valor"),
}
```

Isso seria equivalente a vários `if` aninhados em Python, mas muito mais organizado.

## Seção 4: @ Bindings - Capturando Valores Dentro de Padrões

Podemos capturar valores enquanto fazemos pattern matching:

```rust
enum Mensagem {
    Texto(String),
    Numero(i32),
}

fn processar(m: Mensagem) {
    match m {
        Mensagem::Texto(t) @ Mensagem::Texto(_) if t.len() > 10 => {
            println!("Texto longo: {}", t)
        }
        Mensagem::Texto(t) => println!("Texto: {}", t),
        Mensagem::Numero(n) => println!("Número: {}", n),
    }
}
```

## Comparação com Python: Quando Usar `match` em Rust vs Alternativas em Python

Em Python, pattern matching foi adicionado na versão 3.10, mas é muito menos poderoso que o do Rust. Veja a diferença:

```python
# Python 3.10+
match status:
    case 200:
        print("OK")
    case 404:
        print("Não encontrado")
    case _:
        print("Erro desconhecido")
```

**Limitações do Python:**
- Não suporta destruturação complexa
- Não tem verificações em tempo de compilação
- Não trabalha bem com tipos customizados

## Erros Comuns para Programadores Python

1. **Esquecer o `_`**: Em Rust, o `_` é obrigatório para cobrir todos os casos. Em Python, o `else` é opcional.
2. **Confundir com switch-case**: O `match` do Rust é muito mais poderoso que um `switch` tradicional.
3. **Ignorar enums**: Muitos tentam replicar padrões OO do Python, quando enums com pattern matching são muitas vezes a solução melhor em Rust.

## Exemplo Prático Completo: Sistema de Login

Vamos implementar um sistema simples de autenticação:

```rust
enum Usuario {
    Autenticado { nome: String, admin: bool },
    Convidado,
}

fn saudacao(usuario: Usuario) {
    match usuario {
        Usuario::Autenticado { nome, admin: true } => {
            println!("Bem-vindo administrador {}!", nome)
        }
        Usuario::Autenticado { nome, admin: false } => {
            println!("Bem-vindo {}!", nome)
        }
        Usuario::Convidado => println!("Por favor faça login"),
    }
}
```

## O Que Aprendemos

- Pattern matching é mais expressivo e seguro que cadeias de `if-elif-else`
- O compilador do Rust garante que todos os casos são tratados
- Podemos destruturar enums e structs de forma poderosa
- Guards permitem condições adicionais nos padrões
- @ bindings ajudam a capturar valores durante o matching

Se você quer se aprofundar ainda mais em Rust e descobrir como aproveitar ao máximo seus recursos avançados, não deixe de conferir o livro completo [Desbravando Rust](https://desbravandorust.com.br).
