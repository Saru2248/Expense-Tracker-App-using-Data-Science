"""
========================================================
  Expense Tracker App – Streamlit Interactive Dashboard
  Run : streamlit run dashboard.py
========================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ─── Page Config ──────────────────────────────────────
st.set_page_config(
    page_title = "💸 Expense Tracker App",
    page_icon  = "💸",
    layout     = "wide",
    initial_sidebar_state = "expanded",
)

# ─── CSS Styling ──────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp { background: linear-gradient(135deg, #0F0F1A 0%, #1A1A2E 50%, #16213E 100%); }

    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, rgba(123,47,190,0.15), rgba(0,201,167,0.10));
        border: 1px solid rgba(123,47,190,0.3);
        border-radius: 16px;
        padding: 20px 24px;
        text-align: center;
        backdrop-filter: blur(10px);
        transition: transform 0.2s, box-shadow 0.2s;
        margin-bottom: 8px;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 32px rgba(123,47,190,0.3);
    }
    .kpi-title  { color: #A0A0C0; font-size: 0.80rem; font-weight: 500; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 6px; }
    .kpi-value  { color: #FFFFFF; font-size: 1.65rem; font-weight: 700; line-height: 1.2; }
    .kpi-sub    { color: #7B2FBE; font-size: 0.78rem; margin-top: 4px; }

    /* Section headers */
    .section-header {
        font-size: 1.1rem; font-weight: 600; color: #C9A8FF;
        border-left: 3px solid #7B2FBE;
        padding-left: 10px; margin: 24px 0 12px 0;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F0F1A, #1A1A2E) !important;
        border-right: 1px solid rgba(123,47,190,0.3);
    }

    /* Streamlit metric tweaks */
    [data-testid="metric-container"] { background: transparent !important; }

    /* Insight card */
    .insight-card {
        background: rgba(123,47,190,0.08);
        border: 1px solid rgba(123,47,190,0.2);
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 8px;
        color: #E0E0F0;
        font-size: 0.9rem;
    }

    /* Entry form card */
    .entry-card {
        background: linear-gradient(135deg, rgba(0,201,167,0.08), rgba(123,47,190,0.05));
        border: 1px solid rgba(0,201,167,0.25);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 16px;
    }

    /* Success toast */
    .success-toast {
        background: linear-gradient(135deg, rgba(38,222,129,0.15), rgba(0,201,167,0.10));
        border: 1px solid rgba(38,222,129,0.4);
        border-radius: 12px;
        padding: 14px 20px;
        color: #26DE81;
        font-weight: 600;
        font-size: 0.95rem;
        margin: 12px 0;
    }

    /* Recent log table */
    .recent-row {
        background: rgba(123,47,190,0.06);
        border: 1px solid rgba(123,47,190,0.12);
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 6px;
        color: #D0D0E8;
        font-size: 0.85rem;
        display: flex;
        justify-content: space-between;
    }
</style>
""", unsafe_allow_html=True)

PALETTE = ["#7B2FBE","#00C9A7","#F7B731","#FC5C65","#45AAF2",
           "#FD9644","#26DE81","#2BCBBA","#A55EEA","#EB3B5A"]

CATEGORIES = [
    "Food & Dining", "Rent & Housing", "Transportation", "Shopping",
    "Health & Medical", "Entertainment", "Education", "Utilities",
    "Travel", "Personal Care", "Other",
]
PAYMENT_METHODS = ["UPI", "Cash", "Credit Card", "Debit Card", "Net Banking", "Wallet"]
PERSONS_DEFAULT = ["Priya Sharma", "Arjun Mehta", "Sunita Patel", "Rohan Das", "Anita Joshi"]

CLEANED_CSV = "data/expenses_cleaned.csv"
INCOME_CSV  = "data/income_data.csv"
MANUAL_CSV  = "data/manual_expenses.csv"   # separate log for manually entered rows


# ─── Data Loading ─────────────────────────────────────
@st.cache_data
def load_base_data():
    """Load generated synthetic data (cached)."""
    if not os.path.exists(CLEANED_CSV):
        from src.data_generator import save_datasets
        from src.data_cleaner   import clean_expense_data
        paths = save_datasets(output_dir="data")
        clean_expense_data(raw_path=paths["dirty"], output_dir="data", save=True)

    df     = pd.read_csv(CLEANED_CSV)
    df_inc = pd.read_csv(INCOME_CSV)
    df["date"]     = pd.to_datetime(df["date"])
    df_inc["date"] = pd.to_datetime(df_inc["date"])
    return df, df_inc


def load_manual_entries() -> pd.DataFrame:
    """Load manually entered expenses (not cached — always fresh)."""
    if os.path.exists(MANUAL_CSV):
        df = pd.read_csv(MANUAL_CSV)
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
            return df
    return pd.DataFrame()


def save_manual_entry(row: dict) -> None:
    """Append a new expense row to the manual CSV log."""
    os.makedirs("data", exist_ok=True)
    new_row = pd.DataFrame([row])
    if os.path.exists(MANUAL_CSV):
        existing = pd.read_csv(MANUAL_CSV)
        updated  = pd.concat([existing, new_row], ignore_index=True)
    else:
        updated = new_row
    updated.to_csv(MANUAL_CSV, index=False)


def build_combined_df(df_base: pd.DataFrame, df_manual: pd.DataFrame) -> pd.DataFrame:
    """Merge synthetic + manual entries into one working DataFrame."""
    if df_manual.empty:
        return df_base.copy()

    # Ensure manual entries have all required derived columns
    def _enrich(df):
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])
        df["month_name"]  = df["date"].dt.strftime("%B")
        df["month_num"]   = df["date"].dt.month
        df["year"]        = df["date"].dt.year
        df["quarter"]     = df["date"].dt.quarter.map({1:"Q1",2:"Q2",3:"Q3",4:"Q4"})
        df["day_of_week"] = df["date"].dt.day_name()
        df["is_weekend"]  = df["date"].dt.dayofweek >= 5
        bins   = [0, 500, 2000, 5000, float("inf")]
        labels = ["Low (<₹500)", "Medium (₹500–2K)", "High (₹2K–5K)", "Very High (>₹5K)"]
        df["amount_bucket"] = pd.cut(df["amount"], bins=bins, labels=labels)
        return df

    df_manual = _enrich(df_manual)
    combined  = pd.concat([df_base, df_manual], ignore_index=True)
    combined  = combined.sort_values("date").reset_index(drop=True)
    return combined


# ─── Load data ────────────────────────────────────────
df_base, df_income = load_base_data()
df_manual           = load_manual_entries()
df                  = build_combined_df(df_base, df_manual)

# ─── Sidebar Filters ──────────────────────────────────
with st.sidebar:
    st.markdown("## 💸 Expense Tracker")
    st.markdown("---")

    all_persons = ["All Persons"] + sorted(df["person"].unique().tolist())
    sel_person  = st.selectbox("👤 Select Person", all_persons)

    all_months = ["All Months"] + [
        "January","February","March","April","May","June",
        "July","August","September","October","November","December"
    ]
    sel_month = st.selectbox("📅 Select Month", all_months)

    all_cats = ["All Categories"] + sorted(df["category"].unique().tolist())
    sel_cat  = st.multiselect("🏷️ Categories", all_cats, default=["All Categories"])

    budget = st.slider("💰 Monthly Budget (₹)", 10000, 100000, 30000, step=1000,
                       format="₹%d")

    st.markdown("---")
    manual_count = len(df_manual) if not df_manual.empty else 0
    st.markdown(f"📝 **Manual entries:** {manual_count}")
    st.markdown(f"📦 **Synthetic rows:** {len(df_base)}")
    st.markdown(f"📊 **Total records:** {len(df)}")

    if manual_count > 0 and st.button("🗑️ Clear Manual Entries", type="secondary"):
        if os.path.exists(MANUAL_CSV):
            os.remove(MANUAL_CSV)
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.markdown("**Built with ❤️ Python & Streamlit**")
    st.markdown("*Data Science Portfolio Project*")


# ─── Apply Filters ────────────────────────────────────
filtered = df.copy()
if sel_person != "All Persons":
    filtered = filtered[filtered["person"] == sel_person]
if sel_month != "All Months":
    filtered = filtered[filtered["month_name"] == sel_month]
if "All Categories" not in sel_cat and sel_cat:
    filtered = filtered[filtered["category"].isin(sel_cat)]


# ─── Page Header ──────────────────────────────────────
st.markdown("""
<h1 style="text-align:center; color:#FFFFFF; font-size:2rem; font-weight:700; margin-bottom:4px;">
  💸 Expense Tracker App
</h1>
<p style="text-align:center; color:#A0A0C0; font-size:0.95rem; margin-bottom:8px;">
  Data Science Project · Synthetic + Manual Data · 2024 Annual Analysis
</p>
""", unsafe_allow_html=True)

# ─── Tab Navigation ───────────────────────────────────
tab_dashboard, tab_add, tab_log = st.tabs([
    "📊  Dashboard & Analytics",
    "➕  Add Expense",
    "📋  Transaction Log",
])


# ══════════════════════════════════════════════════════
#   TAB 1 — DASHBOARD
# ══════════════════════════════════════════════════════
with tab_dashboard:

    # ── KPI Cards ─────────────────────────────────────
    total_spend = filtered["amount"].sum()
    avg_daily   = filtered.groupby("date")["amount"].sum().mean() if not filtered.empty else 0
    top_cat     = filtered.groupby("category")["amount"].sum().idxmax() if not filtered.empty else "N/A"
    num_txn     = len(filtered)
    avg_txn     = filtered["amount"].mean() if not filtered.empty else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    for col, title, val, sub in [
        (c1, "Total Spend",     f"₹{total_spend:,.0f}", "All time"),
        (c2, "Avg Daily Spend", f"₹{avg_daily:,.0f}",   "Per day"),
        (c3, "Transactions",    f"{num_txn:,}",          "Records"),
        (c4, "Avg Transaction", f"₹{avg_txn:,.0f}",     "Mean value"),
        (c5, "Top Category",    top_cat,                  "Highest spend"),
    ]:
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">{title}</div>
                <div class="kpi-value">{val}</div>
                <div class="kpi-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    if filtered.empty:
        st.warning("No records match the current filters. Try adjusting the sidebar.")
    else:
        month_order = ["January","February","March","April","May","June",
                       "July","August","September","October","November","December"]

        # ── Row 1: Pie + Monthly Bar ───────────────────
        col_l, col_r = st.columns([1, 1.4])

        with col_l:
            st.markdown('<div class="section-header">📊 Spending by Category</div>', unsafe_allow_html=True)
            cat_data = filtered.groupby("category")["amount"].sum().reset_index()
            fig_pie  = px.pie(cat_data, names="category", values="amount",
                              color_discrete_sequence=PALETTE, hole=0.38, template="plotly_dark")
            fig_pie.update_traces(textposition="inside", textinfo="percent+label",
                                  marker=dict(line=dict(color="#0F0F1A", width=1.5)))
            fig_pie.update_layout(paper_bgcolor="#1A1A2E", plot_bgcolor="#1A1A2E",
                                  margin=dict(t=10,b=10,l=10,r=10), showlegend=False, height=340)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_r:
            st.markdown('<div class="section-header">📅 Monthly Spending Trend</div>', unsafe_allow_html=True)
            monthly = filtered.groupby("month_name")["amount"].sum().reindex(
                [m for m in month_order if m in filtered["month_name"].unique()]
            ).reset_index()
            monthly.columns = ["month_name", "amount"]
            fig_bar = px.bar(monthly, x="month_name", y="amount",
                             color="amount", color_continuous_scale="Plasma",
                             template="plotly_dark",
                             text=monthly["amount"].apply(lambda x: f"₹{x/1000:.1f}K"))
            fig_bar.update_traces(textposition="outside")
            fig_bar.add_hline(y=budget, line_dash="dash", line_color="#F7B731",
                              annotation_text=f"Budget ₹{budget/1000:.0f}K")
            fig_bar.update_layout(paper_bgcolor="#1A1A2E", plot_bgcolor="#1A1A2E",
                                  margin=dict(t=10,b=30,l=10,r=10),
                                  xaxis_title="", yaxis_title="Amount (₹)",
                                  coloraxis_showscale=False, height=340,
                                  yaxis=dict(tickformat="₹,.0f"))
            st.plotly_chart(fig_bar, use_container_width=True)

        # ── Row 2: Trend Line + Payment Donut ─────────
        col_l2, col_r2 = st.columns([1.6, 1])

        with col_l2:
            st.markdown('<div class="section-header">📈 Daily Spending (7-Day Rolling Avg)</div>', unsafe_allow_html=True)
            daily = filtered.groupby("date")["amount"].sum().reset_index().sort_values("date")
            daily["rolling_7"] = daily["amount"].rolling(7, min_periods=1).mean()
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(x=daily["date"], y=daily["amount"],
                fill="tozeroy", name="Daily",
                line=dict(color=PALETTE[0], width=0.8), fillcolor="rgba(123,47,190,0.15)"))
            fig_line.add_trace(go.Scatter(x=daily["date"], y=daily["rolling_7"],
                name="7-Day Avg", line=dict(color=PALETTE[1], width=2.5)))
            fig_line.update_layout(paper_bgcolor="#1A1A2E", plot_bgcolor="#1A1A2E",
                                   margin=dict(t=10,b=10,l=10,r=10), height=310,
                                   legend=dict(bgcolor="#1A1A2E", bordercolor="#2A2A4A"),
                                   yaxis=dict(tickformat="₹,.0f"),
                                   xaxis_title="", yaxis_title="Amount (₹)")
            st.plotly_chart(fig_line, use_container_width=True)

        with col_r2:
            st.markdown('<div class="section-header">💳 Payment Methods</div>', unsafe_allow_html=True)
            pay = filtered.groupby("payment_method")["amount"].sum().reset_index()
            fig_donut = px.pie(pay, names="payment_method", values="amount",
                               color_discrete_sequence=PALETTE, hole=0.5, template="plotly_dark")
            fig_donut.update_traces(textposition="inside", textinfo="percent",
                                    marker=dict(line=dict(color="#0F0F1A", width=1.5)))
            fig_donut.update_layout(paper_bgcolor="#1A1A2E", plot_bgcolor="#1A1A2E",
                                    margin=dict(t=10,b=10,l=10,r=10), height=310, showlegend=True,
                                    legend=dict(bgcolor="#1A1A2E", bordercolor="#2A2A4A", font=dict(size=10)))
            st.plotly_chart(fig_donut, use_container_width=True)

        # ── Row 3: Heatmap ────────────────────────────
        if "month_name" in filtered.columns and filtered["month_name"].nunique() > 1:
            st.markdown('<div class="section-header">🗓️ Category × Month Heatmap (₹K)</div>', unsafe_allow_html=True)
            pivot      = filtered.pivot_table(index="category", columns="month_name",
                                              values="amount", aggfunc="sum", fill_value=0)
            month_cols = [m for m in month_order if m in pivot.columns]
            pivot      = pivot.reindex(columns=month_cols)
            fig_heat   = px.imshow(pivot / 1000, text_auto=".1f", aspect="auto",
                                   color_continuous_scale="YlOrRd", template="plotly_dark")
            fig_heat.update_layout(paper_bgcolor="#1A1A2E", plot_bgcolor="#1A1A2E",
                                   margin=dict(t=10,b=10,l=10,r=10), height=320,
                                   xaxis_title="", yaxis_title="",
                                   coloraxis_colorbar=dict(title="₹K", tickformat=".0f"))
            st.plotly_chart(fig_heat, use_container_width=True)

        # ── Row 4: Person + Overspending ──────────────
        col_l3, col_r3 = st.columns(2)

        with col_l3:
            st.markdown('<div class="section-header">👤 Person-wise Spending</div>', unsafe_allow_html=True)
            person_data = filtered.groupby("person")["amount"].sum().sort_values().reset_index()
            fig_person  = px.bar(person_data, x="amount", y="person", orientation="h",
                                 color="amount", color_continuous_scale="Purples",
                                 template="plotly_dark",
                                 text=person_data["amount"].apply(lambda x: f"₹{x:,.0f}"))
            fig_person.update_traces(textposition="outside")
            fig_person.update_layout(paper_bgcolor="#1A1A2E", plot_bgcolor="#1A1A2E",
                                     margin=dict(t=10,b=10,l=10,r=10), height=320,
                                     coloraxis_showscale=False,
                                     xaxis_title="Total Spend (₹)", yaxis_title="")
            st.plotly_chart(fig_person, use_container_width=True)

        with col_r3:
            st.markdown('<div class="section-header">⚠️ Overspending Detection</div>', unsafe_allow_html=True)
            overspend = filtered.groupby("month_name")["amount"].sum().reindex(
                [m for m in month_order if m in filtered["month_name"].unique()]
            ).reset_index()
            overspend.columns = ["month_name", "amount"]
            overspend["color"] = overspend["amount"].apply(
                lambda x: "#FC5C65" if x > budget else "#26DE81"
            )
            fig_over = go.Figure(go.Bar(
                x=overspend["month_name"], y=overspend["amount"],
                marker_color=overspend["color"],
                text=overspend["amount"].apply(lambda x: f"₹{x/1000:.1f}K"),
                textposition="outside",
            ))
            fig_over.add_hline(y=budget, line_dash="dash", line_color="#F7B731",
                               annotation_text=f"Budget: ₹{budget:,.0f}")
            fig_over.update_layout(paper_bgcolor="#1A1A2E", plot_bgcolor="#1A1A2E",
                                   template="plotly_dark",
                                   margin=dict(t=10,b=30,l=10,r=10), height=320,
                                   yaxis=dict(tickformat="₹,.0f"),
                                   xaxis_title="", yaxis_title="Spend (₹)")
            st.plotly_chart(fig_over, use_container_width=True)

        # ── Row 5: Savings Rate ────────────────────────
        st.markdown('<div class="section-header">💹 Monthly Savings Rate</div>', unsafe_allow_html=True)
        df_income_m = df_income.copy()
        df_income_m["month_num"] = df_income_m["date"].dt.month
        inc_monthly = df_income_m.groupby("month_num")["income"].sum().reset_index()

        df_m = filtered.copy()
        df_m["month_num"] = df_m["date"].dt.month
        exp_monthly = df_m.groupby("month_num")["amount"].sum().reset_index()
        exp_monthly.columns = ["month_num", "expense"]

        savings = pd.merge(inc_monthly, exp_monthly, on="month_num", how="left").fillna(0)
        savings["savings_rate"] = ((savings["income"] - savings["expense"]) / savings["income"] * 100).round(1)
        savings["month_short"]  = savings["month_num"].map(
            {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
             7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
        )
        fig_sav = go.Figure()
        fig_sav.add_trace(go.Scatter(
            x=savings["month_short"], y=savings["savings_rate"],
            fill="tozeroy", name="Savings Rate",
            line=dict(color=PALETTE[1], width=2.5),
            fillcolor="rgba(0,201,167,0.15)",
            mode="lines+markers+text",
            text=[f"{v:.1f}%" for v in savings["savings_rate"]],
            textposition="top center",
        ))
        fig_sav.add_hline(y=20, line_dash="dash", line_color="#F7B731",
                          annotation_text="Target 20%")
        fig_sav.update_layout(paper_bgcolor="#1A1A2E", plot_bgcolor="#1A1A2E",
                              template="plotly_dark",
                              margin=dict(t=10,b=10,l=10,r=10), height=280,
                              yaxis_title="Savings Rate (%)", xaxis_title="",
                              showlegend=False)
        st.plotly_chart(fig_sav, use_container_width=True)

        # ── Row 6: Top Transactions + Insights ────────
        col_l4, col_r4 = st.columns([1.4, 1])

        with col_l4:
            st.markdown('<div class="section-header">💸 Top 10 Expensive Transactions</div>', unsafe_allow_html=True)
            top10 = filtered.nlargest(10, "amount")[
                ["date","person","category","description","amount","payment_method"]
            ].copy()
            top10["date"]   = top10["date"].dt.strftime("%Y-%m-%d")
            top10["amount"] = top10["amount"].apply(lambda x: f"₹{x:,.2f}")
            st.dataframe(top10, use_container_width=True, hide_index=True)

        with col_r4:
            st.markdown('<div class="section-header">🔍 Auto-Generated Insights</div>', unsafe_allow_html=True)
            if not filtered.empty:
                monthly_vals = filtered.groupby("month_name")["amount"].sum()
                top_c   = filtered.groupby("category")["amount"].sum().idxmax()
                peak_m  = monthly_vals.idxmax()
                low_m   = monthly_vals.idxmin()
                top_pay = filtered["payment_method"].mode()[0]
                insights_list = [
                    f"💰 Total spend: ₹{filtered['amount'].sum():,.2f}",
                    f"🏆 Highest category: **{top_c}**",
                    f"📈 Peak month: **{peak_m}** (₹{monthly_vals.max():,.0f})",
                    f"📉 Lowest month: **{low_m}** (₹{monthly_vals.min():,.0f})",
                    f"💳 Top payment: **{top_pay}**",
                    f"📊 Transactions: **{len(filtered):,}**",
                ]
                over_months = (monthly_vals > budget).sum()
                if over_months:
                    insights_list.append(f"⚠️ Overspent in **{over_months} months** — cut discretionary spend!")
                else:
                    insights_list.append("✅ Budget maintained all months — great discipline!")
                for ins in insights_list:
                    st.markdown(f'<div class="insight-card">{ins}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#   TAB 2 — ADD EXPENSE (Manual Entry)
# ══════════════════════════════════════════════════════
with tab_add:

    st.markdown("""
    <h2 style="color:#C9A8FF; font-size:1.4rem; font-weight:600; margin-bottom:4px;">
        ➕ Add a New Expense
    </h2>
    <p style="color:#A0A0C0; font-size:0.9rem; margin-bottom:20px;">
        Fill in the form below. Your entry is saved immediately and reflected in all charts.
    </p>
    """, unsafe_allow_html=True)

    # ── Collect all known persons from data ───────────
    known_persons = sorted(df["person"].unique().tolist())
    # Allow typing a new name not in the list
    person_options = known_persons + ["+ Add new person..."]

    with st.form("expense_entry_form", clear_on_submit=True):
        st.markdown('<div class="entry-card">', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            entry_date = st.date_input(
                "📅 Date",
                value=date.today(),
                min_value=date(2020, 1, 1),
                max_value=date(2030, 12, 31),
                help="Date the expense occurred",
            )
            entry_category = st.selectbox(
                "🏷️ Category",
                CATEGORIES,
                help="Select the spending category",
            )
            entry_amount = st.number_input(
                "💰 Amount (₹)",
                min_value=1.0,
                max_value=500000.0,
                value=500.0,
                step=50.0,
                format="%.2f",
                help="Enter the expense amount in Indian Rupees",
            )

        with col2:
            person_choice = st.selectbox(
                "👤 Person",
                person_options,
                help="Who made this expense?",
            )
            # If user chose '+ Add new person...' show a text input
            if person_choice == "+ Add new person...":
                entry_person = st.text_input(
                    "Enter new person's name",
                    placeholder="e.g., Vikram Singh",
                ).strip()
            else:
                entry_person = person_choice

            entry_payment = st.selectbox(
                "💳 Payment Method",
                PAYMENT_METHODS,
                help="How was it paid?",
            )
            entry_description = st.text_input(
                "📝 Description",
                placeholder="e.g., Dinner at Pizza Hut",
                help="Brief description of the expense",
            )

        entry_note = st.text_area(
            "🗒️ Note (optional)",
            placeholder="Any additional notes — reference numbers, receipts, etc.",
            height=80,
        )

        st.markdown('</div>', unsafe_allow_html=True)

        col_submit, col_help = st.columns([1, 3])
        with col_submit:
            submitted = st.form_submit_button(
                "💾 Save Expense",
                type="primary",
                use_container_width=True,
            )
        with col_help:
            st.markdown(
                "<small style='color:#888;'>💡 The Dashboard tab will reflect your entry immediately after saving.</small>",
                unsafe_allow_html=True,
            )

    # ── Process submission ─────────────────────────────
    if submitted:
        # Validation
        errors = []
        if not entry_person or entry_person.strip() == "":
            errors.append("Person name cannot be empty.")
        if entry_amount <= 0:
            errors.append("Amount must be greater than ₹0.")
        if not entry_description.strip():
            entry_description = f"{entry_category} Expense"  # auto-fill if blank

        if errors:
            for err in errors:
                st.error(f"❌ {err}")
        else:
            # Build row
            new_entry = {
                "id":             f"M{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}",
                "date":           str(entry_date),
                "person":         entry_person.strip(),
                "category":       entry_category,
                "description":    entry_description.strip(),
                "amount":         round(float(entry_amount), 2),
                "payment_method": entry_payment,
                "note":           entry_note.strip() if entry_note.strip() else "N/A",
                "source":         "manual",
            }
            save_manual_entry(new_entry)
            st.cache_data.clear()   # clear cache so charts reload

            st.markdown(f"""
            <div class="success-toast">
                ✅ Expense saved! &nbsp;
                <strong>{entry_category}</strong> — ₹{entry_amount:,.2f} —
                {entry_person} — {entry_date.strftime("%d %b %Y")} — {entry_payment}
            </div>
            """, unsafe_allow_html=True)

            st.balloons()
            st.info("↑ Switch to the **Dashboard & Analytics** tab to see your updated charts.")

    # ── Recent Manual Entries Preview ─────────────────
    st.markdown('<div class="section-header">🕓 Recently Added Entries</div>', unsafe_allow_html=True)
    df_manual_now = load_manual_entries()
    if df_manual_now.empty:
        st.markdown(
            '<p style="color:#666; font-size:0.9rem;">No manual entries yet. Use the form above to add your first expense.</p>',
            unsafe_allow_html=True
        )
    else:
        recent = df_manual_now.sort_values("date", ascending=False).head(10)
        for _, row in recent.iterrows():
            dt  = pd.to_datetime(row["date"]).strftime("%d %b %Y")
            amt = f"₹{float(row['amount']):,.2f}"
            st.markdown(
                f'<div class="recent-row">'
                f'  <span>📅 {dt} &nbsp;|&nbsp; 🏷️ {row["category"]} &nbsp;|&nbsp; {row["description"]}</span>'
                f'  <span style="color:#00C9A7; font-weight:600;">{amt} &nbsp; ({row["payment_method"]})</span>'
                f'</div>',
                unsafe_allow_html=True
            )


# ══════════════════════════════════════════════════════
#   TAB 3 — TRANSACTION LOG (Full Table)
# ══════════════════════════════════════════════════════
with tab_log:
    st.markdown('<div class="section-header">📋 Full Transaction Log</div>', unsafe_allow_html=True)

    # Source indicator
    if not df_manual.empty:
        st.markdown(
            f'<p style="color:#A0A0C0; font-size:0.88rem;">'
            f'Showing <strong style="color:#00C9A7">{len(df)}</strong> records '
            f'({len(df_base)} synthetic + '
            f'<strong style="color:#F7B731">{len(df_manual)} manual</strong>). '
            f'Use sidebar to filter.</p>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<p style="color:#A0A0C0; font-size:0.88rem;">'
            f'Showing <strong>{len(filtered)}</strong> records (all synthetic). '
            f'Go to <strong>Add Expense</strong> tab to enter real data.</p>',
            unsafe_allow_html=True
        )

    # Display table
    display_cols = ["date","person","category","description","amount","payment_method","note"]
    log_df = filtered[[c for c in display_cols if c in filtered.columns]].copy()
    log_df["date"]   = log_df["date"].dt.strftime("%Y-%m-%d")
    log_df["amount"] = log_df["amount"].apply(lambda x: f"₹{x:,.2f}")
    log_df = log_df.sort_values("date", ascending=False).reset_index(drop=True)

    st.dataframe(log_df, use_container_width=True, height=500)

    # Download
    csv_export = filtered.copy()
    csv_export["date"] = csv_export["date"].dt.strftime("%Y-%m-%d")
    st.download_button(
        label     = "⬇️ Download Filtered Data as CSV",
        data      = csv_export.to_csv(index=False).encode("utf-8"),
        file_name = "expense_tracker_export.csv",
        mime      = "text/csv",
    )


# ─── Footer ───────────────────────────────────────────
st.markdown("---")
st.markdown("""
<p style="text-align:center; color:#555577; font-size:0.82rem;">
💸 Expense Tracker App · Data Science Portfolio Project · Built with Python, Pandas, Plotly & Streamlit
</p>
""", unsafe_allow_html=True)
