"""
========================================================
  Expense Tracker App - Synthetic Data Generator
  Author: Data Science Student Project
  Purpose: Generate realistic synthetic expense data
           for analysis, EDA, and visualization
========================================================
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# ─── Set seed for reproducibility ─────────────────────
np.random.seed(42)
random.seed(42)


# ─── Constants ────────────────────────────────────────

CATEGORIES = {
    "Food & Dining":    {"min": 100,  "max": 2500,  "weight": 0.25},
    "Rent & Housing":   {"min": 3000, "max": 15000, "weight": 0.08},
    "Transportation":   {"min": 50,   "max": 800,   "weight": 0.15},
    "Shopping":         {"min": 200,  "max": 5000,  "weight": 0.12},
    "Health & Medical": {"min": 100,  "max": 3000,  "weight": 0.08},
    "Entertainment":    {"min": 100,  "max": 2000,  "weight": 0.10},
    "Education":        {"min": 500,  "max": 5000,  "weight": 0.07},
    "Utilities":        {"min": 200,  "max": 1500,  "weight": 0.08},
    "Travel":           {"min": 500,  "max": 8000,  "weight": 0.04},
    "Personal Care":    {"min": 100,  "max": 1500,  "weight": 0.03},
}

PAYMENT_METHODS = ["Cash", "Credit Card", "Debit Card", "UPI", "Net Banking", "Wallet"]

PERSONS = ["Priya Sharma", "Arjun Mehta", "Sunita Patel", "Rohan Das", "Anita Joshi"]

DESCRIPTION_MAP = {
    "Food & Dining":    ["Zomato Order", "Restaurant Bill", "Grocery Shopping", "Cafe Coffee", "Swiggy Delivery", "Home Cooked Supplies"],
    "Rent & Housing":   ["Monthly Rent", "House Maintenance", "Water Bill", "Society Charges", "Room Rent"],
    "Transportation":   ["Ola Cab", "Bus Pass", "Petrol Fill", "Auto Rickshaw", "Metro Card Recharge", "Uber Ride"],
    "Shopping":         ["Amazon Purchase", "Flipkart Order", "Clothing Store", "Electronics", "Meesho Order", "Grocery Mart"],
    "Health & Medical": ["Doctor Consultation", "Pharmacy", "Lab Test", "Medicine", "Gym Membership", "Yoga Class"],
    "Entertainment":    ["Netflix Subscription", "Movie Ticket", "OTT Platform", "Gaming", "Concert Ticket", "Book Purchase"],
    "Education":        ["Online Course", "Udemy Purchase", "Books & Stationery", "Coaching Fee", "College Fee"],
    "Utilities":        ["Electricity Bill", "Mobile Recharge", "Internet Bill", "DTH Recharge", "Gas Bill"],
    "Travel":           ["Train Ticket", "Flight Booking", "Hotel Stay", "Holiday Package", "Taxi for Trip"],
    "Personal Care":    ["Salon Visit", "Skincare Products", "Haircut", "Spa", "Cosmetics"],
}

INCOME_SOURCES = ["Salary", "Freelance", "Part-time Job", "Scholarship", "Family Support"]


def generate_expense_data(
    n_records: int = 500,
    start_date: str = "2024-01-01",
    end_date: str = "2024-12-31",
    persons: list = None
) -> pd.DataFrame:
    """
    Generate synthetic expense records.

    Parameters
    ----------
    n_records  : Number of expense rows to generate
    start_date : Start date (YYYY-MM-DD)
    end_date   : End date   (YYYY-MM-DD)
    persons    : List of person names

    Returns
    -------
    pd.DataFrame : Synthetic expense DataFrame
    """
    if persons is None:
        persons = PERSONS

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end   = datetime.strptime(end_date,   "%Y-%m-%d")
    delta = (end - start).days

    # Sample categories using weighted probability
    cat_names   = list(CATEGORIES.keys())
    cat_weights = [CATEGORIES[c]["weight"] for c in cat_names]

    records = []
    for i in range(n_records):
        person   = random.choice(persons)
        category = random.choices(cat_names, weights=cat_weights, k=1)[0]
        cfg      = CATEGORIES[category]

        # Amount with slight seasonal variation
        base_amount = round(random.uniform(cfg["min"], cfg["max"]), 2)

        # Date with slight weekend/holiday clustering
        date = start + timedelta(days=random.randint(0, delta))

        # Payment method bias per category
        if category in ["Rent & Housing", "Utilities"]:
            payment = random.choices(
                ["Net Banking", "UPI", "Cash"], weights=[0.5, 0.3, 0.2]
            )[0]
        elif category in ["Shopping"]:
            payment = random.choices(
                ["Credit Card", "Debit Card", "UPI"], weights=[0.4, 0.3, 0.3]
            )[0]
        else:
            payment = random.choice(PAYMENT_METHODS)

        description = random.choice(DESCRIPTION_MAP[category])

        # Add notes (sometimes empty – realistic!)
        note = random.choices(
            [f"Reference #{random.randint(1000,9999)}", ""],
            weights=[0.4, 0.6]
        )[0]

        records.append({
            "id":             i + 1,
            "date":           date.strftime("%Y-%m-%d"),
            "person":         person,
            "category":       category,
            "description":    description,
            "amount":         base_amount,
            "payment_method": payment,
            "note":           note,
        })

    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    return df


def generate_income_data(
    persons: list = None,
    start_date: str = "2024-01-01",
    end_date: str = "2024-12-31",
) -> pd.DataFrame:
    """
    Generate monthly income records per person.

    Returns
    -------
    pd.DataFrame : Income records with date, person, source, amount
    """
    if persons is None:
        persons = PERSONS

    income_map = {
        "Priya Sharma": 45000,
        "Arjun Mehta":  38000,
        "Sunita Patel": 55000,
        "Rohan Das":    32000,
        "Anita Joshi":  42000,
    }

    records = []
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end   = datetime.strptime(end_date,   "%Y-%m-%d")

    current = start.replace(day=1)
    while current <= end:
        for person in persons:
            base = income_map.get(person, 40000)
            # Small month-to-month variation ±5%
            amount = round(base * random.uniform(0.95, 1.10), 2)
            records.append({
                "date":   current.strftime("%Y-%m-%d"),
                "person": person,
                "source": random.choices(
                    INCOME_SOURCES, weights=[0.6, 0.15, 0.1, 0.1, 0.05]
                )[0],
                "income": amount,
            })
        # Next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)

    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    return df


def introduce_data_quality_issues(df: pd.DataFrame, pct: float = 0.05) -> pd.DataFrame:
    """
    Realistically insert missing values and outliers for data-cleaning practice.

    Parameters
    ----------
    df  : Clean expense DataFrame
    pct : Fraction of rows to corrupt

    Returns
    -------
    pd.DataFrame : DataFrame with intentional quality issues
    """
    df_dirty = df.copy()
    n = len(df_dirty)
    n_corrupt = int(n * pct)

    # Missing notes (already realistic), but also missing descriptions
    miss_idx = np.random.choice(n, n_corrupt, replace=False)
    df_dirty.loc[miss_idx, "description"] = np.nan

    # Outlier amounts (data entry errors)
    outlier_idx = np.random.choice(n, max(1, int(n * 0.01)), replace=False)
    df_dirty.loc[outlier_idx, "amount"] = df_dirty.loc[outlier_idx, "amount"] * random.uniform(8, 12)

    # Duplicate rows (5 duplicates)
    dup_idx = np.random.choice(n, 5, replace=False)
    df_dirty = pd.concat([df_dirty, df_dirty.iloc[dup_idx]], ignore_index=True)

    return df_dirty


def save_datasets(output_dir: str = "data") -> dict:
    """
    Generate and save all datasets as CSV files.

    Returns
    -------
    dict : File paths of saved CSVs
    """
    os.makedirs(output_dir, exist_ok=True)

    print("⏳ Generating synthetic expense data...")
    df_clean  = generate_expense_data(n_records=500)
    df_dirty  = introduce_data_quality_issues(df_clean.copy(), pct=0.06)
    df_income = generate_income_data()

    clean_path  = os.path.join(output_dir, "expenses_clean.csv")
    dirty_path  = os.path.join(output_dir, "expenses_raw.csv")
    income_path = os.path.join(output_dir, "income_data.csv")

    df_clean.to_csv(clean_path,   index=False)
    df_dirty.to_csv(dirty_path,   index=False)
    df_income.to_csv(income_path, index=False)

    print(f"✅ Clean expenses  → {clean_path}  ({len(df_clean)} rows)")
    print(f"✅ Raw expenses    → {dirty_path}  ({len(df_dirty)} rows)")
    print(f"✅ Income data     → {income_path} ({len(df_income)} rows)")

    return {
        "clean":  clean_path,
        "dirty":  dirty_path,
        "income": income_path,
    }


# ─── Run standalone ───────────────────────────────────
if __name__ == "__main__":
    paths = save_datasets(output_dir="data")
    print("\n📊 Sample Expense Records:")
    df = pd.read_csv(paths["clean"])
    print(df.head(10).to_string(index=False))
    print(f"\n📈 Shape: {df.shape}")
    print(f"📅 Date Range: {df['date'].min()} → {df['date'].max()}")
    print(f"💰 Total Spend: ₹{df['amount'].sum():,.2f}")
