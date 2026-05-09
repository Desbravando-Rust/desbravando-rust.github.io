# Macros em Rust: Automatizando Código Além do que Python Permite

Metaprogramação é a arte de escrever código que gera ou manipula outro código. Se você vem do Python, provavelmente já usou decoradores, metaclasses ou funções de geração de código para automatizar tarefas repetitivas. O Rust também oferece poderosas ferramentas de metaprogramação, mas com uma abordagem fundamentalmente diferente e mais segura: as macros.

Enquanto Python permite modificar o código em tempo de execução, Rust opera em tempo de compilação através de seu poderoso sistema de macros. Isso oferece vantagens significativas: verificação de tipos antecipada, maior segurança e melhor performance, já que todo o código é expandido antes do programa rodar.

Neste artigo, vamos explorar como as macros do Rust vão além do que Python permite, oferecendo um controle granular sobre a geração de código com segurança em tempo de compilação.

## O Que São Macros e Por Que São Diferentes de Python

Em Python, a metaprogramação acontece principalmente em tempo de execução. Decoradores modificam funções, metaclasses controlam a criação de classes, e funções como `eval()` permitem executar strings como código. Isso é flexível, mas também pode levar a erros que só aparecem quando o programa está rodando.

Rust, por outro lado, realiza toda metaprogramação em tempo de compilação através de macros. Existem dois tipos principais:

1. **Macros declarativas** (com `macro_rules!`): Mais simples, funcionam como correspondência de padrões
2. **Macros procedurais**: Mais poderosas, permitem manipulação arbitrária de tokens

A principal diferença é que as macros Rust são **higiênicas** (não causam efeitos colaterais inesperados) e **seguras** (o compilador verifica todo o código gerado).

## Macros Declarativas: Criando Seu Próprio `print!` 🛠️

Vamos começar com macros declarativas, que são mais fáceis de entender para iniciantes. Elas funcionam através do `macro_rules!` e permitem criar syntax extensions usando regras de correspondência de padrões.

### Um Exemplo Básico: `meu_println!`

Em Python, estamos acostumados com `print()` sendo uma função simples. Em Rust, `println!` é na verdade uma macro! Vamos criar nossa própria versão simplificada:

```rust
// Define uma macro chamada meu_println
macro_rules! meu_println {
    // Primeira regra: sem argumentos (apenas println vazio)
    () => {
        println!()  // Chama a macro println! existente
    };
    
    // Segunda regra: com um ou mais argumentos
    ($($arg:tt)*) => {
        println!($($arg)*)  // Repassa os argumentos para println!
    };
}

fn main() {
    meu_println!();  // Imprime uma linha em branco
    meu_println!("Olá, {}!", "mundo");  // Imprime: Olá, mundo!
    meu_println!("Valores: {}, {}, {}", 1, 2, 3);  // Múltiplos argumentos
}
```

O que está acontecendo aqui:
- `macro_rules!` inicia a definição da macro
- `()` define uma regra para quando a macro é chamada sem argumentos
- `$($arg:tt)*` captura todos os tokens (tt = token tree) passados para a macro
- `$($arg)*` expande os tokens capturados na chamada para `println!`

### Comparação com Python

Em Python, poderíamos criar algo similar com uma função:

```python
def meu_print(*args, **kwargs):
    if not args and not kwargs:
        print()
    else:
        print(*args, **kwargs)

# Exemplo de uso
meu_print()
meu_print("Olá, {}!".format("mundo"))
meu_print("Valores:", 1, 2, 3)
```

A diferença crucial é que a versão Python roda em tempo de execução, enquanto a macro Rust é expandida durante a compilação. O código Rust resultante não tem overhead de chamada de função extra.

### Um Exemplo Mais Útil: `vetor!`

Vamos criar uma macro mais útil que simplifica a criação de vetores:

```rust
macro_rules! vetor {
    // Caso vazio: cria um Vec vazio
    () => {
        Vec::new()
    };
    
    // Caso com elementos: $x:expr captura uma expressão
    ($($x:expr),*) => {
        {
            let mut temp_vec = Vec::new();
            $(temp_vec.push($x);)*  // Expande para push() para cada expressão
            temp_vec
        }
    };
    
    // Caso com repetição: cria múltiplos elementos iguais
    ($x:expr; $n:expr) => {
        {
            let mut temp_vec = Vec::new();
            for _ in 0..$n {
                temp_vec.push($x.clone());
            }
            temp_vec
        }
    };
}

fn main() {
    let v1 = vetor!();  // Vec vazio
    let v2 = vetor!(1, 2, 3);  // Vec com valores 1, 2, 3
    let v3 = vetor!("a"; 5);  // Vec com 5 strings "a"
    
    println!("{:?}", v1);  // []
    println!("{:?}", v2);  // [1, 2, 3]
    println!("{:?}", v3);  // ["a", "a", "a", "a", "a"]
}
```

Em Python, teríamos que usar uma função normal:

```python
def criar_vetor(*args):
    if len(args) == 0:
        return []
    elif len(args) == 2 and isinstance(args[1], int):
        return [args[0]] * args[1]
    else:
        return list(args)

# Exemplo de uso
v1 = criar_vetor()
v2 = criar_vetor(1, 2, 3)
v3 = criar_vetor("a", 5)

print(v1)  # []
print(v2)  # [1, 2, 3]
print(v3)  # ["a", "a", "a", "a", "a"]
```

A versão Rust é mais poderosa porque:
1. Verifica tipos em tempo de compilação
2. Não tem overhead de runtime (a macro é expandida antes da execução)
3. Oferece syntax mais limpa com múltiplos padrões

## Macros Procedurais: O Poder Real da Metaprogramação 💪

As macros procedurais são muito mais poderosas que as declarativas. Elas permitem manipular arbitráriamente o código fonte usando a API de tokens do Rust. Existem três tipos:

1. **Macros de Derive**: Automatizam implementação de traits
2. **Macros de Atributo**: Aplicam transformações a itens
3. **Macros Function-like**: Parecidas com as declarativas, mas mais poderosas

### Configuração para Macros Procedurais

Para criar macros procedurais, precisamos de uma crate especial. Vamos configurar:

**Cargo.toml:**
```toml
[package]
name = "meu_projeto"
version = "0.1.0"
edition = "2021"

[lib]
proc-macro = true  # Esta é uma crate de macro procedural!

[dependencies]
syn = { version = "2.0", features = ["full"] }
quote = "1.0"
```

### Macro de Derive: `MinhaSerde`

Vamos criar uma macro de derive simples que automaticamente gera serialização/deserialização básica, similar ao que o Serde faz:

```rust
// main.rs
use minha_serde::MinhaSerde;

#[derive(MinhaSerde)]
struct Pessoa {
    nome: String,
    idade: u32,
    ativo: bool,
}

fn main() {
    let pessoa = Pessoa {
        nome: "João".to_string(),
        idade: 30,
        ativo: true,
    };
    
    let serializado = pessoa.serializar();
    println!("{}", serializado);  // {"nome": "João", "idade": 30, "ativo": true}
    
    // Desserialização seria implementada de forma similar
}
```

```rust
// lib.rs da crate minha_serde
use proc_macro::TokenStream;
use quote::quote;
use syn::{parse_macro_input, DeriveInput};

#[proc_macro_derive(MinhaSerde)]
pub fn minha_serde_derive(input: TokenStream) -> TokenStream {
    // Parse do input para AST
    let input = parse_macro_input!(input as DeriveInput);
    let nome = input.ident;
    
    // Extrai os campos da struct
    let campos = if let syn::Data::Struct(syn::DataStruct {
        fields: syn::Fields::Named(ref campos_nomeados),
        ..
    }) = input.data {
        &campos_nomeados.named
    } else {
        panic!("MinhaSerde só funciona com structs com campos nomeados!");
    };
    
    // Gera os nomes dos campos como strings
    let nomes_campos: Vec<String> = campos
        .iter()
        .map(|campo| {
            campo
                .ident
                .as_ref()
                .unwrap()
                .to_string()
        })
        .collect();
    
    // Gera a implementação do trait
    let expandido = quote! {
        impl #nome {
            pub fn serializar(&self) -> String {
                let mut resultado = String::from("{");
                #(
                    resultado.push_str(&format!("\"{}\": {:?}, ", #nomes_campos, self.#nomes_campos));
                )*
                resultado.pop();  // Remove última vírgula
                resultado.pop();  // Remove último espaço
                resultado.push('}');
                resultado
            }
        }
    };
    
    TokenStream::from(expandido)
}
```

Este exemplo mostra o poder real das macros procedurais: analisamos a estrutura da struct em tempo de compilação e geramos código específico baseado em seus campos.

### Comparação com Python

Em Python, usaríamos decoradores de classe ou metaclasses para funcionalidade similar:

```python
def minha_serde(cls):
    def serializar(self):
        campos = []
        for nome, valor in self.__dict__.items():
            campos.append(f'"{nome}": {repr(valor)}')
        return "{" + ", ".join(campos) + "}"
    
    cls.serializar = serializar
    return cls

@minha_serde
class Pessoa:
    def __init__(self, nome, idade, ativo):
        self.nome = nome
        self.idade = idade
        self.ativo = ativo

# Exemplo de uso
pessoa = Pessoa("João", 30, True)
print(pessoa.serializar())  # {"nome": "João", "idade": 30, "ativo": True}
```

As diferenças são fundamentais:
- A versão Rust verifica tipos em tempo de compilação
- O código Rust gerado é otimizado especificamente para cada struct
- Não há overhead de runtime para análise reflexiva
- Erros são detectados durante a compilação, não durante a execução

## Macros de Atributo: Personalizando Comportamento

Macros de atributo permitem criar atributos personalizados que modificam itens. Vamos criar um atributo `medir_tempo` que automaticamente mede o tempo de execução de funções:

```rust
// main.rs
use medir_tempo::medir_tempo;

#[medir_tempo]
fn funcao_lenta() {
    std::thread::sleep(std::time::Duration::from_secs(1));
    println!("Função executada!");
}

fn main() {
    funcao_lenta();
    // Imprime: "funcao_lenta levou 1.003s"
}
```

```rust
// lib.rs da crate medir_tempo
use proc_macro::TokenStream;
use quote::quote;
use syn::{parse_macro_input, ItemFn};

#[proc_macro_attribute]
pub fn medir_tempo(_attr: TokenStream, item: TokenStream) -> TokenStream {
    let input = parse_macro_input!(item as ItemFn);
    let nome_funcao = &input.sig.ident;
    let blocos = &input.block;
    let visibilidade = &input.vis;
    let assinatura = &input.sig;
    
    let expandido = quote! {
        #visibilidade #assinatura {
            let inicio = std::time::Instant::now();
            let resultado = (|| #blocos)();
            let duracao = inicio.elapsed();
            println!("{} levou {:.3}s", stringify!(#nome_funcao), duracao.as_secs_f64());
            resultado
        }
    };
    
    TokenStream::from(expandido)
}
```

### Comparação com Python

Em Python, usaríamos um decorador normal:

```python
import time

def medir_tempo(funcao):
    def wrapper(*args, **kwargs):
        inicio = time.time()
        resultado = funcao(*args, **kwargs)
        duracao = time.time() - inicio
        print(f"{funcao.__name__} levou {duracao:.3f}s")
        return resultado
    return wrapper

@medir_tempo
def funcao_lenta():
    time.sleep(1)
    print("Função executada!")

funcao_lenta()  # "funcao_lenta levou 1.003s"
```

Novamente, a diferença fundamental está em quando a transformação acontece:
- Python: Em tempo de execução, com overhead de chamadas de função
- Rust: Em tempo de compilação, sem overhead de runtime

## Erros Comuns de Pythonistas em Rust

1. **Tentar usar macros como funções**: Macros parecem funções, mas têm regras diferentes. Use `!` na chamada.

2. **Esquecer da higiene**: Macros Rust são higiênicas (variáveis não vazam), ao contrário de algumas técnicas Python.

3. **Subestimar a complexidade**: Macros procedurais são mais complexas que decoradores Python.

4. **Não entender a expansão**: Use `cargo expand` para ver o código gerado pelas macros.

## Quando Usar Macros no Rust

Use macros quando:
- Você precisa de boilerplate repetitivo que não pode ser abstraído com funções
- Quer criar APIs com syntax personalizada
- Precisa de código gerado em tempo de compilação para performance
- Está implementando traits comuns para muitos tipos

Não use macros quando:
- Uma função normal resolveria o problema
- Você está começando a aprender Rust (aprenda os fundamentos primeiro)
- A complexidade não justifica o benefício

## O Que Aprendemos

- **Macros declarativas** (`macro_rules!`) permitem criação de syntax extensions através de regras de pattern matching
- **Macros procedurais** oferecem poder total sobre manipulação de código em três variedades: derive, attribute e function-like
- **Macros de derive** automatizam implementação de traits com base na análise de estruturas
- **Macros de atributo** modificam itens anotados com comportamentos personalizados
- **O processo de compilação** do Rust expande macros antes da geração de código, oferecendo segurança e performance
- **Comparação com Python**: Enquanto Python usa runtime metaprogramming (decoradores, metaclasses), Rust faz compile-time metaprogramming com verificação de tipos

As macros são uma das características mais poderosas do Rust, permitindo criar código conciso, seguro e eficiente que seria impossível ou inseguro em muitas outras linguagens.

---

Este artigo é um material de apoio do livro **Desbravando Rust**, que explora em profundidade todos esses conceitos e muitos outros. Se você quer dominar Rust vindo de background Python, [compre agora em desbravandorust.com.br](https://desbravandorust.com.br) e acelere sua jornada Rust!