// Installs the check tools pinned in package.json's tools field, leaving matching tools alone.
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const repositoryDirectory = join(dirname(fileURLToPath(import.meta.url)), "..");
const { tools } = JSON.parse(readFileSync(join(repositoryDirectory, "package.json"), "utf8"));

if (typeof tools !== "object" || tools === null) {
  throw new Error("package.json is missing the tools field.");
}

function uv(args) {
  const result = spawnSync("uv", args, { cwd: repositoryDirectory, encoding: "utf8" });
  if (result.error !== undefined) {
    console.error("uv is required to install the pinned tools: https://docs.astral.sh/uv/");
    console.error(result.error.message);
    process.exit(1);
  }
  if (result.status !== 0) {
    process.stderr.write(result.stderr ?? "");
    process.exit(result.status ?? 1);
  }
  return result.stdout ?? "";
}

const installed = new Set(
  uv(["tool", "list"])
    .split("\n")
    .map((line) => line.trim()),
);

for (const [name, version] of Object.entries(tools)) {
  if (installed.has(`${name} v${version}`)) {
    continue;
  }
  uv(["tool", "install", "--force", "--quiet", `${name}==${version}`]);
}
