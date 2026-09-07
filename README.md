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

## Local setup status

The original dependencies pin Flask 2.0.2, Flask-Cors 3.0.10, Flask-Mail 0.9.1, joblib 1.0.1, and NumPy 1.21.2. A complete, freshly tested environment for the serialized model is not supplied, so these pins should be reviewed before attempting a local run.

The source expects the API to run from the repository directory on `http://127.0.0.1:5000`; the browser interface is `index.html`. The intended backend entry point is:

```sh
python flask_model_server.py
```

Before running it, establish a compatible model-loading environment. For email, set `SMTP_USERNAME` and `SMTP_PASSWORD` for your own SMTP account. Set `SMTP_SENDER` if the sender should differ from the username. Do not commit credentials. When `SMTP_PASSWORD` is absent, it does not block application initialization, but authenticated email delivery will not work. The backend currently starts in Flask debug mode and is intended for local development.

## Current limitations

- The browser's holiday conversion checks the misspelling `"flase"`, so the form's `false` option is incorrectly sent as a holiday.
- `index.html` loads `script.js` twice, which can duplicate event handlers.
- The inventory view draws a chart, but the email handler still reads table rows from an older interface. Inventory records therefore do not flow into email through the current UI.
- SMTP settings require configuration; successful email delivery is not established by the presence of a form.
- Model compatibility, prediction accuracy, and end-to-end operation need validation before deployment.

These limitations describe the committed prototype honestly and identify the next improvements needed for a dependable demonstration.

## License

See [`LICENSE`](LICENSE) for the MIT license.
