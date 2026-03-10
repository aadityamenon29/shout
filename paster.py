import subprocess
import time

from pynput.keyboard import Controller, Key

_keyboard = Controller()


def _pbcopy(text: str):
    subprocess.run(["pbcopy"], input=text.encode(), check=True)


def _pbpaste() -> str:
    return subprocess.run(["pbpaste"], capture_output=True, check=True).stdout.decode()


def _cmd_v_pynput():
    _keyboard.press(Key.cmd)
    _keyboard.press("v")
    _keyboard.release("v")
    _keyboard.release(Key.cmd)


def _cmd_v_applescript():
    subprocess.run([
        "osascript", "-e",
        'tell application "System Events" to keystroke "v" using command down',
    ], check=True)


def _press_enter():
    _keyboard.press(Key.enter)
    _keyboard.release(Key.enter)


# Trigger words that cause Enter to be pressed after pasting (case-insensitive)
_SEND_TRIGGERS = ("over", "enter", "send")


def process_text(text: str) -> tuple[str, bool]:
    """Check if text ends with a send trigger word. Returns (cleaned_text, should_send)."""
    stripped = text.rstrip(" .")
    for trigger in _SEND_TRIGGERS:
        if stripped.lower().endswith(trigger):
            cleaned = stripped[:-len(trigger)].rstrip(" ,.")
            return cleaned, True
    return text, False


def paste_text(text: str, send: bool = False):
    """Copy text to clipboard, simulate Cmd+V, and leave text in clipboard for easy re-paste."""
    _pbcopy(text)
    time.sleep(0.05)
    try:
        _cmd_v_pynput()
    except Exception:
        _cmd_v_applescript()
    if send:
        time.sleep(0.05)
        _press_enter()
