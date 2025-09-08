# Architecture of the Language Learning App in Flet

IMPORTANT NOTE:
1. KEEP STRUCTURE FROM structure.md FILE, MODIFY structure.md IN CASE YOU CHANGE SOMETHING

This document describes the structure and data flow of the application, and serves as a guide for future updates and improvements.  
The architecture is designed to be **modular**, **scalable**, and **easy to understand**.

---

## Architecture Flow

The application follows a simple design pattern where the **UI is a reflection of the state**, and the data that powers it is **decoupled from the presentation logic**.

- **lessons.json**: Single source of truth for all learning content.  
- **DataManager**: Loads the JSON and provides data to the rest of the app.  
- **AppState**: State manager that tracks the current lesson, slide, and theme.  
- **main.py (Router)**: Decides which view to render depending on the route.  
- **Views (HomeView, LessonView)**: Screen builders, define the layout and UI.  
- **UIFactory**: Component factory that transforms JSON slide definitions into Flet controls.  
- **LLMClient**: External service that communicates with the DeepSeek API for exercise correction.  

---

## File Descriptions

### **main.py**
- **Purpose**: Entry point of the application.  
- **Responsibilities**: Initializes Flet, `AppState`, `DataManager`, and `LLMClient`. Manages routing and global theme switching. Displays loading screen with logo and sets app icon.  

### **config.py**
- **Purpose**: Store configurations and secrets.  
- **Responsibilities**: Holds the DeepSeek API key, base URL, and theme palettes. Should not be shared if it contains real keys.  

### **lessons.json**
- **Purpose**: Content database.  
- **Responsibilities**: Defines lessons, their order, and slides. Allows updating content without modifying code.  

### **data_manager.py**
- **Purpose**: Abstract data access.  
- **Responsibilities**: Load `lessons.json` into memory and provide helper functions for accessing lessons and slides.  

### **app_state.py**
- **Purpose**: Manage ephemeral state.  
- **Responsibilities**: Track current lesson (`current_lesson_id`), current slide index, and active theme. Provides methods like `next_slide()` and `previous_slide()`.

### **llm_client.py**
- **Purpose**: Encapsulate AI API logic.  
- **Responsibilities**: Build system prompts, send user responses to DeepSeek, and return formatted corrections.  

### **ui_factory.py**
- **Purpose**: Convert JSON data into Flet components.  
- **Responsibilities**: Map slide `type` (e.g. `"vocabulary"`) to specific controls (`ft.Text`, `ft.Column`, etc.).

### **ui_components.py**
- **Purpose**: Reusable UI components for the application.
- **Responsibilities**: Provides `ChatMessage` and `LoadingMessage` components. Both use the app logo for AI assistant avatars.

### **assets/logo.svg**
- **Purpose**: Application logo and branding.
- **Responsibilities**: Used as app icon, loading screen logo, AI assistant avatar, and in all app bar headers throughout the application.  

### **views/**
- **home_view.py**: Defines the home screen with a list of lessons. Features logo in the app bar header.  
- **lesson_view.py**: Defines the lesson screen. Manages its own internal state to update slides without reloading the entire view. Includes logo in the app bar.
- **settings_view.py**: Defines the settings screen for API key configuration. Features logo in the app bar header.  

---

## How to Update the Application

### Add a New Lesson
1. Open `lessons.json`.  
2. Copy an existing lesson object.  
3. Change the `id`, `title`, and `content`.  
The app will automatically render it.  

### Add a New Slide Type
- Define the structure in `lessons.json`, for example:

```json
{ 
  "type": "multiple_choice",
  "question": "What does 'Mizu' mean?",
  "options": ["Water", "Fire", "Earth"],
  "correct_answer": "Water"
}
```

## Implementing New Features

### UI Implementation
- Implement the UI in `ui_factory.py` (e.g. `elif slide_type == "multiple_choice"`).  
- Add interactivity in `lesson_view.py` if required.  

### Add a New Theme
1. Open `config.py`.  
2. Add a new dictionary to the `THEMES` list.  
The app will automatically include it in the theme rotation.  

---

## TODO List

### Core Features
- [ ] Save user progress (using `page.client_storage` or local file).  
- [ ] Add a progress bar in `LessonView`.  
- [ ] Add a summary screen at the end of each lesson with scores.  
- [ ] Implement final open conversation with LLM (with a personality prompt, e.g. "you are a waiter").  

### UI/UX Improvements
- [x] **Logo Integration**: Added logo as app icon, loading screen, AI assistant avatar, and in all app bar headers.
- [ ] Add animations with `ft.Animation`.  
- [ ] Add audio playback button for vocabulary slides.  
- [ ] Provide visual feedback for correct/incorrect answers.  
- [ ] Improve phrase-building slides with drag-and-drop interaction.  

### Refactoring and Code
- [ ] Improve error handling in `llm_client`.  
- [ ] Investigate asynchronous loading for large JSON files.  
- [ ] Add unit tests for `data_manager` and `app_state`.
