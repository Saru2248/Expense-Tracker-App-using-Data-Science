"""
========================================================
  Expense Tracker App - Data Cleaning Module
  Purpose: Clean, validate, and prepare expense data
           for analysis. Handles missing values,
           outliers, duplicates, and type casting.
========================================================
"""

import pandas as pd
import numpy as np
import os


def load_raw_data(filepath: str) -> pd.DataFrame:
    """Load raw CSV expense data."""
    df = pd.read_csv(filepath)
    print(f"📥 Loaded raw data: {df.shape[0]} rows × {df.shape[1]} cols")
    return df


def inspect_data(df: pd.DataFrame) -> None:
    """Print a comprehensive data quality report."""
    print("\n" + "="*55)
    print("  📋 DATA QUALITY REPORT")
    print("="*55)
    print(f"  Shape         : {df.shape[0]} rows × {df.shape[1]} cols")
    print(f"  Memory        : {df.memory_usage(deep=True).sum() / 1024:.1f} KB")
    print(f"\n  Dtypes:\n{df.dtypes.to_string()}")
    print(f"\n  Missing Values:")
    miss = df.isnull().sum()
    miss_pct = (miss / len(df) * 100).round(2)
    for col in df.columns:
        if miss[col] > 0:
            print(f"    {col:20s} → {miss[col]:3d} ({miss_pct[col]:.1f}%)")
    print(f"\n  Duplicate Rows : {df.duplicated().sum()}")
    print(f"\n  Amount Summary:")
    print(df["amount"].describe().to_string())
    print("="*55)


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove exact duplicate rows."""
    before = len(df)
    df = df.drop_duplicates()
    after = len(df)
    print(f"🔁 Duplicates removed : {before - after}")
    return df.reset_index(drop=True)


def fix_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values:
    - description → fill with category name
    - note        → fill with 'N/A'
    - amount      → drop (critical field)
    """
    # Description: fill with category
    if "description" in df.columns:
        n_miss = df["description"].isnull().sum()
        df["description"] = df.apply(
            lambda r: r["category"] + " Expense" if pd.isnull(r["description"]) else r["description"],
            axis=1
        )
        print(f"📝 Missing descriptions filled : {n_miss}")

    # Note: fill with N/A
    if "note" in df.columns:
        df["note"] = df["note"].fillna("N/A")

    # Drop rows where amount is missing (critical)
    before = len(df)
    df = df.dropna(subset=["amount"])
    print(f"💰 Rows dropped (null amount) : {before - len(df)}")

    return df


def fix_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure correct data types for all columns."""
    # Date
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])  # drop unparseable dates

    # Amount
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").round(2)
    df = df.dropna(subset=["amount"])

    # String columns
    for col in ["person", "category", "description", "payment_method", "note"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    print("✅ Data types fixed")
    return df


def remove_outliers(df: pd.DataFrame, method: str = "iqr") -> pd.DataFrame:
    """
    Remove amount outliers using IQR method.

    Parameters
    ----------
    method : 'iqr' or 'zscore'
    """
    before = len(df)

    if method == "iqr":
        Q1 = df["amount"].quantile(0.25)
        Q3 = df["amount"].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 3.0 * IQR   # lenient lower bound
        upper = Q3 + 3.0 * IQR
        mask = (df["amount"] >= max(lower, 10)) & (df["amount"] <= upper)
        df = df[mask]

    elif method == "zscore":
        from scipy import stats
        z_scores = np.abs(stats.zscore(df["amount"]))
        df = df[z_scores < 3.5]

    after = len(df)
    print(f"📊 Outliers removed ({method.upper()}) : {before - after} rows")
    return df.reset_index(drop=True)


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add useful derived columns for analysis:
    - month_name, month_num, year, quarter
    - day_of_week, is_weekend
    - amount_bucket (Low / Medium / High / Very High)
    """
    df["month_name"] = df["date"].dt.strftime("%B")          # January …
    df["month_num"]  = df["date"].dt.month                   # 1 … 12
    df["year"]       = df["date"].dt.year
    df["quarter"]    = df["date"].dt.quarter.map(
        {1: "Q1", 2: "Q2", 3: "Q3", 4: "Q4"}
    )
    df["day_of_week"] = df["date"].dt.day_name()
    df["is_weekend"]  = df["date"].dt.dayofweek >= 5

    # Amount bucket
    bins   = [0, 500, 2000, 5000, np.inf]
    labels = ["Low (<₹500)", "Medium (₹500–2K)", "High (₹2K–5K)", "Very High (>₹5K)"]
    df["amount_bucket"] = pd.cut(df["amount"], bins=bins, labels=labels)

    print("🔧 Derived columns added : month_name, quarter, day_of_week, amount_bucket")
    return df


def validate_cleaned_data(df: pd.DataFrame) -> bool:
    """Run final validation checks on cleaned dataset."""
    print("\n🔍 Final Validation:")
    checks = {
        "No nulls in date"   : df["date"].isnull().sum() == 0,
        "No nulls in amount" : df["amount"].isnull().sum() == 0,
        "All amounts > 0"    : (df["amount"] > 0).all(),
        "No duplicates"      : df.duplicated().sum() == 0,
    }
    all_pass = True
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check}")
        if not result:
            all_pass = False
    return all_pass


def clean_expense_data(
    raw_path: str,
    output_dir: str = "data",
    save: bool = True
) -> pd.DataFrame:
    """
    Full cleaning pipeline.

    Parameters
    ----------
    raw_path   : Path to raw CSV
    output_dir : Where to save cleaned CSV
    save       : Whether to persist cleaned data

    Returns
    -------
    pd.DataFrame : Cleaned expense data
    """
    df = load_raw_data(raw_path)
    inspect_data(df)

    print("\n🚿 Cleaning pipeline running …")
    df = remove_duplicates(df)
    df = fix_missing_values(df)
    df = fix_data_types(df)
    df = remove_outliers(df, method="iqr")
    df = add_derived_columns(df)

    validate_cleaned_data(df)

    if save:
        os.makedirs(output_dir, exist_ok=True)
        out_path = os.path.join(output_dir, "expenses_cleaned.csv")
        df.to_csv(out_path, index=False)
        print(f"\n💾 Cleaned data saved → {out_path}")
        print(f"   Final shape: {df.shape[0]} rows × {df.shape[1]} cols")

    return df


# ─── Run standalone ───────────────────────────────────
if __name__ == "__main__":
    df = clean_expense_data(
        raw_path   = "data/expenses_raw.csv",
        output_dir = "data",
        save       = True,
    )
    print("\n✅ Cleaning complete!")
    print(df[["date", "category", "amount", "month_name", "quarter"]].head(8).to_string(index=False))
