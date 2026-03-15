# Dominando Enums em Rust: Do Básico ao Avançado para Pythonistas

🦀🔍 Se você vem do Python, enums (ou "enumerações") podem parecer apenas uma forma elegante de definir constantes. Mas em Rust, eles são uma superpotência! Neste post, vamos explorar como os enums em Rust vão muito além do que você está acostumado no Python, permitindo associar dados, implementar métodos e usar pattern matching de forma poderosa.

## Introdução: Enums no Python vs Rust

Em Python, enums são principalmente usados para definir conjuntos de constantes relacionadas. Veja um exemplo básico:

```python
from enum import Enum

class DiaDaSemana(Enum):
    SEGUNDA = 1
    TERCA = 2
    QUARTA = 3
    # ... e assim por diante
```

Isso é útil para organizar constantes e evitar "números mágicos" no código. Mas em Rust, os enums podem fazer muito mais!

Rust expande o conceito de enums para:
- Associar dados diretamente às variantes
- Implementar métodos (como em structs)
- Usar pattern matching exaustivo
- Ser a base para sistemas de erro (Result) e opcionais (Option)

## Seção 1: Enums Básicos em Rust - Similar ao Python

Vamos começar com o equivalente em Rust ao enum Python que vimos:

```rust
// Definindo um enum básico
enum DiaDaSemana {
    Segunda,
    Terca,
    Quarta,
    Quinta,
    Sexta,
    Sabado,
    Domingo,
}

// Usando o enum
let hoje = DiaDaSemana::Segunda;
```

Até aqui, parece bem similar ao Python. Mas mesmo nesse caso simples, Rust oferece vantagens:

1. **Segurança de tipos**: O compilador sabe exatamente todos os valores possíveis
2. **Sem overhead**: Enums em Rust são otimizados, muitas vezes usando apenas um byte
3. **Pattern matching nativo** (veremos mais adiante)

## Seção 2: Enums Avançados - Associando Dados e Métodos

🚀 Aqui é onde Rust brilha! Enums podem carregar dados adicionais em cada variante. Vamos criar um enum para representar diferentes tipos de eventos em um sistema:

```rust
// Enum com dados associados
enum Evento {
    Login { usuario: String, hora: String },
    Logout { usuario: String },
    AcessoRecurso { usuario: String, recurso: String, status: u16 },
}

// Criando instâncias
let evento1 = Evento::Login {
    usuario: String::from("joao"),
    hora: String::from("10:00"),
};

let evento2 = Evento::AcessoRecurso {
    usuario: String::from("maria"),
    recurso: String::from("/dashboard"),
    status: 200,
};
```

Em Python, precisaríamos usar classes e herança para algo similar:

```python
from dataclasses import dataclass

@dataclass
class Login:
    usuario: str
    hora: str

@dataclass
class Logout:
    usuario: str

@dataclass
class AcessoRecurso:
    usuario: str
    recurso: str
    status: int

# Uso
evento1 = Login(usuario="joao", hora="10:00")
evento2 = AcessoRecurso(usuario="maria", recurso="/dashboard", status=200)
```

**Diferenças importantes**:
1. Em Rust, todos os casos estão sob o mesmo tipo `Evento`
2. O compilador Rust vai forçar você a lidar com todos os casos possíveis
3. A representação em memória é mais eficiente em Rust

### Implementando Métodos

Assim como structs, enums em Rust podem ter métodos:

```rust
impl Evento {
    fn get_usuario(&self) -> &str {
        match self {
            Evento::Login { usuario, .. } => usuario,
            Evento::Logout { usuario } => usuario,
            Evento::AcessoRecurso { usuario, .. } => usuario,
        }
    }
}

// Uso
println!("Usuário do evento: {}", evento1.get_usuario());
```

## Seção 3: Pattern Matching com Enums - Poder Além do if-elif-else

🔥 Pattern matching é onde os enums de Rust realmente brilham. Vamos comparar como lidaríamos com nosso enum `Evento` em Python vs Rust.

**Em Python** (usando if-elif e isinstance):

```python
def processar_evento(evento):
    if isinstance(evento, Login):
        print(f"Usuário {evento.usuario} fez login às {evento.hora}")
    elif isinstance(evento, Logout):
        print(f"Usuário {evento.usuario} fez logout")
    elif isinstance(evento, AcessoRecurso):
        print(f"Acesso a {evento.recurso} com status {evento.status}")
    else:
        raise ValueError("Tipo de evento desconhecido")
```

**Em Rust** (usando match):

```rust
fn processar_evento(evento: Evento) {
    match evento {
        Evento::Login { usuario, hora } => {
            println!("Usuário {} fez login às {}", usuario, hora);
        }
        Evento::Logout { usuario } => {
            println!("Usuário {} fez logout", usuario);
        }
        Evento::AcessoRecurso { usuario, recurso, status } => {
            println!("Acesso a {} com status {}", recurso, status);
        }
    }
}
```

**Vantagens do pattern matching em Rust**:
1. **Exaustividade**: O compilador verifica se todos os casos foram tratados
2. **Desestruturação**: Podemos extrair valores diretamente no match
3. **Concisão**: Muito mais limpo que vários if-elif

### Exemplo Avançado com Match

Vamos criar um sistema de autenticação que trata diferentes erros:

```rust
enum ErroAutenticacao {
    UsuarioNaoEncontrado,
    SenhaIncorreta,
    ContaBloqueada,
    LimiteTentativas,
}

fn tratar_erro(erro: ErroAutenticacao) -> String {
    match erro {
        ErroAutenticacao::UsuarioNaoEncontrado => "Usuário não cadastrado".to_string(),
        ErroAutenticacao::SenhaIncorreta => "Senha incorreta".to_string(),
        ErroAutenticacao::ContaBloqueada => "Conta bloqueada - contate o suporte".to_string(),
        ErroAutenticacao::LimiteTentativas => "Muitas tentativas - espere 5 minutos".to_string(),
    }
}
```

## Comparação com Python: Quando Usar Enums

Em Python, enums são úteis para:
- Definir constantes relacionadas
- Melhorar legibilidade do código
- Evitar strings/números mágicos

Em Rust, enums devem ser usados para:
- Representar estados mutuamente exclusivos
- Sistemas de erro (como Result e Option)
- Máquinas de estado
- Dados que podem ter diferentes "formatos"

💡 **Dica para Pythonistas**: Pense em enums Rust como uma combinação de enums Python + classes + unions types + pattern matching!

## Erros Comuns de Pythonistas em Rust

1. **Esquecer de tratar todos os casos no match**:
   - Rust força você a tratar todas as variantes
   - Solução: Use `_ => {}` ou trate explicitamente cada caso

2. **Tentar usar enums Rust como dicionários Python**:
   - Enums não são estruturas de dados flexíveis
   - Para dados dinâmicos, considere structs ou enums com dados associados

3. **Subestimar a capacidade de associação de dados**:
   - Em Python, é comum usar classes separadas
   - Em Rust, enums com dados são mais idiomáticos

## Exemplo Prático: Sistema de Arquivos Simulado

Vamos criar um sistema que representa diferentes tipos de arquivos:

```rust
enum SistemaArquivosItem {
    Arquivo {
        nome: String,
        tamanho: u64,
        extensao: String,
    },
    Diretorio {
        nome: String,
        itens: Vec<SistemaArquivosItem>,
    },
    LinkSimbolico {
        nome: String,
        destino: String,
    },
}

impl SistemaArquivosItem {
    fn calcular_tamanho(&self) -> u64 {
        match self {
            SistemaArquivosItem::Arquivo { tamanho, .. } => *tamanho,
            SistemaArquivosItem::Diretorio { itens, .. } => {
                itens.iter().map(|item| item.calcular_tamanho()).sum()
            }
            SistemaArquivosItem::LinkSimbolico { .. } => 0,
        }
    }
}

// Uso
let root = SistemaArquivosItem::Diretorio {
    nome: "root".to_string(),
    itens: vec![
        SistemaArquivosItem::Arquivo {
            nome: "foto.jpg".to_string(),
            tamanho: 1024,
            extensao: "jpg".to_string(),
        },
        SistemaArquivosItem::LinkSimbolico {
            nome: "atalho".to_string(),
            destino: "/outro/lugar".to_string(),
        },
    ],
};

println!("Tamanho total: {}", root.calcular_tamanho());
```

## O que aprendemos

- 🎯 Enums em Rust vão muito além de simples constantes
- 🔗 Podem associar dados diretamente às variantes
- 🧩 Pattern matching permite lidar com todos os casos de forma segura
- ⚙️ Podem implementar métodos como structs
- 🐍 São mais poderosos que enums Python, substituindo vários padrões
- 🛡️ O compilador garante que todos os casos sejam tratados

## Conclusão: Por que enums são essenciais em Rust

Enums são uma das características mais poderosas de Rust, permitindo modelar domínios complexos de forma segura e eficiente. Para Pythonistas, pode parecer estranho no começo, mas logo você vai perceber como eles tornam seu código mais expressivo e seguro.

Quer se aprofundar ainda mais em Rust? Confira nosso livro **"Desbravando Rust"** com muito mais conteúdo para quem vem do Python: [www.desbravandorust.com.br](https://www.desbravandorust.com.br)