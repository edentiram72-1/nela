# Vision Module

## Purpose

Vision provides interfaces for screen capture, screen reading, OCR, and UI element detection.

## Responsibilities

- Capture screen frames.
- Read visible text.
- Detect UI controls.
- Provide desktop state context for the Brain and Agents.

## Public API

- `ScreenCapture.capture()`
- `ScreenReader.read(frame)`
- `UIDetector.detect(frame)`

## Known Limitations

- No real screen capture implementation exists yet.
- No OCR engine is configured yet.
- UI detection is a placeholder.

## Future Improvements

- macOS screen capture adapter.
- OCR provider integration.
- Accessibility API integration.
- Visual grounding for desktop Agents.

