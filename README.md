# Customer 360 Revenue Intelligence Platform

**Customer Segmentation · Churn Risk Prediction · Health Scoring · Revenue Action Planning**

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-DuckDB%201.1.3-F4C519?logo=duckdb&logoColor=black)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?logo=streamlit&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4.2-F7931E?logo=scikit-learn&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-2.0.3-006600)
![SHAP](https://img.shields.io/badge/SHAP-0.45.1-8A2BE2)
![Plotly](https://img.shields.io/badge/Plotly-5.22-3F4F75?logo=plotly&logoColor=white)
![Status](https://img.shields.io/badge/Status-Deployed%20on%20Streamlit%20Cloud-brightgreen)

**Live App:** [Streamlit Dashboard](https://customer-360-revenue-intelligence-4r8ryklwgjkwcdhrpzmf3v.streamlit.app)  
**GitHub Repo:** [customer-360-revenue-intelligence](https://github.com/PrajwalShekar22/customer-360-revenue-intelligence)


---

## Live Demo

[Open the Streamlit Dashboard](https://customer-360-revenue-intelligence-4r8ryklwgjkwcdhrpzmf3v.streamlit.app)

The dashboard is deployed on Streamlit Community Cloud and provides an interactive Customer 360 view for customer segmentation, churn risk, health scoring, revenue insights, SQL-backed reporting o[...]


## Executive Summary

An end-to-end customer analytics platform that processes 1M+ online retail transactions, segments 5,878 customers using RFM scoring, predicts churn risk with a Logistic Regression model (ROC-AUC 0[...]

**Core Business Problem:**
How can a business use customer transaction history to identify high-value customers, predict who is likely to churn, and prioritize retention and growth actions?

**Solution:**
A fully reproducible end-to-end Python pipeline that transforms raw Excel transaction data into cleaned transactions, 27-feature customer profiles, RFM segments, churn predictions, health scores, [...]

**Key Insight:**
Champions represent 22.1% of customers but generate **68.3% of revenue (£11.86M)**. Meanwhile, 2,952 customers are flagged as retention targets and 874 are classified as Critical Risk.

---

## Key Results at a Glance

| Metric | Result |
|---|---|
| Raw transaction rows | 1,067,371 |
| Clean transaction rows | 779,425 |
| Customers analyzed | 5,878 |
| Total revenue | £17,374,804.27 |
| Repeat buyers | 4,255 customers (72.4%) |
| Revenue from repeat buyers | £16,814,532 (96.8% of total) |
| Champion customers | 1,297 (22.1% of customers) |
| Revenue from Champions | £11.86M (68.3% of total) |
| Churn model ROC-AUC | **0.8148** (Logistic Regression) |
| Observation window customers | 5,041 |
| Churned customers (label) | 2,512 (49.8%) |
| Retained customers (label) | 2,529 (50.2%) |
| Retention targets flagged | 2,952 customers |
| VIP customers | 1,511 customers |
| Dashboard tabs | 7 |
| SQL analytics layer | 10 DuckDB SQL queries · 10 validated reporting outputs |
| Revenue reconciliation (SQL) | £0.00 difference across Python and SQL outputs |

---

## Project Overview

This project uses the [UCI Online Retail II dataset](https://archive.ics.uci.edu/dataset/502/online+retail+ii) to build a Customer 360 analytics platform for a UK-based online retailer. The pipeli[...]

The project demonstrates practical skills in data analytics, business analytics, machine learning, model explainability, and business dashboarding.

---

## Business Problem

Retail businesses need answers to key questions that raw transaction data alone cannot provide:

- Who are our most valuable customers?
- Which customers are at risk of churning?
- Which customer groups generate the majority of revenue?
- Which customers should receive retention campaigns vs loyalty rewards vs growth nurture?
- How do we quantify customer health in a single, business-friendly metric?

This project addresses each question using a structured, reproducible customer analytics workflow built entirely from transaction history.

---

## Dataset

| Property | Value |
|---|---|
| Name | UCI Online Retail II |
| Source | UC Irvine Machine Learning Repository |
| Raw rows | 1,067,371 |
| Sheets | Year 2009-2010, Year 2010-2011 |
| Date range | December 2009 – December 2011 |
| Retailer | UK-based online gift/retail store |
| Columns | Invoice, StockCode, Description, Quantity, InvoiceDate, Price, Customer ID, Country |

**Currency note:** All monetary values are treated as GBP (£), consistent with the UK-based retailer source. Country filters customer location only and does not change transaction currency.

**Important limitations of this dataset:**
- Does not contain a true churn label — churn was engineered using a time-window method
- Does not contain customer demographics
- Does not include marketing campaign or contact history data
- Does not include exchange rates or multi-currency pricing

---

## Tech Stack

| Category | Tools | Version | Purpose |
|---|---|---|---|
| Language | Python | 3.11 | All pipeline scripts |
| Data Processing | pandas, NumPy | 2.2.2, 1.26.4 | Cleaning, EDA, feature engineering |
| Storage Format | Parquet (pyarrow), CSV | — | Processed datasets for efficient I/O |
| Machine Learning | scikit-learn, XGBoost | 1.4.2, 2.0.3 | Churn model training and comparison |
| Explainability | SHAP | 0.45.1 | Model driver interpretation |
| Visualization | Plotly, matplotlib | 5.22, 3.8.4 | Interactive and static charts |
| Dashboard | Streamlit | 1.35.0 | Interactive Customer 360 dashboard |
| SQL Analytics | SQL, DuckDB | 1.1.3 | Local SQL analytics layer over Parquet files for executive KPI and reporting outputs |
| Version Control | Git | — | Local commits and project history |

**Future / optional extensions (not yet implemented):**
BigQuery · Looker Studio · Docker · GitHub Actions · Streamlit Community Cloud

---

## Project Architecture

```
Raw Excel Data (online_retail_II.xlsx)
          ↓
   Data Inspection                  →  reports/data_inspection.txt
          ↓
  Data Quality Audit                →  reports/data_quality_summary.csv
          ↓
     Data Cleaning                  →  clean_transactions.parquet
          ↓
   Clean Output Verification        →  22-point assertion checks
          ↓
 Exploratory Data Analysis          →  7 CSV tables + 6 Plotly HTML charts
          ↓
Customer Feature Engineering        →  customer_features.parquet (5,878 × 27)
          ↓
     RFM Segmentation               →  rfm_segments.parquet (10 segments)
          ↓
   Churn Label Creation             →  churn_model_base.parquet (5,041 labeled)
          ↓
  Churn Model Training              →  churn_model.pkl (LR, RF, XGBoost compared)
          ↓
   SHAP Explainability              →  SHAP plots + feature importance CSV
          ↓
  Customer Health Score             →  customer_360.parquet (5,878 × 46)
          ↓
DuckDB SQL Analytics Layer          →  reports/sql_outputs/ (10 CSV reporting tables)
          ↓
  Streamlit Dashboard               →  app/streamlit_app.py (7 tabs)
```

All processed outputs are stored as Parquet and CSV files for reproducible, fast local analytics and efficient dashboard loading.

> The DuckDB SQL layer queries the processed Parquet datasets and generates reusable reporting tables under `reports/sql_outputs/`.

---

## Folder Structure

```
customer-360-revenue-intelligence/
├── app/
│   └── streamlit_app.py              # 7-tab Streamlit dashboard
├── data/
│   ├── raw/                          # Source Excel file (gitignored)
│   ├── interim/                      # Intermediate outputs
│   └── processed/                    # Final cleaned datasets (gitignored)
├── models/
│   ├── churn_model.pkl               # Trained LR pipeline (gitignored)
│   ├── churn_feature_columns.json    # Feature metadata
│   └── model_metrics.json            # Performance metrics for all models
├── notebooks/                        # Jupyter notebooks (exploratory)
├── reports/
│   ├── figures/                      # Plotly HTML + SHAP PNG charts
│   ├── screenshots/                  # Dashboard screenshots (for README)
│   └── sql_outputs/                  # DuckDB SQL reporting outputs (10 CSVs)
├── sql/
```