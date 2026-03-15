# Installation

## Prerequisites

- Docker installed and running

## Install

```bash
curl caic.xyz/install.sh | bash
```

This installs both `caic` and `md` binaries.

## Install from source

### Dependencies

- Go 1.25+
- Docker installed and running

### Build and install

```bash
go install github.com/caic-xyz/caic/backend/cmd/caic@latest
```

## Next steps

- [Configure caic](./configuration) — environment variables, auth modes, systemd service
- [GitHub integration](./github) — connect GitHub for automatic PR creation
- [GitLab integration](./gitlab) — connect GitLab for automatic MR creation
- [Android app](./android) — build and install the companion app
