"""Detect and guide users through required macOS permissions."""

import subprocess
import sys


def check_accessibility() -> bool:
    """Check if the app has Accessibility permission."""
    try:
        from ApplicationServices import AXIsProcessTrusted
        return AXIsProcessTrusted()
    except ImportError:
        # If pyobjc ApplicationServices isn't available, try via subprocess
        result = subprocess.run(
            [
                "osascript", "-e",
                'tell application "System Events" to keystroke ""',
            ],
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


def open_accessibility_settings():
    subprocess.Popen([
        "open",
        "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility",
    ])


def open_microphone_settings():
    subprocess.Popen([
        "open",
        "x-apple.systempreferences:com.apple.preference.security?Privacy_Microphone",
    ])


def open_input_monitoring_settings():
    subprocess.Popen([
        "open",
        "x-apple.systempreferences:com.apple.preference.security?Privacy_ListenEvent",
    ])


def check_all() -> list[dict]:
    """Run all permission checks. Returns list of issues found."""
    issues = []

    if not check_accessibility():
        issues.append({
            "name": "Accessibility",
            "message": (
                "Shout needs Accessibility access to listen for hotkeys "
                "and paste text into apps."
            ),
            "open_settings": open_accessibility_settings,
        })

    if not check_microphone():
        issues.append({
            "name": "Microphone",
            "message": "Shout needs Microphone access to record your speech.",
            "open_settings": open_microphone_settings,
        })

    return issues


def run_checks_cli():
    """Run permission checks and print results to terminal."""
    print("Checking macOS permissions...\n")
    issues = check_all()

    if not issues:
        print("All permissions granted. You're good to go!")
        return True

    for issue in issues:
        print(f"  MISSING: {issue['name']}")
        print(f"           {issue['message']}\n")

    print("To fix: Open System Settings > Privacy & Security and grant access")
    print("to your terminal app (or Python) for each permission listed above.")
    return False


if __name__ == "__main__":
    ok = run_checks_cli()
    sys.exit(0 if ok else 1)
