#!/bin/bash
# Reproduces the version matrix in plugins/ocaml-lsp/README.md, in the official
# ocaml/opam images so it does not touch your own switches.
#   ./test/matrix.sh [ocaml versions...]     (default: 4.14 5.1 5.2 5.3 5.4)
set -u
D="$(mktemp -d)"; trap 'rm -rf "$D"' EXIT
cp "$(dirname "$(readlink -f "$0")")/lsp_probe.py" "$D/"
mkdir -p "$D/proj"
echo '(lang dune 3.0)'          > "$D/proj/dune-project"
echo '(library (name probe_lib))' > "$D/proj/dune"
echo 'let double x = x * 2'     > "$D/proj/probe.ml"
echo 'val double : int -> int'  > "$D/proj/probe.mli"

for V in "${@:-4.14 5.1 5.2 5.3 5.4}"; do
  IMG="docker.io/ocaml/opam:debian-ocaml-$V"
  echo "=========== ocaml $V ==========="
  podman pull -q "$IMG" >/dev/null 2>&1 || { echo "[ocaml $V] image unavailable"; continue; }
  podman run --rm -v "$D:/host:ro,Z" "$IMG" bash -lc '
    set -e
    sudo apt-get update -qq >/dev/null 2>&1
    sudo apt-get install -y -qq python3 >/dev/null 2>&1
    opam update -y >/dev/null 2>&1
    opam install -y dune ocaml-lsp-server >/dev/null 2>&1
    LSPV=$(opam list --installed --short --columns=version ocaml-lsp-server)
    mkdir -p ~/proj && cp /host/proj/dune-project /host/proj/dune /host/proj/probe.ml /host/proj/probe.mli ~/proj/
    cd ~/proj && dune build 2>&1 | tail -2
    python3 /host/lsp_probe.py "$HOME/proj" "ocaml $(ocamlc -version) / lsp $LSPV"
  ' || echo "[ocaml $V] FAILED"
done
