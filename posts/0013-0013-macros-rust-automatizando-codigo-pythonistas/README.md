# Macros em Rust: Automatizando Código para Pythonistas

Se você vem do Python, provavelmente já usou decoradores para modificar funções ou metaclasses para alterar o comportamento de classes. Em Rust, não temos esses recursos exatamente como no Python, mas temos algo ainda mais poderoso: **macros**. Neste artigo, vamos explorar como as macros em Rust podem substituir e expandir os padrões de metaprogramação que você conhece do Python.

## Introdução: Metaprogramação em Python vs Macros em Rust

No Python, a metaprogramação geralmente envolve:

- Decoradores para modificar funções
- Metaclasses para personalizar criação de classes
- Funções como `eval()` e `exec()` para executar código dinâmico

Em Rust, a abordagem é diferente. As macros permitem que você escreva código que escreve outro código (meta, não?). Existem dois tipos principais:

1. **Macros declarativas** (`macro_rules!`): Para substituir padrões repetitivos
2. **Macros procedurais**: Para criar DSLs (Domain Specific Languages) e expandir a sintaxe

Vamos explorar cada uma delas, sempre comparando com equivalentes (ou aproximações) em Python.

## Seção 1: Macros Declarativas (`macro_rules!`) - Automatizando Padrões Repetitivos

Imagine que no Python você frequentemente escreve funções como:

```python
def add(a: int, b: int) -> int:
    return a + b

def multiply(a: int, b: int) -> int:
    return a * b
```

Isso é repetitivo. Em Rust, podemos criar uma macro para gerar essas funções automaticamente:

```rust
// Define a macro chamada `create_math_functions`
macro_rules! create_math_functions {
    // Padrão: recebe o nome da função e a operação
    ($func_name:ident, $op:tt) => {
        // Gera uma função com o nome e operação fornecidos
        fn $func_name(a: i32, b: i32) -> i32 {
            a $op b  // Aplica a operação
        }
    };
}

// Usa a macro para criar funções
create_math_functions!(add, +);
create_math_functions!(multiply, *);

fn main() {
    println!("Soma: {}", add(2, 3));        // Output: 5
    println!("Multiplicação: {}", multiply(2, 3)); // Output: 6
}
```

### Comparação com Python

Em Python, poderíamos usar metaprogramação para algo similar, mas seria mais complexo:

```python
def create_math_function(name, op):
    def func(a, b):
        return eval(f"a {op} b")
    func.__name__ = name
    globals()[name] = func

create_math_function("add", "+")
create_math_function("multiply", "*")

print(add(2, 3))        # Output: 5
print(multiply(2, 3))   # Output: 6
```

A diferença crucial é que a macro Rust é expandida durante a compilação, enquanto a solução Python usa execução dinâmica em runtime.

## Seção 2: Macros Procedurais - Criando DSLs Poderosas

As macros procedurais são mais avançadas e permitem criar verdadeiras linguagens específicas de domínio (DSLs). Vamos criar uma macro que transforma structs em formatos JSON, similar ao que fazem bibliotecas Python como `dataclasses` ou `pydantic`.

### Exemplo: Macro `json_serializable`

```rust
use proc_macro::TokenStream;
use quote::quote;
use syn::{parse_macro_input, DeriveInput};

// Define a macro procedural
#[proc_macro_derive(JsonSerializable)]
pub fn json_serializable(input: TokenStream) -> TokenStream {
    // Parse the input tokens into a syntax tree
    let input = parse_macro_input!(input as DeriveInput);
    
    // Get the struct name
    let name = input.ident;
    
    // Generate the implementation
    let expanded = quote! {
        impl #name {
            pub fn to_json(&self) -> String {
                let mut json = String::from("{");
                // Aqui viria a implementação real de serialização
                json.push_str("\"type\": \"");
                json.push_str(stringify!(#name));
                json.push_str("\"");
                json.push_str("}");
                json
            }
        }
    };
    
    // Convert back to TokenStream
    TokenStream::from(expanded)
}
```

Agora podemos usar essa macro:

```rust
#[derive(JsonSerializable)]
struct User {
    id: u32,
    name: String,
}

fn main() {
    let user = User {
        id: 1,
        name: "Ana".to_string(),
    };
    println!("{}", user.to_json()); // Output: {"type": "User"}
}
```

### Comparação com Python

Em Python, usaríamos decoradores ou metaclasses para funcionalidade similar:

```python
from dataclasses import dataclass
import json

def json_serializable(cls):
    def to_json(self):
        return json.dumps(self.__dict__)
    cls.to_json = to_json
    return cls

@json_serializable
class User:
    def __init__(self, id, name):
        self.id = id
        self.name = name

user = User(1, "Ana")
print(user.to_json())  # Output: {"id": 1, "name": "Ana"}
```

A diferença principal é que a macro Rust opera em tempo de compilação, enquanto o decorador Python opera em tempo de execução.

## Seção 3: Caso Prático - Implementando um Logger

Vamos implementar um sistema de logging que registra a entrada e saída de funções, similar a um decorador Python.

### Solução Rust com Macro

```rust
macro_rules! log_function {
    ($func:ident($($param:ident: $typ:ty),*) -> $ret:ty $body:block) => {
        fn $func($($param: $typ),*) -> $ret {
            println!("[ENTRADA] {}({})", stringify!($func), stringify!($($param),*));
            let result = $body;
            println!("[SAÍDA] {}: {:?}", stringify!($func), result);
            result
        }
    };
}

// Usando a macro
log_function!(add(a: i32, b: i32) -> i32 {
    a + b
});

fn main() {
    add(2, 3);  // Output:
                // [ENTRADA] add(a, b)
                // [SAÍDA] add: 5
}
```

### Solução Python com Decorador

```python
def log_function(func):
    def wrapper(*args, **kwargs):
        print(f"[ENTRADA] {func.__name__}({args}, {kwargs})")
        result = func(*args, **kwargs)
        print(f"[SAÍDA] {func.__name__}: {result}")
        return result
    return wrapper

@log_function
def add(a, b):
    return a + b

add(2, 3)  # Output:
           # [ENTRADA] add((2, 3), {})
           # [SAÍDA] add: 5
```

## Comparação com Python: Quando Usar Macros

- **Use macros Rust quando**:
  - Precisa de verificação em tempo de compilação
  - Quer evitar overhead de runtime
  - Necessita de geração de código complexa

- **Prefira decoradores/metaclasses Python quando**:
  - Flexibilidade em runtime é importante
  - Não quer lidar com sistema de macros mais complexo
  - Está trabalhando em um projeto puramente Python

## Erros Comuns de Pythonistas em Rust

1. **Tentar usar macros como funções**: Macros são expandidas antes da compilação, não são chamadas em runtime
2. **Esquecer a sintaxe especial**: Macros usam `!` e têm regras de pattern matching próprias
3. **Abusar das macros**: Nem tudo precisa ser macro; muitas vezes funções normais são suficientes
4. **Ignorar a fase de compilação**: Macros operam durante a compilação, o que pode afetar mensagens de erro

## O que aprendemos

- **Macros declarativas** (`macro_rules!`) servem para substituir padrões repetitivos de código
- **Macros procedurais** permitem criar DSLs e expandir a sintaxe de Rust
- **Comparação com Python**: Macros operam em tempo de compilação, enquanto decoradores/metaclasses atuam em runtime
- **Caso prático**: Implementamos um logger como macro, similar a um decorador Python
- **Quando usar**: Macros são ideais para verificação em tempo de compilação e geração de código complexa

As macros em Rust abrem um mundo de possibilidades para automação e geração de código seguro e eficiente. Embora a curva de aprendizado seja mais acentuada que a dos decoradores Python, o ganho em segurança e performance compensa o investimento.

Quer se aprofundar ainda mais em Rust e descobrir como dominar todos os seus recursos? Confira o livro completo [Desbravando Rust](https://desbravandorust.com.br), onde exploramos desde conceitos básicos até tópicos avançados com detalhes que transformarão sua jornada com Rust.