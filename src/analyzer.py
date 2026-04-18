"""
========================================================
  Expense Tracker App - Analysis Module
  Purpose: Perform comprehensive exploratory data analysis
           including category, monthly, and person-wise
           breakdowns, and overspending detection.
========================================================
"""

import pandas as pd
import numpy as np
import os


# ─── 1. Basic Summary ──────────────────────────────────

def basic_summary(df: pd.DataFrame) -> dict:
    """
    Compute high-level KPIs.

    Returns
    -------
    dict : total_spend, avg_monthly, top_category, num_transactions
    """
    summary = {
        "total_spend":       round(df["amount"].sum(), 2),
        "avg_monthly_spend": round(df.groupby("month_num")["amount"].sum().mean(), 2),
        "num_transactions":  len(df),
        "avg_transaction":   round(df["amount"].mean(), 2),
        "max_transaction":   round(df["amount"].max(), 2),
        "min_transaction":   round(df["amount"].min(), 2),
        "top_category":      df.groupby("category")["amount"].sum().idxmax(),
        "top_payment":       df["payment_method"].mode()[0],
        "date_range":        f"{df['date'].min().date()} → {df['date'].max().date()}",
        "num_persons":       df["person"].nunique(),
    }

    print("\n" + "="*55)
    print("  💰 KEY PERFORMANCE INDICATORS")
    print("="*55)
    for k, v in summary.items():
        label = k.replace("_", " ").title()
        print(f"  {label:25s} : {v:,}" if isinstance(v, (int, float)) else f"  {label:25s} : {v}")
    print("="*55)
    return summary


# ─── 2. Category Analysis ─────────────────────────────

def category_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Breakdown of spending by category.

    Returns
    -------
    pd.DataFrame : category, total, avg, count, % share
    """
    cat = df.groupby("category")["amount"].agg(
        total="sum", avg="mean", count="count"
    ).reset_index()

    cat["total"] = cat["total"].round(2)
    cat["avg"]   = cat["avg"].round(2)
    cat["share_pct"] = (cat["total"] / cat["total"].sum() * 100).round(2)
    cat = cat.sort_values("total", ascending=False)

    print("\n📊 Category-wise Spending:")
    print(cat.to_string(index=False))
    return cat


# ─── 3. Monthly Trend Analysis ────────────────────────

def monthly_trend_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Monthly total and transaction count.

    Returns
    -------
    pd.DataFrame : month, total_spend, num_transactions, avg_spend
    """
    month_order = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]

    monthly = df.groupby(["month_num", "month_name"]).agg(
        total_spend      = ("amount", "sum"),
        num_transactions = ("amount", "count"),
        avg_spend        = ("amount", "mean"),
    ).reset_index()

    monthly["total_spend"] = monthly["total_spend"].round(2)
    monthly["avg_spend"]   = monthly["avg_spend"].round(2)
    monthly["month_name"]  = pd.Categorical(
        monthly["month_name"], categories=month_order, ordered=True
    )
    monthly = monthly.sort_values("month_num").reset_index(drop=True)

    # MoM growth
    monthly["mom_growth_pct"] = monthly["total_spend"].pct_change() * 100
    monthly["mom_growth_pct"] = monthly["mom_growth_pct"].round(2)

    print("\n📅 Monthly Spending Trend:")
    print(monthly[["month_name", "total_spend", "num_transactions", "mom_growth_pct"]].to_string(index=False))
    return monthly


# ─── 4. Person-wise Analysis ──────────────────────────

def person_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Spending breakdown per person.
    """
    person = df.groupby("person")["amount"].agg(
        total="sum", avg="mean", count="count", max_single="max"
    ).reset_index()

    person["total"] = person["total"].round(2)
    person["avg"]   = person["avg"].round(2)
    person = person.sort_values("total", ascending=False)

    print("\n👤 Person-wise Spending:")
    print(person.to_string(index=False))
    return person


# ─── 5. Payment Method Analysis ───────────────────────

def payment_method_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Preferred payment methods by volume and count."""
    pay = df.groupby("payment_method")["amount"].agg(
        total="sum", count="count"
    ).reset_index()

    pay["total"] = pay["total"].round(2)
    pay["share_pct"] = (pay["total"] / pay["total"].sum() * 100).round(2)
    pay = pay.sort_values("total", ascending=False)

    print("\n💳 Payment Method Analysis:")
    print(pay.to_string(index=False))
    return pay


# ─── 6. Overspending Detection ────────────────────────

def detect_overspending(
    df: pd.DataFrame,
    budget_per_month: float = 30000.0
) -> pd.DataFrame:
    """
    Flag months where total spending exceeds the budget.

    Parameters
    ----------
    budget_per_month : Monthly budget cap (₹)

    Returns
    -------
    pd.DataFrame : Monthly spending with overspend flag
    """
    monthly = df.groupby(["month_num", "month_name"])["amount"].sum().reset_index()
    monthly.columns = ["month_num", "month_name", "total_spend"]
    monthly["budget"]       = budget_per_month
    monthly["overspent"]    = monthly["total_spend"] > budget_per_month
    monthly["over_by"]      = (monthly["total_spend"] - budget_per_month).clip(lower=0).round(2)
    monthly["savings"]      = (budget_per_month - monthly["total_spend"]).clip(lower=0).round(2)
    monthly["total_spend"]  = monthly["total_spend"].round(2)
    monthly = monthly.sort_values("month_num")

    print(f"\n⚠️  Overspending Report (Budget: ₹{budget_per_month:,.0f}/month)")
    over = monthly[monthly["overspent"]]
    if over.empty:
        print("  🟢 No months exceeded the budget!")
    else:
        print(f"  🔴 Overspent in {len(over)} months:")
        print(over[["month_name", "total_spend", "over_by"]].to_string(index=False))

    return monthly


# ─── 7. Category–Month Heatmap Data ───────────────────

def category_month_pivot(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a pivot table: rows = categories, cols = months.
    Useful for seaborn heatmap.
    """
    pivot = df.pivot_table(
        index="category",
        columns="month_name",
        values="amount",
        aggfunc="sum",
        fill_value=0,
    )

    month_order = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
    pivot = pivot.reindex(columns=[m for m in month_order if m in pivot.columns])

    return pivot


# ─── 8. Weekend vs Weekday Analysis ───────────────────

def weekend_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Compare spending on weekdays vs weekends."""
    wk = df.groupby("is_weekend")["amount"].agg(
        total="sum", avg="mean", count="count"
    ).reset_index()
    wk["label"] = wk["is_weekend"].map({True: "Weekend", False: "Weekday"})
    print("\n📆 Weekend vs Weekday Spending:")
    print(wk[["label", "total", "avg", "count"]].to_string(index=False))
    return wk


# ─── 9. Top Expensive Transactions ────────────────────

def top_transactions(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Return the top-N most expensive transactions."""
    top = df.nlargest(n, "amount")[["date", "person", "category", "description", "amount", "payment_method"]]
    print(f"\n💸 Top {n} Most Expensive Transactions:")
    print(top.to_string(index=False))
    return top


# ─── 10. Savings Rate ─────────────────────────────────

def savings_analysis(
    df_expense: pd.DataFrame,
    df_income: pd.DataFrame
) -> pd.DataFrame:
    """
    Compute monthly savings rate = (income - expense) / income × 100

    Parameters
    ----------
    df_expense : Cleaned expense DataFrame
    df_income  : Income DataFrame

    Returns
    -------
    pd.DataFrame : month, income, expense, savings, savings_rate
    """
    exp = df_expense.groupby("month_num")["amount"].sum().reset_index()
    exp.columns = ["month_num", "expense"]

    df_income["month_num"] = pd.to_datetime(df_income["date"]).dt.month
    inc = df_income.groupby("month_num")["income"].sum().reset_index()

    merged = pd.merge(inc, exp, on="month_num", how="left").fillna(0)
    merged["savings"]      = merged["income"] - merged["expense"]
    merged["savings_rate"] = (merged["savings"] / merged["income"] * 100).round(2)

    print("\n💹 Monthly Savings Analysis:")
    print(merged.to_string(index=False))
    return merged


# ─── 11. Generate Insights ────────────────────────────

def generate_insights(df: pd.DataFrame, summary: dict) -> list:
    """
    Auto-generate human-readable insights from data.

    Returns
    -------
    list : Plain-English insight strings
    """
    insights = []
    monthly = df.groupby("month_num")["amount"].sum()

    insights.append(f"💰 Total spend for the year: ₹{summary['total_spend']:,.2f}")
    insights.append(f"📊 Average monthly spend: ₹{summary['avg_monthly_spend']:,.2f}")
    insights.append(f"🏆 Highest spending category: {summary['top_category']}")
    insights.append(f"💳 Most preferred payment method: {summary['top_payment']}")

    peak_month_num   = monthly.idxmax()
    lowest_month_num = monthly.idxmin()

    month_names = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                   7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
    insights.append(f"📈 Peak spending month   : {month_names[peak_month_num]}"
                    f" (₹{monthly[peak_month_num]:,.2f})")
    insights.append(f"📉 Lowest spending month : {month_names[lowest_month_num]}"
                    f" (₹{monthly[lowest_month_num]:,.2f})")

    # Weekend flag
    wk = df.groupby("is_weekend")["amount"].mean()
    if True in wk.index and False in wk.index:
        if wk[True] > wk[False]:
            diff = wk[True] - wk[False]
            insights.append(
                f"📆 Weekend spending is ₹{diff:.0f} HIGHER than weekday average"
            )

    print("\n🔍 AUTO-GENERATED INSIGHTS:")
    for idx, ins in enumerate(insights, 1):
        print(f"  {idx}. {ins}")

    return insights


# ─── Run standalone ───────────────────────────────────
if __name__ == "__main__":
    df  = pd.read_csv("data/expenses_cleaned.csv")
    df["date"] = pd.to_datetime(df["date"])
    inc = pd.read_csv("data/income_data.csv")

    summary = basic_summary(df)
    category_analysis(df)
    monthly_trend_analysis(df)
    person_analysis(df)
    payment_method_analysis(df)
    detect_overspending(df, budget_per_month=30000)
    weekend_analysis(df)
    top_transactions(df, n=10)
    savings_analysis(df, inc)
    generate_insights(df, summary)
