# Voice

Voice mode lets you supervise and control tasks hands-free. You ask for status, answer an agent's questions, and steer work by speaking, which is useful when you are away from the keyboard or running several agents at once. Voice is available in the web app and in the [Go Mode Android app](./android).

## Using voice

Press `F4` in the web app to start or stop voice mode, even when the task editor has focus. You can also say "hang up", "end call", or "stop voice mode" to end the session.

Voice presents active tasks before settled tasks when assigning task numbers. This keeps the tasks most likely to need attention easy to reference. Check the visible task list when a number could be ambiguous.

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

The local stack processes voice entirely on your own hardware. Set the backend to `local-stack` and the gateway uses managed [llama.cpp](https://github.com/ggml-org/llama.cpp) servers for speech recognition and the language model, plus KittenTTS for speech synthesis. It is half-duplex, meaning you speak and listen in turns rather than at the same time.

```toml
[voice-gateway.config]
backend = "local-stack"
```

The current embedded-gateway activation also requires `GEMINI_API_KEY` to be present. The local-stack backend does not consume that key or send audio to Gemini.

By default caic manages a Qwen3 ASR model, a Gemma LLM, and a KittenTTS worker, so you do not need to run anything yourself. You can point ASR or LLM at servers you run instead. See the [gateway config template](https://github.com/caic-xyz/caic/blob/main/contrib/voice-gateway-config.toml) for the local stack options.

## WebRTC and firewalls

Voice streams over WebRTC, which needs a reachable UDP port. By default caic uses an OS-assigned ephemeral port, which works for local use. When a browser connects from outside your LAN, caic automatically asks a compatible UPnP router to map the selected UDP port and advertises that external address. The mapping is removed when the gateway stops.

For a firewall rule that stays the same across restarts, set a static port with `webrtc_udp_port` and open that UDP port in your firewall:

```toml
[voice-gateway.config.server]
webrtc_udp_port = 3479
```

See [Configuration](./configuration) for the full set of voice keys.
