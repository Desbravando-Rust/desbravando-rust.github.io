# Entendendo Ownership em Rust: Um Guia para Pythonistas

Se você vem do Python e está começando com Rust, provavelmente já se deparou com mensagens de erro misteriosas sobre "ownership", "borrowing" ou "value moved here". Calma, você não está sozinho nessa jornada. Vamos explorar juntos esse conceito que é o coração da segurança e performance do Rust.

## Por que Ownership é tão importante em Rust?

Imagine que você está organizando uma festa na sua casa — sua memória RAM é a casa. Em Python, é como se você tivesse um assistente (o coletor de lixo) que fica anotando quem veio, quem saiu e limpando tudo depois. Já em Rust, você é o anfitrião responsável: precisa garantir que cada convidado (dado) tenha um lugar certo, sem bagunça e sem invasores.

Esse sistema permite ao Rust:
- Garantir segurança de memória sem coletor de lixo
- Prevenir vazamentos de memória e acessos inválidos
- Permitir otimizações de performance em tempo de compilação

## Os três princípios do Ownership

Direto do livro oficial do Rust, as regras são:

1. Cada valor em Rust tem um dono (owner)
2. Só pode haver um dono por vez
3. Quando o dono sai de escopo, o valor é descartado

Parece simples, mas as implicações são profundas. Vamos entender com exemplos.

### Princípio 1: Cada valor tem um dono

Em Rust, toda variável é dona do valor que armazena:

```rust
fn main() {
    let s = String::from("hello");  // s é a dona da String "hello"
    println!("{}", s);              // podemos usar s aqui
} // s sai de escopo e a memória é liberada automaticamente
```

Compare com Python, onde os objetos têm vida própria:

```python
def main():
    s = "hello"  # s referencia o objeto string
    print(s)     # mas não é sua "dona" exclusiva
    # O coletor de lixo decide quando liberar a memória
```

### Princípio 2: Um único dono por vez

Em Rust, você não pode ter múltiplos donos para o mesmo valor. Note também que tipos simples como inteiros e booleanos implementam o trait Copy e não sofrem move — são copiados automaticamente:

```rust
fn main() {
    // Tipos que implementam Copy são copiados, não movidos
    let x = 5;
    let y = x;
    println!("{} {}", x, y); // Ok: i32 implementa Copy

    // String NÃO implementa Copy: sofre move
    let s1 = String::from("hello");
    let s2 = s1; // O valor é MOVIDO de s1 para s2

    // println!("{}", s1); // ERRO! s1 não é mais dona de nada
    println!("{}", s2);    // Ok, s2 é a nova dona
}
```

Em Python, isso seria perfeitamente válido em ambos os casos:

```python
s1 = "hello"
s2 = s1  # Ambos referenciam o mesmo objeto
print(s1)  # Funciona
print(s2)  # Funciona
```

### Princípio 3: Descarte quando sai de escopo

Rust automaticamente libera memória quando o dono sai de escopo. Quando isso acontece, o compilador chama implicitamente o trait Drop do valor — o equivalente a um destrutor que você pode até customizar para seus próprios tipos:

```rust
fn main() {
    let outer = String::from("outer");
    {
        // Novo escopo
        let inner = String::from("inner");
        println!("{}", outer); // Ok
        println!("{}", inner); // Ok
    } // inner é dropada aqui; Drop é chamado automaticamente

    // println!("{}", inner); // ERRO! inner não existe mais aqui
    println!("{}", outer);    // outer ainda é válida
}

```

Em Python, não temos essa garantia imediata:

```python
def main():
    s = "hello"
    print(s)
    # O objeto pode ou não ser liberado imediatamente
    # Depende do coletor de lixo
```

## Erros comuns de Pythonistas em Rust

Agora que vimos os princípios, vamos aos problemas que você provavelmente enfrentará.

### 1. Tentar usar uma variável após movê-la

```rust
let s1 = String::from("texto");
let s2 = s1;
println!("{}", s1);  // ERRO: value borrowed here after move
```

**Solução:** Use referências (`&`) ou clone explicitamente:

```rust
let s1 = String::from("texto");
let s2 = &s1; // Empresta s1 sem mover
println!("{} {}", s1, s2); // Ok
```

### 2. Modificar uma referência imutável

Este erro é sutil: o problema não é só tentar modificar uma referência imutável, mas tentar criar uma referência mutável enquanto referências imutáveis ainda estão ativas:


```rust
let mut s = String::from("hello");
let r = &s;              // Referência imutável ativa
s.push_str(", world");   // ERRO: cannot borrow `s` as mutable
                         // because it is also borrowed as immutable
println!("{}", r);

```

**Solução:** Use referências mutáveis somente quando não há referências imutáveis ativas:


```rust
let mut s = String::from("hello");
// Não há referências imutáveis ativas aqui
let r = &mut s;
r.push_str(", world"); // Ok
println!("{}", r);
```

### 3. Criar referências inválidas (dangling references)

```rust
fn cria_referencia() -> &String {
    let s = String::from("hello");
    &s // ERRO: s será liberada ao final da função!
}
```

**Solução:** Retorne o valor diretamente, transferindo ownership para quem chamou:

```rust
fn cria_string() -> String {
    let s = String::from("hello");
    s // Transfere ownership para o caller
}
```

## Exemplo prático completo:

Vamos ver um exemplo completo que mostra ownership na prática, comparando Rust e Python:

### Versão Rust

```rust
fn main() {
    // Passamos ownership para a função; original não pode ser usada depois
    let original = String::from("Rust é seguro");
    let comprimento = calcula_comprimento(original);
    println!("Comprimento: {}", comprimento);
    // println!("{}", original); // ERRO: original foi movida

    // Com borrowing, original permanece válida
    let original2 = String::from("Rust é eficiente");
    let comprimento2 = calcula_comprimento_emprestado(&original2);
    println!("Original2 ainda válida: {}", original2);
    println!("Comprimento: {}", comprimento2);

    // Clone cria uma cópia real e independente
    let copia = original2.clone();
    let comprimento3 = calcula_comprimento(copia);
    println!("Original2 ainda válida: {}", original2);
    println!("Comprimento da cópia: {}", comprimento3);
}

// Recebe ownership da String; ela é liberada ao final
fn calcula_comprimento(s: String) -> usize {
    s.len()
}

// Recebe uma referência; usa &str para ser mais idiomático
fn calcula_comprimento_emprestado(s: &str) -> usize {
    s.len()
}
```

### Versão Python

```python
def main():
    original = "Python é dinâmico"

    # Em Python, passamos referências, não ownership
    comprimento = calcula_comprimento(original)

    # Original ainda está acessível
    print(f"Original: {original}")

    # Não precisamos nos preocupar com borrowing ou moving
    original2 = "Python é flexível"
    comprimento2 = calcula_comprimento(original2)
    print(f"Original2 ainda válida: {original2}")

def calcula_comprimento(s):
    return len(s)  # Não afetamos o caller

```

### Ownership em tipos customizados
O sistema de ownership se aplica igualmente a structs e outros tipos compostos. Sempre que uma struct contém um campo como String, ela também não implementa Copy — portanto sofre move na atribuição:

```rust
struct Item {
    nome: String,
}

fn main() {
    let item = Item { nome: String::from("Exemplo") };
    let item2 = item; // Move ocorre aqui

    // println!("{}", item.nome); // ERRO: item foi movido
    println!("{}", item2.nome);   // Ok
}
```

## Comparação: Gerenciamento de memória em Python vs Rust

| Característica | Python                          | Rust                             |
| -------------- | ------------------------------- | -------------------------------- |
| Modelo         | Coleta de lixo (GC)             | Ownership system                 |
| Performance    | Overhead do GC                  | Sem overhead de runtime          |
| Segurança      | Possíveis referências inválidas | Garantido em tempo de compilação |
| Controle       | Automático                      | Manual (com garantias)           |
| Concorrência   | GIL pode ser limitante          | Sem GIL, seguro por design       |

## Semântica de operações: Python vs Rust

| Operação             | Python               | Rust                       |
| -------------------- | -------------------- | -------------------------- |
| Atribuição (=)       | Cria nova referência | Move ou copia (Copy types) |
| Cópia profunda       | copy.deepcopy()      | .clone()                   |
| Passagem para função | Por referência       | Move ou borrow (&)         |

## Quando usar clone() em Rust?

Pythonistas muitas vezes esperam que a atribuição crie cópias independentes. Em Rust, isso não acontece automaticamente para tipos alocados no heap. Se você precisa de uma cópia real, use clone() — mas use com consciência, pois ele aloca nova memória:

```rust
let s1 = String::from("texto");
let s2 = s1.clone(); // Cópia real, não só da referência

println!("s1 = {}, s2 = {}", s1, s2); // Ambos válidos
```

Em Python, isso seria equivalente a:

```python
import copy
s1 = "texto"
s2 = copy.deepcopy(s1)  # Para strings é desnecessário, mas ilustra a ideia
```


## Exercício prático
Para fixar o conceito, tente resolver o seguinte problema:

O código abaixo não compila. Modifique apenas a assinatura de exibe_tamanho para que nome permaneça válido após a chamada da função:

```rust
fn main() {
    let nome = String::from("Rustacean");
    exibe_tamanho(nome);
    println!("{}", nome); // Como fazer isso funcionar?
}

fn exibe_tamanho(s: String) {
    println!("Tamanho: {}", s.len());
}
```

*Dica: a solução está na diferença entre mover e emprestar.*

## O que aprendemos? 📚

- Ownership é o sistema único do Rust para gerenciar memória sem GC
- Cada valor tem apenas um dono por vez em Rust
- Quando o dono sai de escopo, o valor é liberado
- Em Python, o coletor de lixo cuida da memória automaticamente
- Erros comuns incluem tentar usar valores após movê-los
- Referências (`&`) permitem "emprestar" valores sem transferir ownership
- `Clone()` cria cópias reais quando necessário

## Próximos passos na sua jornada Rust

Dominar ownership é o primeiro passo para escrever código Rust seguro e eficiente. No próximo post, exploraremos o conceito de borrowing e lifetimes em profundidade — incluindo como o compilador rastreia o tempo de vida das referências para garantir que nunca apontem para memória inválida.

Para se aprofundar ainda mais com exemplos práticos e exercícios, confira o livro Desbravando Rust em [https://desbravandorust.com.br](https://desbravandorust.com.br).
