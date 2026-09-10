#!/bin/bash
# Reproduces the version matrix in plugins/ocaml-lsp/README.md, in the official
# ocaml/opam images, so it touches none of your own opam switches.
#   ./test/matrix.sh [ocaml versions...]     (default: 4.14 5.1 5.2 5.3 5.4)
#
# The probe and the test project are passed in as base64 through the
# environment rather than a bind mount: rootless podman remaps uids, so a
# mounted host directory is unreadable inside the container.
set -u
HERE="$(dirname "$(readlink -f "$0")")"
PROBE_B64="$(base64 -w0 "$HERE/lsp_probe.py")"

PAYLOAD='
set -e
sudo apt-get update -qq >/dev/null 2>&1
sudo apt-get install -y -qq python3 >/dev/null 2>&1
opam install -y dune ocaml-lsp-server >/dev/null 2>&1
LSPV=$(opam list --installed --short --columns=version ocaml-lsp-server)
mkdir -p ~/proj
printf "%s\n" "$PROBE_B64" | base64 -d > ~/lsp_probe.py
echo "(lang dune 3.0)"           > ~/proj/dune-project
echo "(library (name probe_lib))" > ~/proj/dune
echo "let double x = x * 2"       > ~/proj/probe.ml
echo "val double : int -> int"    > ~/proj/probe.mli
cd ~/proj && dune build 2>&1 | tail -2
python3 ~/lsp_probe.py "$HOME/proj" "ocaml $(ocamlc -version) / lsp $LSPV"
'

for V in "${@:-4.14 5.1 5.2 5.3 5.4}"; do
  IMG="docker.io/ocaml/opam:debian-ocaml-$V"
  echo "=========== ocaml $V ==========="
  podman pull -q "$IMG" >/dev/null 2>&1 || { echo "[ocaml $V] image unavailable"; continue; }
  podman run --rm -e PROBE_B64="$PROBE_B64" "$IMG" bash -lc "$PAYLOAD" \
    || echo "[ocaml $V] FAILED (exit $?)"
done
