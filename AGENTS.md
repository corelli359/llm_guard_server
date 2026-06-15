# Repository Guidelines

## Project Structure & Module Organization

This is a Python/Sanic guardrails service for LLM traffic. Application code lives in `src/`.

- `src/app/`: Sanic app factory, middleware, and lifecycle wiring.
- `src/services/`: route modules grouped by feature, including guard, rule engine, sensitive word, DB, and config views.
- `src/tools/`: sensitive-word matching, rule decisions, data loading, DB access, intent tools, and semantic cache.
- `src/models/`: Pydantic request/response and DB metadata models.
- `src/config/`: runtime settings and data-source configuration.
- `assets/`, `data/`, `data_sample/`: rule templates, word lists, and JSON data for file-backed runs.
- `k8s/`: Kubernetes deployment configuration.
- `tests/`: script-style tests, demos, benchmarks, and sample images.

## Build, Test, and Development Commands

Create an isolated environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run locally with file-backed sample data:

```bash
DATA_SOURCE_MODE=FILE DATA_SOURCE_FILE_BASE_PATH=data_sample PYTHONPATH=src python src/start.py
```

Run in DB mode when database settings are configured:

```bash
DATA_SOURCE_MODE=DB PYTHONPATH=src python src/start.py
```

Run the current request logging smoke test:

```bash
PYTHONPATH=src python -m tests.test_request_logger
```

## Coding Style & Naming Conventions

Use Python 3 style with 4-space indentation. Keep modules and packages in `snake_case`; classes should use `PascalCase`; functions, variables, and route helpers should use `snake_case`. Prefer Pydantic models for request/response data and Sanic routes under the matching `src/services/*_view/` package. Keep environment/config reads inside `src/config/`.

## Testing Guidelines

Tests currently use executable Python modules rather than a configured pytest project. Add new tests under `tests/` with names like `test_<feature>.py`, make them runnable with `python -m tests.test_<feature>`, and set `PYTHONPATH=src`. Name benchmarks and demos clearly, for example `benchmark_<topic>.py` or `<topic>_demo.py`.

## Commit & Pull Request Guidelines

Recent commits use short Chinese summaries, for example `优化日志功能` or `支持b64解析`. Follow that style: one concise subject line describing the behavior change. For pull requests, include the purpose, affected endpoints or tools, configuration changes, test commands run, and data or migration notes.

## Security & Configuration Tips

Do not commit secrets, API keys, database credentials, generated logs, or production word-list exports. Never delete or overwrite existing databases or production data; use migrations, backups, or file-mode fixtures instead. Prefer `DATA_SOURCE_MODE=FILE` with `data_sample/` locally. When changing matching, exemption, or rule decisions, document the effect and include representative sample inputs.
