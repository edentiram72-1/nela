"""Animation hook registry for Claude-provided motion design."""

from __future__ import annotations

from collections import defaultdict
from typing import Callable, DefaultDict

from ui.state import EyeState

AnimationHook = Callable[[EyeState], None]


class AnimationRegistry:
    """Stores state-based animation callbacks without owning visual design."""

    def __init__(self) -> None:
        self._hooks: DefaultDict[EyeState, list[AnimationHook]] = defaultdict(list)

    def register(self, state: EyeState, hook: AnimationHook) -> None:
        self._hooks[state].append(hook)

    def trigger(self, state: EyeState) -> None:
        for hook in tuple(self._hooks[state]):
            hook(state)
