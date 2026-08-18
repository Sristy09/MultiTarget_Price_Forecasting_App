# Pokhara Price Intelligence

A Flask dashboard for the Pokhara wholesale vegetable & fruit price
forecasting project — built on the cleaned/feature-engineered data and
model outputs from the accompanying notebooks (01–07).

## Pages

| Route            | Description                                                        |
|-------------------|---------------------------------------------------------------------|
| `/`               | Overview — key stats, model comparison chart, top volatile products |
| `/products`       | Browse all 95 products, filter by category, search                  |
| `/products/<name>`| Product detail — price history chart, regional supply, forecast     |
| `/forecast`       | Month-11 forecast table (Baseline / RF / LightGBM)                  |
| `/performance`    | Validation metrics, MAE/R² charts, tuned LightGBM hyperparameters   |
| `/errors`         | Error breakdown by category and by unit                             |
| `/volatility`      | Products ranked by price-spread volatility                          |

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

## Project structure

```
vegprice_app/
├── app.py                  # Flask routes + data loading
├── data/                   # CSV / JSON outputs from the notebooks
├── templates/               # Jinja2 templates (black & white theme)
├── static/
│   ├── css/style.css        # Theme, layout, responsive rules
│   └── js/main.js           # Sidebar toggle, filters, chart defaults
└── requirements.txt
```

## Notes

- All data is read once at startup from the `data/` folder — no database
  needed. To refresh, re-run the notebooks and drop the updated CSVs in
  `data/` (keep the same filenames), then restart the app.
- Charts are rendered client-side with Chart.js (loaded from CDN).
- The UI is fully responsive: the sidebar collapses into a slide-out
  drawer below 780px width.
