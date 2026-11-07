// Integers 0..n-1 from JavaScript (Node.js), two ways. Math.random() cannot be seeded.
//   floorrandom : Math.floor(Math.random() * n)   (mult; V8 fills 52 mantissa bits)
//   cryptorandint : crypto.randomInt(n)           (rejection: unbiased)
// Usage: node src/languages/javascript/sample_js.js <n> <N> <outdir>
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const [n, N] = [Number(process.argv[2]), Number(process.argv[3])];
const out = process.argv[4];
fs.mkdirSync(out, { recursive: true });
const tag = `n${n}_N${N}_noseed`;

function dump(name, f) {
  const lines = new Array(N);
  for (let i = 0; i < N; i++) lines[i] = String(f());
  fs.writeFileSync(path.join(out, `js_${name}_${tag}.txt`), lines.join("\n") + "\n");
}
dump("floorrandom", () => Math.floor(Math.random() * n));
dump("cryptorandint", () => crypto.randomInt(n));
fs.writeFileSync(path.join(out, "version.txt"), `node ${process.version} v8 ${process.versions.v8}\n`);
