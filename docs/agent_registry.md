# Agent Registry And Capability Manifests

Status: implemented foundation on `feature/NELA-safety-spine-routing`.

## Purpose

The Agent Registry and Capability Registry make Agent execution explicit. The
Brain plans semantic work; the Dispatcher asks the registries which Agents may
perform that work, then the Permission Engine decides what may actually run.

## Runtime Agent Registry

`agents.registry.AgentRegistry` stores live Agent instances.

Public API:

- `register(agent)`: inserts a new Agent ID.
- `replace(agent)`: explicit controlled replacement.
- `get(name)`: returns a registered Agent.
- `list()`: lists current Agent IDs.
- `health_check()`: asks each Agent for health.

Duplicate Agent IDs are rejected by default. This prevents accidental overwrite
of a trusted Agent by another object with the same name.

## Capability Registry

`permissions.registry.CapabilityRegistry` stores `AgentManifest` objects.

Public API:

- `register_agent(agent)`: registers a runtime Agent and its manifest.
- `register_manifest(manifest, replace=False)`: registers a manifest directly.
- `find_agents_for_capability(capability, platform=None)`: returns candidates.
- `get_capability(agent, action_or_capability)`: resolves allowed capability.
- `list_capabilities()`: returns declared capability IDs.

Manifest registration is insert-only by default. A replacement must be requested
explicitly and is recorded in `registration_audit`.

## Manifest Validation

Each manifest must define:

- Agent identity.
- Manifest version.
- Capability IDs.
- Declared actions.
- Permission tier.
- Optional platform and scope constraints.
- Optional confirmation requirement.

Unknown actions fail closed. Capabilities may also be declared but disabled, as
with the current Terminal and Coding foundation manifests.

## Safety Notes

- Capability tier is declared, never inferred from user wording.
- Duplicate capability IDs inside one manifest are rejected.
- Tier downgrades below policy floors are rejected.
- Registration attempts are auditable.
- Future plugin loading must use this same manifest path.
