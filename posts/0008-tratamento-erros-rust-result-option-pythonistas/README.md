# Tratamento de Erros em Rust: Desmistificando Result e Option para Pythonistas

👋 Bem-vindos, desbravadores! Hoje vamos explorar um dos aspectos mais poderosos e característicos de Rust: seu sistema de tratamento de erros. Se você vem do Python, onde usamos exceções para quase tudo, prepare-se para uma abordagem mais segura e explícita que vai mudar sua forma de pensar sobre erros.

## Introdução: Por Que Rust Faz Diferente?

No Python, estamos acostumados com o clássico `try/except` - lançamos exceções quando algo dá errado e as capturamos quando queremos lidar com os problemas. É prático, mas também propenso a erros: podemos facilmente esquecer de tratar um erro ou deixar escapar exceções inesperadas.

Rust toma um caminho diferente: **erros são tratados como valores**, não como exceções controladas. Isso significa que o compilador nos força a lidar com possíveis falhas explicitamente, tornando nosso código mais seguro e previsível.

Vamos comparar as duas abordagens:
- **Python**: Exceções (try/except/finally)
- **Rust**: Tipos enumerados (Result e Option) + pattern matching

## 🧩 Seção 1: Entendendo Option<T> - O Equivalente ao None do Python

Em Python, usamos `None` para representar a ausência de valor. Em Rust, temos `Option<T>`, que é muito mais poderoso e seguro.

### Option<T> Explicado para Pythonistas

`Option<T>` é um enum (tipo enumerado) que pode ser:
- `Some(T)` - contém um valor do tipo T
- `None` - não contém nenhum valor

Vejamos a diferença na prática:

```python
# Python: Função que pode retornar None
def encontrar_primeiro_par(numeros):
    for num in numeros:
        if num % 2 == 0:
            return num
    return None

# Uso (podemos esquecer de verificar None)
resultado = encontrar_primeiro_par([1, 3, 5])
if resultado is not None:
    print(f"Encontrado: {resultado}")
else:
    print("Nenhum par encontrado")
```

```rust
// Rust: Função que retorna Option<i32>
fn encontrar_primeiro_par(numeros: &[i32]) -> Option<i32> {
    for &num in numeros {
        if num % 2 == 0 {
            return Some(num); // Temos um valor
        }
    }
    None // Nenhum valor encontrado
}

// Uso (o compilador nos força a tratar ambos os casos)
fn main() {
    let numeros = vec![1, 3, 5];
    match encontrar_primeiro_par(&numeros) {
        Some(num) => println!("Encontrado: {}", num),
        None => println!("Nenhum par encontrado"),
    }
}
```

A grande vantagem do `Option` é que **o compilador não deixa você esquecer** de tratar o caso `None`. Em Python, é fácil esquecer de verificar se um valor é `None` - em Rust, isso é impossível.

### Métodos Úteis do Option<T>

Rust oferece vários métodos para trabalhar com `Option` de forma concisa:

```rust
let valor_some = Some(42);
let valor_none: Option<i32> = None;

// unwrap(): obtém o valor ou entra em pânico se for None (⚠️ perigoso!)
println!("{}", valor_some.unwrap()); // 42
// println!("{}", valor_none.unwrap()); // PANIC!

// unwrap_or(): valor padrão se for None
println!("{}", valor_none.unwrap_or(0)); // 0

// map(): transforma o valor se for Some
let valor_dobrado = valor_some.map(|x| x * 2); // Some(84)

// and_then(): transforma e "achata" o resultado
let resultado = valor_some.and_then(|x| Some(x * 2)); // Some(84)
```

## 🎯 Seção 2: Dominando Result<T, E> - Uma Alternativa às Exceções

Enquanto `Option` lida com a ausência de valor, `Result<T, E>` lida com operações que podem falhar. É o equivalente rusticano das exceções do Python, mas muito mais seguro.

### Result<T, E> Explicado

`Result` é um enum com duas variantes:
- `Ok(T)` - operação bem-sucedida, contém o resultado
- `Err(E)` - operação falhou, contém informação do erro

Vamos comparar com Python:

```python
# Python: Divisão com possível exceção
def dividir(a, b):
    if b == 0:
        raise ValueError("Não pode dividir por zero!")
    return a / b

# Uso (podemos esquecer de capturar a exceção)
try:
    resultado = dividir(10, 0)
    print(f"Resultado: {resultado}")
except ValueError as e:
    print(f"Erro: {e}")
```

```rust
// Rust: Divisão com Result
fn dividir(a: f64, b: f64) -> Result<f64, String> {
    if b == 0.0 {
        return Err("Não pode dividir por zero!".to_string());
    }
    Ok(a / b)
}

// Uso (devemos tratar ambos os casos)
fn main() {
    match dividir(10.0, 0.0) {
        Ok(resultado) => println!("Resultado: {}", resultado),
        Err(erro) => println!("Erro: {}", erro),
    }
}
```

### Tipos de Erro Personalizados

Em Rust, podemos (e devemos!) criar nossos próprios tipos de erro:

```rust
// Definindo um tipo de erro personalizado
#[derive(Debug)]
enum ErroMatematico {
    DivisaoPorZero,
    RaizNegativa,
    Overflow,
}

// Implementando mensagem de erro
impl std::fmt::Display for ErroMatematico {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            ErroMatematico::DivisaoPorZero => write!(f, "Divisão por zero"),
            ErroMatematico::RaizNegativa => write!(f, "Raiz quadrada de número negativo"),
            ErroMatematico::Overflow => write!(f, "Overflow matemático"),
        }
    }
}

// Função que usa nosso erro personalizado
fn dividir_seguro(a: f64, b: f64) -> Result<f64, ErroMatematico> {
    if b == 0.0 {
        return Err(ErroMatematico::DivisaoPorZero);
    }
    Ok(a / b)
}
```

## 🧰 Seção 3: Pattern Matching e Operador ? para Tratamento Conciso

### Pattern Matching: O Poderoso Match

O `match` é uma das ferramentas mais poderosas de Rust para tratar `Option` e `Result`:

```rust
fn processar_resultado(resultado: Result<i32, String>) {
    match resultado {
        Ok(valor) => {
            println!("Sucesso! Valor: {}", valor);
            // Podemos fazer mais processamento aqui
        },
        Err(erro) => {
            println!("Falha! Erro: {}", erro);
            // Podemos tratar o erro ou propagar
        }
    }
}

// Match também funciona com Option
fn processar_option(opcao: Option<String>) {
    match opcao {
        Some(texto) => println!("Texto: {}", texto),
        None => println!("Nenhum texto fornecido"),
    }
}
```

### Operador ?: Propagação de Erros Simplificada

O operador `?` é uma das características mais convenientes de Rust. Ele propaga erros automaticamente:

```rust
// Sem o operador ? (mais verboso)
fn ler_arquivo_caminho(caminho: &str) -> Result<String, std::io::Error> {
    let arquivo_resultado = std::fs::File::open(caminho);
    
    let mut arquivo = match arquivo_resultado {
        Ok(arquivo) => arquivo,
        Err(erro) => return Err(erro),
    };
    
    let mut conteudo = String::new();
    match std::io::Read::read_to_string(&mut arquivo, &mut conteudo) {
        Ok(_) => Ok(conteudo),
        Err(erro) => Err(erro),
    }
}

// Com o operador ? (muito mais limpo!)
fn ler_arquivo_caminho_simples(caminho: &str) -> Result<String, std::io::Error> {
    let mut arquivo = std::fs::File::open(caminho)?;
    let mut conteudo = String::new();
    std::io::Read::read_to_string(&mut arquivo, &mut conteudo)?;
    Ok(conteudo)
}

// Podemos ainda simplificar mais com métodos de conveniência
fn ler_arquivo_mais_simples(caminho: &str) -> Result<String, std::io::Error> {
    std::fs::read_to_string(caminho)
}
```

## 🔄 Seção 4: Como as Exceções do Python se Comparam com Rust

### Diferenças Fundamentais

| Característica | Python | Rust |
|----------------|--------|------|
| **Propagação** | Automática (call stack) | Manual (com `?`) |
| **Verificação** | Em runtime | Em tempo de compilação |
| **Obrigatoriedade** | Opcional tratar | Obrigatório tratar |
| **Performance** | Custo alto (stack unwinding) | Custo zero (erros são valores) |

### Quando Usar Cada Abordagem

**Em Python**, use exceções para:
- Erros verdadeiramente excepcionais (raros)
- Quando quer propagar automaticamente pela call stack
- Em código onde performance não é crítica

**Em Rust**, use `Result`/`Option` para:
- Erros esperados (comuns na lógica do programa)
- Quando quer controle explícito sobre o fluxo de erro
- Em código onde performance e segurança são importantes

### Exemplo Prático Completo: Processador de Configurações

Vamos ver um exemplo completo que processa um arquivo de configuração:

```python
# Python: Processador de configuração com exceções
import json

def carregar_configuracao(caminho):
    try:
        with open(caminho, 'r') as arquivo:
            config = json.load(arquivo)
        
        if 'porta' not in config:
            raise ValueError("Porta não especificada na configuração")
        
        if not isinstance(config['porta'], int):
            raise TypeError("Porta deve ser um número inteiro")
            
        return config
        
    except FileNotFoundError:
        print(f"Arquivo {caminho} não encontrado")
        return {"porta": 8080}  # Valor padrão
    except json.JSONDecodeError:
        print("Erro ao decodificar JSON")
        return {"porta": 8080}
    except (ValueError, TypeError) as e:
        print(f"Erro de configuração: {e}")
        return {"porta": 8080}

# Uso
config = carregar_configuracao("config.json")
print(f"Porta: {config['porta']}")
```

```rust
// Rust: Processador de configuração com Result
use std::fs;
use serde::Deserialize; // ⚠️ Necessário adicionar serde no Cargo.toml

#[derive(Debug, Deserialize)]
struct Configuracao {
    porta: u16,
}

// Definimos nossos tipos de erro
#[derive(Debug)]
enum ErroConfiguracao {
    ArquivoNaoEncontrado,
    ParseErro,
    PortaNaoEspecificada,
    PortaInvalida,
}

// Implementamos tratamento de erro personalizado
impl std::fmt::Display for ErroConfiguracao {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            ErroConfiguracao::ArquivoNaoEncontrado => write!(f, "Arquivo não encontrado"),
            ErroConfiguracao::ParseErro => write!(f, "Erro ao analisar JSON"),
            ErroConfiguracao::PortaNaoEspecificada => write!(f, "Porta não especificada"),
            ErroConfiguracao::PortaInvalida => write!(f, "Porta deve ser um número válido"),
        }
    }
}

fn carregar_configuracao(caminho: &str) -> Result<Configuracao, ErroConfiguracao> {
    // Usamos ? para propagar erros automaticamente
    let conteudo = fs::read_to_string(caminho)
        .map_err(|_| ErroConfiguracao::ArquivoNaoEncontrado)?;
    
    // Parse do JSON com tratamento de erro
    let config: Configuracao = serde_json::from_str(&conteudo)
        .map_err(|_| ErroConfiguracao::ParseErro)?;
    
    // Validação adicional
    if config.porta == 0 {
        return Err(ErroConfiguracao::PortaInvalida);
    }
    
    Ok(config)
}

// Função principal com tratamento de erro
fn main() {
    match carregar_configuracao("config.json") {
        Ok(config) => println!("Porta: {}", config.porta),
        Err(ErroConfiguracao::ArquivoNaoEncontrado) => {
            println!("Usando configuração padrão (porta 8080)");
            let config_default = Configuracao { porta: 8080 };
            println!("Porta: {}", config_default.porta);
        },
        Err(erro) => {
            println!("Erro na configuração: {}. Usando padrão (porta 8080)", erro);
            let config_default = Configuracao { porta: 8080 };
            println!("Porta: {}", config_default.porta);
        }
    }
}
```

## ⚠️ Erros Comuns de Pythonistas em Rust

1. **Esquecer de tratar Option/Result**: O compilador vai te avisar, mas inicialmente é frustrante!
2. **Usar unwrap() demais**: É tentador, mas não é tratamento de erro de verdade!
3. **Não usar o operador ?**: Pythonistas tendem a usar match excessivamente no início
4. **Criar tipos de erro complexos**: Comece simples, depois evolua conforme a necessidade
5. **Ignorar os erros de bibliotecas**: Em Rust, quase todas as operações de I/O retornam Result

## 🎓 O que Aprendemos

- **Option<T>** é o equivalente seguro do `None` do Python, forçando tratamento explícito
- **Result<T, E>** substitui exceções com verificação em tempo de compilação
- **Pattern matching** com `match` oferece controle preciso sobre o fluxo de erros
- **Operador ?** simplifica a propagação de erros de forma segura
- **Erros customizados** permitem criar hierarquias de erro específicas para sua aplicação
- **Rust exige mais boilerplate** inicialmente, mas resulta em código muito mais seguro

O sistema de erros de Rust pode parecer verboso no início, especialmente vindo do Python, mas essa "verborragia" é na verdade **explícita documentação em tempo de compilação**. O compilator é seu amigo aqui, garantindo que você nunca se esqueça de tratar um erro possível.

## 📚 Próximos Passsos

Quer se aprofundar ainda mais em Rust? O livro **"Desbravando Rust"** cobre esses e muitos outros conceitos com exemplos práticos, exercícios e projetos reais. 

Visite nosso site [www.desbravandorust.com.br](https://www.desbravandorust.com.br) para adquirir seu exemplar e continuar sua jornada na linguagem mais amada pela comunidade!

Nos próximos posts, vamos explorar concorrência em Rust, sistemas de tipos avançados, e como interoperar Rust com Python. Até lá! 🚀

*Artigo publicado no blog Desbravando Rust - Material de apoio para o livro "Desbravando Rust"*