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

`ocamllsp` is not bundled with the compiler, and it is not in any system
package manager worth using (see below). opam is the route:

```bash
opam install ocaml-lsp-server
eval $(opam env)                # required: the binary lives in the switch
```

Install it into the switch you are working in, not once and globally: the
server has to match the compiler that built the project.

### macOS

Homebrew has no `ocaml-lsp` formula — it packages `ocaml` and `opam` only. So
Homebrew gets you opam, and opam gets you the server:

```bash
brew install opam
opam init && opam install ocaml-lsp-server
```

### Nix

```bash
nix-shell -p ocamlPackages.ocaml-lsp
```

Nixpkgs pins a different `ocaml-lsp` version per compiler, the same way opam
resolves a different one per switch.

### Windows

Untested — treat this as an open question, not a claim. opam has had native
Windows support since 2.2, so `ocamllsp.exe` can be on `PATH`; what has not
been verified here is whether the bare `ocamllsp` command in the manifest
resolves to it. WSL2 is the route that certainly works, since it is Linux.
Reports either way are welcome.

### Where it is *not* packaged

Checked 2026-09-10, so that nobody burns an afternoon on it:

| | |
|---|---|
| Homebrew | no `ocaml-lsp` or `ocaml-lsp-server` formula |
| Debian / Ubuntu | no `apt` package (searched trixie) |
| Fedora | no `dnf` package |
| Arch | not in the official repos; AUR has only `ocaml-lsp-git`, an unversioned git snapshot with no votes |

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

| OCaml | ocaml-lsp-server | Capabilities | `.ml` | `.mli` | Where |
|---|---|---|---|---|---|
| 4.14.4 | 1.21.0-4.14 | 22 | OK | OK | Fedora host + Debian container |
| 5.1.1 | 1.18.0 | 22 | OK | OK | Debian container |
| 5.2.1 | 1.21.0 | 22 | OK | OK | Debian container |
| 5.3.0 | 1.23.1 | 22 | OK | OK | Fedora host + Debian container |
| 5.4.1 | 1.26.0 | 23 | OK | OK | Fedora host + Debian container |
| 5.5.1 | 1.27.0 | 23 | OK | OK | Fedora host |

`hoverProvider`, `definitionProvider` and `publishDiagnostics` are present in
every row. The plugin pins no version — it runs whatever `ocamllsp` the switch
provides — so the oldest row is what matters: `ocaml.interface` is already
accepted by 1.18.0, nine releases before the version this was written against.

Every row is Linux. Host rows: Fedora 44, dune 3.24.2, opam 2.5.2. Container rows: official
`ocaml/opam:debian-ocaml-*` images, whose pinned opam snapshot is what selects
each `ocaml-lsp-server` version. Re-run the matrix yourself with
[`test/matrix.sh`](../../test/matrix.sh) — it uses the official `ocaml/opam`
container images and leaves your switches alone.

## More Information

- [ocaml-lsp repository](https://github.com/ocaml/ocaml-lsp) (ISC)
- [OCaml Platform](https://ocaml.org/tools)
