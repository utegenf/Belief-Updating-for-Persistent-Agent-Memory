# Content Interprets, Origin Decides

**Source-aware belief updating for persistent LLM-agent memory.**

A lifelong agent must decide which experiences may enter its persistent world model.
That decision has two irreducible parts: **content** (what kind of thing is this?) and
**origin** (does this source warrant a belief update?). This repo studies a specific
failure of content-only memory and one coherent response to it.

## The question

Should an experience be *admitted* as a persistent personal belief? That is an
**epistemic** question about what the agent should *believe*, distinct from:

- the **security** question of what memory should be allowed to *authorize as action*
  (Louck 2026; Xu 2026; Cerruti 2026), and
- the **probabilistic** question of how belief *strength* should update given a
  reliability signal (Singh 2026).

We do not claim priority for provenance-aware memory, the source-vs-content ablation,
or the observation that origin matters. Recent work already establishes those. Our
contribution is a narrower, upstream question: the admission decision itself.

## The Point of Indistinguishability

Let `C` be the content representation an admission policy sees (schema-fit, functional
type, classification confidence — any function of the item text) and `O` the item's
provenance. Two experiences `x1`, `x2` are content-indistinguishable under `C` if

```
C(x1) = C(x2)   and   O(x1) ≠ O(x2)
```

Any admission rule of the form `A(x) = f(C(x))` then satisfies `A(x1) = A(x2)`: it
cannot accept one and reject the other. The **Point of Indistinguishability** is the
regime in which a legitimate update and a fabricated update lie in this class.
Within the content representation used for admission, origin is the discriminative
variable that separates them.

The definition is representation-relative by design: it does not claim no semantic
signal could ever discriminate the two, only that the content signals available to the
admission policy cannot.

## What we measure

A **controlled ablation** (20 personas, 5 items per condition, `n=100` per cell,
temperature 0, deterministic outcome inspection) holds episode content, persona, schema
history, router, model, and consolidation fixed, and toggles only the source metadata
attached to a single injected claim. Under identical input differing only in origin:

| Injected item | source-blind | confidence-thresholded | source-aware |
|---|---|---|---|
| plausible-false personal claim, untrusted source | 100/100 trusted | 100/100 trusted | **0/100 trusted** |
| genuine preference reversal, trusted source (want: learn) | 99/100 | 98/100 | **98/100** |
| true world fact, untrusted source (want: candidate) | 100/100 candidate | 100/100 candidate | **100/100 candidate** |

The two reversal misses under `schema_prov` are dropped identically by
`schema_conf` (which contains no provenance gate), tracing them to a Stage-1 content
routing error, not the origin gate.

The pattern replicates on a second model family (Llama-4-Maverick) and on the
off-the-shelf memory layer **Mem0**, which assimilates the fabrication in 50/50 cases.

## Three epistemic states

The policy admits a consolidated item to one of three destinations, held explicit:

```
[ BELIEF ]     [ CANDIDATE EVIDENCE ]     [ REJECTED ]
```

An untrusted external observation is neither believed (that would let external noise
act as a persistent prior) nor discarded (that would treat uncertainty as falsehood);
it is held as candidate evidence, distinct in kind from a personal belief.

## What this is / isn't

**Is:**
- an epistemic formulation of provenance-sensitive memory admission;
- a functional-type × source admission policy (preference / rule / relational-fact /
  external-fact / event) evaluated for coherence;
- a deterministic store-inspection measurement of the admission outcome, replicated
  across two model families and one off-the-shelf memory layer.

**Isn't:**
- a truth oracle: a trusted source asserting a plausible lie remains admitted (the
  irreducible case, bounded in-paper);
- a claim about all memory architectures (we evaluate specific configurations);
- a defense against provenance laundering upstream: the gate assumes authenticated
  source metadata. That is a real limitation; joint evaluation is future work
  (Louck 2026; Xu 2026; Cerruti 2026).

## Repository layout

```
src/        experiment + figure code
data/       hand-authored benchmark (personas, schema, injected items; author-set ground truth)
results/    experiment outputs (JSON): the numbers behind the findings
figures/    generated figures (mechanism diagram, Point of Indistinguishability, result plots)
```

### `src/`
| file | purpose |
|---|---|
| `model_client.py` | provider-neutral LLM interface (`complete_text` / `complete_structured`); the only file with model-provider code |
| `run_experiment_v2.py` | core: typed, provenanced belief store (`SleepAgent`) and the compared memory agents |
| `run_provenance_ablation.py` | the source-aware ablation → `results/prov_ablation_sonnet45.json` (and `_llama4` for the cross-family run) |
| `run_mem0_spotcheck.py` | external-validity anchor: identical target items through Mem0 |
| `instrument_reversal.py` | traces why 2/50 reversals are dropped (a Stage-1 routing error) |
| `make_figures.py` | result plots from `results/prov_ablation_sonnet45.json` |
| `make_schematics.py` | concept diagrams (mechanism, Point of Indistinguishability) |

## Running

All model access is isolated in `src/model_client.py` (a provider-neutral `complete_text` /
`complete_structured` interface). The reference implementation uses **Anthropic Claude** via the
official `anthropic` SDK. Models are configured by name; the API key is read from the standard
`ANTHROPIC_API_KEY` environment variable:

```bash
export ANTHROPIC_API_KEY=<your key>
export AGENT_MODEL=claude-sonnet-4-5                      # agent
export JUDGE_MODEL=<a different-family model>             # cross-family presence judge only

pip install -r requirements.txt

python3 src/run_provenance_ablation.py   # core ablation
python3 src/run_mem0_spotcheck.py        # external anchor
python3 src/make_figures.py              # result plots
python3 src/make_schematics.py           # concept diagrams
```

All model calls use temperature 0 (greedy decoding); variation across `n=100` comes from personas
and items, not sampling. The core schema-agent metric is deterministic (source-id inspection, no
LLM in the loop); a cross-family judge is used only for paraphrase-robust presence checks on the
summarization baseline.

## Citing

If you use this benchmark or the framing, please cite the paper (arXiv link forthcoming
after the current workshop-submission cycle).
