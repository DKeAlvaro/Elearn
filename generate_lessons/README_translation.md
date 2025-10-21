# Language Settings Translation Script

This script automatically translates the English language settings file (`app_languages/en.json`) to other languages using Google Translate API through the deep-translator library.

## Installation

First, install the required dependency:

```bash
pip install deep-translator>=1.11.4
```

## Usage

### Basic Usage

To translate to a specific language:

```bash
python generate_language_settings.py --language spanish
```

This will create `app_languages/es.json` with Spanish translations.

### Advanced Usage

You can specify custom input and output paths:

```bash
python generate_language_settings.py --language french --input ../app_languages/en.json --output-dir ../app_languages
```

### Supported Languages

The script supports many languages including:
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Dutch (nl)
- Russian (ru)
- Chinese (zh)
- Japanese (ja)
- Korean (ko)
- Arabic (ar)
- And many more...

## Examples

```bash
# Generate Spanish translations
python generate_language_settings.py --language spanish

# Generate French translations
python generate_language_settings.py --language french

# Generate German translations
python generate_language_settings.py --language german
```

## Output

The script will:
1. Load the English settings from `app_languages/en.json`
2. Translate each text string to the target language
3. Preserve placeholder formatting (e.g., `{error}`, `{goal}`)
4. Save the translated file as `app_languages/{language_code}.json`
5. Ask for confirmation before overwriting existing files

## Notes

- The script preserves JSON structure and formatting
- Placeholder variables like `{error}` and `{goal}` are maintained
- If translation fails for any string, the original English text is kept
- The script uses Google Translate API through the `deep-translator` library