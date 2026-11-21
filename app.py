"""Rupee Do — a tiny Gen Z banking demo. Sample data only, no real payments."""

import math
import random

import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------------- page setup
st.set_page_config(page_title="Rupee Do", page_icon="₹", layout="wide")

GREEN, YELLOW, RED = "#12B76A", "#F79009", "#F04438"   # our 🟢🟡🔴 theme
PALETTE = [GREEN, YELLOW, RED, "#3B82F6", "#8B5CF6", "#14B8A6"]
BUDGET = 12000   # default monthly budget (₹)

# A little CSS to make the default Streamlit look nicer (and phone friendly)
st.markdown(
    """
    <style>
    .block-container {max-width: 920px; padding-top: 1.2rem;}
    .hero {background: linear-gradient(135deg, #0f172a, #134e4a 60%, #065f46);
           border-radius: 20px; padding: 20px 24px; color: #fff; margin-bottom: 18px;}
    .hero h1 {font-size: 1.9rem; margin: 0; color: #fff; letter-spacing: -.5px;}
    .hero p {margin: 4px 0 0; color: #d1fae5; font-size: .9rem;}
    .card {background: #fff; border: 1px solid #e5e7eb; border-radius: 16px;
           padding: 16px 18px; margin-bottom: 12px;}
    .pill {display: inline-block; padding: 3px 10px; border-radius: 999px;
           font-size: .8rem; font-weight: 600;}
    .g {background: #e7f8ef; color: #067647;}
    .y {background: #fff6e5; color: #b54708;}
    .r {background: #fee4e2; color: #b42318;}
    /* keep primary buttons in brand green, not Streamlit red */
    .stButton > button[kind="primary"] {background: #12B76A; border-color: #12B76A;}
    .stButton > button[kind="primary"]:hover {background: #0E9F5B; border-color: #0E9F5B;}
    /* small screens (phones) */
    @media (max-width: 640px) {
      .hero {padding: 16px 18px; border-radius: 16px;}
      .hero h1 {font-size: 1.45rem;}
      .hero p {font-size: .78rem;}
      .hero .logo {width: 42px; height: 42px; font-size: 22px;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def rupees(x):
    """Format a number as rupees, e.g. 1214.5 -> ₹1,214.50"""
    x = round(float(x), 2)
    return f"₹{x:,.0f}" if x.is_integer() else f"₹{x:,.2f}"


def bar(value, maximum, colour):
    """Draw a simple rounded progress bar."""
    pct = min(value / maximum, 1.0) * 100 if maximum else 0
    st.markdown(
        f"""<div style="background:#eef0f3;border-radius:999px;height:14px;
                    margin:6px 0 10px;overflow:hidden">
              <div style="width:{pct:.0f}%;height:100%;background:{colour};
                          border-radius:999px"></div>
            </div>""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------- sample data
# Dates are relative to today, so two transactions always show up as "today".
today = pd.Timestamp.today().normalize()
rows = [
    (0, "Zomato", "Food", 386), (0, "Uber", "Transport", 248),
    (1, "Starbucks", "Food", 341), (1, "BookMyShow", "Fun", 520),
    (2, "Myntra", "Shopping", 1499), (3, "Jio recharge", "Bills", 299),
    (4, "Swiggy", "Food", 457), (5, "Metro card", "Transport", 150),
    (6, "Nykaa", "Shopping", 689), (8, "Coursera", "Study", 999),
    (10, "Blinkit", "Food", 623), (12, "Spotify", "Bills", 119),
    (15, "Decathlon", "Shopping", 1249), (18, "Cafe Coffee Day", "Food", 287),
    (21, "Electricity bill", "Bills", 860),
]
txns = pd.DataFrame(rows, columns=["days_ago", "Merchant", "Category", "Amount"])
txns["Today"] = txns["days_ago"] == 0
txns["Date"] = (today - pd.to_timedelta(txns["days_ago"], "D")).dt.strftime("%d %b")
# Round each amount UP to the next ₹10; the gap is the spare change
txns["Round-up"] = [round(math.ceil(a / 10) * 10 - a, 2) for a in txns["Amount"]]

spent = txns["Amount"].sum()
today_spent = txns.loc[txns["Today"], "Amount"].sum()
monthly_roundups = txns["Round-up"].sum()
days_covered = int(txns["days_ago"].max()) + 1

# ---------------------------------------------------------------- demo memory
CARRY_OVER = 1180.0   # spare change already saved last month (head start for demos)

if "savings" not in st.session_state:
    st.session_state.savings = round(CARRY_OVER + monthly_roundups, 2)
if "pot" not in st.session_state:
    st.session_state.pot = 0.0
if "tip" not in st.session_state:
    st.session_state.tip = "Small amounts saved daily become large amounts saved yearly."

total_saved = st.session_state.savings + st.session_state.pot

# ---------------------------------------------------------------- sidebar nav
with st.sidebar:
    st.markdown("### ₹ Rupee Do")
    st.caption("Demo bank for Gen Z · sample data only")
    page = st.radio(
        "Navigate",
        ["🏠 Home", "🪙 Round-off savings", "🎯 Goal tracker", "🚦 Spending status",
         "🥧 Expense chart", "🛟 Emergency buffer", "😹 Money tips",
         "👨‍👩‍👧 Parent mode", "🚧 Coming soon"],
        label_visibility="collapsed",
    )
    st.divider()
    if st.button("🔄 Reset demo"):
        st.session_state.clear()
        st.rerun()
    st.caption("No real payments. Ever. 🙅")

# ---------------------------------------------------------------- header
st.markdown(
    """
    <div class="hero">
      <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap">
        <div class="logo" style="flex:0 0 auto;width:52px;height:52px;border-radius:16px;
                    background:#12B76A;display:flex;align-items:center;
                    justify-content:center;font-size:28px;font-weight:800;
                    color:#052e22">₹</div>
        <div style="flex:1;min-width:0">
          <h1>Rupee Do</h1>
          <p>Spare change, goals and green-yellow-red vibes. Demo only — no real payments.</p>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ================================================================ pages
if page == "🏠 Home":
    budget = st.session_state.get("budget", BUDGET)
    c1, c2 = st.columns(2)
    c1.metric("Spare change", rupees(st.session_state.savings))
    c2.metric("Savings pot", rupees(st.session_state.pot))
    c3, c4 = st.columns(2)
    c3.metric("Spent this month", rupees(spent), f"of {rupees(budget)} budget",
              delta_color="off")
    c4.metric("Buffer days", f"{total_saved / (spent / days_covered):.1f} days")

    ratio = spent / budget
    label, css = (("Safe 🟢", "g") if ratio <= 0.75 else
                  ("Close to the limit 🟡", "y") if ratio <= 1 else
                  ("Over the limit 🔴", "r"))
    st.markdown(f'<div class="card">Monthly budget status: '
                f'<span class="pill {css}">{label}</span></div>',
                unsafe_allow_html=True)
    st.caption("Use the sidebar to explore 👉 (on mobile, tap the » arrow top-left).")

elif page == "🪙 Round-off savings":
    st.subheader("🪙 Round-off savings")
    st.caption("Every spend is rounded up to the next ₹10. The difference is your spare change.")
    c1, c2, c3 = st.columns(3)
    c1.metric("This month's round-ups", rupees(monthly_roundups))
    c2.metric("Spare change balance", rupees(st.session_state.savings))
    c3.metric("Savings pot", rupees(st.session_state.pot))
    st.caption(f"Balance includes {rupees(CARRY_OVER)} carried over from last month.")

    st.dataframe(
        txns[["Date", "Merchant", "Category", "Amount", "Round-up"]],
        hide_index=True,
        height=340,
        column_config={
            "Amount": st.column_config.NumberColumn("Amount (₹)", format="₹%.0f"),
            "Round-up": st.column_config.NumberColumn("Round-up (₹)", format="₹%.2f"),
        },
    )

    just_moved = st.session_state.pop("just_moved", False)
    if just_moved:  # message for the run AFTER the transfer click
        st.success(f"🎉 Transferred {rupees(st.session_state.pop('moved', 0))} "
                   "to your savings pot!")
        st.balloons()

    if st.button(f"➡️ Transfer {rupees(st.session_state.savings)} to savings pot",
                 type="primary", disabled=st.session_state.savings < 1000):
        st.session_state.pot += st.session_state.savings
        st.session_state.moved = st.session_state.savings
        st.session_state.savings = 0.0
        st.session_state.just_moved = True
        st.rerun()
    if st.session_state.savings < 1000 and not just_moved:
        st.caption("Transfer unlocks when spare change crosses ₹1,000.")

elif page == "🎯 Goal tracker":
    st.subheader("🎯 Saving goal tracker")
    goal_name = st.text_input("Goal name", "A new phone 📱")
    goal_amount = st.number_input("Goal amount (₹)", min_value=500,
                                  max_value=200000, value=5000, step=500)
    progress = min(total_saved / goal_amount, 1.0)
    st.progress(progress, text=f"{rupees(total_saved)} of {rupees(goal_amount)} "
                               f"· {progress * 100:.0f}%")
    if total_saved >= goal_amount:
        st.success(f"Goal reached 🎉 — “{goal_name}” is officially funded (in demo money).")
        st.balloons()
    else:
        left = goal_amount - total_saved
        weeks = math.ceil(left / 500)
        st.info(f"{rupees(left)} to go for “{goal_name}”. "
                f"Save ₹500 a week and you'll get there in about {weeks} weeks.")

elif page == "🚦 Spending status":
    st.subheader("🚦 Spending status")
    budget = st.number_input("Monthly budget (₹)", min_value=2000, max_value=50000,
                             value=BUDGET, step=500, key="budget")
    ratio = spent / budget
    if ratio <= 0.75:
        label, colour, css = "Safe 🟢", GREEN, "g"
        note = "You're cruising. Keep it up."
    elif ratio <= 1.0:
        label, colour, css = "Close to the limit 🟡", YELLOW, "y"
        note = "Tread carefully — the limit is near."
    else:
        label, colour, css = "Over the limit 🔴", RED, "r"
        note = f"You've crossed the budget by {rupees(spent - budget)}."

    st.markdown(f"""<div class="card">
        <span class="pill {css}">{label}</span>
        <div style="background:#eef0f3;border-radius:999px;height:16px;margin-top:12px;
                    overflow:hidden">
          <div style="width:{min(ratio, 1) * 100:.0f}%;height:100%;background:{colour};
                      border-radius:999px"></div>
        </div>
        <p style="margin:10px 0 0;color:#475467;font-size:.9rem">
          {rupees(spent)} spent of a {rupees(budget)} budget ({ratio * 100:.0f}% used)
        </p></div>""", unsafe_allow_html=True)
    st.write(note)

elif page == "🥧 Expense chart":
    st.subheader("🥧 Where the money went")
    by_cat = (txns.groupby("Category", as_index=False)["Amount"].sum()
              .sort_values("Amount", ascending=False))
    kind = st.radio("Chart type", ["Pie", "Bar"], horizontal=True,
                    label_visibility="collapsed")
    if kind == "Pie":
        fig = px.pie(by_cat, names="Category", values="Amount", hole=0.45,
                     color_discrete_sequence=PALETTE)
    else:
        fig = px.bar(by_cat, x="Category", y="Amount", color="Category",
                     color_discrete_sequence=PALETTE, text_auto=".2s")
        fig.update_layout(showlegend=False)
    fig.update_layout(margin=dict(l=10, r=10, t=20, b=10), height=380)
    st.plotly_chart(fig)

    top = by_cat.iloc[0]
    st.caption(f"Biggest category: **{top['Category']}** at {rupees(top['Amount'])} "
               f"({top['Amount'] / spent * 100:.0f}% of all spending).")

elif page == "🛟 Emergency buffer":
    st.subheader("🛟 Emergency buffer")
    daily_avg = spent / days_covered
    days = total_saved / daily_avg if daily_avg else 0
    colour, label, css = ((GREEN, "Comfortable 🟢", "g") if days >= 7 else
                          (YELLOW, "Tight 🟡", "y") if days >= 3 else
                          (RED, "Risky 🔴", "r"))
    st.markdown(
        f'<div class="card"><span class="pill {css}">{label}</span>'
        f'<h2 style="margin:10px 0 0;color:{colour}">{days:.1f} days</h2>'
        '<p style="margin:0;color:#475467;font-size:.9rem">of expenses your savings can cover</p>'
        '</div>', unsafe_allow_html=True)
    bar(days, 30, colour)
    st.caption(f"Based on {rupees(total_saved)} saved and your average spend of "
               f"{rupees(daily_avg)}/day over the last {days_covered} days. "
               "Goal: 30 days of cover.")

elif page == "😹 Money tips":
    st.subheader("😹 Money tips, but funny")
    tips = [
        "Your bank balance called. It's not angry, just disappointed.",
        "Swiggy isn't a food app, it's a savings leak with great UI.",
        "Budget = telling your money where to go instead of wondering where it went.",
        "That ₹249 in-app purchase? Do it 40 times and it's a flight to Goa.",
        "Compound interest is the only friend that gets richer while you sleep. Don't ghost it.",
        "A free trial is a subscription with a countdown timer you will definitely forget.",
        "Retail therapy works. The bill is the side effect.",
        "Never spend money you don't have, to impress people who don't care.",
        "Round-up savings: ₹4 here and ₹6 there is literally how phones get bought.",
        "Your UPI PIN is not a personality. Please don't share it.",
        "Investing ₹500 today beats 'I'll start next month' for the 47th time.",
    ]
    if st.button("Show me a tip 💸", type="primary"):
        st.session_state.tip = random.choice(tips)
    st.markdown(f'<div class="card" style="font-size:1.05rem">'
                f'“{st.session_state.tip}”</div>', unsafe_allow_html=True)
    st.caption(f"Tap again — there are {len(tips)} of these.")

elif page == "👨‍👩‍👧 Parent mode":
    st.subheader("👨‍👩‍👧 Parent mode")
    parent_on = st.toggle("Parent mode is ON")
    if not parent_on:
        st.info("Parent mode is off. Toggle it on to set a daily spending limit.")
    else:
        limit = st.number_input("Daily spending limit (₹)", min_value=100,
                                max_value=5000, value=500, step=50)
        if today_spent > limit:
            colour, label, css = RED, "Daily limit crossed 🔴", "r"
        elif today_spent > 0.8 * limit:
            colour, label, css = YELLOW, "Close to today's limit 🟡", "y"
        else:
            colour, label, css = GREEN, "Within today's limit 🟢", "g"
        st.markdown(f'<div class="card"><span class="pill {css}">{label}</span></div>',
                    unsafe_allow_html=True)
        bar(today_spent, limit, colour)
        st.write(f"Spent today: **{rupees(today_spent)}** of a {rupees(limit)} limit.")
        if today_spent > limit:
            st.error("🚨 Daily limit crossed! A demo alert has been sent to your parent.")
        else:
            st.success("All good — you're inside today's limit.")
        st.caption("Demo alert only. No real parents were notified. 😌")

elif page == "🚧 Coming soon":
    st.subheader("🚧 Coming soon")
    items = [
        ("📈", "SIP investing", "Start a SIP from ₹500, right inside the app."),
        ("✈️", "Travel tickets", "Book trains, buses and flights in one place."),
        ("🎁", "Gift cards", "Send ₹100 gift cards to friends without leaving the group chat."),
        ("🔐", "Biometric login", "Face or fingerprint login — no more typing PINs."),
        ("🧊", "Auto freeze/unfreeze", "Instantly freeze your card when you smell a scam."),
        ("🔁", "Autopay", "Rent, recharge and subscriptions paid automatically."),
        ("📱", "Tap to pay", "Pay by tapping your phone at the counter."),
    ]
    cols = st.columns(2)
    for i, (icon, name, blurb) in enumerate(items):
        with cols[i % 2]:
            st.markdown(
                f"""<div class="card" style="min-height:132px">
                <div style="font-size:1.5rem">{icon}</div>
                <b>{name}</b><br>
                <span style="color:#667085;font-size:.85rem">{blurb}</span><br>
                <span class="pill y" style="margin-top:10px">🚧 Coming soon</span>
                </div>""",
                unsafe_allow_html=True,
            )
