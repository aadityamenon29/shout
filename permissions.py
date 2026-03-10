"""Detect and guide users through required macOS permissions."""

import subprocess
import sys


def check_accessibility() -> bool:
    """Check if the app has Accessibility permission."""
    try:
        from ApplicationServices import AXIsProcessTrusted
        return AXIsProcessTrusted()
    except ImportError:
        result = subprocess.run(
            ["osascript", "-e",
             'tell application "System Events" to keystroke ""'],
            capture_output=True,
        )
        return result.returncode == 0


def check_microphone() -> bool:
    """Check if the app has Microphone permission by attempting to open a stream."""
    try:
        import sounddevice as sd
        stream = sd.InputStream(samplerate=16000, channels=1, dtype="int16")
        stream.start()
        stream.stop()
        stream.close()
        return True
    except Exception:
        return False


def check_input_monitoring() -> bool:
    """Check if the app has Input Monitoring permission.

    There's no direct API to check this. We try starting a pynput listener
    briefly — if it fails or we can't receive events, it's likely denied.
    On macOS, pynput will usually work once Accessibility is granted,
    but Input Monitoring is technically separate. We check it as a
    best-effort signal.
    """
    try:
        from pynput.keyboard import Listener
        got_event = False

        def on_press(key):
            nonlocal got_event
            got_event = True
            return False

        listener = Listener(on_press=on_press)
        listener.start()
        listener.join(timeout=0.2)
        listener.stop()
        # If we got here without an exception, the listener started OK.
        # macOS will prompt if not yet allowed, so we assume it's fine.
        return True
    except Exception:
        return False


_SETTINGS_URLS = {
    "Accessibility": "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility",
    "Input Monitoring": "x-apple.systempreferences:com.apple.preference.security?Privacy_ListenEvent",
    "Microphone": "x-apple.systempreferences:com.apple.preference.security?Privacy_Microphone",
}

# Each permission the app requires, in the order the user should grant them.
_REQUIRED_PERMISSIONS = [
    {
        "name": "Accessibility",
        "check": check_accessibility,
        "why": (
            "Shout needs Accessibility access to simulate keyboard shortcuts "
            "(Cmd+V) for pasting transcribed text into your apps."
        ),
        "how": (
            "In the System Settings window that opens:\n"
            "1. Find your terminal app (Terminal, iTerm, Ghostty, etc.)\n"
            "2. Toggle it ON\n"
            "3. Come back here and click 'Next'"
        ),
    },
    {
        "name": "Input Monitoring",
        "check": check_input_monitoring,
        "why": (
            "Shout needs Input Monitoring access to detect when you press "
            "and release the Right Option key (the push-to-talk hotkey)."
        ),
        "how": (
            "In the System Settings window that opens:\n"
            "1. Find your terminal app\n"
            "2. Toggle it ON\n"
            "3. Come back here and click 'Next'"
        ),
    },
    {
        "name": "Microphone",
        "check": check_microphone,
        "why": "Shout needs Microphone access to record your speech.",
        "how": (
            "In the System Settings window that opens:\n"
            "1. Find your terminal app\n"
            "2. Toggle it ON\n"
            "3. Come back here and click 'Next'"
        ),
    },
]


def open_settings(name: str):
    url = _SETTINGS_URLS[name]
    subprocess.Popen(["open", url])


def get_missing_permissions() -> list[dict]:
    """Return list of permissions that are not yet granted."""
    missing = []
    for perm in _REQUIRED_PERMISSIONS:
        if not perm["check"]():
            missing.append(perm)
    return missing


def run_checks_cli():
    """Run permission checks and print results to terminal."""
    print("Checking macOS permissions...\n")
    missing = get_missing_permissions()

    if not missing:
        print("All permissions granted. You're good to go!")
        return True

    for perm in missing:
        print(f"  MISSING: {perm['name']}")
        print(f"           {perm['why']}\n")

    print("To fix: Open System Settings > Privacy & Security and grant access")
    print("to your terminal app (or Python) for each permission listed above.")
    return False


if __name__ == "__main__":
    ok = run_checks_cli()
    sys.exit(0 if ok else 1)
