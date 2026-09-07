# Walmart Sales Prediction

**A local web prototype connecting a sales-prediction model, inventory data, and an interactive browser interface.**

The application combines a Flask API with HTML, CSS, JavaScript, and Chart.js. It accepts store and department features, calls a saved model to estimate weekly sales, and plots inventory records from the included CSV.

## What's included

| File | Purpose |
| --- | --- |
| [`flask_model_server.py`](flask_model_server.py) | Prediction, inventory lookup, and email API handlers |
| [`index.html`](index.html) | Prediction, inventory, and email forms |
| [`script.js`](script.js) | Form handling, API requests, and inventory chart |
| [`style.css`](style.css) | Browser interface styling |
| [`requirements.txt`](requirements.txt) | Original Python dependency pins |
| `trained_model2.pkl` | Serialized prediction model loaded with joblib |
| `test_with_last_known_inventory.csv` | Inventory records queried by store and department |

## Request flow

| Route | Input | Output |
| --- | --- | --- |
| `POST /predict` | Store, department, temperature, markdowns, size, store type, month, day, and holiday flag | Predicted weekly sales |
| `GET /get_data` | `store_number` and `dept_number` | Matching rows from the local CSV |
| `POST /send-email` | Recipient and client-supplied prediction/inventory data | Email delivery attempt through Flask-Mail |

Inventory is a lookup of saved records, not a connection to live stock systems. The repository includes a model artifact but does not include its training pipeline or a reproducible accuracy evaluation.

## Run locally

Use Python 3.11 and a virtual environment:

```sh
python -m venv .venv
# Activate the environment, then:
python -m pip install -r requirements.txt
python flask_model_server.py
```

Serve the browser files from a second terminal with `python -m http.server 8000` and open `http://127.0.0.1:8000`. The interface calls the local API at `http://127.0.0.1:5000`.

The requirements cover the web/API layer. The included serialized model has no recorded training environment; its additional estimator dependencies and compatibility still need establishing before real predictions can be claimed. Loading is deferred until a prediction is requested, so inventory lookup works independently. A model-loading failure produces a controlled error rather than preventing the API from starting.

For email, configure `SMTP_USERNAME`, `SMTP_PASSWORD`, and optionally `SMTP_SENDER` in the environment. Never commit these values. Email delivery requires working SMTP credentials. Debug mode is off unless `FLASK_DEBUG=1` is set.

## Behavior and checks

The interface sends one request per submission, maps holiday selections to 0/1, allows exactly one store type, and passes the fetched inventory records into the email payload. Failed inventory lookups clear stale records. The API validates prediction features and email payloads, and resolves inventory paths relative to its own source file.

```sh
python -m pip install -r requirements-dev.txt
python -m pytest --rootdir=. tests/test_api.py
npm install
npm test
```

Tests cover real form behavior using a local DOM and Flask routes. Network/model/email boundaries are substituted: tests do not deserialize the supplied model, contact SMTP, establish prediction accuracy, or demonstrate production readiness. The application remains a local prototype; its email route is not suitable for public deployment without access controls and abuse prevention.

## License

See [`LICENSE`](LICENSE) for the MIT license.
