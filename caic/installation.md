# Installation

## Prerequisites

- Go 1.21+
- Docker installed and running
- [md](../md/installation) installed (caic uses it to manage containers)

## Install the binary

```bash
go install github.com/caic-xyz/caic/backend/cmd/caic@latest
```

## Next steps

- [Configure caic](./configuration) — environment variables, auth modes, systemd service
- [Forge integration](./forge) — connect GitHub or GitLab for automatic PR/MR creation
- [Android app](./android) — build and install the companion app
