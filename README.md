# Content Interprets, Origin Decides

**Source-aware belief updating for persistent LLM-agent memory.**

A lifelong agent must decide which experiences may enter its persistent world model. That
decision has two irreducible parts: **content** (what kind of thing is this?) and **origin**
(does this source warrant a belief update?). This project demonstrates a failure mode of
content-based memory and evaluates a source-aware alternative.

## The idea

A plausible fabrication that *fits* an agent's existing schema is assimilated as a trusted
belief — because, on content alone, it is indistinguishable from a genuine update. We call this
the **Point of Indistinguishability**. Content can tell you *what* a claim is, but not whether it
should be *allowed to change* your beliefs; that requires knowing the origin.

## What we found

- **Controlled ablation** (10 personas, `n=50` per condition, deterministic outcome inspection):
  source-blind and confidence-thresholded memory both assimilate the plausible fabrication in
  every case; a source-aware policy prevents it. Controls confirm the source-aware gate still
  *learns* genuine trusted preference reversals (96%) and routes untrusted world facts to a
  candidate/evidence layer rather than trusting or discarding them.
- **External validity:** Mem0, an off-the-shelf memory layer with no source-trust mechanism,
  assimilates the same fabrication in **50/50** cases — locating the failure in the content-based
  consolidation *paradigm*, not in a weak in-house baseline.

## Repository layout

```
src/        experiment + figure code
data/       hand-authored benchmark (personas, schema, injected items; author-set ground truth)
results/    experiment outputs (JSON) — the numbers behind the findings
figures/    generated figures (mechanism diagram, Point of Indistinguishability, result plots)
```

### `src/`
| file | purpose |
|---|---|
| `model_client.py` | provider-neutral LLM interface (`complete_text` / `complete_structured`) — the only file with model-provider code |
| `run_experiment_v2.py` | core: typed, provenanced belief store (`SleepAgent`) and the compared memory agents |
| `run_provenance_ablation.py` | the source-aware ablation → `results/prov_final_n50.json` |
| `run_mem0_spotcheck.py` | external-validity anchor: identical target items through Mem0 |
| `instrument_reversal.py` | traces why 2/50 reversals are dropped (a Stage-1 routing error) |
| `make_figures.py` | result plots from `results/prov_final_n50.json` |
| `make_schematics.py` | concept diagrams (mechanism, Point of Indistinguishability) |

## Running

All model access is isolated in `src/model_client.py` (a provider-neutral `complete_text` /
`complete_structured` interface). The reference implementation calls a hosted LLM API and uses the
standard default credential chain — no profiles or account identifiers are committed. Configure via
environment variables:

```bash
export AGENT_MODEL=<agent model id, e.g. a Claude Sonnet model>
export JUDGE_MODEL=<cross-family judge model id>
export API_REGION=<region for the hosted API>            # default: us-east-1
# credentials come from the standard default chain (env vars / role)

pip install -r requirements.txt

python3 src/run_provenance_ablation.py   # core ablation
python3 src/run_mem0_spotcheck.py        # external anchor
python3 src/make_figures.py              # result plots
python3 src/make_schematics.py           # concept diagrams
```

All model calls use temperature 0 (greedy decoding); variation across `n=50` comes from personas
and items, not sampling. The core schema-agent metric is deterministic (source-id inspection, no
LLM in the loop); a cross-family judge is used only for paraphrase-robust presence checks on the
summarization baseline.
