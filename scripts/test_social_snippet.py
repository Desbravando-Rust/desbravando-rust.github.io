from social_snippet import parse_post, format_linkedin, slug_from_path

SAMPLE = """# Macros em Rust: Automatizando Código
###### Por [@zejuniortdr](https://github.com/zejuniortdr/) em Mai 12, 2026

![Macros em Rust](imgs/cover.png)

Metaprogramação é a arte de escrever código que gera outro código.

## Seção

```rust
macro_rules! diga {
    () => { println!("oi"); };
}
```
"""

def test_parse_extrai_titulo_numero_e_paragrafo():
    p = parse_post(SAMPLE, "0014-macros-em-rust")
    assert p["titulo"] == "Macros em Rust: Automatizando Código"
    assert p["numero"] == "0014"
    assert p["primeiro_paragrafo"].startswith("Metaprogramação é a arte")
    assert "###### Por" not in p["primeiro_paragrafo"]
    assert p["url"] == "https://desbravandorust.com.br/posts/0014-macros-em-rust/"

def test_parse_captura_primeiro_bloco_de_codigo():
    p = parse_post(SAMPLE, "0014-macros-em-rust")
    assert "macro_rules!" in p["codigo"]

def test_parse_sem_codigo_retorna_none():
    md = "# T\n###### Por x em Y\n\n![a](imgs/cover.png)\n\nParágrafo só.\n"
    p = parse_post(md, "0001-x")
    assert p["codigo"] is None

def test_format_linkedin_inclui_gancho_e_link_no_fim():
    p = parse_post(SAMPLE, "0014-macros-em-rust")
    out = format_linkedin(p)
    assert "Macros em Rust" in out
    assert out.rstrip().endswith("https://desbravandorust.com.br/posts/0014-macros-em-rust/")
    assert "#rustlang" in out

def test_slug_from_path_relativo_absoluto_e_dotslash():
    assert slug_from_path("posts/0014-macros-rust-pythonistas/README.md") == "0014-macros-rust-pythonistas"
    assert slug_from_path("./posts/0014-macros-rust-pythonistas/README.md") == "0014-macros-rust-pythonistas"
    assert slug_from_path("/abs/repo/posts/0007-enums/README.md") == "0007-enums"

if __name__ == "__main__":
    import sys
    n = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn(); n += 1; print("ok:", name)
    print(f"\n{n} testes passaram")
    sys.exit(0)
