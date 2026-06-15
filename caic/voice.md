# Voice

Voice mode lets you supervise and control tasks hands-free. You ask for status, answer an agent's questions, and steer work by speaking, which is useful when you are away from the keyboard or running several agents at once. Voice is available in the web app and in the [Go Mode Android app](./android).

## Enabling voice

caic derives voice support automatically from your configuration:

- **Embedded gateway**: set `GEMINI_API_KEY` and leave the gateway URL empty. caic hosts the voice gateway in-process using Gemini Live.
- **Standalone gateway**: set `[voice-gateway] url` to point at a gateway you run separately. caic advertises that gateway to clients.
- **Disabled**: with no URL and no `GEMINI_API_KEY`, voice is off.

Set `GEMINI_API_KEY` under `[core.env]` in `~/.config/caic/config.toml`:

```toml
[core.env]
GEMINI_API_KEY = "AIza..."
```

To point at a standalone gateway instead:

```toml
[voice-gateway]
url = "https://voice.example.com"
```

## Local stack

The local stack runs voice entirely on your own hardware with no cloud API key. Set the backend to `local-stack` and the gateway uses a managed [llama.cpp](https://github.com/ggml-org/llama.cpp) for speech recognition and the language model, and KittenTTS for speech synthesis. It is half-duplex, meaning you speak and listen in turns rather than at the same time.

```toml
[voice-gateway.config]
backend = "local-stack"
```

By default caic manages llama.cpp with a bundled model, so you do not need to run anything yourself. You can point at servers you run instead. See the [gateway config template](https://github.com/caic-xyz/caic/blob/main/contrib/voice-gateway-config.toml) for the local stack options.

## WebRTC and firewalls

Voice streams over WebRTC, which needs a reachable UDP port. By default caic uses an OS-assigned ephemeral port, which works for local use. For remote access, set a static port with `webrtc_udp_port` and open that UDP port in your firewall:

```toml
[voice-gateway.config.server]
webrtc_udp_port = 3479
```

See [Configuration](./configuration) for the full set of voice keys.
