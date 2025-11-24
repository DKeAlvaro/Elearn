# Project Structure

This document outlines the structure of the language learning application, providing guidance on where to find key components and how to make changes.

## High-Level Overview

The application is built using the Flet framework for the user interface and a language model (LLM) for AI-powered features. The architecture is designed to be modular and centralized.

A key architectural pattern is the use of a singleton, `UserDataManager`, which handles all data persistence. It reads and writes to a single `user_data.json` file, which acts as the single source of truth for user settings, progress, and application data.

Higher-level managers (`ProgressManager`, `DataManager`, `SettingsManager`) provide specific APIs and business logic, but they all rely on `UserDataManager` for the actual data storage. This creates a clean separation of concerns.

The core of the application is organized into the following directories:

-   **`src/`**: The main source code for the application.
-   **`src/views/`**: Contains the different screens (Views) of the application.
-   **`src/view_models/`**: Handles the logic and state for the Views (ViewModels).
-   **`src/managers/`**: Contains high-level managers for different parts of the application's logic.
-   **`src/state/`**: Contains state classes used by view models.
-   **`src/services/`**: External integrations (e.g., GitHub).
-   **`src/utils/`**: Utility helpers (network, typing simulator).
-   **`src/llm_client.py`**: Client for interacting with the language model.
-   **`src/config.py`**: Stores configuration settings.
-   **`app_languages/`**: JSON files for UI localization.
-   **`lessons/`**: Runtime-downloaded lesson content in JSON format (ignored by git).

## Key Files and Directories

### `main.py`

This is the entry point of the application. It initializes the Flet app, sets up the main page, wires up all the managers, and handles routing between different views.

Routes:
- `/` → Home
- `/lesson` → Lesson
- `/settings` → Settings
- `/language_selection` → First-run language setup

### `src/config.py`

This is the central configuration file. It manages:

-   **Unified Language Setting**: A single value like `en-nl` (UI language-target language) is stored via `UserDataManager` on first run and used by config. UI strings are loaded from `app_languages/<ui>.json`.
-   **Lesson Paths**: Dynamically builds `lessons/<target_folder>/<ui-target>` via `get_lessons_folder()` and `get_target_language_folder()`.
-   **API Keys**: `get_effective_api_key()` prioritizes a runtime key, then the user-saved key, then environment variables (`OPENAI_API_KEY` or `DEEPSEEK_API_KEY`).

### `src/managers/user_data_manager.py`

A critical component that acts as a **singleton** for all data persistence. It reads from and writes to `user_data.json`, providing a single, consistent source of truth for all user settings, progress, and application data. It is initialized once in `main.py` and passed to other managers.

Schema:
- `settings`: persisted preferences (e.g., `deepseek_api_key`, `selected_language`).
- `progress`: `completed_lessons`, `interactive_scenario_progress`, `lesson_slide_positions`, `user_data`.
- `app_data`: flags like `first_run`.

### `src/managers/progress_manager.py`

Provides a high-level API for managing user progress. It acts as an abstraction layer on top of `UserDataManager`, handling the business logic for marking lessons as completed and saving progress in interactive scenarios.

### `src/managers/settings_manager.py`

Handles the logic for the settings UI. It interacts with `UserDataManager` to get and set user-specific settings like the API key.

### `src/managers/data_manager.py`

Loads lesson data from JSON files in the language-specific folder returned by `config.get_lessons_folder()`. Supports reloading and sorting lessons by ID.

### `src/llm_client.py`

This class is the core of the AI functionality and features a dual-backend architecture:

1.  **DeepSeek API**: Used if the user provides their own API key in the settings.
2.  **Gradio/Hugging Face Fallback**: A free, public endpoint used if no API key is provided.

The client uses structured prompting to get machine-readable JSON output from the LLM, which is key for the interactive exercises.

Behavior:
- Validates and uses DeepSeek via OpenAI SDK when a valid key is present.
- Falls back to a Gradio client when no valid key is available.

### `src/services/github_service.py`

This service is responsible for downloading language assets (UI translations and lesson files) from an external GitHub repository.

-   **Repository**: It connects to the `DKeAlvaro/llmers-langs` repository.
-   **Functionality**: It fetches the list of available languages and downloads the corresponding files for the selected language combination.
-   **File Overwriting**: The service overwrites local files in the `app_languages/` and `lessons/` directories with the versions from the GitHub repository. This ensures that the application is always using the latest version of the language assets.
-   **Authentication**: It uses a GitHub Personal Access Token (PAT) stored in the `GITHUB_PAT` environment variable to authenticate with the GitHub API.

This service is a key component for the application's language management, but it's important to be aware that it will overwrite local changes to the lesson and language files.

### `src/app_state.py`

This class aggregates various state managers (`DataManager`, `ProgressManager`, `LessonState`) and contains high-level business logic, such as the system for unlocking lessons sequentially.

Also exposes `reload_lessons()` and encapsulates scenario state for interactive exercises.

### `src/views/`

This directory contains the different views of the application. Each view is a Flet `View` object that represents a screen.

-   **`home_view.py`**: The main screen, which displays a list of lessons.
-   **`lesson_view.py`**: The screen where the user interacts with a lesson.
-   **`settings_view.py`**: The screen where the user can configure their API key.
-   **`language_selection_view.py`**: First-run setup where the user selects the target language and downloads assets.

### `src/view_models/`

This directory contains the view models, which handle the logic for the views, following the MVVM pattern.

-   **`home_view_model.py`**: Manages the state of the home view, including the list of lessons.
-   **`lesson_view_model.py`**: Manages the state of the lesson view, including the current slide and user input.
-   **`language_selection_view_model.py`**: Orchestrates language discovery and downloads via `GitHubService`, persists the selection, and refreshes config.

### `ui_components.py`

Reusable UI components: app bar, titles, multiple slide types (vocabulary, expression, grammar, tips, pronunciation), interactive scenario and LLM-check slides, and a network status indicator.

### `lessons/`

Runtime-downloaded lesson content in JSON format, organized by target language. Path structure: `lessons/<target_folder>/<ui-target>/...`. This directory is ignored by git and is populated by `GitHubService` during the first run and when the user re-downloads assets.

### `src/utils/`

Utilities such as `network_utils.py` (offline detection and status helpers) and `typing_simulator.py`.

### `app_languages/`

This directory contains JSON files for UI localization. `config.py` loads `app_languages/<ui>.json` based on the unified language setting.

## How to Make Changes

### Adding a New Language

1.  **Use the Language Selection screen**: On first run (or via the route `/language_selection`), pick the target language. The app will download the UI file and lessons from `DKeAlvaro/llmers-langs` using your `GITHUB_PAT`.
2.  **Persist Selection**: The chosen combination (e.g., `en-nl`) is saved to `user_data.json` (`selected_language`), and `config.load_language()` refreshes UI strings.
3.  **Contribute upstream for new languages**: To add a brand-new language not listed, add assets to the `llmers-langs` repository so they can be fetched by the app.

### Modifying a Lesson

Edit the corresponding JSON file under `lessons/<target_folder>/<ui-target>/`. Note that re-downloading assets from GitHub will overwrite local changes; for persistent changes, update the upstream repository.

### Adding a New Feature

1.  Create a new view in the `src/views/` directory.
2.  Create a corresponding view model in the `src/view_models/` directory.
3.  Add a route for the new view in `main.py`.
4.  Implement the UI and logic for the new feature, ensuring to connect it to the appropriate managers and state objects.
