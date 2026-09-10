# ocaml-lsp

OCaml language server for Claude Code, providing code intelligence and analysis.

Wraps [`ocaml-lsp-server`](https://github.com/ocaml/ocaml-lsp) (the `ocamllsp`
binary), the language server behind the OCaml Platform editor extensions.
It reads its per-file configuration from Dune, so the project must build.

## Supported Extensions

`.ml`, `.mli`

Other syntaxes `ocamllsp` accepts (`.mll`, `.mly`, `.t`, `.re`/`.rei`,
`.mlx`, `.eliom`) are deliberately not declared: the server takes the
documents but returns no symbols or types for them, so there is nothing for
Claude to read.

## Installation

`ocamllsp` is not bundled with the compiler — install it into the switch you
are working in, not globally:

```bash
opam install ocaml-lsp-server
eval $(opam env)                # required: the binary lives in the switch
```

### Via package manager

```bash
# Nix
nix-shell -p ocamlPackages.ocaml-lsp

# Arch Linux
sudo pacman -S ocaml-lsp
```

## Requirements

- **Launch `claude` from a shell where `eval $(opam env)` has run.** The
  binary sits in `~/.opam/<switch>/bin`, which is not on the default `PATH`;
  without it the server never starts. This is the same failure mode as OCaml
  autocompletion dying in VS Code.
- **The project must build.** `ocamllsp` gets its include paths and flags from
  `dune ocaml-merlin`, so types and diagnostics on a project that does not
  compile are partial at best. Run `dune build` first.
- One switch per project: a server from switch A cannot type-check code
  compiled against switch B's compiler.

## Tested versions

Every row was checked by driving the server over stdio: `initialize`, then
`didOpen` + `documentSymbol` + `hover` on a `.ml` and a `.mli` in a built Dune
project. A row is OK only if both files return symbols *and* a type.

| OCaml | ocaml-lsp-server | Capabilities | `.ml` | `.mli` | Result |
|---|---|---|---|---|---|
| 4.14.4 | 1.21.0-4.14 | 22 | OK | OK | OK |
| 5.3.0 | 1.23.1 | 22 | OK | OK | OK |
| 5.4.1 | 1.26.0 | 23 | OK | OK | OK |
| 5.5.1 | 1.27.0 | 23 | OK | OK | OK |

`hoverProvider`, `definitionProvider` and `publishDiagnostics` are present in
every row. The plugin pins no version — it runs whatever `ocamllsp` the switch
provides — so the oldest row is what matters: `ocaml.interface` is already
accepted by 1.21.0, the version opam resolves for a 4.14 switch.

Host: Fedora 44, dune 3.24.2, opam 2.5.2. Re-run the matrix yourself with
[`test/matrix.sh`](../../test/matrix.sh) — it uses the official `ocaml/opam`
container images and leaves your switches alone.

## More Information

- [ocaml-lsp repository](https://github.com/ocaml/ocaml-lsp) (ISC)
- [OCaml Platform](https://ocaml.org/tools)
