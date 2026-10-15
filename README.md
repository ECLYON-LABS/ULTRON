<p align="center"><img src="assets/pluto-logo.webp" width="520" alt="Pluto logo" /></p>

# Pluto

**CA:** `6jijW4Ne924kqj8XYLKXFrhpeHy5y2qxoKgGzJHQpump`

**Auditable agent architecture, memory, training, evaluation, and local inference.**

**Made by ECLYON LABS.**

Pluto Brain is Pluto's Python stack for training, evaluating, and serving local model checkpoints. The workflow is dataset validation → SFT → DPO → checkpoint → evaluation → inference.

## Development log

| Milestone | Status |
| --- | --- |
| Training infrastructure | Live — code available |
| Agent architecture | Live — code available |
| Memory and tools | Live — code available |
| Dataset preparation | Next |
| GPU training | Next |
| Initial checkpoint | Next |
| Inference verification | Next |
| Measured evaluation results | Next |

Live refers to code available in this repository, not a trained model or verified benchmark result.

## Codebase

| Path | Purpose |
| --- | --- |
| `training/datasets/` | Validate SFT examples and preference pairs. |
| `training/sft/`, `training/dpo/` | LoRA training with optional 4-bit NF4 QLoRA. |
| `training/model_registry.py` | Checkpoint manifests, file hashes, and registry. |
| `evals/` | Generate checkpoint responses and score held-out JSONL cases. |
| `eclipse/brain/` | Local checkpoint inference and token streaming. |
| `eclipse/agents/`, `eclipse/reasoning/` | Bounded task planning and 36 role profiles on a shared model backend. |
| `eclipse/memory/` | Scoped SQLite memory retrieval with local embeddings. |
| `eclipse/tools/` | Approved-URL research and external Python sandbox adapters. |
| `eclipse/api/` | Loopback JSON/SSE API with bearer-token authentication. |

## Development

Use Python 3.10+ from the repository root:

```bash
python -m unittest discover -s tests -v
```

Training data formats and SFT/DPO commands are in [training/README.md](training/README.md). Install `requirements-training.txt` with a CUDA-compatible PyTorch build for GPU training; install `requirements-qlora.txt` and use `--qlora` in both stages for the optional 4-bit path.

To generate responses for held-out cases and score them against a checkpoint, follow [evals/README.md](evals/README.md). The generator prints the settings ID required by the strict evaluation command.

## Local API

Set a local checkpoint path and an API token, then start the server:

```bash
export PLUTO_MODEL_PATH=/path/to/checkpoint
export PLUTO_API_TOKEN="$(openssl rand -hex 32)"
python -m eclipse.api.server
```

The server listens on `127.0.0.1:8765`. For example:

```bash
curl http://127.0.0.1:8765/v1/chat \
  -H "Authorization: Bearer $PLUTO_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello"}]}'
```

`POST /v1/chat/stream` streams responses; `POST /v1/tasks` runs bounded agent tasks. `GET /health` and authenticated `GET /metrics` provide service status.

## Optional capabilities

- **Memory:** Install `requirements-memory.txt`. Set `PLUTO_MEMORY_DB_PATH`, `PLUTO_EMBEDDING_MODEL_PATH`, and `PLUTO_MEMORY_SCOPE_ID` together. Chat and tasks retrieve from that scope; authenticated `POST /v1/memory` writes entries.
- **Research:** Set `PLUTO_ENABLE_WEB_RESEARCH=1`. Research tasks can retrieve URLs explicitly approved in their request.
- **Python execution:** Configure `PLUTO_SANDBOX_URL` and `PLUTO_SANDBOX_TOKEN` for an isolated HTTPS sandbox, then set `PLUTO_ENABLE_SANDBOX_EXECUTION=1`. Execution requires an explicit task request.

See [.env.example](.env.example) for configuration names.

Existing installations remain compatible with previous configuration names. If both names are set, the `PLUTO_` setting takes precedence, including an explicitly empty value.

## Ownership

© 2026 ECLYON LABS. All rights reserved. Publicly viewable source; see [LICENSE](LICENSE).
