# Project Context: llm_guard_server

## Overview
`llm_guard_server` is a Sanic-based web service designed to act as a guardrails server for vLLM (and potentially other LLMs). It provides mechanisms to filter, validate, and sanitize inputs and outputs, likely for safety and compliance purposes. It employs a modular architecture with a custom "Promise" based execution flow for handling requests.

## Tech Stack
*   **Language:** Python
*   **Web Framework:** Sanic
*   **Data Validation:** Pydantic
*   **Database:** ( implied usage via `db` and `tools.db_tools`, connectors likely in `db/`)
*   **Testing:** `sanic-testing`

## Architecture
The project follows a layered architecture:

*   **`app/`**: Contains the application factory (`llm_server_app.py`) where the Sanic app is initialized, middleware is configured, and routes are registered.
*   **`services/`**: Defines the HTTP view handlers (controllers). Each submodule (e.g., `guard_view`, `sensitive_view`) typically contains a `view.py` with `HTTPMethodView` classes.
*   **`tools/`**: Contains the business logic and processing units. It seems to use a "Promise" or pipeline pattern (`tools.guard_tools.GuardTool`) to chain operations.
*   **`models/`**: Pydantic models defining the data structures for requests, responses, and internal context (`SensitiveContext`).
*   **`config/`**: Configuration management.
*   **`assets/`**: Data files like sensitive word lists and rule templates.

## Key Files & Directories

*   **`start.py`**: The entry point to run the server.
*   **`app/llm_server_app.py`**: Main application setup and routing logic.
*   **`config/settings.py`**: Default configuration and environment variable loading.
*   **`requirements.txt`**: Python dependencies.
*   **`assets/`**: Contains text files for filtering (e.g., `sensitive_words_lines.txt`, `999999-vip-black.txt`).

## Setup & Running

### Prerequisites
*   Python 3.x

### Installation
1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Server
To start the server using the default configuration:
```bash
python start.py
```
This will start the Sanic server, typically on `127.0.0.1:8000` (configurable).

### Configuration
Environment variables can be used to override defaults (defined in `config/settings.py`):
*   `HOST`: Server host (default: `127.0.0.1`)
*   `PORT`: Server port (default: `8000`)
*   `DEBUG`: Debug mode (default: `False`)
*   `AUTO_RELOAD`: Auto-reload on change (default: `True`)

## Development Conventions
*   **Request Handling**: Requests are typically validated using Pydantic models (e.g., `SensitiveContext`) via the `@validate` decorator.
*   **Logic Separation**: Keep HTTP handling in `services/` and core business logic in `tools/`.
*   **Logging**: Uses Sanic's built-in logger (`sanic.log.logger`) and a custom config in `utils/logging_config.py`.
