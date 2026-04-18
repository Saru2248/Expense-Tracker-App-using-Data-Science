"""
========================================================
  Expense Tracker App using Data Science
  Author   : [Your Name]
  Date     : 2024
  Purpose  : Main entry-point that orchestrates all 5 phases.
  Run with : python main.py
========================================================
"""
import io
import sys
import os
import time

# Fix Windows cp1252 encoding issue - forces UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import project modules
from src.data_generator   import save_datasets
from src.data_cleaner     import clean_expense_data
from src.analyzer         import (
    basic_summary, category_analysis, monthly_trend_analysis,
    person_analysis, payment_method_analysis, detect_overspending,
    weekend_analysis, top_transactions, savings_analysis, generate_insights
)
from src.visualizer       import generate_all_charts
from src.report_generator import save_analysis_report, save_csv_reports

import pandas as pd


BANNER = (
    "\n" +
    "=" * 58 + "\n"
    "   EXPENSE TRACKER APP - DATA SCIENCE PROJECT\n"
    "   Synthetic Data | EDA | Analysis | Visualization\n" +
    "=" * 58
)


def main():
    print(BANNER)
    t_start = time.time()

    DATA_DIR   = "data"
    OUTPUT_DIR = "outputs"
    BUDGET     = 30000.0   # Monthly budget cap (Rs.)

    # ── PHASE 1: Generate Synthetic Data ──────────────
    print("\n" + "-" * 55)
    print("  [PHASE 1] Generating Synthetic Data ...")
    print("-" * 55)
    paths = save_datasets(output_dir=DATA_DIR)

    # ── PHASE 2: Clean the Raw Data ───────────────────
    print("\n" + "-" * 55)
    print("  [PHASE 2] Cleaning Data ...")
    print("-" * 55)
    df = clean_expense_data(
        raw_path   = paths["dirty"],
        output_dir = DATA_DIR,
        save       = True,
    )

    # Load income data
    df_income = pd.read_csv(paths["income"])
    df_income["date"] = pd.to_datetime(df_income["date"])

    # ── PHASE 3: EDA & Analysis ───────────────────────
    print("\n" + "-" * 55)
    print("  [PHASE 3] Exploratory Data Analysis ...")
    print("-" * 55)

    summary    = basic_summary(df)
    cat_df     = category_analysis(df)
    monthly_df = monthly_trend_analysis(df)
    person_df  = person_analysis(df)
    pay_df     = payment_method_analysis(df)
    over_df    = detect_overspending(df, budget_per_month=BUDGET)
    weekend_df = weekend_analysis(df)
    top_df     = top_transactions(df, n=10)
    savings_df = savings_analysis(df, df_income)
    insights   = generate_insights(df, summary)

    # ── PHASE 4: Visualization ────────────────────────
    print("\n" + "-" * 55)
    print("  [PHASE 4] Generating Charts ...")
    print("-" * 55)
    chart_paths = generate_all_charts(
        df         = df,
        summary    = summary,
        savings_df = savings_df,
        output_dir = OUTPUT_DIR,
        budget     = BUDGET,
    )

    # ── PHASE 5: Reports ──────────────────────────────
    print("\n" + "-" * 55)
    print("  [PHASE 5] Saving Reports ...")
    print("-" * 55)
    save_analysis_report(summary, cat_df, monthly_df, insights, output_dir=OUTPUT_DIR)
    save_csv_reports(cat_df, monthly_df, person_df, savings_df, output_dir=OUTPUT_DIR)

    # ── SUMMARY ───────────────────────────────────────
    elapsed = round(time.time() - t_start, 1)
    print("\n" + "=" * 55)
    print(f"  ALL PHASES COMPLETE in {elapsed}s")
    print("=" * 55)
    print(f"  Data    --> {DATA_DIR}/")
    print(f"  Outputs --> {OUTPUT_DIR}/")
    print(f"  Charts  : {len(chart_paths)} PNG files saved")
    print(f"  Reports : expense_analysis_report.txt + CSVs")
    print("\n  To launch interactive dashboard:")
    print("       streamlit run dashboard.py")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    main()
