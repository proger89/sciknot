# Model Selection

Deadline-mode default: `gpt://{YANDEX_FOLDER_ID}/yandexgpt-5.1`.

Fallback: `gpt://{YANDEX_FOLDER_ID}/qwen3-235b-a22b-fp8`, then `qwen3.6-35b-a3b` if the first Qwen3 URI is unavailable.

Reason: the demo needs a stable Russian technical extraction path quickly, so the plan uses a 30-minute sanity probe over 3 cases instead of a full model tournament. Current live probe result:

- `yandexgpt-5.1`: `pass`, HTTP 200.
- `qwen3-235b-a22b-fp8`: API blocker, HTTP 400.

Embeddings are configured as `text-embeddings-v2-doc` and `text-embeddings-v2-query`, but table-first retrieval remains the production fallback for the hackathon demo. In the UI, LLM is optional: it summarizes facts already found by deterministic GraphRAG.
