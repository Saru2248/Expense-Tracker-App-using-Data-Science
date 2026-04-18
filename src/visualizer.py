"""
========================================================
  Expense Tracker App - Visualization Module
  Purpose: Generate all charts, plots, and the
           static report figure for the project.
========================================================
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")   # non-interactive backend (safe for all OS)
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os

# ─── Global Style ─────────────────────────────────────
PALETTE    = ["#7B2FBE", "#00C9A7", "#F7B731", "#FC5C65", "#45AAF2",
              "#FD9644", "#26DE81", "#2BCBBA", "#A55EEA", "#EB3B5A"]
DARK_BG    = "#0F0F1A"
CARD_BG    = "#1A1A2E"
ACCENT     = "#7B2FBE"
TEXT_COLOR = "#E8E8F0"

def _setup_dark_style():
    """Apply global dark matplotlib style."""
    plt.rcParams.update({
        "figure.facecolor":  DARK_BG,
        "axes.facecolor":    CARD_BG,
        "axes.edgecolor":    "#2A2A4A",
        "axes.labelcolor":   TEXT_COLOR,
        "xtick.color":       TEXT_COLOR,
        "ytick.color":       TEXT_COLOR,
        "text.color":        TEXT_COLOR,
        "grid.color":        "#2A2A4A",
        "grid.linestyle":    "--",
        "grid.alpha":        0.5,
        "font.family":       "DejaVu Sans",
        "axes.titlesize":    13,
        "axes.labelsize":    11,
        "xtick.labelsize":   9,
        "ytick.labelsize":   9,
        "legend.fontsize":   9,
        "legend.facecolor":  CARD_BG,
        "legend.edgecolor":  "#2A2A4A",
    })

_setup_dark_style()


def _save(fig: plt.Figure, output_dir: str, filename: str) -> str:
    """Save figure and return absolute path."""
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"💾 Saved → {path}")
    return path


# ─── 1. Category Pie Chart ────────────────────────────

def plot_category_pie(df: pd.DataFrame, output_dir: str = "outputs") -> str:
    """Pie chart showing spending share per category."""
    cat = df.groupby("category")["amount"].sum().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(9, 6), facecolor=DARK_BG)
    wedges, texts, autotexts = ax.pie(
        cat.values,
        labels=cat.index,
        colors=PALETTE[:len(cat)],
        autopct="%1.1f%%",
        startangle=140,
        wedgeprops=dict(linewidth=1.5, edgecolor=DARK_BG),
        pctdistance=0.82,
    )
    for t in texts:
        t.set(color=TEXT_COLOR, fontsize=8)
    for at in autotexts:
        at.set(color="white", fontsize=7, fontweight="bold")

    ax.set_facecolor(DARK_BG)
    ax.set_title("Category-wise Spending Distribution", color=TEXT_COLOR,
                 fontsize=14, fontweight="bold", pad=15)
    plt.tight_layout()
    return _save(fig, output_dir, "01_category_pie.png")


# ─── 2. Monthly Bar Chart ─────────────────────────────

def plot_monthly_bar(df: pd.DataFrame, output_dir: str = "outputs") -> str:
    """Bar chart of total monthly spending."""
    month_order = ["January","February","March","April","May","June",
                   "July","August","September","October","November","December"]

    monthly = df.groupby("month_name")["amount"].sum()
    monthly = monthly.reindex([m for m in month_order if m in monthly.index])

    fig, ax = plt.subplots(figsize=(12, 5), facecolor=DARK_BG)
    bars = ax.bar(monthly.index, monthly.values,
                  color=PALETTE[0], edgecolor=DARK_BG, linewidth=0.8, width=0.6)

    # Gradient color effect
    norm = plt.Normalize(monthly.values.min(), monthly.values.max())
    cmap = plt.colormaps["plasma"]
    for bar, val in zip(bars, monthly.values):
        bar.set_facecolor(cmap(norm(val)))

    # Value labels
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 200,
                f"₹{h/1000:.1f}K", ha="center", va="bottom",
                fontsize=8, color=TEXT_COLOR)

    ax.set_title("Monthly Expense Trend (2024)", color=TEXT_COLOR,
                 fontsize=14, fontweight="bold")
    ax.set_xlabel("Month", color=TEXT_COLOR)
    ax.set_ylabel("Total Spend (₹)", color=TEXT_COLOR)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1000:.0f}K"))
    ax.set_xticklabels(monthly.index, rotation=30, ha="right")
    ax.grid(axis="y")
    plt.tight_layout()
    return _save(fig, output_dir, "02_monthly_bar.png")


# ─── 3. Category Bar Chart (Horizontal) ──────────────

def plot_category_bar(df: pd.DataFrame, output_dir: str = "outputs") -> str:
    """Horizontal bar chart sorted by total spend."""
    cat = df.groupby("category")["amount"].sum().sort_values()

    fig, ax = plt.subplots(figsize=(10, 6), facecolor=DARK_BG)
    bars = ax.barh(cat.index, cat.values, color=PALETTE[:len(cat)],
                   edgecolor=DARK_BG, height=0.6)

    for bar, val in zip(bars, cat.values):
        ax.text(val + 100, bar.get_y() + bar.get_height() / 2,
                f"₹{val:,.0f}", va="center", fontsize=9, color=TEXT_COLOR)

    ax.set_title("Total Spending by Category", color=TEXT_COLOR,
                 fontsize=14, fontweight="bold")
    ax.set_xlabel("Total Amount (₹)", color=TEXT_COLOR)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1000:.0f}K"))
    ax.grid(axis="x")
    plt.tight_layout()
    return _save(fig, output_dir, "03_category_bar.png")


# ─── 4. Heatmap: Category × Month ────────────────────

def plot_heatmap(df: pd.DataFrame, output_dir: str = "outputs") -> str:
    """Seaborn heatmap of category vs month spending."""
    month_order = ["January","February","March","April","May","June",
                   "July","August","September","October","November","December"]

    pivot = df.pivot_table(
        index="category", columns="month_name",
        values="amount", aggfunc="sum", fill_value=0
    )
    pivot = pivot.reindex(columns=[m for m in month_order if m in pivot.columns])

    fig, ax = plt.subplots(figsize=(14, 6), facecolor=DARK_BG)
    sns.heatmap(
        pivot / 1000,          # show in thousands
        ax=ax,
        cmap="YlOrRd",
        annot=True,
        fmt=".1f",
        linewidths=0.5,
        linecolor=DARK_BG,
        cbar_kws={"label": "Spend (₹K)", "shrink": 0.8},
    )
    ax.set_title("Category × Month Spending Heatmap (₹K)", color=TEXT_COLOR,
                 fontsize=14, fontweight="bold")
    ax.set_xlabel("Month", color=TEXT_COLOR)
    ax.set_ylabel("Category", color=TEXT_COLOR)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right")
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    cbar = ax.collections[0].colorbar
    cbar.ax.yaxis.label.set_color(TEXT_COLOR)
    plt.tight_layout()
    return _save(fig, output_dir, "04_heatmap.png")


# ─── 5. Payment Method Donut ──────────────────────────

def plot_payment_donut(df: pd.DataFrame, output_dir: str = "outputs") -> str:
    """Donut chart for payment method preference."""
    pay = df.groupby("payment_method")["amount"].sum().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(8, 6), facecolor=DARK_BG)
    wedges, texts, autotexts = ax.pie(
        pay.values,
        labels=pay.index,
        colors=PALETTE[:len(pay)],
        autopct="%1.1f%%",
        startangle=90,
        wedgeprops=dict(width=0.5, linewidth=1.5, edgecolor=DARK_BG),
    )
    for t in texts:
        t.set(color=TEXT_COLOR, fontsize=9)
    for at in autotexts:
        at.set(color="white", fontsize=8, fontweight="bold")

    ax.set_title("Payment Method Distribution", color=TEXT_COLOR,
                 fontsize=14, fontweight="bold")
    plt.tight_layout()
    return _save(fig, output_dir, "05_payment_donut.png")


# ─── 6. Person Comparison Bar ─────────────────────────

def plot_person_comparison(df: pd.DataFrame, output_dir: str = "outputs") -> str:
    """Grouped bar comparing persons across top categories."""
    top_cats = df.groupby("category")["amount"].sum().nlargest(5).index.tolist()
    sub = df[df["category"].isin(top_cats)]
    pivot = sub.pivot_table(index="category", columns="person",
                            values="amount", aggfunc="sum", fill_value=0)

    fig, ax = plt.subplots(figsize=(12, 6), facecolor=DARK_BG)
    pivot.plot(kind="bar", ax=ax, color=PALETTE[:len(pivot.columns)],
               edgecolor=DARK_BG, width=0.7)
    ax.set_title("Person-wise Spending Across Top 5 Categories",
                 color=TEXT_COLOR, fontsize=14, fontweight="bold")
    ax.set_xlabel("Category", color=TEXT_COLOR)
    ax.set_ylabel("Total Amount (₹)", color=TEXT_COLOR)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1000:.0f}K"))
    ax.set_xticklabels(ax.get_xticklabels(), rotation=25, ha="right")
    ax.legend(title="Person", title_fontsize=9)
    ax.grid(axis="y")
    plt.tight_layout()
    return _save(fig, output_dir, "06_person_comparison.png")


# ─── 7. Spending Line Trend ───────────────────────────

def plot_spending_trend(df: pd.DataFrame, output_dir: str = "outputs") -> str:
    """Line chart of total daily spending (rolling avg)."""
    daily = df.groupby("date")["amount"].sum().reset_index()
    daily = daily.sort_values("date")
    daily["rolling_7"] = daily["amount"].rolling(7, min_periods=1).mean()

    fig, ax = plt.subplots(figsize=(13, 5), facecolor=DARK_BG)
    ax.fill_between(daily["date"], daily["amount"], alpha=0.2, color=PALETTE[0])
    ax.plot(daily["date"], daily["amount"], color=PALETTE[0], alpha=0.4,
            linewidth=0.8, label="Daily Spend")
    ax.plot(daily["date"], daily["rolling_7"], color=PALETTE[1],
            linewidth=2.2, label="7-Day Rolling Avg")

    ax.set_title("Daily Spending Trend with 7-Day Rolling Average",
                 color=TEXT_COLOR, fontsize=14, fontweight="bold")
    ax.set_xlabel("Date", color=TEXT_COLOR)
    ax.set_ylabel("Spend (₹)", color=TEXT_COLOR)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
    ax.legend()
    ax.grid()
    plt.tight_layout()
    return _save(fig, output_dir, "07_spending_trend.png")


# ─── 8. Overspending Detection ────────────────────────

def plot_overspending(df: pd.DataFrame, budget: float = 30000,
                      output_dir: str = "outputs") -> str:
    """Bar chart flagging over-budget months in red."""
    month_order = ["Jan","Feb","Mar","Apr","May","Jun",
                   "Jul","Aug","Sep","Oct","Nov","Dec"]
    month_map   = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                   7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}

    monthly = df.groupby("month_num")["amount"].sum().reset_index()
    monthly["month_short"] = monthly["month_num"].map(month_map)
    monthly = monthly.sort_values("month_num")
    colors = ["#FC5C65" if v > budget else "#26DE81" for v in monthly["amount"]]

    fig, ax = plt.subplots(figsize=(12, 5), facecolor=DARK_BG)
    bars = ax.bar(monthly["month_short"], monthly["amount"], color=colors,
                  edgecolor=DARK_BG, linewidth=0.8, width=0.65)

    ax.axhline(y=budget, color="#F7B731", linewidth=2, linestyle="--",
               label=f"Budget (₹{budget:,.0f})")

    for bar, val in zip(bars, monthly["amount"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 300,
                f"₹{val/1000:.1f}K", ha="center", va="bottom",
                fontsize=8, color=TEXT_COLOR)

    ax.set_title("Monthly Spending vs Budget (🔴 = Over Budget  🟢 = Under Budget)",
                 color=TEXT_COLOR, fontsize=13, fontweight="bold")
    ax.set_ylabel("Spend (₹)", color=TEXT_COLOR)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1000:.0f}K"))
    ax.legend()
    ax.grid(axis="y")
    plt.tight_layout()
    return _save(fig, output_dir, "08_overspending.png")


# ─── 9. Savings Rate Line Chart ───────────────────────

def plot_savings_rate(savings_df: pd.DataFrame, output_dir: str = "outputs") -> str:
    """Line chart showing monthly savings rate %."""
    month_map = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                 7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
    savings_df["month_short"] = savings_df["month_num"].map(month_map)

    fig, ax = plt.subplots(figsize=(12, 5), facecolor=DARK_BG)
    ax.fill_between(savings_df["month_short"], savings_df["savings_rate"],
                    alpha=0.25, color=PALETTE[1])
    ax.plot(savings_df["month_short"], savings_df["savings_rate"],
            color=PALETTE[1], linewidth=2.5, marker="o", markersize=7, label="Savings Rate %")
    ax.axhline(y=20, color="#F7B731", linewidth=1.5, linestyle="--",
               label="Target 20% Savings Rate")

    for i, row in savings_df.iterrows():
        ax.text(i, row["savings_rate"] + 0.5, f"{row['savings_rate']:.1f}%",
                ha="center", fontsize=8, color=TEXT_COLOR)

    ax.set_title("Monthly Savings Rate (%)", color=TEXT_COLOR,
                 fontsize=14, fontweight="bold")
    ax.set_ylabel("Savings Rate (%)", color=TEXT_COLOR)
    ax.set_xlabel("Month", color=TEXT_COLOR)
    ax.legend()
    ax.grid()
    plt.tight_layout()
    return _save(fig, output_dir, "09_savings_rate.png")


# ─── 10. Amount Distribution ──────────────────────────

def plot_amount_distribution(df: pd.DataFrame, output_dir: str = "outputs") -> str:
    """Histogram + KDE of expense amounts."""
    fig, ax = plt.subplots(figsize=(10, 5), facecolor=DARK_BG)
    sns.histplot(df["amount"], bins=40, kde=True, ax=ax,
                 color=PALETTE[0], edgecolor=DARK_BG, line_kws={"linewidth": 2})
    ax.set_title("Distribution of Expense Amounts", color=TEXT_COLOR,
                 fontsize=14, fontweight="bold")
    ax.set_xlabel("Amount (₹)", color=TEXT_COLOR)
    ax.set_ylabel("Frequency", color=TEXT_COLOR)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
    ax.grid(axis="y")
    plt.tight_layout()
    return _save(fig, output_dir, "10_amount_distribution.png")


# ─── 11. Dashboard Grid (Summary Figure) ─────────────

def plot_dashboard_summary(df: pd.DataFrame, summary: dict,
                            output_dir: str = "outputs") -> str:
    """
    4-panel summary dashboard (one PNG proof image).
    Panel layout:
      [Pie Chart]  |  [Monthly Bar]
      [Top 5 Cat]  |  [Trend Line]
    """
    month_order = ["Jan","Feb","Mar","Apr","May","Jun",
                   "Jul","Aug","Sep","Oct","Nov","Dec"]
    month_map   = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                   7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}

    fig = plt.figure(figsize=(18, 12), facecolor=DARK_BG)
    fig.suptitle("📊 Expense Tracker App – Annual Dashboard (2024)",
                 color=TEXT_COLOR, fontsize=18, fontweight="bold", y=0.98)

    # ── Panel 1: Pie ──
    ax1 = fig.add_subplot(2, 2, 1)
    cat = df.groupby("category")["amount"].sum().sort_values(ascending=False)
    wedges, _, autotexts = ax1.pie(
        cat.values, labels=cat.index, colors=PALETTE[:len(cat)],
        autopct="%1.0f%%", startangle=140,
        wedgeprops=dict(linewidth=1, edgecolor=DARK_BG), pctdistance=0.82
    )
    for at in autotexts:
        at.set(color="white", fontsize=7)
    ax1.set_title("Spending by Category", color=TEXT_COLOR, fontsize=12, fontweight="bold")
    ax1.set_facecolor(DARK_BG)

    # ── Panel 2: Monthly Bar ──
    ax2 = fig.add_subplot(2, 2, 2)
    monthly = df.groupby("month_num")["amount"].sum()
    months = [month_map[m] for m in sorted(monthly.index)]
    vals   = [monthly[m] for m in sorted(monthly.index)]
    colors_ = plt.colormaps["plasma"](np.linspace(0.2, 0.9, len(months)))
    ax2.bar(months, vals, color=colors_, edgecolor=DARK_BG, width=0.65)
    ax2.set_title("Monthly Spending (₹)", color=TEXT_COLOR, fontsize=12, fontweight="bold")
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1000:.0f}K"))
    ax2.tick_params(axis="x", rotation=30)
    ax2.grid(axis="y")

    # ── Panel 3: Top 5 Categories ──
    ax3 = fig.add_subplot(2, 2, 3)
    top5 = cat.head(5)
    bars = ax3.barh(top5.index, top5.values,
                    color=PALETTE[:5], edgecolor=DARK_BG, height=0.6)
    for b, v in zip(bars, top5.values):
        ax3.text(v + 50, b.get_y() + b.get_height()/2,
                 f"₹{v:,.0f}", va="center", fontsize=9, color=TEXT_COLOR)
    ax3.set_title("Top 5 Categories", color=TEXT_COLOR, fontsize=12, fontweight="bold")
    ax3.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1000:.0f}K"))
    ax3.grid(axis="x")

    # ── Panel 4: Trend Line ──
    ax4 = fig.add_subplot(2, 2, 4)
    daily = df.groupby("date")["amount"].sum().reset_index().sort_values("date")
    daily["rolling_7"] = daily["amount"].rolling(7, min_periods=1).mean()
    ax4.fill_between(daily["date"], daily["amount"], alpha=0.15, color=PALETTE[0])
    ax4.plot(daily["date"], daily["rolling_7"], color=PALETTE[1],
             linewidth=2.2, label="7-Day Avg")
    ax4.set_title("Daily Spend Trend", color=TEXT_COLOR, fontsize=12, fontweight="bold")
    ax4.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
    ax4.legend()
    ax4.grid()

    for ax in [ax2, ax3, ax4]:
        ax.set_facecolor(CARD_BG)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    return _save(fig, output_dir, "00_dashboard_summary.png")


# ─── Master Generator ─────────────────────────────────

def generate_all_charts(
    df: pd.DataFrame,
    summary: dict,
    savings_df: pd.DataFrame = None,
    output_dir: str = "outputs",
    budget: float = 30000.0,
) -> list:
    """
    Generate all charts and return list of saved paths.

    Parameters
    ----------
    df          : Cleaned expense DataFrame
    summary     : KPI dict from basic_summary()
    savings_df  : Optional savings analysis DataFrame
    output_dir  : Folder to save PNGs
    budget      : Monthly budget for overspend chart
    """
    print("\n🎨 Generating all charts …")
    paths = []
    paths.append(plot_dashboard_summary(df, summary, output_dir))
    paths.append(plot_category_pie(df, output_dir))
    paths.append(plot_monthly_bar(df, output_dir))
    paths.append(plot_category_bar(df, output_dir))
    paths.append(plot_heatmap(df, output_dir))
    paths.append(plot_payment_donut(df, output_dir))
    paths.append(plot_person_comparison(df, output_dir))
    paths.append(plot_spending_trend(df, output_dir))
    paths.append(plot_overspending(df, budget, output_dir))
    paths.append(plot_amount_distribution(df, output_dir))
    if savings_df is not None:
        paths.append(plot_savings_rate(savings_df, output_dir))

    print(f"\n✅ {len(paths)} charts saved to '{output_dir}/'")
    return paths


# ─── Run standalone ───────────────────────────────────
if __name__ == "__main__":
    from src.analyzer import basic_summary, savings_analysis

    df  = pd.read_csv("data/expenses_cleaned.csv")
    df["date"] = pd.to_datetime(df["date"])
    inc = pd.read_csv("data/income_data.csv")

    summary     = basic_summary(df)
    savings_df  = savings_analysis(df, inc)
    generate_all_charts(df, summary, savings_df, output_dir="outputs", budget=30000)
