# Voice

Use voice to ask about tasks, answer an agent's question, and steer work away from the keyboard. caic supplies task-specific tools and context; [Go Mode](https://docs.gomode.dev/guide/voice) supplies the shared voice interface and gateway. Voice is available in the web app and the [Go Mode Android shell](./android).

## Start a session

Press `F4` in the web app to start or stop voice mode, including while the composer has focus. Say “hang up”, “end call”, or “stop voice mode” to end the session.

On a phone, the voice panel stays at the bottom of the screen, and the task prompt stays above it while you scroll.

caic announces every task transition to waiting, asking, failed, or crashed immediately, before answering anything else, even when no one asked for a status update. For a failure, it reads the recorded error instead of an unknown cause.

Voice numbers active tasks before settled tasks. Check the visible list when a number could be ambiguous. The voice interface's supported speech modes and language settings depend on the client platform; see the [Go Mode voice guide](https://docs.gomode.dev/guide/voice).

## Embedded gateway

Voice stays disabled until you choose a mode. Set `mode = "embedded"` to host the gateway inside caic:

```toml
[voice-gateway]
mode = "embedded"
```

The embedded gateway offers the same voice choices as the [standalone Go Mode gateway](https://docs.gomode.dev/guide/voice#voice-choices): realtime models, separate recognition, language model, and speech stages, and local models. Without a `voice-choices.toml` file beside `config.toml`, caic uses the defaults built into its release. Copy the [default choices](https://github.com/gomodedev/gomode/blob/main/voicegateway/voice-choices.toml) to customize them; the copy replaces the defaults entirely.

Provider API keys such as `GEMINI_API_KEY` come from caic's process environment, including values imported from your login shell. `[core.env]` does not supply them. Audio for a cloud choice is sent to that provider.

## Standalone gateway

A standalone gateway lets you run voice separately from caic. Set `mode = "external"`, a fixed service URL and instance ID, and choose its session credential mode. Before using OAuth credentials, configure a supported [dashboard login provider](./configuration#github) so caic can issue and verify authenticated sessions. Then add:

```toml
[server]
external_url = "https://caic.example.com"

[voice-gateway]
mode = "external"
url = "https://voice.example.com"
instance_id = "caic-main"
token_mode = "oauth"
```

Configure the gateway to trust service `caic` with issuer `https://caic.example.com` and `oauth = true`. The gateway discovers caic's verification keys through authorization-server metadata. caic issues short-lived voice-only credentials rather than sharing provider or forge tokens.

The default `token_mode = "scoped"` uses a separate Ed25519 signing key instead. Generate it with:

```bash
openssl genpkey -algorithm Ed25519 -out ~/.config/caic/voice-signing-key.pem
```

Change `token_mode` to `"scoped"` and set `signing_private_key_pem = "voice-signing-key.pem"` alongside `instance_id`, and configure the gateway's trusted issuer with the public key printed by caic at startup. See [Go Mode voice](https://docs.gomode.dev/guide/voice) for gateway installation and trust configuration.

## Network access

The embedded gateway's WebRTC audio needs a reachable UDP port. The default chooses an ephemeral port; the gateway can request a temporary UPnP mapping on a compatible router. To create a stable firewall rule, set a fixed port:

```toml
[voice-gateway]
mode = "embedded"
webrtc_udp_port = 3479
```

Allow that UDP port through your firewall. Signaling also needs access to the gateway's HTTP endpoint. A working HTTPS page does not prove that WebRTC UDP traffic can reach the gateway.

See [Configuration](./configuration#voice-gateway) for caic's gateway fields and [Security](./security#voice-security) for the trust boundary.
