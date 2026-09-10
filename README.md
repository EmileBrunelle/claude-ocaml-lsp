# claude-ocaml-lsp

An [OCaml language server](https://github.com/ocaml/ocaml-lsp) plugin for
[Claude Code](https://claude.com/claude-code), so Claude reads types,
signatures and compiler diagnostics from `ocamllsp` instead of inferring them
from the source text.

There is no OCaml entry among Claude Code's official LSP plugins (Rust, Go,
Java, Swift, Python, Ruby, C/C++, C#, Kotlin, Lua, PHP, TypeScript). This is
that entry, in the same shape.

## Install

```
/plugin marketplace add EmileBrunelle/claude-ocaml-lsp
/plugin install ocaml-lsp@ocaml-lsp
```

The server itself is not bundled — see
[`plugins/ocaml-lsp/README.md`](plugins/ocaml-lsp/README.md) for
`opam install ocaml-lsp-server`, the `eval $(opam env)` requirement, and the
tested version matrix.

## What it declares

`.ml` → `ocaml`, `.mli` → `ocaml.interface`, over `ocamllsp --stdio`.
Nothing else, on purpose: the server accepts `.mll`, `.mly`, `.t`, `.re` and
`.mlx` documents but returns no symbols or types for them, and a file Claude
believes it understands but knows nothing about is worse than an undeclared
one.

## Contributing

The whole plugin is one manifest, so there is little to change — except the
one thing that must not change casually: the declared extensions.

Adding one means proving it, not assuming it. Add the case to `CASES` in
[`test/lsp_probe.py`](test/lsp_probe.py), then run one version:

```bash
./test/matrix.sh 5.3      # official ocaml/opam image, ~5 min, touches no switch of yours
```

An extension earns its place in `extensionToLanguage` only if
`documentSymbol` returns symbols *and* `hover` returns a type. `.mll`,
`.mly`, `.t`, `.re` and `.mlx` all fail that bar today — the server accepts
the document and answers `null`. Declaring them would hand Claude files it
believes it understands and knows nothing about.

Bump `version` in `plugins/ocaml-lsp/.claude-plugin/plugin.json` when the
manifest changes: Claude Code only offers installed users an update when that
field moves. README-only changes don't need it.

## License

ISC, matching upstream `ocaml-lsp-server`.
