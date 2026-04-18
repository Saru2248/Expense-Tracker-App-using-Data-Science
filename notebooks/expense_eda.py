"""
Expense Tracker EDA Notebook Runner
Run this as a Python script to get the notebook output.
For Jupyter: rename to .ipynb format or use jupytext.
"""
# ============================================================
# EXPENSE TRACKER APP – FULL EDA NOTEBOOK
# ============================================================
# Cell 1: Imports and Setup
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

print("✅ Libraries imported successfully")
print(f"   Pandas  : {pd.__version__}")
print(f"   NumPy   : {np.__version__}")

# ----------------------------------------------------------
# Cell 2: Generate & Load Data
# ----------------------------------------------------------
import sys, os
sys.path.insert(0, "..")

from src.data_generator import save_datasets
from src.data_cleaner   import clean_expense_data

paths = save_datasets(output_dir="../data")
df    = clean_expense_data(raw_path=paths["dirty"], output_dir="../data", save=True)
inc   = pd.read_csv("../data/income_data.csv")
inc["date"] = pd.to_datetime(inc["date"])

print(f"\n✅ Data shape : {df.shape}")
print(df.dtypes)

# ----------------------------------------------------------
# Cell 3: Dataset Preview
# ----------------------------------------------------------
print("\n📋 First 10 rows:")
print(df.head(10).to_string(index=False))

print("\n📊 Descriptive Statistics:")
print(df.describe().to_string())

# ----------------------------------------------------------
# Cell 4: Category Analysis
# ----------------------------------------------------------
from src.analyzer import category_analysis, basic_summary
summary = basic_summary(df)
cat_df  = category_analysis(df)

# ----------------------------------------------------------
# Cell 5: Monthly Trend
# ----------------------------------------------------------
from src.analyzer import monthly_trend_analysis
monthly_df = monthly_trend_analysis(df)

# ----------------------------------------------------------
# Cell 6: All Visualizations
# ----------------------------------------------------------
from src.visualizer      import generate_all_charts
from src.analyzer        import savings_analysis
savings_df = savings_analysis(df, inc)

generate_all_charts(df, summary, savings_df, output_dir="../outputs", budget=30000)

print("\n✅ EDA Complete!")
