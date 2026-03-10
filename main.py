import os
import subprocess
import threading

import rumps
from pynput.keyboard import Key, Listener

from audio import AudioRecorder
from transcriber import transcribe, get_model
from paster import paste_text, process_text

# Right Option key code on macOS
RIGHT_OPTION_KEY = Key.alt_r

_SOUNDS = "/System/Library/Sounds"


def _beep(name: str):
    """Play a system sound in the background."""
    subprocess.Popen(["afplay", f"{_SOUNDS}/{name}.aiff"])


class ShoutApp(rumps.App):
    def __init__(self):
        super().__init__("Shout", title="🎤")
        self._status_item = rumps.MenuItem("Status: Idle")
        self.menu = [
            self._status_item,
            None,  # separator
            rumps.MenuItem("Quit", callback=self._quit),
        ]
        self.recorder = AudioRecorder()
        self._recording = False
        self._start_hotkey_listener()
        # Preload Whisper model in background so first transcription is fast
        threading.Thread(target=get_model, daemon=True).start()

    def _start_hotkey_listener(self):
        self._listener = Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release,
        )
        self._listener.daemon = True
        self._listener.start()

    def _on_key_press(self, key):
        if key == RIGHT_OPTION_KEY and not self._recording:
            self._recording = True
            self.title = "🔴"
            self._status_item.title = "Status: Recording..."
            self.recorder.start()
            _beep("Tink")
            print("[shout] Recording started")

    def _on_key_release(self, key):
        if key == RIGHT_OPTION_KEY and self._recording:
            self._recording = False
            self.title = "⏳"
            self._status_item.title = "Status: Transcribing..."
            wav_path = self.recorder.stop()
            print(f"[shout] Recording stopped, wav={wav_path}")
            if wav_path:
                threading.Thread(
                    target=self._transcribe_and_paste,
                    args=(wav_path,),
                    daemon=True,
                ).start()
            else:
                self._set_idle()

    def _transcribe_and_paste(self, wav_path: str):
        try:
            text = transcribe(wav_path)
            print(f"[shout] Transcribed: {text!r}")
            if text:
                text, send = process_text(text)
                paste_text(text, send=send)
                _beep("Pop")
                print(f"[shout] Pasted (send={send})")
        except Exception as e:
            print(f"[shout] Error: {e}")
            try:
                rumps.notification("Shout", "Transcription error", str(e))
            except Exception:
                pass
        finally:
            os.unlink(wav_path)
            self._set_idle()

    def _set_idle(self):
        self.title = "🎤"
        self._status_item.title = "Status: Idle"

    def _quit(self, _):
        if self._listener:
            self._listener.stop()
        rumps.quit_application()


def _check_permissions_gui():
    """Walk the user through each missing permission one at a time."""
    from permissions import get_missing_permissions, open_settings

    missing = get_missing_permissions()
    if not missing:
        return

    total = len(missing)
    for i, perm in enumerate(missing, 1):
        response = rumps.alert(
            title=f"Shout Setup ({i}/{total}): {perm['name']}",
            message=f"{perm['why']}\n\n{perm['how']}",
            ok="Open Settings",
            cancel="Skip",
        )
        if response == 1:  # OK
            open_settings(perm["name"])
            # Wait for user to grant permission before moving on
            rumps.alert(
                title=f"{perm['name']}",
                message=(
                    f"Once you've enabled {perm['name']} access, click OK to continue.\n\n"
                    "Note: you may need to restart Shout for changes to take effect."
                ),
                ok="OK",
            )


if __name__ == "__main__":
    _check_permissions_gui()
    ShoutApp().run()
