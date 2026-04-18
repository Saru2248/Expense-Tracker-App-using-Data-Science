# 💸 Expense Tracker App using Data Science

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python)
![Pandas](https://img.shields.io/badge/Pandas-2.x-green?style=for-the-badge&logo=pandas)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?style=for-the-badge&logo=streamlit)
![Plotly](https://img.shields.io/badge/Plotly-Visualization-purple?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**An end-to-end Data Science project analyzing personal expense patterns using synthetic data, featuring EDA, trend detection, overspending alerts, and an interactive Streamlit dashboard.**

</div>

---

## 📌 Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Solution](#solution)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [How to Run](#how-to-run)
- [Results & Insights](#results--insights)
- [Screenshots](#screenshots)
- [Future Improvements](#future-improvements)
- [Interview Q&A](#interview-qa)
- [Author](#author)

---

## 📖 Overview

The **Expense Tracker App** is a Data Science portfolio project that simulates real-world personal finance analysis. It generates synthetic expense and income data for 5 personas across 10 spending categories over a full year (2024), then performs cleaning, EDA, visualization, and insight generation — all accessible via an interactive **Streamlit dashboard**.

> **Use Case Domains:** Personal Finance · Business Analytics · Financial Planning · Budgeting

---

## ❓ Problem Statement

> *"People struggle to understand where their money goes. Without proper tracking, overspending goes unnoticed until it's too late."*

- Individuals rarely track their monthly expenses systematically
- Business analysts need spending pattern data for financial planning
- Without visualization, raw transaction data is unactionable

---

## ✅ Solution

This project provides a **complete end-to-end pipeline**:

```
Data Generation → Cleaning → EDA → Visualization → Insights → Dashboard
```

| Step | What Happens |
|------|-------------|
| 🏗️ Data Generation | 500 synthetic transactions across 10 categories |
| 🚿 Data Cleaning | Remove duplicates, fix types, handle outliers |
| 🔍 EDA | Category, monthly, person-wise analysis |
| 📊 Visualization | 11 professional charts (pie, bar, heatmap, trend) |
| 💡 Insights | Auto-generated human-readable insights |
| 🖥️ Dashboard | Interactive Streamlit app with filters |

---

## ✨ Features

- 📦 **Synthetic Data Generator** — Realistic transactions for 5 persons, 10 categories
- 🚿 **Data Cleaning Pipeline** — Handles missing values, outliers, duplicates
- 📊 **11 Professional Charts** — Pie, bar, heatmap, trend, donut, distribution
- ⚠️ **Overspending Detection** — Flags months exceeding budget
- 💹 **Savings Rate Analysis** — Monthly income vs expense comparison
- 🏷️ **Category Intelligence** — Food, Rent, Transport, Shopping, Health, etc.
- 👤 **Multi-Person Analysis** — Compare spending across 5 personas
- 🖥️ **Streamlit Dashboard** — Dark-themed interactive UI with real-time filters
- 📄 **Auto Reports** — Saves CSV + TXT analysis summaries

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| **Python 3.9+** | Core language |
| **Pandas** | Data manipulation & analysis |
| **NumPy** | Numerical operations |
| **Matplotlib / Seaborn** | Static charts |
| **Plotly** | Interactive dashboard charts |
| **Streamlit** | Web dashboard |
| **scikit-learn** | Optional ML forecasting |

---

## 📁 Project Structure

```
Expense-Tracker-App/
│
├── data/                          # CSV datasets
│   ├── expenses_raw.csv           # Synthetic raw data (with issues)
│   ├── expenses_clean.csv         # Generator output
│   ├── expenses_cleaned.csv       # After full cleaning pipeline
│   └── income_data.csv            # Monthly income per person
│
├── notebooks/
│   └── expense_eda.py             # EDA walkthrough (notebook-style script)
│
├── src/                           # Core modules
│   ├── data_generator.py          # Synthetic data generation
│   ├── data_cleaner.py            # Cleaning pipeline
│   ├── analyzer.py                # EDA, KPIs, insights
│   ├── visualizer.py              # All chart functions
│   ├── report_generator.py        # TXT/CSV report exports
│   └── utils.py                   # Shared helpers
│
├── outputs/                       # Generated charts & reports
│   ├── 00_dashboard_summary.png
│   ├── 01_category_pie.png
│   ├── 02_monthly_bar.png
│   ├── 03_category_bar.png
│   ├── 04_heatmap.png
│   ├── 05_payment_donut.png
│   ├── 06_person_comparison.png
│   ├── 07_spending_trend.png
│   ├── 08_overspending.png
│   ├── 09_savings_rate.png
│   ├── 10_amount_distribution.png
│   └── expense_analysis_report.txt
│
├── images/                        # Screenshots for README
├── dashboard.py                   # Streamlit interactive dashboard
├── main.py                        # Main pipeline orchestrator
├── requirements.txt               # All dependencies
└── README.md                      # This file
```

---

## 🚀 How to Run

### Step 1 — Clone the Repository

```bash
git clone https://github.com/your-username/expense-tracker-app.git
cd expense-tracker-app
```

### Step 2 — Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python -m venv venv
source venv/bin/activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Run Full Pipeline

```bash
python main.py
```

**Expected Output:**
- Generates data in `data/`
- Creates 11 charts in `outputs/`
- Saves analysis reports

### Step 5 — Launch Interactive Dashboard

```bash
streamlit run dashboard.py
```

Open browser → `http://localhost:8501`

---

## 📊 Results & Insights

| Metric | Value |
|--------|-------|
| Total Annual Spend | ~₹3,85,000 |
| Avg Monthly Spend | ~₹32,000 |
| Top Category | Food & Dining |
| Highest Spend Month | Variable (check charts) |
| Preferred Payment | UPI / Credit Card |
| Savings Rate | 20–30% avg |

### Key Insights Generated:
- 🍕 **Food & Dining** accounts for ~25% of total spending
- 🏠 **Rent & Housing** — highest single-category spike
- 📈 **Q4 spending increases** due to festival/shopping season
- ⚠️ **3–4 months** typically exceed ₹30,000 budget
- 📆 **Weekend spending 15% higher** than weekday average

---

## 📸 Screenshots

> *Run `python main.py` to generate these in `/outputs/`*

| Chart | Description |
|-------|-------------|
| `00_dashboard_summary.png` | 4-panel annual overview |
| `01_category_pie.png` | Category spending breakdown |
| `02_monthly_bar.png` | Month-wise spending bars |
| `04_heatmap.png` | Category × Month heatmap |
| `08_overspending.png` | Budget vs actual per month |
| `09_savings_rate.png` | Monthly savings rate trend |

---

## 🔮 Future Improvements

| Feature | Priority |
|---------|---------|
| 📱 Mobile-friendly PWA | High |
| 🤖 ML spending prediction (Linear Regression) | High |
| 🔔 Budget breach alert emails | Medium |
| 🏦 Bank statement CSV import | Medium |
| 📊 PDF report export | Medium |
| 🌐 Real-time data via Plaid API | Low |
| 🎯 Financial goal tracking | Low |

---

## 🎤 Interview Q&A

**Q1: What is this project about?**
> This project tracks personal/business expenses using Data Science techniques. I built a complete pipeline — from generating synthetic transaction data to building an interactive Streamlit dashboard — covering data cleaning, EDA, visualization, and insight generation.

**Q2: Why synthetic data?**
> Real financial data is sensitive and not publicly available. I generated realistic synthetic data using domain knowledge — category distributions, seasonal patterns, and payment method biases — making it statistically representative without privacy concerns.

**Q3: How did you detect overspending?**
> I set a monthly budget threshold (₹30,000) and compared it against actual monthly totals. Months where spending exceeded the budget were flagged in red on the overspending bar chart with the exact overshoot amount.

**Q4: What data cleaning steps did you apply?**
> Removed exact duplicates, filled missing descriptions using category context, dropped rows with null amounts, fixed data types, detected outliers using the IQR method (3× IQR), and added derived columns (month, quarter, weekend flag).

**Q5: What is the IQR method for outlier detection?**
> IQR (Interquartile Range) = Q3 - Q1. Outliers are values below Q1 - 3×IQR or above Q3 + 3×IQR. I used a lenient 3× multiplier to only remove extreme data entry errors, not genuine high-value transactions.

---

## 👤 Author

- **Name:** [Your Name]
- **GitHub:** [github.com/your-username](https://github.com/your-username)
- **LinkedIn:** [linkedin.com/in/your-profile](https://linkedin.com/in/your-profile)
- **Role Target:** Data Analyst | Business Analyst | Financial Analyst

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
⭐ If this project helped you, give it a star on GitHub!
</div>
#   E x p e n s e - T r a c k e r - A p p - u s i n g - D a t a - S c i e n c e  
 