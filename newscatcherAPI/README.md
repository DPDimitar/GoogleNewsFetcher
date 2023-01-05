# NEWSCATCHER API

## Setup development environment
1. Create environment (e.g. venv, conda, ...)
   - https://docs.python.org/3/library/venv.html
2. Install requirements
   - pip install -r requirements.txt

## Project structure
- \__main__.py
  - Entrypoint to configure and execute the fetcher
- config.py
  - Credentials, Time Range, Keywords configurations
    - Credentials
      - config.py > credentials
    - API KEY
      - config.py > x_api_key
    - Keywords
      - config.py > keywords
        - general_keywords_AND = all combinations of different keywords from this array, others normally

## Execution
1. Configure credentials, x_api_key and the keywords in config.py (for connection to the needed services and defining search queries)
2. Define parameters for execution in config.py
3. Execute `python __main__.py`