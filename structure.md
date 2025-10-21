# Project Structure

This document outlines the structure of the language learning application, providing guidance on where to find key components and how to make changes.

## High-Level Overview

The application is built using the Flet framework for the user interface and a language model (LLM) for AI-powered features. The core of the application is organized into the following directories:

-   **`views/`**: Contains the different screens of the application.
-   **`view_models/`**: Handles the logic for the views.
-   **`data/`**: Manages loading and saving data, including lesson content and user progress.
-   **`llm/`**: Interacts with the language model API.
-   **`config/`**: Stores configuration settings.
-   **`lessons/`**: Contains the lesson content in JSON format.

## Key Files and Directories

### `main.py`

This is the entry point of the application. It initializes the Flet app, sets up the main page, and handles routing between different views.

### `config.py`

This file contains the application's configuration, including:

-   **API Keys**: `DEEPSEEK_API_KEY` and `OPENAI_API_KEY` for the language model.
-   **Language Settings**: `DEFAULT_LANGUAGE` to set the UI and lesson language.
-   **Themes**: A list of color schemes for the UI.

To change the application's language, modify the `DEFAULT_LANGUAGE` variable. For example, to use a Spanish UI with lessons for learning French, set it to `"es-fr"`.

### `data_manager.py`

This class is responsible for loading lesson data from the JSON files in the `lessons/` directory. It provides methods to get all lessons, a specific lesson by ID, and the content of a lesson.

### `app_state.py`

This class manages the global state of the application, including:

-   **Lesson Progress**: Tracks which lessons the user has completed.
-   **Premium Status**: Determines whether the user has access to premium content.
-   **Current Theme**: The currently selected UI theme.

### `llm_client.py`

This class is a client for interacting with the language model API. It provides methods for:

-   **Getting a scenario response**: Used in interactive conversation scenarios.
-   **Extracting information**: Extracts specific information from user input.
-   **Evaluating goal completion**: Determines if the user has completed a learning objective.
-   **Getting a correction**: Provides feedback on user input.

### `views/`

This directory contains the different views of the application. Each view is a Flet `View` object that represents a screen.

-   **`home_view.py`**: The main screen, which displays a list of lessons.
-   **`lesson_view.py`**: The screen where the user interacts with a lesson.
-   **`settings_view.py`**: The screen where the user can configure their API key.
-   **`premium_view.py`**: The screen for purchasing premium access.
-   **`intro_view.py`**: The welcome screen shown on the first run.

### `view_models/`

This directory contains the view models, which handle the logic for the views. Each view has a corresponding view model.

-   **`home_view_model.py`**: Manages the state of the home view, including the list of lessons.
-   **`lesson_view_model.py`**: Manages the state of the lesson view, including the current slide and user input.

### `ui_components.py`

This file contains reusable UI components, such as chat messages, slide templates, and buttons.

### `managers/`

This directory contains managers for different parts of the application.

-   **`progress_manager.py`**: Manages loading and saving user progress.
-   **`billing_manager.py`**: Manages in-app purchases.

### `state/`

This directory contains classes that manage the state of different parts of the application.

-   **`lesson_state.py`**: Manages the state of the current lesson, including the current slide index.
-   **`scenario_state.py`**: Manages the state of an interactive scenario.

### `lessons/`

This directory contains the lesson content in JSON format, organized by language. Each language has a subdirectory (e.g., `dutch/`, `spanish/`), which contains the lesson files.

### `generate_lessons/`

This directory contains scripts for generating the lesson files. These scripts use a language model to create lesson content based on a predefined structure.

## How to Make Changes

### Adding a New Language

1.  Add the language to the `lessons/languages.txt` file.
2.  Run the `generate_lessons/generate_lessons.py` script to create the lesson files.
3.  Add the language to the `language_folder_map` in `config.py`.

### Modifying a Lesson

To modify a lesson, edit the corresponding JSON file in the `lessons/` directory. The lesson files have a specific structure, so be sure to follow the existing format.

### Adding a New Feature

1.  Create a new view in the `views/` directory.
2.  Create a corresponding view model in the `view_models/` directory.
3.  Add a route for the new view in `main.py`.
4.  Implement the UI and logic for the new feature.