# minodu-forum
Backend for the minodu forum

## Env Vars

These env vars need to be defined
```
JWT_SECRET_KEY=?
JWT_ALGORITHM=HS256
DATABASE_URL=sqlite:///./database.db
PORT=3001
API_PREFIX=/forum"
```

## Development

### Setup

* create virtual env `python -m venv .venv` and activate with `source .venv/bin/activate`
* install requirements: `pip install -r requirements`

### Tests

* run tests with `pytest`or `pytest -s`