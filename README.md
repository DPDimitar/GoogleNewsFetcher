# GOOGLE NEWS FETCHER

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
    - Time Range
      - config.py > time_range
    - Keywords
      - config.py > keywords

## Execution
1. Configure credentials in config.py (for connection to the needed services)
2. Define parameters for execution in config.py
3. Execute `python __main__.py`