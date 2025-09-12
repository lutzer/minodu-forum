# minodu-forum
Backend for the minodu forum

Deprecated, new repo can be found here: https://github.com/lutzer/minodu

## Env Vars

* check *src/config.py* to see what env vars can be changed
* you need to supply a different *JWT_SECRET_KEY*
* you probably want to supply a different *DATABASE_URL*

## Development

### Setup

* create virtual env `python -m venv .venv` and activate with `source .venv/bin/activate`
* install requirements: `pip install -r requirements`

### Tests

* run tests with `pytest`or `pytest -s`
