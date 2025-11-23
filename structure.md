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
-   **`src/llm/`**: Contains the client for interacting with the language model.
-   **`src/config.py`**: Stores configuration settings.
-   **`lessons/`**: Contains the lesson content in JSON format.
-   **`app_languages/`**: Contains JSON files for UI localization.

## Key Files and Directories

### `main.py`

This is the entry point of the application. It initializes the Flet app, sets up the main page, wires up all the managers, and handles routing between different views.

### `src/config.py`

This is the central configuration file. It manages:

-   **Language Settings**: `DEFAULT_LANGUAGE` sets the UI and lesson language. It loads the UI localization from the `app_languages/` directory.
-   **Lesson Paths**: Dynamically constructs the path to the lesson content using the `language_folder_map`.
-   **API Keys**: Manages the logic for API keys using `get_effective_api_key`. The application can use a user-provided DeepSeek API key, but will fall back to a free Gradio-based endpoint if no key is provided.

### `src/managers/user_data_manager.py`

A critical component that acts as a **singleton** for all data persistence. It reads from and writes to `user_data.json`, providing a single, consistent source of truth for all user settings, progress, and application data. It is initialized once in `main.py` and passed to other managers.

### `src/managers/progress_manager.py`

Provides a high-level API for managing user progress. It acts as an abstraction layer on top of `UserDataManager`, handling the business logic for marking lessons as completed and saving progress in interactive scenarios.

### `src/managers/settings_manager.py`

Handles the logic for the settings UI. It interacts with `UserDataManager` to get and set user-specific settings like the API key.

### `src/managers/data_manager.py`

This class is responsible for loading lesson data from the JSON files in the `lessons/` directory.

### `src/llm_client.py`

This class is the core of the AI functionality and features a dual-backend architecture:

1.  **DeepSeek API**: Used if the user provides their own API key in the settings.
2.  **Gradio/Hugging Face Fallback**: A free, public endpoint used if no API key is provided.

The client uses structured prompting to get machine-readable JSON output from the LLM, which is key for the interactive exercises.

### `src/services/github_service.py`

This service is responsible for downloading language assets (UI tranºslations and lesson files) from an external GitHub repository.

-   **Repository**: It connects to the `DKeAlvaro/llmers-langs` repository.
-   **Functionality**: It fetches the list of available languages and downloads the corresponding files for the selected language combination.
-   **File Overwriting**: The service overwrites local files in the `app_languages/` and `lessons/` directories with the versions from the GitHub repository. This ensures that the application is always using the latest version of the language assets.
-   **Authentication**: It uses a GitHub Personal Access Token (PAT) stored in the `GITHUB_PAT` environment variable to authenticate with the GitHub API.

This service is a key component for the application's language management, but it's important to be aware that it will overwrite local changes to the lesson and language files.

### `src/app_state.py`

This class aggregates various state managers (`DataManager`, `ProgressManager`, `LessonState`) and contains high-level business logic, such as the system for unlocking lessons sequentially.

### `src/views/`

This directory contains the different views of the application. Each view is a Flet `View` object that represents a screen.

-   **`home_view.py`**: The main screen, which displays a list of lessons.
-   **`lesson_view.py`**: The screen where the user interacts with a lesson.
-   **`settings_view.py`**: The screen where the user can configure their API key.
-   **`intro_view.py`**: The welcome screen shown on the first run.

### `src/view_models/`

This directory contains the view models, which handle the logic for the views, following the MVVM pattern.

-   **`home_view_model.py`**: Manages the state of the home view, including the list of lessons.
-   **`lesson_view_model.py`**: Manages the state of the lesson view, including the current slide and user input.

### `ui_components.py`

This file contains reusable UI components, such as chat messages, slide templates, and buttons.

### `lessons/`

This directory contains the lesson content in JSON format, organized by language. Each language has a subdirectory (e.g., `dutch/`, `french/`).

### `generate_lessons/`

This directory contains Python scripts for generating the lesson files. These scripts use a language model to create lesson content based on a predefined structure.

### `app_languages/`

This directory contains JSON files for UI localization. The `config.py` file loads the appropriate language file from here based on the `DEFAULT_LANGUAGE` setting.

## How to Make Changes

### Adding a New Language

1.  **Generate Lessons**: Use the scripts in `generate_lessons/` (e.g., `generate_lessons.py`) to create a new folder with JSON lesson files for the desired language (e.g., `lessons/spanish/`).
2.  **Translate UI (Optional)**: If you want to add UI translations for the new language, run `python generate_lessons/generate_language_settings.py --language <language_name>` to create the translated UI files in `app_languages/`.
3.  **Update Config**: Add the new language to the `language_folder_map` dictionary in `src/config.py`. This will link the language code to the folder name you created in step 1.

### Modifying a Lesson

To modify a lesson, edit the corresponding JSON file in the `lessons/` directory. The lesson files have a specific structure, so be sure to follow the existing format.

### Adding a New Feature

1.  Create a new view in the `src/views/` directory.
2.  Create a corresponding view model in the `src/view_models/` directory.
3.  Add a route for the new view in `main.py`.
4.  Implement the UI and logic for the new feature, ensuring to connect it to the appropriate managers and state objects.
