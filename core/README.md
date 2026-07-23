# Core Module

## Purpose

The Core module contains runtime primitives shared across NELA OS.

## Responsibilities

- Load configuration.
- Configure logging.
- Define and publish events.
- Bootstrap the runtime.
- Expose the application entry point.

## Public API

- `AppConfig.from_env()`
- `EventBus.subscribe(event_type, handler)`
- `EventBus.publish(event)`
- `EventBus.history()`
- `configure_logging(log_dir="logs", level="INFO")`
- `bootstrap(config=None)`

## Events

Event names are centralized in `core/events.py`.

## Known Limitations

- The event bus is synchronous and in-process.
- No durable event log exists yet.
- No environment file loader is included yet.

## Future Improvements

- Async event bus.
- Durable event journal.
- Structured JSON logging.
- Runtime health endpoint.

