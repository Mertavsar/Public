// Tüm kareleri paralel render eder: node render.cjs [işçi sayısı=4]
const { spawn } = require("child_process"); const fs = require("fs");
const END = JSON.parse(fs.readFileSync(__dirname + "/timeline.json", "utf8")).END, N = Math.ceil(END * 30), K = +(process.argv[2] || 4), Q = Math.ceil(N / K);
fs.mkdirSync(__dirname + "/fr", { recursive: true }); const t0 = Date.now(); let left = K;
for (let w = 0; w < K; w++) { const a = w * Q, b = Math.min(N, a + Q);
  const p = spawn(process.execPath, [__dirname + "/cap.cjs", "frames", a, b, __dirname + "/fr"], { env: Object.assign({}, process.env, { NOCAP: "1" }), stdio: "inherit" });
  p.on("exit", () => { if (--left === 0) console.log(`bitti: ${fs.readdirSync(__dirname + "/fr").length}/${N} kare, ${Math.round((Date.now() - t0) / 1000)} sn`); }); }
setInterval(() => { const n = fs.readdirSync(__dirname + "/fr").length; process.stdout.write(`\r${n}/${N}`); if (n >= N) process.exit(0); }, 5000).unref();
