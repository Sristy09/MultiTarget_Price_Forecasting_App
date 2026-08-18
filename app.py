"""
Pokhara Price Intelligence — Flask Application
A dashboard for exploring Nepal vegetable/fruit market prices,
model performance, and Month-11 price forecasts.
"""
import os
import json
import math
import pandas as pd
import numpy as np
from flask import Flask, render_template, jsonify, request, abort

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

app = Flask(__name__)


# ----------------------------------------------------------------------
# Data loading (once, at startup)
# ----------------------------------------------------------------------
def _read_csv(name):
    return pd.read_csv(os.path.join(DATA_DIR, name))


df_clean = _read_csv("all_months_clean.csv")
df_features = _read_csv("all_months_features.csv")
df_validation_summary = _read_csv("baseline_vs_rf_vs_lightgbm_validation.csv")
df_category_error = _read_csv("category_wise_error.csv")
df_forecast = _read_csv("month_11_forecast.csv")
df_unit_error = _read_csv("unit_wise_error.csv")
df_val_preds = _read_csv("validation_month_9_predictions.csv")
df_volatile = _read_csv("volatile_product_analysis.csv")

with open(os.path.join(DATA_DIR, "lightgbm_best_params.json")) as f:
    lgbm_params = json.load(f)

MONTH_NAME_ORDER = ["shrawan", "bhadra", "ashwin", "kartik", "mangsir",
                     "poush", "magh", "falgun", "chaitra", "baishakh"]
MONTH_LABEL = {i + 1: m.capitalize() for i, m in enumerate(MONTH_NAME_ORDER)}

REGION_COLS = [c for c in df_clean.columns if c not in [
    'Product_Name', 'Category', 'bs_year', 'bs_month', 'month_idx', 'month_name',
    'Volume', 'Min_Price', 'Max_Price', 'Avg_Price', 'Unit', 'unit_canonical',
    'unit_changed', 'Total_Amount', 'Volume_Equals', 'TOTAL_sources',
    'reconciliation_gap', 'import_share', 'n_months_present', 'is_balanced'
]]


def clean_json(obj):
    """Recursively replace NaN/Inf with None so jsonify never breaks."""
    if isinstance(obj, dict):
        return {k: clean_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_json(v) for v in obj]
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return round(obj, 4)
    return obj


def df_records(df):
    return clean_json(df.replace({np.nan: None}).to_dict(orient="records"))


def confidence_label(n_months_present):
    """Map months-of-history to a human confidence tier for forecast trust."""
    if n_months_present is None:
        return ("unknown", "Unknown")
    if n_months_present >= 9:
        return ("high", "High confidence")
    if n_months_present >= 5:
        return ("medium", "Medium confidence")
    if n_months_present >= 2:
        return ("low", "Low confidence")
    return ("single", "Single observation")


app.jinja_env.filters["confidence"] = confidence_label


# ----------------------------------------------------------------------
# Shared / derived stats
# ----------------------------------------------------------------------
def get_overview_stats():
    n_products = df_clean['Product_Name'].nunique()
    n_categories = df_clean['Category'].nunique()
    n_months = df_clean['month_idx'].nunique()
    n_balanced = df_clean[df_clean['is_balanced']]['Product_Name'].nunique()
    avg_price = round(df_clean['Avg_Price'].mean(), 2)
    total_volume = int(df_clean['Volume'].sum())

    best_row = df_validation_summary.loc[
        df_validation_summary['LightGBM MAE'].idxmin()
    ]
    forecast_coverage = df_forecast['Product_Name'].nunique()
    low_confidence_n = int((df_forecast['n_months_present'] < 5).sum())

    return {
        "n_products": n_products,
        "n_categories": n_categories,
        "n_months": n_months,
        "n_balanced": n_balanced,
        "avg_price": avg_price,
        "forecast_coverage": forecast_coverage,
        "low_confidence_n": low_confidence_n,
        "total_volume": total_volume,
        "best_target": best_row['Target'],
        "best_mae": round(float(best_row['LightGBM MAE']), 2),
    }


# ----------------------------------------------------------------------
# Page routes
# ----------------------------------------------------------------------
@app.route("/")
def home():
    stats = get_overview_stats()
    top_volatile = df_volatile.sort_values(
        'Price_Spread_STD', ascending=False
    ).head(6).to_dict(orient="records")
    top_volatile = clean_json(pd.DataFrame(top_volatile).replace({np.nan: None}).to_dict(orient="records"))
    return render_template(
        "index.html",
        active="home",
        stats=stats,
        validation_summary=df_records(df_validation_summary),
        top_volatile=top_volatile,
    )


@app.route("/products")
def products():
    category = request.args.get("category", "all")
    search = request.args.get("q", "").strip().lower()

    latest = (
        df_clean.sort_values(["Product_Name", "month_idx"])
        .groupby("Product_Name")
        .tail(1)
        .copy()
    )

    if category != "all":
        latest = latest[latest["Category"] == category]
    if search:
        latest = latest[latest["Product_Name"].str.lower().str.contains(search)]

    latest = latest.sort_values("Product_Name")
    products_list = df_records(
        latest[["Product_Name", "Category", "Avg_Price", "Min_Price",
                "Max_Price", "Unit", "month_name", "is_balanced"]]
    )

    categories = sorted(df_clean["Category"].unique().tolist())
    return render_template(
        "products.html",
        active="products",
        products=products_list,
        categories=categories,
        selected_category=category,
        search=search,
        total=len(products_list),
    )


@app.route("/products/<product_name>")
def product_detail(product_name):
    pdata = df_clean[df_clean["Product_Name"] == product_name].sort_values("month_idx")
    if pdata.empty:
        abort(404)

    history = df_records(
        pdata[["month_idx", "month_name", "Min_Price", "Avg_Price", "Max_Price", "Volume"]]
    )

    # Region / district supply breakdown (latest month with data)
    latest_row = pdata.tail(1).iloc[0]
    region_supply = {
        col: float(latest_row[col]) for col in REGION_COLS
        if col in latest_row and pd.notna(latest_row[col]) and latest_row[col] > 0
    }
    region_supply = dict(sorted(region_supply.items(), key=lambda x: -x[1])[:8])

    category = latest_row["Category"]
    unit = latest_row["unit_canonical"]
    is_balanced = bool(latest_row["is_balanced"])
    n_months_present = int(latest_row["n_months_present"])

    # Forecast for this product, if available
    forecast_row = df_forecast[df_forecast["Product_Name"] == product_name]
    forecast = df_records(forecast_row)[0] if not forecast_row.empty else None

    # Volatility info
    vol_row = df_volatile[df_volatile["Product_Name"] == product_name]
    volatility = df_records(vol_row)[0] if not vol_row.empty else None

    all_products = sorted(df_clean["Product_Name"].unique().tolist())

    return render_template(
        "product_detail.html",
        active="products",
        product_name=product_name,
        category=category,
        unit=unit,
        is_balanced=is_balanced,
        n_months_present=n_months_present,
        history=history,
        region_supply=region_supply,
        forecast=forecast,
        volatility=volatility,
        all_products=all_products,
    )


@app.route("/forecast")
def forecast():
    category = request.args.get("category", "all")
    search = request.args.get("q", "").strip().lower()
    confidence = request.args.get("confidence", "all")

    # df_forecast (from the updated notebook) already carries Category,
    # Last_Observed_Month_Idx/Name, Forecast_Month_Idx, n_months_present,
    # is_balanced — one row per product, full coverage, no merge needed.
    fdf = df_forecast.copy()

    if category != "all":
        fdf = fdf[fdf["Category"] == category]
    if search:
        fdf = fdf[fdf["Product_Name"].str.lower().str.contains(search)]
    if confidence == "low":
        fdf = fdf[fdf["n_months_present"] < 5]
    elif confidence == "high":
        fdf = fdf[fdf["n_months_present"] >= 9]

    fdf = fdf.sort_values("Product_Name")
    forecast_list = df_records(fdf)
    categories = sorted(df_clean["Category"].unique().tolist())
    full_coverage = df_forecast["Product_Name"].nunique()
    low_confidence_n = int((df_forecast["n_months_present"] < 5).sum())

    return render_template(
        "forecast.html",
        active="forecast",
        forecasts=forecast_list,
        categories=categories,
        selected_category=category,
        selected_confidence=confidence,
        search=search,
        total=len(forecast_list),
        full_coverage=full_coverage,
        low_confidence_n=low_confidence_n,
    )


@app.route("/performance")
def performance():
    return render_template(
        "performance.html",
        active="performance",
        validation_summary=df_records(df_validation_summary),
        lgbm_params=lgbm_params,
        val_preds=df_records(df_val_preds),
    )


@app.route("/errors")
def errors():
    return render_template(
        "errors.html",
        active="errors",
        category_error=df_records(df_category_error),
        unit_error=df_records(df_unit_error),
    )


@app.route("/volatility")
def volatility():
    sort_by = request.args.get("sort", "Price_Spread_STD")
    vdf = df_volatile.copy()
    if sort_by in vdf.columns:
        vdf = vdf.sort_values(sort_by, ascending=False)
    return render_template(
        "volatility.html",
        active="volatility",
        volatile=df_records(vdf),
        sort_by=sort_by,
    )


# ----------------------------------------------------------------------
# JSON API endpoints (for chart data / autocomplete)
# ----------------------------------------------------------------------
@app.route("/api/product/<product_name>/history")
def api_product_history(product_name):
    pdata = df_clean[df_clean["Product_Name"] == product_name].sort_values("month_idx")
    return jsonify(df_records(
        pdata[["month_idx", "month_name", "Min_Price", "Avg_Price", "Max_Price"]]
    ))


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, host="0.0.0.0", port=port)
