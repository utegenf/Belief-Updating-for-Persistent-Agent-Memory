# Content Interprets, Origin Decides

**Source-aware belief updating for persistent LLM-agent memory.**

A lifelong agent must decide which experiences may enter its persistent world model. This project separates two questions: **content** (what kind of thing is this?) and **origin** (does this source warrant a belief update?).

## 5-minute integration

The v0 API is designed to be small enough to sit in front of an existing agent-memory store:

```python
from belief_memory import SourceAwareMemory, SourceTypePolicy

memory = SourceAwareMemory(
    trusted_sources={"user"},
)

memory.observe(
    "I've started learning Rust.",
    source="user",
)

memory.observe(
    "The user is an expert Rust developer.",
    source="external_document",
)

memory.consolidate()

print(memory.beliefs())
print(memory.candidates())
```

Consolidation is explicit. Provenance is supplied by the application and is never inferred from content. The core package does not require an LLM provider.

## The idea

A plausible fabrication that fits an agent's existing schema can be content-wise indistinguishable from a genuine personal update. We call this the **Point of Indistinguishability**. Content determines the interpretation of an experience; origin determines whether that experience is allowed to change beliefs.

## Research findings

- **Controlled ablation** (20 personas, `n=100` per condition, deterministic outcome inspection): source-blind and confidence-thresholded memory assimilate the plausible fabrication in every case; a source-aware policy prevents it. Controls confirm the source-aware gate retains genuine trusted preference reversals in 98% of cases and routes untrusted world facts to a candidate/evidence layer.
- **Cross-family:** the same pattern replicates on a second base-model family (Llama-4-Maverick), indicating the failure is architectural rather than tied to one model family.
- **External validity:** the repository includes a Mem0 spot-check as an external anchor; see the research results for the exact evaluated sample and protocol.

## Architecture

```text
experience
    │
    ▼
Content Router ──► functional type
    │
    ▼
Source × Type Policy ──► belief / candidate / episodic / reject
    │
    ▼
Backend
```

- **Router:** pluggable. v0 provides an LLM router, a dependency-free rule router, and a null router for pre-typed inputs.
- **Policy:** configurable source × functional-type admission rules.
- **Provenance:** application-supplied metadata; never inferred from message text.
- **Backend:** in-memory in v0, with a `Backend` protocol for application-owned persistence.
- **Consolidation:** explicit and controllable; never triggered automatically by `observe()`.

See [`docs/architecture.md`](docs/architecture.md) for the protocol contracts and design boundary.

## v0 non-goals

v0 deliberately does **not** ship:

- SQLite or another built-in persistent storage implementation;
- automatic corroboration or candidate-to-belief promotion;
- learned multi-tier trust or source reputation;
- a hosted memory service;
- non-Python bindings;
- automatic consolidation;
- a mandatory LLM dependency;
- framework-specific integrations as a requirement for the core package.

These are deliberate scope boundaries, not missing features. Later versions can add them when real integration requirements justify the complexity.

## Repository layout

```text
src/belief_memory/   reusable library
src/research/        paper/reproducibility implementation (target layout)
examples/             integration examples
tests/                library and conformance tests
data/                 hand-authored research benchmark
results/              experiment outputs
figures/              generated research figures
docs/                 architecture and developer documentation
```

## Research

The paper's controlled experiments are kept separate from the reusable library. The research implementation may preserve experiment-specific prompts, metrics, baselines, and model clients without turning those choices into requirements for library users.

## Development status

The repository is currently being refactored toward the v0 reusable API. The public library layer is intentionally being stabilized before the research scripts are migrated. Do not treat the current branch as a published PyPI release yet.

## Running the research implementation

The current research scripts use Anthropic through `src/model_client.py` and the existing research dependencies. See `requirements.txt` and the individual research scripts for the reproduction commands.