"""
========================================================
  Expense Tracker App - Report Generator
  Purpose: Save analysis results as CSV/TXT reports
           to the outputs/ folder.
========================================================
"""

import pandas as pd
import os
from datetime import datetime


def save_analysis_report(summary: dict, cat_df: pd.DataFrame,
                          monthly_df: pd.DataFrame, insights: list,
                          output_dir: str = "outputs") -> str:
    """
    Write a human-readable text report.

    Returns
    -------
    str : Path to the saved .txt file
    """
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "expense_analysis_report.txt")

    lines = []
    divider = "=" * 60
    lines += [
        divider,
        "   EXPENSE TRACKER APP – ANNUAL ANALYSIS REPORT",
        f"   Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        divider, "",
        "📊 KEY PERFORMANCE INDICATORS",
        "-" * 40,
    ]

    for k, v in summary.items():
        label = k.replace("_", " ").title()
        if isinstance(v, float):
            lines.append(f"  {label:<28}: ₹{v:,.2f}" if "spend" in k or "transaction" in k else f"  {label:<28}: {v}")
        else:
            lines.append(f"  {label:<28}: {v}")

    lines += ["", "📋 CATEGORY-WISE BREAKDOWN", "-" * 40]
    lines.append(f"  {'Category':<22} {'Total (₹)':>12} {'Avg (₹)':>10} {'Count':>6} {'Share':>8}")
    lines.append("  " + "-" * 60)
    for _, row in cat_df.iterrows():
        lines.append(
            f"  {row['category']:<22} {row['total']:>12,.2f} {row['avg']:>10,.2f} "
            f"{row['count']:>6} {row['share_pct']:>7.1f}%"
        )

    lines += ["", "📅 MONTHLY TREND", "-" * 40]
    lines.append(f"  {'Month':<12} {'Total Spend':>12} {'Transactions':>13} {'MoM Growth':>12}")
    lines.append("  " + "-" * 50)
    for _, row in monthly_df.iterrows():
        growth = f"{row['mom_growth_pct']:+.1f}%" if pd.notnull(row['mom_growth_pct']) else "  N/A"
        lines.append(
            f"  {row['month_name']:<12} ₹{row['total_spend']:>11,.2f} "
            f"{row['num_transactions']:>13} {growth:>12}"
        )

    lines += ["", "🔍 AUTO-GENERATED INSIGHTS", "-" * 40]
    for i, ins in enumerate(insights, 1):
        lines.append(f"  {i}. {ins}")

    lines += ["", divider, "  END OF REPORT", divider]

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"📄 Report saved → {report_path}")
    return report_path


def save_csv_reports(cat_df, monthly_df, person_df, savings_df=None,
                     output_dir: str = "outputs") -> list:
    """Save all analysis DataFrames as CSVs."""
    os.makedirs(output_dir, exist_ok=True)
    paths = []

    files = {
        "report_category.csv": cat_df,
        "report_monthly.csv":  monthly_df,
        "report_persons.csv":  person_df,
    }
    if savings_df is not None:
        files["report_savings.csv"] = savings_df

    for fname, df in files.items():
        path = os.path.join(output_dir, fname)
        df.to_csv(path, index=False)
        paths.append(path)
        print(f"💾 CSV saved → {path}")

    return paths
