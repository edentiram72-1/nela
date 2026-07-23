"""macOS local speech provider using the built-in `say` command."""

from __future__ import annotations

import shutil
import subprocess
from uuid import uuid4

from voice.providers.base import SpeechProvider
from voice.voice_profile import VoiceProfile


class MacOSSpeechProvider(SpeechProvider):
    """Simple replaceable provider for local macOS speech output."""

    name = "macos_say"

    def __init__(self) -> None:
        self._process: subprocess.Popen[bytes] | None = None

    def speak(self, text: str, profile: VoiceProfile) -> str:
        if not text.strip():
            raise ValueError("Cannot speak empty text.")
        if shutil.which("say") is None:
            raise RuntimeError("macOS 'say' command is not available.")
        self.stop()
        command = ["say", "-r", str(max(80, int(200 * profile.rate)))]
        if profile.provider_voice:
            command.extend(["-v", profile.provider_voice])
        command.append(text)
        self._process = subprocess.Popen(command)
        return str(uuid4())

    def stop(self) -> None:
        if self._process and self._process.poll() is None:
            self._process.terminate()
        self._process = None

    def pause(self) -> None:
        # The macOS `say` command does not expose portable pause/resume controls.
        raise NotImplementedError("Pause is not supported by the macOS say provider.")

    def resume(self) -> None:
        raise NotImplementedError("Resume is not supported by the macOS say provider.")

    def health_check(self) -> dict[str, object]:
        return {
            "provider": self.name,
            "available": shutil.which("say") is not None,
            "supports_pause": False,
            "supports_resume": False,
        }
