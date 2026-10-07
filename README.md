# docs.caic.xyz

End-user documentation for caic and md. Go Mode owns its native shell and shared
voice documentation at [docs.gomode.dev](https://docs.gomode.dev/).

## Build and preview

```bash
pnpm install --frozen-lockfile
pnpm run fix
pnpm run verify
pnpm run build
pnpm run preview --host 0.0.0.0
```

The build uses committed screenshots and checks their catalog hashes. It needs
neither a sibling checkout nor an Android emulator.

## Refresh screenshots

In a sibling caic checkout, run its screenshot update and check targets first:

```bash
make -C ../caic screenshots-update
make -C ../caic screenshots-check
pnpm run screenshots:import
```

For another checkout, pass `--source /path/to/caic/e2e/screenshots/frontend`.
The importer reads the capture manifest, checks hashes and dimensions, and
publishes only the web screenshots referenced by site pages. The
committed subset manifest preserves the producer revision and capture-input
fingerprint, including captures made before their source changes are committed.
`pnpm run screenshots:check` validates published assets without the source repo.
Native Go Mode captures belong on the Go Mode sites.

Screenshot refreshes serialize through a local advisory lock. New assets are
staged and verified before publication. An interrupted refresh retains the
previous catalog outside the published directory; run `pnpm run screenshots:import`
to recover it. Read-only checks refuse unfinished publication with an actionable
error and leave the recovery files intact.

## Cloudflare publication

The Worker `caic-xyz-docs` serves `.vitepress/dist` on `docs.caic.xyz`. Custom
domain routing is declared in `wrangler.jsonc`; Cloudflare manages DNS and TLS
for a zone in the same account. `pnpm exec wrangler deploy --dry-run` validates
the Worker locally. No credentials are needed for a dry run.

Connect `main` to this Worker through Cloudflare Workers Builds and set:

- Build command: `pnpm install --frozen-lockfile && pnpm run build`
- Deploy command: `pnpm exec wrangler deploy`
- Version command: `pnpm exec wrangler versions upload`
- Build variable: `SKIP_DEPENDENCY_INSTALL` = `1`

Workers Builds settings live in the Cloudflare dashboard. The committed lockfile
and package manager configuration own dependency installation. Manual publication
is `pnpm run deploy` after verification; local builds do not publish.

See Cloudflare's [custom domain guide](https://developers.cloudflare.com/workers/configuration/routing/custom-domains/)
and [Workers Builds configuration](https://developers.cloudflare.com/workers/ci-cd/builds/configuration/).
