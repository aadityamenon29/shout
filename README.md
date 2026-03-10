# Shout

Push-to-talk speech-to-text for macOS. Hold a key, speak, release — your words get typed into whatever app is focused.

Uses [Whisper](https://github.com/ggerganov/whisper.cpp) for transcription. Runs entirely on-device, no API calls, no cloud.

## Quickstart

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/aadityamenon29/shout.git
cd shout
make setup   # downloads Whisper model (~466MB) + installs deps
make run
```

On first launch, Shout will prompt you to grant the macOS permissions it needs (see below).

## How it works

1. **Hold Right Option** key to start recording
2. **Speak**
3. **Release** the key — Shout transcribes and pastes the text into your active app

A red dot appears in the menu bar while recording, and an hourglass while transcribing.

### Send triggers

End your speech with **"over"**, **"enter"**, or **"send"** and Shout will press Enter after pasting — useful for chat apps.

## macOS Permissions

Shout needs three permissions. macOS will prompt you on first use, or you can grant them ahead of time in **System Settings > Privacy & Security**:

| Permission | Why | Settings path |
|---|---|---|
| **Accessibility** | Simulate keyboard input (Cmd+V to paste) | Privacy & Security > Accessibility |
| **Input Monitoring** | Listen for the hotkey | Privacy & Security > Input Monitoring |
| **Microphone** | Record audio | Privacy & Security > Microphone |

Grant these to your **terminal app** (e.g. Terminal, iTerm, Ghostty) or to **Python** if it appears.

You can check your permissions anytime:

```bash
make check
```

## Troubleshooting

**"Whisper model not found"** — Run `make setup` to download the model.

**Text isn't pasting** — Accessibility permission is probably missing. Check `make check` and grant access in System Settings.

**No audio / silence** — Microphone permission is missing, or the wrong input device is selected in System Settings > Sound.

**Hotkey not working** — Input Monitoring permission is missing. Grant it to your terminal app and restart Shout.

## License

MIT
