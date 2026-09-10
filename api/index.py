'''SalesLens API — customer, retention, revenue, and action intelligence.'''
from functools import lru_cache
from io import StringIO
from pathlib import Path
import json

import pandas as pd
from flask import Flask, Response, jsonify, request
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "customer_360.parquet"
TRANSACTIONS_PATH = ROOT / "data" / "processed" / "clean_transactions.parquet"
REPORTS = ROOT / "reports"

class StrictJSONProvider(DefaultJSONProvider):
    """Emit JSON that browsers can parse (no NaN/Infinity tokens)."""

    def dumps(self, obj, **kwargs):
        def sanitize(value):
            if isinstance(value, dict):
                return {key: sanitize(item) for key, item in value.items()}
            if isinstance(value, (list, tuple)):
                return [sanitize(item) for item in value]
            try:
                if value != value:
                    return None
            except Exception:
                pass
            return value

        return super().dumps(sanitize(obj), **kwargs)

app = Flask(__name__)
app.json = StrictJSONProvider(app)
CORS(app)

@lru_cache(maxsize=1)
def data() -> pd.DataFrame:
    return pd.read_parquet(DATA_PATH)

@lru_cache(maxsize=1)
def transactions() -> pd.DataFrame:
    return pd.read_parquet(TRANSACTIONS_PATH)

def records(frame: pd.DataFrame) -> list[dict]:
    # pandas float NaN cannot become None via to_dict; to_json emits valid JSON nulls.
    return json.loads(frame.to_json(orient="records", date_format="iso"))

def currency(value: float) -> str:
    return f"£{value / 1_000_000:.2f}M" if value >= 1_000_000 else f"£{value:,.0f}"

def filtered_customers() -> pd.DataFrame:
    """Apply the shared cohort controls to every analysis endpoint."""
    df = data()
    field_map = {"health": "health_tier", "rfm": "rfm_segment", "risk": "churn_risk_tier", "action": "action_priority", "value": "customer_value_tier", "country": "country_mode"}
    for param, field in field_map.items():
        values = [v for v in request.args.get(param, "").split(",") if v]
        if values:
            df = df[df[field].isin(values)]
    for param, field in (("revenue_min", "total_revenue"), ("revenue_max", "total_revenue"), ("probability_min", "churn_probability"), ("probability_max", "churn_probability")):
        raw = request.args.get(param)
        if raw:
            try:
                df = df[df[field] >= float(raw)] if param.endswith("min") else df[df[field] <= float(raw)]
            except ValueError:
                pass
    return df.copy()

def aggregate(frame: pd.DataFrame, group: str) -> list[dict]:
    result = frame.groupby(group, as_index=False).agg(customers=("customer_id", "count"), revenue=("total_revenue", "sum"), average_revenue=("total_revenue", "mean"), average_churn_probability=("churn_probability", "mean")).sort_values("revenue", ascending=False)
    return records(result)

def summarize(df: pd.DataFrame) -> dict:
    total_revenue = float(df.total_revenue.sum())
    high_risk = df[df.churn_risk_tier.isin(["High Risk", "Critical Risk"])]
    by_segment, by_priority = aggregate(df, "rfm_segment"), aggregate(df, "action_priority")
    top_segment = max(by_segment, key=lambda item: item["revenue"], default={"rfm_segment": "No segment", "revenue": 0})
    return {
        "metrics": [
            {"label": "Customers in view", "value": f"{len(df):,}", "detail": "Customer-level profiles"},
            {"label": "Revenue represented", "value": currency(total_revenue), "detail": "Lifetime transaction revenue"},
            {"label": "Retention targets", "value": f"{int(df.retention_target_flag.sum()):,}", "detail": "Prioritised for intervention"},
            {"label": "Revenue at high risk", "value": currency(float(high_risk.total_revenue.sum())), "detail": "High + critical churn risk"}
        ],
        "segments": by_segment,
        "priorities": by_priority,
        "health": aggregate(df, "health_tier"),
        "risk": aggregate(df, "churn_risk_tier"),
        "insights": [
            f"{int(df.vip_flag.sum()):,} high-value customers are flagged as VIPs.",
            f"{int(high_risk.shape[0]):,} customers require immediate retention attention.",
            f"{top_segment['rfm_segment']} is the highest-revenue segment at {currency(float(top_segment['revenue']))}."
        ]
    }

def pagination(frame: pd.DataFrame, default_limit: int = 12) -> tuple[pd.DataFrame, dict]:
    try:
        page, limit = max(int(request.args.get("page", 1)), 1), min(max(int(request.args.get("limit", default_limit)), 1), 100)
    except ValueError:
        page, limit = 1, default_limit
    total, pages = len(frame), max((len(frame) + limit - 1) // limit, 1)
    page = min(page, pages)
    return frame.iloc[(page - 1) * limit:page * limit], {"page": page, "limit": limit, "total": total, "pages": pages}

@app.get("/health")
def health_check():
    return {"status": "ok", "product": "SalesLens"}

@app.get("/api/dashboard")
def dashboard():
    response = summarize(filtered_customers())
    response["page"] = request.args.get("page", "overview")
    return jsonify(response)

@app.get("/api/filters")
def filters():
    df = data()
    return jsonify({"health": sorted(df.health_tier.dropna().unique().tolist()), "rfm": sorted(df.rfm_segment.dropna().unique().tolist()), "risk": sorted(df.churn_risk_tier.dropna().unique().tolist()), "action": sorted(df.action_priority.dropna().unique().tolist()), "value": sorted(df.customer_value_tier.dropna().unique().tolist()), "country": sorted(df.country_mode.dropna().unique().tolist())})

@app.get("/api/segments")
def segments():
    df = filtered_customers()
    table = df.groupby("rfm_segment", as_index=False).agg(customers=("customer_id", "count"), revenue=("total_revenue", "sum"), avg_recency_days=("recency_days", "mean"), avg_invoices=("total_invoices", "mean"))
    return jsonify({"rfm": aggregate(df, "rfm_segment"), "value": aggregate(df, "customer_value_tier"), "health_by_segment": records(df.groupby(["rfm_segment", "health_tier"], as_index=False).agg(customers=("customer_id", "count"), revenue=("total_revenue", "sum")))})

@app.get("/api/retention")
def retention():
    df = filtered_customers()
    bands = pd.cut(df.churn_probability, [-.01, .2, .4, .6, .8, 1], labels=["0–20%", "20–40%", "40–60%", "60–80%", "80–100%"])
    distribution = df.assign(probability_band=bands).groupby("probability_band", observed=False, as_index=False).agg(customers=("customer_id", "count"), revenue=("total_revenue", "sum"))
    high = df.sort_values(["churn_probability", "total_revenue"], ascending=False)
    high_page, meta = pagination(high[["customer_id", "country_mode", "total_revenue", "rfm_segment", "health_tier", "churn_probability", "churn_risk_tier", "final_recommended_action"]], 15)
    drivers = pd.read_csv(REPORTS / "churn_global_feature_importance.csv").sort_values("abs_coefficient", ascending=False).head(12)
    return jsonify({"risk": aggregate(df, "churn_risk_tier"), "distribution": records(distribution), "high_risk": records(high_page), "pagination": meta, "drivers": records(drivers), "model_metrics": records(pd.read_csv(REPORTS / "model_metrics.csv"))})

@app.get("/api/revenue")
def revenue():
    df = filtered_customers()
    tx = transactions()
    if len(df) != len(data()):
        tx = tx[tx.customer_id.isin(df.customer_id)]
    monthly = tx.groupby("invoice_yearmonth", as_index=False).agg(revenue=("revenue", "sum"), invoices=("invoice_id", "nunique"), customers=("customer_id", "nunique")).sort_values("invoice_yearmonth", ascending=True)
    monthly["average_order_value"] = monthly.revenue / monthly.invoices
    countries = tx.groupby("country", as_index=False).agg(revenue=("revenue", "sum"), customers=("customer_id", "nunique")).sort_values("revenue", ascending=False).head(12)
    products = tx.groupby(["stock_code", "description"], as_index=False).agg(revenue=("revenue", "sum"), quantity=("quantity", "sum"), customers=("customer_id", "nunique")).sort_values("revenue", ascending=False).head(12)
    return jsonify({"monthly": records(monthly), "countries": records(countries), "products": records(products), "segments": aggregate(df, "rfm_segment"), "priorities": aggregate(df, "action_priority")})

@app.get("/api/actions")
def actions():
    df = filtered_customers()
    plan = df.groupby(["action_priority", "final_recommended_action"], as_index=False).agg(customers=("customer_id", "count"), revenue=("total_revenue", "sum"), average_churn_probability=("churn_probability", "mean"))
    queue, meta = pagination(df.sort_values(["action_priority", "churn_probability", "total_revenue"], ascending=[True, False, False])[["customer_id", "action_priority", "final_recommended_action", "total_revenue", "churn_probability"]], 15)
    return jsonify({"priorities": aggregate(df, "action_priority"), "health": aggregate(df, "health_tier"), "plan": records(plan), "queue": records(queue), "pagination": meta})

@app.get("/api/customers")
def customers():
    df = filtered_customers()
    search = request.args.get("search", "").strip()
    if search:
        df = df[df.customer_id.astype(str).str.contains(search, na=False) | df.country_mode.str.contains(search, case=False, na=False) | df.rfm_segment.str.contains(search, case=False, na=False)]
    cols = ["customer_id", "country_mode", "total_revenue", "rfm_segment", "churn_risk_tier", "customer_health_score", "final_recommended_action"]
    rows, meta = pagination(df[cols].sort_values("total_revenue", ascending=False))
    return jsonify({"records": records(rows), **meta})

@app.get("/api/customer/<customer_id>")
def customer_profile(customer_id: str):
    customer = data()[data().customer_id.astype(str) == customer_id]
    if customer.empty:
        return jsonify({"error": "Customer not found"}), 404
    row = records(customer)[0]
    tx = transactions()[transactions().customer_id.astype(str) == customer_id]
    row["recent_purchases"] = records(tx.sort_values("invoice_date", ascending=False)[["invoice_id", "invoice_date", "description", "quantity", "revenue"]].head(8))
    return jsonify(row)

@app.get("/api/export/<kind>")
def export(kind: str):
    df = filtered_customers()
    if kind == "high-risk":
        df = df[df.churn_risk_tier.isin(["High Risk", "Critical Risk"])]
    elif kind == "vip":
        df = df[df.vip_flag]
    elif kind == "action-plan":
        df = df.sort_values(["action_priority", "churn_probability", "total_revenue"], ascending=[True, False, False])
    elif kind != "customers":
        return jsonify({"error": "Unknown export"}), 404
    output = StringIO()
    df.to_csv(output, index=False)
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": f"attachment; filename=saleslens-{kind}.csv"})
