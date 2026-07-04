# Strings em Rust: por que existem `String` e `&str` (e o que o Python esconde de você)
###### Por [@zejuniortdr](https://github.com/zejuniortdr/) em Jul 04, 2026

Se você vem do Python, texto sempre foi a parte fácil da vida. `nome = "Rust"` e pronto — concatena, fatia, passa pra função, ninguém pergunta nada. Aí você chega no Rust, escreve o que parece óbvio, e o compilador te devolve um `expected &str, found String` ou o clássico `borrow of moved value`. A primeira reação é achar que Rust está sendo difícil de propósito.

Não está. O que acontece é que Rust te mostra na cara uma distinção que o Python sempre fez nos bastidores e nunca te contou: a diferença entre **ser dono de um texto** e **apenas olhar para um texto emprestado**. Neste post vamos desmistificar `String` e `&str` usando exatamente o que você já sabe de Python — e no fim aquele erro vai virar algo óbvio.

Este tema conversa direto com [ownership](../0005-entendendo-ownership-rust-guia-pythonistas): se aquele post ainda não fez sentido, ele é a base para tudo o que vem aqui.

## Os dois tipos que confundem todo mundo

Em Python existe um tipo só: `str`. Ele é imutável, e você nunca pensa em quem é "dono" dele.

```python
s = "hello"          # str
s2 = s               # s2 aponta para o MESMO objeto
print(s, s2)         # tudo funciona, sem cópia, sem preocupação
```

Em Rust, "texto" se divide em dois tipos com papéis diferentes:

```rust
fn main() {
    // String: dona do texto, alocada no heap, pode crescer
    let dona: String = String::from("hello");

    // &str: uma "vista" emprestada de um texto que vive em outro lugar
    let emprestada: &str = "hello"; // literais são &str, gravados no binário

    println!("{} {}", dona, emprestada);
}
```

A analogia que funciona: `String` é o **arquivo** que você tem na sua máquina — você o criou, é seu, pode editar e apagar. `&str` é o **link** para um arquivo: dá pra ler, mas ele aponta para algo que é dono em outro lugar. O Python só te dá "objetos str" e um coletor de lixo que decide quando jogar fora; Rust te obriga a dizer, no tipo, se você tem o arquivo ou só o link.

## Por que dois tipos? Porque um pode crescer e o outro não

`String` é dona: mora no heap e pode ser modificada.

```rust
fn main() {
    let mut s = String::from("Rust");
    s.push_str(" é rápido"); // ok: nós somos donos, podemos crescer
    println!("{}", s);       // Rust é rápido
}
```

Compare com Python, onde a "mutação" na verdade cria um novo objeto (str é imutável), mas a sintaxe esconde isso:

```python
s = "Rust"
s += " é rápido"   # parece mutação, mas cria um novo str por baixo
print(s)
```

Já `&str` é só uma janela para bytes que já existem — não dá pra fazer crescer, porque você não é dono do espaço:

```rust
fn main() {
    let s: &str = "Rust";
    // s.push_str(" é rápido"); // ERRO: &str não tem push_str, você não é dono
    println!("{}", s);
}
```

## A regra de ouro: receba `&str`, guarde `String`

Este é o padrão idiomático que resolve 90% da sua confusão inicial:

- **Parâmetros de função** → receba `&str` (aceita os dois: `String` vira `&str` de graça).
- **Campos de struct e valores que você precisa guardar** → use `String` (você precisa ser dono).

```rust
// Recebe &str: funciona tanto com literal quanto com String
fn saudacao(nome: &str) -> String {
    format!("Olá, {}!", nome) // format! devolve uma String nova, da qual seremos donos
}

fn main() {
    let dono = String::from("Ana");
    println!("{}", saudacao(&dono)); // &String vira &str automaticamente (deref coercion)
    println!("{}", saudacao("Bruno")); // literal &str: funciona também
}
```

Compare com Python, onde você nunca teve essa escolha — todo parâmetro recebe uma referência ao objeto e o resto é com o coletor de lixo:

```python
def saudacao(nome: str) -> str:
    return f"Olá, {nome}!"

print(saudacao("Ana"))
print(saudacao("Bruno"))
```

A "chatice" do Rust aqui é justamente o que te dá o ganho: ao receber `&str`, sua função não força ninguém a alocar memória só para chamá-la.

## Erros comuns de Pythonistas em Rust

### 1. Concatenar como se fosse Python

Em Python você soma strings sem pensar. Em Rust, `+` entre textos tem uma regra que pega todo mundo:

```rust
let a = String::from("Olá, ");
let b = String::from("mundo");
let c = a + &b; // repare no & : o operador + consome `a` (move) e empresta `b`
// println!("{}", a); // ERRO: value borrowed here after move — `a` foi movida!
println!("{}", c);
```

**Solução:** use `format!`, que não move nada e lê muito melhor:

```rust
let a = String::from("Olá, ");
let b = String::from("mundo");
let c = format!("{}{}", a, b); // a e b continuam válidas
println!("{} | {} | {}", a, b, c);
```

### 2. Achar que indexar string funciona igual

Em Python isso é trivial:

```python
s = "café"
print(s[0])   # 'c'
```

Em Rust, isso **nem compila** — de propósito:

```rust
let s = String::from("café");
// let primeiro = s[0]; // ERRO: `String` cannot be indexed by `usize`
```

O motivo: `String` é UTF-8, e um "caractere" pode ocupar mais de um byte (`é` ocupa dois). Indexar por byte poderia te devolver meio caractere. **Solução:** seja explícito sobre o que você quer — caracteres ou bytes:

```rust
let s = String::from("café");
let primeiro = s.chars().next().unwrap(); // 'c' — itera por caractere Unicode
println!("{}", primeiro);
println!("{}", s.chars().count());        // 4 caracteres
println!("{}", s.len());                  // 5 bytes (o é ocupa 2)
```

Curiosidade: o Python 3 também sofre com isso por baixo — `len("café")` é 4 porque ele guarda pontos de código, mas a conta de bytes reais só aparece quando você faz `"café".encode("utf-8")`. Rust só te obriga a encarar a diferença desde o começo.

### 3. Clonar por medo em vez de emprestar

Vindo do erro de "value moved", a tentação é sair colocando `.clone()` em tudo até o compilador parar de reclamar:

```rust
fn imprime(s: String) { println!("{}", s); }

fn main() {
    let nome = String::from("Rust");
    imprime(nome.clone()); // clona (aloca nova memória) só para calar o compilador
    println!("{}", nome);
}
```

**Solução:** na maioria das vezes você só precisa *emprestar*. Troque o parâmetro para `&str` e o `.clone()` desaparece:

```rust
fn imprime(s: &str) { println!("{}", s); }

fn main() {
    let nome = String::from("Rust");
    imprime(&nome);        // empresta, não copia
    println!("{}", nome);  // nome continua válida, custo zero
}
```

## Comparação: texto em Python vs Rust

| Característica        | Python (`str`)            | Rust (`String` / `&str`)                 |
| -------------------- | ------------------------- | ---------------------------------------- |
| Quantos tipos        | Um (`str`)                | Dois: `String` (dona) e `&str` (emprestada) |
| Mutabilidade         | Imutável (recria)         | `String` mutável; `&str` imutável        |
| Onde vive            | Heap, gerenciado por GC   | `String` no heap; `&str` aponta pra qualquer lugar |
| Concatenar           | `+` sempre novo objeto    | `+` move; prefira `format!`              |
| Indexar por posição  | `s[0]` funciona           | Não compila; use `.chars()` / `.bytes()` |
| Custo de passar p/ função | Referência (implícito) | Você escolhe: emprestar (`&str`) ou dar posse (`String`) |

## Exemplo prático completo

Uma função que monta um slug (URL amigável) a partir de um título. Repare como recebemos `&str` (barato de chamar) e devolvemos `String` (precisamos ser donos do resultado novo):

### Versão Rust

```rust
fn slugify(titulo: &str) -> String {
    titulo
        .trim()
        .to_lowercase()
        .chars()
        .map(|c| if c.is_alphanumeric() { c } else { '-' })
        .collect::<String>() // junta os chars numa String nova
}

fn main() {
    let titulo = String::from("  Strings em Rust  ");
    let slug = slugify(&titulo);      // emprestamos o título
    println!("{}", slug);             // strings-em-rust
    println!("original intacto: {}", titulo); // ainda válido: não movemos nada
}
```

### Versão Python

```python
def slugify(titulo: str) -> str:
    return "".join(
        c if c.isalnum() else "-"
        for c in titulo.strip().lower()
    )

titulo = "  Strings em Rust  "
print(slugify(titulo))         # strings-em-rust
print("original intacto:", titulo)
```

O código é quase o mesmo. A diferença é que, em Rust, a assinatura `(&str) -> String` **documenta** que a função lê o texto sem tomar posse e devolve um texto novo do qual quem chamou passa a ser dono. Em Python, essa informação simplesmente não existe — e é por isso que bugs de "quem é dono desse objeto?" só aparecem em runtime.

## Exercício prático

O código abaixo não compila. Ajuste **apenas a assinatura** de `primeira_palavra` para que `frase` continue válida depois da chamada:

```rust
fn main() {
    let frase = String::from("Rust para pythonistas");
    let p = primeira_palavra(frase);
    println!("{}", p);
    println!("{}", frase); // como fazer isso funcionar?
}

fn primeira_palavra(s: String) -> String {
    s.split_whitespace().next().unwrap_or("").to_string()
}
```

*Dica: você não precisa ser dono da frase inteira só para ler a primeira palavra. Pense em `&str` — e olhe de novo o [post sobre ownership](../0005-entendendo-ownership-rust-guia-pythonistas).*

## O que aprendemos? 📚

- Rust separa em dois tipos o que o Python junta num só: `String` é **dona** do texto, `&str` é uma **vista emprestada**.
- Literais são `&str`; `String::from(...)` e `format!(...)` criam `String` que você possui.
- Regra de ouro: **receba `&str` em funções, guarde `String` em structs**.
- `+` entre strings **move** o operando da esquerda — prefira `format!`.
- Não dá pra indexar `String` por posição porque ela é UTF-8: use `.chars()` para caracteres e `.bytes()`/`.len()` para bytes.
- `.clone()` costuma ser medo disfarçado: quase sempre você só precisava emprestar com `&`.

## Próximos passos

Você deve ter reparado que `&str` é uma referência — e toda referência em Rust carrega uma pergunta implícita: *por quanto tempo o texto original vive?* Essa é exatamente a porta de entrada para [lifetimes](../0012-lifetimes-rust-pythonistas), o mecanismo que garante que um `&str` nunca aponte para memória que já foi liberada. É o próximo degrau natural da sua jornada.

---

Strings são só a ponta do iceberg de como Rust te faz pensar sobre posse de dados — e é justamente esse modelo mental que separa quem "escreve Rust brigando com o compilador" de quem escreve Rust com fluência. O livro **Desbravando Rust** constrói esse raciocínio passo a passo, sempre partindo do Python que você já domina. Conheça em [desbravandorust.com.br](https://desbravandorust.com.br) e transforme o compilador de inimigo em copiloto. 🦀
