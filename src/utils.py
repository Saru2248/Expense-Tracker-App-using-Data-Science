"""
========================================================
  Expense Tracker App – Helper / Utility Functions
========================================================
"""

import os

def ensure_dirs(*dirs):
    """Create directories if they don't exist."""
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def inr(amount: float) -> str:
    """Format a float as Indian Rupee string."""
    return f"₹{amount:,.2f}"

def pct(val: float) -> str:
    """Format float as percentage string."""
    return f"{val:.1f}%"
