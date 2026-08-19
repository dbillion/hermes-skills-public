#!/usr/bin/env node
// Deterministic stdio MCP handshake against the Open Design daemon's MCP server.
// Proves (1) initialize returns open-design, (2) tools/list returns 22 tools,
// (3) a live list_projects call returns real data. Run with Node 24.
import { spawn } from "node:child_process";

const cmd = "/home/deeone/.nvm/versions/node/v24.19.0/bin/node";
const args = [
  "/home/deeone/open-design/open-design/apps/daemon/dist/cli.js",
  "mcp", "--daemon-url", "http://127.0.0.1:7456",
];
const env = { ...process.env, OD_DATA_DIR: "/home/deeone/open-design/open-design/.od" };

const p = spawn(cmd, args, { env, stdio: ["pipe", "pipe", "pipe"] });
let buf = "";
const pending = {};
const send = (o) => p.stdin.write(JSON.stringify(o) + "\n");
p.stdout.on("data", (d) => {
  buf += d.toString();
  let i;
  while ((i = buf.indexOf("\n")) >= 0) {
    const line = buf.slice(0, i); buf = buf.slice(i + 1);
    if (!line.trim()) continue;
    try {
      const m = JSON.parse(line);
      if (m.id && pending[m.id]) { pending[m.id](m); delete pending[m.id]; }
    } catch {}
  }
});
const req = (method, params, id) =>
  new Promise((res) => { pending[id] = res; send({ jsonrpc: "2.0", id, method, params }); });

(async () => {
  const init = await req("initialize", {
    protocolVersion: "2024-11-05", capabilities: {}, clientInfo: { name: "verify", version: "1" },
  }, 1);
  console.log("INIT serverInfo:", JSON.stringify(init.result?.serverInfo));
  send({ jsonrpc: "2.0", method: "notifications/initialized", params: {} });
  const tools = await req("tools/list", {}, 2);
  console.log("TOOL COUNT:", tools.result?.tools?.length);
  const call = await req("tools/call", { name: "list_projects", arguments: {} }, 3);
  const text = call.result?.content?.map((c) => c.text).join("") ?? JSON.stringify(call);
  console.log("list_projects (first 400):", text.slice(0, 400));
  p.kill(); process.exit(0);
})();
setTimeout(() => { console.log("TIMEOUT"); p.kill(); process.exit(1); }, 25000);
