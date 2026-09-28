# docs.caic.xyz

```bash
pnpm install
pnpm run build
pnpm run dev --host 0.0.0.0
```

## Git deployments

Connect `main` to the `caic-xyz-docs` Worker in Cloudflare Workers →
Settings → Build. Set:

- Build command: `pnpm run build`.
- Deploy command: `pnpm exec wrangler deploy`.
- Version command: `pnpm exec wrangler versions upload`.

Workers Builds settings live in Cloudflare. `wrangler.jsonc` configures
the Worker itself.
