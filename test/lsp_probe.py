"""LSP probe: checks exactly what the ocaml-lsp plugin declares, nothing more.
Usage: lsp_probe.py <dune project root> <label>"""
import json, subprocess, sys, os, threading, time

ROOT, LABEL = sys.argv[1], sys.argv[2]

def frame(o):
    b = json.dumps(o).encode()
    return f"Content-Length: {len(b)}\r\n\r\n".encode() + b

def reader(p, out):
    while True:
        n = None
        while True:
            line = p.stdout.readline()
            if not line: return
            if line in (b"\r\n", b"\n"): break
            if line.lower().startswith(b"content-length:"):
                n = int(line.split(b":")[1])
        if n is None: continue
        buf = b""
        while len(buf) < n:
            c = p.stdout.read(n - len(buf))
            if not c: return
            buf += c
        out.append(json.loads(buf))

# exactly the extensions the plugin declares
CASES = [("probe.ml", "ocaml"), ("probe.mli", "ocaml.interface")]

p = subprocess.Popen(["ocamllsp", "--stdio"], stdin=subprocess.PIPE,
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=ROOT)
msgs = []
threading.Thread(target=reader, args=(p, msgs), daemon=True).start()
p.stdin.write(frame({"jsonrpc":"2.0","id":1,"method":"initialize","params":{
    "processId": os.getpid(), "rootUri": f"file://{ROOT}",
    "capabilities": {"textDocument":{"hover":{"contentFormat":["plaintext"]}}}}}))
p.stdin.write(frame({"jsonrpc":"2.0","method":"initialized","params":{}}))
p.stdin.flush()

for i, (rel, lang) in enumerate(CASES):
    path = os.path.join(ROOT, rel)
    text = open(path).read()
    uri = f"file://{path}"
    p.stdin.write(frame({"jsonrpc":"2.0","method":"textDocument/didOpen","params":{
        "textDocument":{"uri":uri,"languageId":lang,"version":1,"text":text}}}))
    p.stdin.write(frame({"jsonrpc":"2.0","id":100+i,"method":"textDocument/documentSymbol",
                         "params":{"textDocument":{"uri":uri}}}))
    # hover on `double` (line 0, column 4 of probe.ml / probe.mli)
    p.stdin.write(frame({"jsonrpc":"2.0","id":200+i,"method":"textDocument/hover","params":{
        "textDocument":{"uri":uri},"position":{"line":0,"character":4}}}))
    p.stdin.flush()
time.sleep(8)
p.stdin.write(frame({"jsonrpc":"2.0","id":99,"method":"shutdown","params":None}))
p.stdin.flush(); time.sleep(1); p.kill()

by_id = {m["id"]: m for m in msgs if "id" in m and m.get("method") is None}
caps = by_id.get(1, {}).get("result", {}).get("capabilities", {})
diags = [m for m in msgs if m.get("method") == "textDocument/publishDiagnostics"]
rows = []
ok = bool(caps)
for i, (rel, lang) in enumerate(CASES):
    sym, hov = by_id.get(100+i, {}), by_id.get(200+i, {})
    def state(r, kind):
        if "error" in r: return f"ERROR({r['error'].get('message')})"
        if "result" not in r: return "no response"
        v = r["result"]
        if v is None: return "null"
        return f"{len(v)} sym." if kind == "sym" else "type returned"
    s, h = state(sym, "sym"), state(hov, "hov")
    rows.append((rel, lang, s, h))
    if not (s.endswith("sym.") and h == "type returned"): ok = False

print(f"[{LABEL}] initialize: {len(caps)} capabilities | hover:{'hoverProvider' in caps} "
      f"definition:{'definitionProvider' in caps} publishDiagnostics:{len(diags)>0}")
for rel, lang, s, h in rows:
    print(f"[{LABEL}]   {rel:10} ({lang:16}) documentSymbol: {s:20} hover: {h}")
print(f"[{LABEL}] VERDICT: {'OK' if ok else 'FAILED'}")
sys.exit(0 if ok else 1)
