"""Rupee Do — a 3-page Gen Z banking demo. Sample data only, no real payments."""

import inspect
import math
import random

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------- page setup
st.set_page_config(page_title="Rupee Do", page_icon="₹", layout="centered")

G, Y, R = "#12B76A", "#F79009", "#F04438"                  # 🟢🟡🔴 status
BLUE, PURPLE, PINK, ORANGE = "#3B82F6", "#8B5CF6", "#EC4899", "#F97316"
BRIGHT = [G, Y, R, BLUE, PURPLE, PINK, "#14B8A6"]          # bright chart palette
CATEGORIES = ["Food", "Shopping", "Transport", "Bills", "Study", "Fun", "Other"]


def _is_dark():
    """True when the viewer's browser is in dark mode."""
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

# Colours picked once, so every card stays readable in both themes
INK = "#EAF0F7" if DARK else "#101828"          # main text
SOFT = "#9AA7B8" if DARK else "#667085"         # small labels
CARD = "rgba(255,255,255,.07)" if DARK else "rgba(255,255,255,.80)"
LINE = "rgba(255,255,255,.13)" if DARK else "rgba(16,24,40,.07)"
SHADOW = "0 8px 24px rgba(0,0,0,.38)" if DARK else "0 8px 24px rgba(16,24,40,.07)"
BG = ("linear-gradient(160deg,#0A1220 0%,#0C1A17 45%,#121024 100%)" if DARK else
      "linear-gradient(160deg,#EFFBF3 0%,#FFFBEC 45%,#F3F5FF 100%)")
TINT = {"g": "18,183,106", "y": "247,144,9", "r": "240,68,56",
        "b": "59,130,246", "p": "139,92,246", "o": "249,115,22", "k": "236,72,153"}
TXT = {"g": "#34D399" if DARK else "#067647", "y": "#FBBF24" if DARK else "#B54708",
       "r": "#F87171" if DARK else "#B42318", "b": "#60A5FA" if DARK else "#1D4ED8",
       "p": "#A78BFA" if DARK else "#6D28D9", "o": "#FB923C" if DARK else "#C2410C",
       "k": "#F472B6" if DARK else "#BE185D"}

# Tinted gradient background for every tone (works on light and dark)
TONES = "\n".join(
    f'.tone-{k} {{background: linear-gradient(135deg, rgba({v},.22), rgba({v},.06)); '
    f'border-color: rgba({v},.42);}}'
    for k, v in TINT.items()
)

st.markdown(f"""
<style>
  /* soft gradient page background instead of plain black / white */
  .stApp, [data-testid="stAppViewContainer"] {{background: {BG} !important;}}
  .block-container {{max-width: 820px; padding-top: 1rem; padding-bottom: 3rem;}}

  /* ---------- banners ---------- */
  .rd-brand {{background: linear-gradient(120deg, #0E9F5B 0%, #34C463 45%, #F7C948 100%);
             border-radius: 20px; padding: 18px 20px; color: #06301f;
             box-shadow: {SHADOW}; margin-bottom: 12px;}}
  .rd-brand .row {{display: flex; align-items: center; gap: 10px;}}
  .rd-brand h1 {{margin: 0; font-size: 1.75rem; letter-spacing: -.7px; color: #06301f;
                white-space: nowrap;}}
  .rd-brand p {{margin: 4px 0 0; font-size: .86rem; font-weight: 500; opacity: .82;}}

  .rd-page {{border-radius: 18px; padding: 16px 20px; color: #fff;
            box-shadow: {SHADOW}; margin-bottom: 16px;}}
  .rd-page .t {{font-size: 1.3rem; font-weight: 800; letter-spacing: -.4px;}}
  .rd-page .s {{font-size: .82rem; opacity: .9; margin-top: 2px;}}
  .pg-money {{background: linear-gradient(120deg, #0E9F5B, #34C463 70%, #A3E635);}}
  .pg-where {{background: linear-gradient(120deg, #4F46E5, #8B5CF6 55%, #EC4899);}}
  .pg-soon  {{background: linear-gradient(120deg, #F97316, #F43F5E 60%, #EC4899);}}

  /* ---------- cards ---------- */
  .rd-card, .rd-stat {{border-radius: 18px; padding: 15px 17px; margin-bottom: 12px;
       background: {CARD}; border: 1px solid {LINE}; box-shadow: {SHADOW};
       backdrop-filter: blur(8px);}}
  .rd-lab {{font-size: .7rem; font-weight: 800; letter-spacing: .08em;
            text-transform: uppercase; color: {SOFT};}}
  .rd-big {{font-size: 1.65rem; font-weight: 800; letter-spacing: -.5px;
            color: {INK}; line-height: 1.2;}}
  .rd-sub {{font-size: .8rem; color: {SOFT}; margin-top: 2px;}}
  .rd-badge {{display: inline-block; padding: 3px 10px; border-radius: 999px;
              font-size: .72rem; font-weight: 800; margin-top: 8px;}}
  .green {{color: {TXT['g']};}} .yellow {{color: {TXT['y']};}} .red {{color: {TXT['r']};}}
  .blue {{color: {TXT['b']};}} .purple {{color: {TXT['p']};}} .orange {{color: {TXT['o']};}}
  .rd-badge.g {{background: rgba(18,183,106,.18); color: {TXT['g']};}}
  .rd-badge.y {{background: rgba(247,144,9,.20); color: {TXT['y']};}}
  .rd-badge.r {{background: rgba(240,68,56,.18); color: {TXT['r']};}}
  .rd-badge.b {{background: rgba(59,130,246,.20); color: {TXT['b']};}}
  .rd-badge.p {{background: rgba(139,92,246,.20); color: {TXT['p']};}}
  .rd-badge.o {{background: rgba(249,115,22,.20); color: {TXT['o']};}}
  .rd-badge.k {{background: rgba(236,72,153,.20); color: {TXT['k']};}}

  /* ---------- headings + progress bars ---------- */
  .rd-h {{font-size: 1.1rem; font-weight: 800; color: {INK}; margin: 22px 0 2px;}}
  .rd-div {{border: none; border-top: 2px solid; opacity: .35; margin: 4px 0 14px;}}
  .rd-bar {{background: {LINE}; border-radius: 999px; height: 14px; overflow: hidden;
            margin: 10px 0 6px;}}
  .rd-fill {{height: 100%; border-radius: 999px; transition: width .3s ease;}}
  .rd-quote {{font-size: 1rem; font-weight: 600; color: {INK}; line-height: 1.45;}}

  /* brand-green buttons, whatever the theme */
  .stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {{
      background: #12B76A; border-color: #12B76A; color: #fff; font-weight: 700;}}
  .stButton > button[kind="primary"]:hover,
  .stFormSubmitButton > button[kind="primary"]:hover {{
      background: #0E9F5B; border-color: #0E9F5B;}}

  /* phones */
  @media (max-width: 480px) {{
    .rd-brand h1 {{font-size: 1.35rem;}}
    .rd-brand p {{font-size: .76rem;}}
    .rd-page .t {{font-size: 1.1rem;}}
    .rd-stat {{padding: 10px 11px; border-radius: 14px;}}
    .rd-stat .rd-lab {{font-size: .56rem; letter-spacing: .03em;}}
    .rd-stat .rd-sub {{font-size: .64rem;}}
    .rd-stat .rd-badge {{font-size: .58rem; padding: 2px 6px; margin-top: 5px;}}
    .rd-big {{font-size: 1.25rem;}}
    .rd-h {{font-size: 1rem; margin-top: 18px;}}
  }}
  {TONES}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------- helpers
def rupees(x):
    """1234.5 -> '₹1,234.50', 1234.0 -> '₹1,234'"""
    x = round(float(x), 2)
    return f"₹{x:,.0f}" if x.is_integer() else f"₹{x:,.2f}"


def stretch():
    """Charts fill the column. Newer Streamlit renamed this kwarg."""
    sig = inspect.signature(st.plotly_chart).parameters
    return {"width": "stretch"} if "width" in sig else {"use_container_width": True}


def head(emoji, title, accent):
    """Section heading + thin coloured divider."""
    st.markdown(f'<div class="rd-h">{emoji} {title}</div>'
                f'<hr class="rd-div" style="border-top-color:{accent}">',
                unsafe_allow_html=True)


def card(html, tone=""):
    """Rounded card. tone: g/y/r/b/p/o/k for a coloured background."""
    cls = f"tone-{tone}" if tone else ""
    st.markdown(f'<div class="rd-card {cls}">{html}</div>', unsafe_allow_html=True)


def stat_card(emoji, label, big, sub, badge="", tone="", big_cls=""):
    """One of the three big stat cards at the top."""
    cls = f"tone-{tone}" if tone else ""
    chip = f'<span class="rd-badge {tone}">{badge}</span>' if badge else ""
    st.markdown(f"""<div class="rd-stat {cls}">
        <div class="rd-lab">{emoji} {label}</div>
        <div class="rd-big {big_cls}">{big}</div>
        <div class="rd-sub">{sub}</div>{chip}</div>""", unsafe_allow_html=True)


def bar(pct, colour):
    """Rounded progress bar in plain HTML."""
    pct = max(0, min(pct, 100))
    st.markdown(f'<div class="rd-bar"><div class="rd-fill" '
                f'style="width:{pct:.0f}%;background:{colour}"></div></div>',
                unsafe_allow_html=True)


def status(ratio):
    """🟢 safe / 🟡 close / 🔴 over from a spend ÷ budget ratio."""
    if ratio <= 0.75:
        return "🟢", "Safe", "g", G
    if ratio <= 1:
        return "🟡", "Close", "y", Y
    return "🔴", "Over", "r", R


def pretty(fig, height=290):
    """Transparent, theme-aware plotly layout."""
    fig.update_layout(
        template="plotly_dark" if DARK else "plotly_white",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=6, r=6, t=28, b=6), font=dict(color=INK, size=12), height=height)
    return fig


# ---------------------------------------------------------------- sample data
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

ss = st.session_state
ss.setdefault("extra", [])          # expenses added with Quick add
ss.setdefault("transferred", 0.0)   # money moved from jar → pot
ss.setdefault("celebrated", None)   # goal we already cheered for
ss.setdefault("tip", "Small savings every day become big savings every year.")
ss.setdefault("budget", 12000)      # settings live here so they survive page switches
ss.setdefault("daily_limit", 600)
ss.setdefault("parent_on", True)

today = pd.Timestamp.today().normalize()
df = pd.DataFrame(BASE_ROWS + ss.extra,
                  columns=["days_ago", "Merchant", "Category", "Amount"])
df["Amount"] = pd.to_numeric(df["Amount"])
df["Round-up"] = df["Amount"].apply(lambda a: round(math.ceil(a / 10) * 10 - a, 2))
df["Date"] = today - pd.to_timedelta(df["days_ago"], "D")

spent = df["Amount"].sum()
today_spent = df.loc[df["days_ago"] == 0, "Amount"].sum()
roundups = df["Round-up"].sum()
days_covered = max(int(df["days_ago"].max()) + 1, 1)

jar = round(CARRY_OVER + roundups - ss.transferred, 2)   # spare change available
pot = round(ss.transferred, 2)                          # already transferred
total_saved = round(jar + pot, 2)
daily_avg = spent / days_covered
buffer_days = total_saved / daily_avg if daily_avg else 0

# toasts / balloons queued by the previous click
flash = ss.pop("flash", None)
party = ss.pop("party", False)

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown("### ₹ Rupee Do")
    page = st.radio("Pages", ["💰 My Money", "📊 Where It Goes", "🚀 Coming Soon"],
                    label_visibility="collapsed")
    st.divider()
    st.caption(f"Spare change **{rupees(jar)}**\n\nSavings **{rupees(total_saved)}**")
    if st.button("🔄 Reset demo", **stretch()):
        for k in ("extra", "transferred", "celebrated", "flash", "party",
                  "budget", "daily_limit", "parent_on"):
            ss.pop(k, None)
        st.rerun()
    st.caption("Demo only · no real payments 🙅")

# ---------------------------------------------------------------- brand banner
st.markdown("""
<div class="rd-brand">
  <div class="row"><div style="font-size:1.7rem">₹</div>
    <div><h1>Rupee Do</h1>
      <p>Spare change · goals · 🟢🟡🔴 vibes</p></div></div>
</div>
""", unsafe_allow_html=True)

if flash:
    st.toast(flash, icon="✅")
if party:
    st.balloons()

# ================================================================ PAGE 1
if page == "💰 My Money":
    st.markdown("""<div class="rd-page pg-money">
        <div class="t">💰 My Money</div>
        <div class="s">Spend, save, transfer — all live</div></div>""",
                unsafe_allow_html=True)

    budget_ratio = spent / ss.budget
    icon, word, cls, colour = status(budget_ratio)

    c1, c2, c3 = st.columns(3)
    with c1:
        stat_card("💸", "Spent", rupees(spent), f"of {rupees(ss.budget)}",
                  f"{icon} {budget_ratio*100:.0f}%", cls)
    with c2:
        stat_card("🪙", "Savings", rupees(total_saved), "jar + pot",
                  f"pot {rupees(pot)}", "g", "green")
    with c3:
        stat_card("🚦", "Budget", word, f"{rupees(max(ss.budget-spent, 0))} left",
                  f"{icon} {budget_ratio*100:.0f}%", cls,
                  {"g": "green", "y": "yellow", "r": "red"}[cls])

    # ---- quick add
    head("➕", "Quick add", G)
    with st.form("add_expense", clear_on_submit=True):
        f1, f2 = st.columns(2)
        amount = f1.number_input("Amount (₹)", 1, 20000, 250, step=10)
        category = f2.selectbox("Category", CATEGORIES)
        merchant = st.text_input("Merchant", placeholder="e.g. Chai Point")
        if st.form_submit_button("Add expense", type="primary", **stretch()):
            ss.extra.append((0, merchant.strip() or "Quick add", category, float(amount)))
            ss.flash = f"Added {rupees(amount)} · {category}"
            st.rerun()

    # ---- coin jar
    head("🫙", "Coin jar", G)
    jar_pct = jar / 1000 * 100
    card(f"""<div class="rd-lab">Round-off savings</div>
        <div class="rd-big">{rupees(jar)} <span class="rd-sub">/ ₹1,000</span></div>
        <div class="rd-sub">{'Ready to transfer 🎉' if jar >= 1000 else rupees(1000-jar) + ' to go'}</div>""",
         "g" if jar >= 1000 else "y")
    bar(jar_pct, G if jar >= 1000 else Y)

    t1, t2 = st.columns([1.2, 1])
    with t1:
        if st.button(f"🪙 Move {rupees(jar)} to pot", type="primary", **stretch(),
                     disabled=jar < 1000):
            ss.transferred += jar
            ss.flash = f"Moved {rupees(jar)} to your savings pot!"
            ss.party = True
            st.rerun()
    with t2:
        st.caption("Unlocks at ₹1,000." if jar < 1000 else "Transfer unlocked ✅")

    with st.expander(f"📄 All {len(df)} transactions"):
        st.dataframe(df[["Date", "Merchant", "Category", "Amount", "Round-up"]]
                     .sort_values("Date", ascending=False), hide_index=True, height=260,
                     **stretch(),
                     column_config={"Amount": st.column_config.NumberColumn(format="₹%d"),
                                    "Round-up": st.column_config.NumberColumn(format="₹%.2f"),
                                    "Date": st.column_config.DateColumn(format="DD MMM")})

    # ---- goal
    head("🎯", "Goal", G)
    g1, g2 = st.columns([1.2, 1])
    goal_name = g1.text_input("Goal name", "New phone 📱", label_visibility="collapsed",
                              placeholder="Goal name")
    goal_amount = g2.number_input("Goal amount", 500, 200000, 5000, step=500,
                                  label_visibility="collapsed")
    goal_pct = min(total_saved / goal_amount * 100, 100)
    reached = total_saved >= goal_amount
    card(f"""<div class="rd-lab">{goal_name or 'Goal'}</div>
        <div class="rd-big">{rupees(min(total_saved, goal_amount))}
          <span class="rd-sub">/ {rupees(goal_amount)}</span></div>
        <div class="rd-sub">{goal_pct:.0f}% funded</div>""", "g" if reached else "")
    bar(goal_pct, G if reached else Y)
    if reached:
        st.success("Goal reached 🎉")
        if ss.celebrated != goal_amount:          # cheer once per goal
            ss.celebrated = goal_amount
            ss.party, ss.flash = True, "Goal reached 🎉"
            st.rerun()
    else:
        st.caption(f"{rupees(goal_amount - total_saved)} to go.")

    # ---- spending status
    head("🚦", "Spending status", G)
    ss.budget = st.slider("💸 Monthly budget", 2000, 50000, value=int(ss.budget),
                          step=500, format="₹%d", key="budget_w")
    ss.budget = ss.budget            # keep the plain copy for other pages
    icon, word, cls, colour = status(spent / ss.budget)
    card(f"""<div class="rd-lab">Monthly budget</div>
        <div class="rd-big {dict(g='green', y='yellow', r='red')[cls]}">{icon} {word}</div>
        <div class="rd-sub">{rupees(spent)} of {rupees(ss.budget)} ·
          {spent/ss.budget*100:.0f}% used</div>""", cls)
    bar(spent / ss.budget * 100, colour)

# ================================================================ PAGE 2
elif page == "📊 Where It Goes":
    st.markdown("""<div class="rd-page pg-where">
        <div class="t">📊 Where It Goes</div>
        <div class="s">Charts, buffer and the parent switch</div></div>""",
                unsafe_allow_html=True)

    # ---- charts
    head("🥧", "Spending by category", PURPLE)
    by_cat = df.groupby("Category", as_index=False)["Amount"].sum()
    donut = px.pie(by_cat, names="Category", values="Amount", hole=0.55,
                   color_discrete_sequence=BRIGHT)
    donut.update_traces(textinfo="percent", textposition="inside", textfont_size=13)
    donut.update_layout(showlegend=True, height=360,
                        legend=dict(orientation="h", y=-0.08, font=dict(size=11)),
                        margin=dict(l=6, r=6, t=10, b=6))
    st.plotly_chart(pretty(donut, 360), config={"displayModeBar": False}, **stretch())

    days = pd.date_range(today - pd.Timedelta(days=13), today)
    daily = df.groupby("Date")["Amount"].sum().reindex(days, fill_value=0).reset_index()
    daily.columns = ["Date", "Amount"]
    daily["col"] = ["rgba(148,163,184,.45)" if a == 0 else
                    G if a < 0.8 * ss.daily_limit else
                    Y if a <= ss.daily_limit else R for a in daily["Amount"]]
    bars = go.Figure(go.Bar(x=daily["Date"], y=daily["Amount"], marker_color=daily["col"]))
    bars.add_hline(y=ss.daily_limit, line_dash="dot", line_color=TXT["r"],
                   annotation_text="limit", annotation_font_size=10)
    bars.update_layout(title=dict(text="Last 14 days", font=dict(size=13)))
    bars.update_xaxes(tickformat="%d %b", showgrid=False)
    bars.update_yaxes(gridcolor="rgba(148,163,184,.2)")
    st.plotly_chart(pretty(bars, 280), config={"displayModeBar": False}, **stretch())
    st.caption("🟢 under your daily limit · 🟡 close · 🔴 over")

    # ---- emergency buffer
    head("🛟", "Emergency buffer", BLUE)
    gcol = G if buffer_days >= 7 else Y if buffer_days >= 3 else R
    gauge = go.Figure(go.Indicator(
        mode="gauge+number", value=round(buffer_days, 1),
        number={"suffix": " days", "font": {"size": 28, "color": INK}},
        domain={"x": [0, 1], "y": [0, 1]},
        gauge={"axis": {"range": [0, 30], "tickwidth": 0, "tickcolor": SOFT,
                        "tickfont": {"size": 10, "color": SOFT}},
               "bar": {"color": gcol, "thickness": 0.28},
               "bgcolor": "rgba(0,0,0,0)", "borderwidth": 0,
               "steps": [{"range": [0, 3], "color": f"rgba({TINT['r']},.22)"},
                         {"range": [3, 7], "color": f"rgba({TINT['y']},.22)"},
                         {"range": [7, 30], "color": f"rgba({TINT['g']},.22)"}],
               "threshold": {"line": {"color": gcol, "width": 3},
                             "thickness": 0.8, "value": buffer_days}}))
    gauge.update_layout(margin=dict(l=10, r=10, t=10, b=0))
    st.plotly_chart(pretty(gauge, 250), config={"displayModeBar": False}, **stretch())
    st.caption(f"{rupees(total_saved)} saved ÷ {rupees(daily_avg)}/day · "
               f"🔴 0–3 · 🟡 3–7 · 🟢 7–30 days")

    # ---- parental control
    head("👨‍👩‍👧", "Parental control", PINK)
    # the widget owns its own key; mirror it into ss.parent_on so it works
    # on the very first render too (no value= here, or the toggle would stick)
    ss.parent_on = st.toggle("Parent mode", value=ss.get("parent_on", True),
                             key="parent_toggle")
    if ss.parent_on:
        ss.daily_limit = st.slider("🚦 Daily spending limit", 100, 3000,
                                   value=int(ss.daily_limit), step=50, format="₹%d",
                                   key="limit_w")
        ss.daily_limit = ss.daily_limit
        day_ratio = today_spent / ss.daily_limit if ss.daily_limit else 0
        d_icon, d_word, d_cls, d_colour = status(day_ratio)
        card(f"""<div class="rd-lab">Today</div>
            <div class="rd-big {dict(g='green', y='yellow', r='red')[d_cls]}">
              {rupees(today_spent)} <span class="rd-sub">/ {rupees(ss.daily_limit)}</span></div>
            <span class="rd-badge {d_cls}">{d_icon} {d_word}</span>""", d_cls)
        bar(day_ratio * 100, d_colour)
        if today_spent > ss.daily_limit:
            st.error("🚨 Daily limit crossed — a demo alert went to your parent.")
        else:
            st.caption(f"✅ {rupees(ss.daily_limit - today_spent)} left today.")
    else:
        st.caption("Parent mode is off — turn it on to set a daily limit.")

    # ---- tips
    head("😹", "Money tip", ORANGE)
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
    with st.expander("😹 Tap for a random one-liner", expanded=True):
        if st.button("Give me a tip", type="primary", **stretch()):
            ss.tip = random.choice(tips)
            ss.flash, ss.party = "Fresh tip served 😹", True
            st.rerun()
        card(f'<div class="rd-quote">“{ss.tip}”</div>', "o")

# ================================================================ PAGE 3
else:
    st.markdown("""<div class="rd-page pg-soon">
        <div class="t">🚀 Coming Soon</div>
        <div class="s">What we're building next</div></div>""",
                unsafe_allow_html=True)

    soon = [
        ("📈", "SIP investing", "From ₹500, in-app", "p"),
        ("✈️", "Travel tickets", "Train · bus · flight", "b"),
        ("🎁", "Gift cards", "₹100 to friends", "k"),
        ("🔐", "Biometric login", "Face or fingerprint", "g"),
        ("🧊", "Auto freeze", "Kill card scams", "b"),
        ("🔁", "Autopay", "Rent + recharges", "o"),
        ("📱", "Tap to pay", "Pay by tap", "k"),
    ]
    rows = [soon[i:i + 2] for i in range(0, len(soon), 2)]
    for pair in rows:
        cols = st.columns(len(pair))
        for col, (emoji, title, blurb, tone) in zip(cols, pair):
            with col:
                st.markdown(f"""<div class="rd-card tone-{tone}"
                    style="min-height:132px">
                    <div style="font-size:1.7rem">{emoji}</div>
                    <div style="font-weight:800;color:{INK};margin:4px 0 2px">{title}</div>
                    <div style="font-size:.76rem;color:{SOFT}">{blurb}</div>
                    <span class="rd-badge {tone}">🚧 Soon</span></div>""",
                            unsafe_allow_html=True)

    card(f"""<div class="rd-lab">That's the demo</div>
        <div class="rd-sub" style="margin-top:6px">Sample data only · no real payments ·
        built with Streamlit + pandas + Plotly</div>""")
