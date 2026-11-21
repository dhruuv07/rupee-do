"""Rupee Do — one-page Gen Z banking demo. Sample data only, no real payments."""

import inspect
import math
import random

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------- 1. page setup
st.set_page_config(page_title="Rupee Do", page_icon="₹", layout="centered")

G, Y, R = "#12B76A", "#F79009", "#F04438"          # our 🟢🟡🔴 theme
GREY = "rgba(148,163,184,.5)"                      # for zero-spend days
CATEGORIES = ["Food", "Shopping", "Transport", "Bills", "Study", "Fun", "Other"]

# Detect dark mode so our custom cards match Streamlit's own theme
def _is_dark():
    try:
        kind = st.context.theme.type
        if kind:
            return kind == "dark"
        hints = " ".join(str(v) for k, v in (st.context.headers or {}).items()
                         if "color-scheme" in k.lower() or "theme" in k.lower())
        return "dark" in hints.lower()
    except Exception:
        return False

DARK = _is_dark()

# Colours for our custom HTML cards (they flip with the theme)
CARD = "rgba(255,255,255,.05)" if DARK else "#ffffff"
LINE = "rgba(255,255,255,.10)" if DARK else "#e7ebf1"
INK = "#e9eef6" if DARK else "#101828"
SOFT = "#93a0b3" if DARK else "#667085"
TINT = {"g": "rgba(18,183,106,.15)", "y": "rgba(247,144,9,.16)", "r": "rgba(240,68,56,.15)"}
TXT = {"g": "#34D399" if DARK else "#067647",
       "y": "#FBBF24" if DARK else "#B54708",
       "r": "#F87171" if DARK else "#B42318"}

st.markdown(f"""
<style>
  .block-container {{padding-top: 1.2rem; padding-bottom: 3rem; max-width: 780px;}}

  /* gradient hero banner, green → yellow */
  .rd-hero {{background: linear-gradient(135deg, #0E9F5B 0%, #34C463 45%, #F7C948 100%);
            border-radius: 22px; padding: 20px 22px; color: #06301f; margin-bottom: 16px;}}
  .rd-hero .row {{display: flex; align-items: center; gap: 12px; flex-wrap: nowrap;}}
  .rd-hero .coin {{flex: 0 0 auto; font-size: 2rem; line-height: 1;}}
  .rd-hero h1 {{margin: 0; font-size: 2rem; letter-spacing: -.8px; color: #06301f;
               white-space: nowrap; line-height: 1.1;}}
  .rd-hero p {{margin: 6px 0 0; font-size: .9rem; font-weight: 500; opacity: .85;}}
  @media (max-width: 480px) {{
    .rd-hero {{padding: 16px 18px;}}
    .rd-hero h1 {{font-size: 1.6rem;}}
    .rd-hero .coin {{font-size: 1.5rem;}}
    .rd-hero p {{font-size: .78rem;}}
    .rd-big {{font-size: 1.32rem;}}
    .rd-stat {{padding: 10px 11px; border-radius: 14px;}}
    .rd-stat .rd-lab {{font-size: .58rem; letter-spacing: .03em;}}
    .rd-stat .rd-sub {{font-size: .66rem;}}
    .rd-stat .rd-badge {{font-size: .6rem; padding: 2px 7px; margin-top: 5px;}}
    .rd-h {{font-size: 1.02rem; margin-top: 20px;}}
  }}

  /* rounded cards */
  .rd-stat, .rd-card {{background: {CARD}; border: 1px solid {LINE};
                       border-radius: 18px; padding: 15px 17px; margin-bottom: 10px;}}
  .rd-g {{background: {TINT['g']}; border-color: rgba(18,183,106,.35);}}
  .rd-y {{background: {TINT['y']}; border-color: rgba(247,144,9,.35);}}
  .rd-r {{background: {TINT['r']}; border-color: rgba(240,68,56,.35);}}

  .rd-lab {{font-size: .72rem; font-weight: 700; letter-spacing: .08em;
            text-transform: uppercase; color: {SOFT}; margin-bottom: 2px;}}
  .rd-big {{font-size: 1.75rem; font-weight: 800; letter-spacing: -.5px;
            color: {INK}; line-height: 1.15;}}
  .rd-sub {{font-size: .82rem; color: {SOFT}; margin-top: 2px;}}
  .rd-green {{color: {TXT['g']};}} .rd-yellow {{color: {TXT['y']};}}
  .rd-red {{color: {TXT['r']};}}

  .rd-badge {{display: inline-block; padding: 3px 10px; border-radius: 999px;
              font-size: .74rem; font-weight: 700; margin-top: 8px;}}
  .rd-badge.g {{background: {TINT['g']}; color: {TXT['g']};}}
  .rd-badge.y {{background: {TINT['y']}; color: {TXT['y']};}}
  .rd-badge.r {{background: {TINT['r']}; color: {TXT['r']};}}

  /* thin section heading + divider */
  .rd-h {{font-size: 1.18rem; font-weight: 800; color: {INK}; margin: 26px 0 4px;}}
  .rd-div {{border: none; border-top: 1px solid {LINE}; margin: 2px 0 14px;}}

  /* our own chunky progress bars */
  .rd-bar {{background: {LINE}; border-radius: 999px; height: 14px; overflow: hidden;
            margin: 10px 0 6px;}}
  .rd-fill {{height: 100%; border-radius: 999px;}}

  .rd-quote {{font-size: 1.02rem; font-weight: 600; color: {INK}; line-height: 1.45;}}

  /* keep buttons brand-green even if the theme file is missing */
  .stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {{
      background: #12B76A; border-color: #12B76A; color: #fff;}}
  .stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover {{
      background: #0E9F5B; border-color: #0E9F5B;}}
  .rd-soon {{min-height: 120px;}}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------- 2. helpers
def rupees(x):
    """1234.5 -> '₹1,234.50', 1234.0 -> '₹1,234'"""
    x = round(float(x), 2)
    return f"₹{x:,.0f}" if x.is_integer() else f"₹{x:,.2f}"


def stretch():
    """Charts/widgets fill the column. New Streamlit renamed this kwarg."""
    sig = inspect.signature(st.plotly_chart).parameters
    return {"width": "stretch"} if "width" in sig else {"use_container_width": True}


def head(emoji, title):
    """Short section heading + thin divider."""
    st.markdown(f'<div class="rd-h">{emoji} {title}</div><hr class="rd-div">',
                unsafe_allow_html=True)


def bar(pct, colour, height=14):
    """Rounded progress bar in plain HTML."""
    pct = max(0, min(pct, 100))
    st.markdown(f'<div class="rd-bar" style="height:{height}px">'
                f'<div class="rd-fill" style="width:{pct:.0f}%;background:{colour}">'
                f'</div></div>', unsafe_allow_html=True)


def status(ratio):
    """🟢 safe / 🟡 close / 🔴 over, from a spend ÷ budget ratio."""
    if ratio <= 0.75:
        return "🟢", "Safe", "g", G
    if ratio <= 1:
        return "🟡", "Close", "y", Y
    return "🔴", "Over", "r", R


def pretty(fig, height=290):
    """Transparent + theme-aware plotly layout."""
    fig.update_layout(
        template="plotly_dark" if DARK else "plotly_white",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=6, r=6, t=26, b=6),
        font=dict(color=INK, size=12),
        height=height,
    )
    return fig


# ---------------------------------------------------------------- 3. sample data
BASE_ROWS = [  # (days ago, merchant, category, amount)
    (0, "Zomato", "Food", 386), (0, "Uber", "Transport", 248),
    (1, "Starbucks", "Food", 341), (1, "BookMyShow", "Fun", 520),
    (2, "Myntra", "Shopping", 1499), (3, "Jio recharge", "Bills", 299),
    (4, "Swiggy", "Food", 457), (5, "Metro card", "Transport", 150),
    (6, "Nykaa", "Shopping", 689), (8, "Coursera", "Study", 999),
    (10, "Blinkit", "Food", 623), (12, "Spotify", "Bills", 119),
    (15, "Decathlon", "Shopping", 1249), (18, "Cafe Coffee Day", "Food", 287),
    (21, "Electricity bill", "Bills", 860),
]
CARRY_OVER = 1180.0   # spare change saved last month (a demo head start)

# ---- memory that survives clicks
st.session_state.setdefault("extra", [])          # expenses added by the user
st.session_state.setdefault("transferred", 0.0)   # money moved to the pot
st.session_state.setdefault("celebrated", None)   # goal we already cheered for
st.session_state.setdefault("tip", "Small savings every day become big savings every year.")

today = pd.Timestamp.today().normalize()
df = pd.DataFrame(BASE_ROWS + st.session_state.extra,
                  columns=["days_ago", "Merchant", "Category", "Amount"])
df["Amount"] = pd.to_numeric(df["Amount"])
df["Round-up"] = df["Amount"].apply(lambda a: round(math.ceil(a / 10) * 10 - a, 2))
df["Date"] = today - pd.to_timedelta(df["days_ago"], "D")

spent = df["Amount"].sum()
today_spent = df.loc[df["days_ago"] == 0, "Amount"].sum()
roundups = df["Round-up"].sum()
days_covered = max(int(df["days_ago"].max()) + 1, 1)

jar = round(CARRY_OVER + roundups - st.session_state.transferred, 2)  # spare change now
pot = round(st.session_state.transferred, 2)                          # moved to pot
total_saved = round(jar + pot, 2)                                     # both are yours
daily_avg = spent / days_covered
buffer_days = total_saved / daily_avg if daily_avg else 0

# ---- one-time toast after an action (shown on the next run)
flash = st.session_state.pop("flash", None)

# ---------------------------------------------------------------- 4. sidebar (settings only)
with st.sidebar:
    st.markdown("#### ₹ Rupee Do")
    st.caption("Settings")
    budget = st.slider("💸 Monthly budget", 2000, 50000, 12000, step=500, format="₹%d")
    st.divider()
    parent_on = st.toggle("👨‍👩‍👧 Parent mode", value=True)
    daily_limit = st.slider("🚦 Daily limit", 100, 3000, 600, step=50, format="₹%d",
                            disabled=not parent_on)
    st.divider()
    if st.button("🔄 Reset demo", **stretch()):
        st.session_state.clear()
        st.rerun()
    st.caption("Demo only · no real payments 🙅")

budget_ratio = spent / budget
icon, word, cls, colour = status(budget_ratio)
day_ratio = today_spent / daily_limit if daily_limit else 0

# ---------------------------------------------------------------- 5. hero
st.markdown("""
<div class="rd-hero">
  <div class="row">
    <div class="coin">₹</div>
    <div>
      <h1>Rupee Do</h1>
      <p>Spare change · goals · 🟢🟡🔴 vibes</p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ---- 3 big stat cards
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""<div class="rd-stat">
        <div class="rd-lab">💸 Spent</div>
        <div class="rd-big">{rupees(spent)}</div>
        <div class="rd-sub">of {rupees(budget)}</div>
        <span class="rd-badge {cls}">{icon} {budget_ratio*100:.0f}%</span>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="rd-stat rd-g">
        <div class="rd-lab">🪙 Savings</div>
        <div class="rd-big rd-green">{rupees(total_saved)}</div>
        <div class="rd-sub">jar + pot</div>
        <span class="rd-badge g">pot {rupees(pot)}</span>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="rd-stat rd-{cls}">
        <div class="rd-lab">🚦 Budget</div>
        <div class="rd-big rd-{'green' if cls=='g' else 'yellow' if cls=='y' else 'red'}">{word}</div>
        <div class="rd-sub">{rupees(max(budget-spent, 0))} left</div>
        <span class="rd-badge {cls}">{icon} {budget_ratio*100:.0f}%</span>
    </div>""", unsafe_allow_html=True)

if flash:
    st.toast(flash, icon="✅")

# ---------------------------------------------------------------- 6. quick add expense
head("➕", "Quick add")
with st.form("add_expense", clear_on_submit=True):
    f1, f2 = st.columns(2)
    amount = f1.number_input("Amount (₹)", 1, 20000, 250, step=10)
    category = f2.selectbox("Category", CATEGORIES)
    merchant = st.text_input("Merchant", placeholder="e.g. Chai Point")
    if st.form_submit_button("Add expense", type="primary", **stretch()):
        # store as a tuple, same shape as BASE_ROWS
        st.session_state.extra.append((0, merchant.strip() or "Quick add",
                                       category, float(amount)))
        st.session_state.flash = f"Added {rupees(amount)} · {category}"
        st.rerun()
st.caption("Every number, chart and colour on this page updates instantly.")

# ---------------------------------------------------------------- 7. coin jar
head("🫙", "Coin jar")
jar_pct = jar / 1000 * 100
jar_colour = G if jar >= 1000 else Y
jar_note = "Ready to transfer 🎉" if jar >= 1000 else f"{rupees(1000 - jar)} to go"
st.markdown(f"""<div class="rd-card">
    <div class="rd-lab">Round-off savings</div>
    <div class="rd-big">{rupees(jar)} <span class="rd-sub">/ ₹1,000</span></div>
    <div class="rd-sub">{jar_note}</div></div>""", unsafe_allow_html=True)
bar(jar_pct, jar_colour)
st.caption(f"₹{roundups:.0f} from round-ups this month + {rupees(CARRY_OVER)} carried over − "
           f"{rupees(pot)} transferred.")

t1, t2 = st.columns([1, 1])
with t1:
    if st.button(f"🪙 Move {rupees(jar)} to pot", type="primary", **stretch(),
                 disabled=jar < 1000):
        st.session_state.transferred += jar
        st.session_state.flash = f"Moved {rupees(jar)} to your savings pot!"
        st.balloons()
        st.rerun()
with t2:
    st.caption("Unlocks at ₹1,000." if jar < 1000 else "Transfer unlocked.")

with st.expander(f"📄 All {len(df)} transactions"):
    st.dataframe(df[["Date", "Merchant", "Category", "Amount", "Round-up"]]
                 .sort_values("Date", ascending=False), hide_index=True, height=280,
                 **stretch(),
                 column_config={"Amount": st.column_config.NumberColumn(format="₹%d"),
                                "Round-up": st.column_config.NumberColumn(format="₹%.2f"),
                                "Date": st.column_config.DateColumn(format="DD MMM")})

# ---------------------------------------------------------------- 8. goal
head("🎯", "Goal")
g1, g2 = st.columns([1.2, 1])
goal_name = g1.text_input("Goal name", "New phone 📱", label_visibility="collapsed",
                          placeholder="Goal name")
goal_amount = g2.number_input("Goal amount", 500, 200000, 5000, step=500,
                              label_visibility="collapsed")
goal_pct = min(total_saved / goal_amount * 100, 100)
reached = total_saved >= goal_amount
st.markdown(f"""<div class="rd-card {'rd-g' if reached else ''}">
    <div class="rd-lab">{goal_name or 'Goal'}</div>
    <div class="rd-big">{rupees(min(total_saved, goal_amount))}
      <span class="rd-sub">/ {rupees(goal_amount)}</span></div>
    <div class="rd-sub">{goal_pct:.0f}% funded</div></div>""", unsafe_allow_html=True)
bar(goal_pct, G if reached else Y)
if reached:
    st.success("Goal reached 🎉")
    if st.session_state.celebrated != goal_amount:      # cheer only once per goal
        st.session_state.celebrated = goal_amount
        st.balloons()
        st.toast("Goal reached 🎉", icon="🎯")
else:
    st.caption(f"{rupees(goal_amount - total_saved)} to go.")

# ---------------------------------------------------------------- 9. spending status
head("🚦", "Spending")
st.markdown(f"""<div class="rd-card rd-{cls}">
    <div class="rd-lab">Monthly budget</div>
    <div class="rd-big rd-{'green' if cls=='g' else 'yellow' if cls=='y' else 'red'}">
      {icon} {word}</div>
    <div class="rd-sub">{rupees(spent)} of {rupees(budget)} · {budget_ratio*100:.0f}% used</div>
    </div>""", unsafe_allow_html=True)
bar(budget_ratio * 100, colour)
zone = ("🟢 under 75%" if cls == "g" else "🟡 75–100%" if cls == "y" else "🔴 over 100%")
st.caption(f"Zones: 🟢 safe · 🟡 close · 🔴 over — you are {zone}.")

# ---------------------------------------------------------------- 10. charts
head("🥧", "Where it goes")
ch1, ch2 = st.columns(2)
with ch1:
    by_cat = df.groupby("Category", as_index=False)["Amount"].sum()
    donut = px.pie(by_cat, names="Category", values="Amount", hole=0.55,
                   color_discrete_sequence=[G, Y, R, "#3B82F6", "#8B5CF6", "#14B8A6"])
    donut.update_traces(textinfo="percent", textposition="inside", sort=False)
    donut.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.15, font=dict(size=11)))
    st.plotly_chart(pretty(donut), config={"displayModeBar": False}, **stretch())
with ch2:
    days = pd.date_range(today - pd.Timedelta(days=13), today)
    daily = df.groupby("Date")["Amount"].sum().reindex(days, fill_value=0).reset_index()
    daily.columns = ["Date", "Amount"]
    daily["col"] = [GREY if a == 0 else
                    G if a < 0.8 * daily_limit else
                    Y if a <= daily_limit else R
                    for a in daily["Amount"]]
    line = go.Figure(go.Bar(x=daily["Date"], y=daily["Amount"],
                            marker_color=daily["col"], marker_line_width=0))
    line.add_hline(y=daily_limit, line_dash="dot", line_color=TXT["r"],
                   annotation_text="limit", annotation_font_size=10)
    line.update_layout(title=dict(text="Last 14 days", font=dict(size=13)), showlegend=False)
    line.update_xaxes(tickformat="%d %b", showgrid=False)
    line.update_yaxes(gridcolor="rgba(128,128,128,.15)")
    st.plotly_chart(pretty(line), config={"displayModeBar": False}, **stretch())
st.caption(f"Bar colour vs your {rupees(daily_limit)} daily limit: 🟢 under · 🟡 close · 🔴 over.")

# ---------------------------------------------------------------- 11. emergency buffer (gauge)
head("🛟", "Emergency buffer")
gauge_colour = G if buffer_days >= 7 else Y if buffer_days >= 3 else R
fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=round(buffer_days, 1),
    domain={"x": [0, 1], "y": [0, 1]},
    number={"suffix": " days", "font": {"size": 28, "color": INK}},
    gauge={
        "axis": {"range": [0, 30], "tickwidth": 0, "tickcolor": SOFT,
                 "tickfont": {"size": 10, "color": SOFT}},
        "bar": {"color": gauge_colour, "thickness": 0.28},
        "bgcolor": "rgba(0,0,0,0)", "borderwidth": 0,
        "steps": [
            {"range": [0, 3], "color": TINT["r"]},
            {"range": [3, 7], "color": TINT["y"]},
            {"range": [7, 30], "color": TINT["g"]},
        ],
        "threshold": {"line": {"color": gauge_colour, "width": 3},
                      "thickness": 0.8, "value": buffer_days},
    },
))
fig.update_layout(margin=dict(l=10, r=10, t=10, b=0))
st.plotly_chart(pretty(fig, height=260), config={"displayModeBar": False}, **stretch())
st.caption(f"{rupees(total_saved)} saved ÷ {rupees(daily_avg)}/day average spend. "
           "🔴 0–3 days · 🟡 3–7 · 🟢 7–30. Target: 30.")

# ---------------------------------------------------------------- 12. parent mode
head("👨‍👩‍👧", "Parent mode")
if parent_on:
    d_icon, d_word, d_cls, d_colour = status(day_ratio)
    if today_spent > daily_limit:
        warn = "🚨 Daily limit crossed — a demo alert went to your parent."
    else:
        warn = f"✅ Inside today's limit · {rupees(daily_limit - today_spent)} left"
    st.markdown(f"""<div class="rd-card rd-{d_cls}">
        <div class="rd-lab">Today</div>
        <div class="rd-big rd-{'green' if d_cls=='g' else 'yellow' if d_cls=='y' else 'red'}">
          {rupees(today_spent)} <span class="rd-sub">/ {rupees(daily_limit)}</span></div>
        <span class="rd-badge {d_cls}">{d_icon} {d_word}</span></div>""",
                unsafe_allow_html=True)
    bar(day_ratio * 100, d_colour)
    if today_spent > daily_limit:
        st.error(warn)
    else:
        st.caption(warn + " Change the daily limit in the sidebar.")
else:
    st.caption("Parent mode is off — turn it on in the sidebar to set a daily limit.")

# ---------------------------------------------------------------- 13. tips
head("😹", "Tip")
tips = [
    "Your bank balance called. It's not angry, just disappointed.",
    "Swiggy isn't a food app, it's a savings leak with great UI.",
    "Budget = telling your money where to go instead of wondering where it went.",
    "That ₹249 in-app purchase, 40 times, is a flight to Goa.",
    "Compound interest is the only friend that gets richer while you sleep.",
    "A free trial is a subscription with a countdown you will forget.",
    "Retail therapy works. The bill is the side effect.",
    "Round-ups: ₹4 here and ₹6 there is literally how phones get bought.",
    "Your UPI PIN is not a personality. Don't share it.",
    "Investing ₹500 today beats 'next month' for the 47th time.",
]
with st.expander("😹 One-liners & captions", expanded=True):
    tip_tab, all_tab = st.tabs(["🎲 Random tip", "📋 All tips"])
    with tip_tab:
        if st.button("Give me a tip", type="primary", **stretch()):
            st.session_state.tip = random.choice(tips)
            st.toast("Fresh tip served 😹", icon="🍳")
            st.balloons()
        st.markdown(f'<div class="rd-card"><div class="rd-quote">“{st.session_state.tip}”</div>'
                    f'</div>', unsafe_allow_html=True)
    with all_tab:
        for t in tips:
            st.markdown(f'<div class="rd-sub" style="margin:6px 0">• {t}</div>',
                        unsafe_allow_html=True)

# ---------------------------------------------------------------- 14. coming soon
head("🚧", "Coming soon")
soon = [("📈", "SIP investing"), ("✈️", "Travel tickets"), ("🎁", "Gift cards"),
        ("🔐", "Biometric login"), ("🧊", "Auto freeze"), ("🔁", "Autopay"),
        ("📱", "Tap to pay")]
s1, s2 = st.columns(2)
for i, (emoji, name) in enumerate(soon):
    with (s1 if i % 2 == 0 else s2):
        st.markdown(f"""<div class="rd-card rd-soon">
            <div style="font-size:1.6rem">{emoji}</div>
            <div style="font-weight:700;color:{INK};margin:4px 0 8px">{name}</div>
            <span class="rd-badge y">🚧 Soon</span></div>""", unsafe_allow_html=True)

st.markdown(f'<hr class="rd-div" style="margin-top:26px">'
            f'<div class="rd-sub" style="text-align:center">Rupee Do · demo bank for Gen Z · '
            f'sample data only, no real payments</div>', unsafe_allow_html=True)
