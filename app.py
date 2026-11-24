"""Self Healing Vault — a small demo banking app.

Sample data only, no real payments, no real investing.
Everything lives in st.session_state, so the screen updates instantly.
"""

import datetime as dt
import inspect
import re

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ================================================================ 1. page setup
st.set_page_config(page_title="Self Healing Vault", page_icon="🛡️", layout="centered")

# Bright Google Pay-ish accent palette
BLUE, GREEN, YELLOW, RED = "#1A73E8", "#1AA260", "#F9AB00", "#EA4335"
PURPLE, GRAY = "#7B61FF", "#5F6368"
PASSCODE = "0000"           # the demo passcode
VAULT_TARGET = 500.0        # progress bar goal for the vault
RD_RATE = 6.5               # fixed demo interest rate for a recurring deposit


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

# Colours chosen once so every card is readable in light AND dark mode
INK = "#E8EAED" if DARK else "#202124"          # main text
SOFT = "#9AA0A6" if DARK else "#5F6368"         # secondary text
CARD = "#1F2228" if DARK else "#FFFFFF"         # card background
CARD2 = "#282B33" if DARK else "#F8F9FA"        # soft inner card
LINE = "rgba(255,255,255,.10)" if DARK else "rgba(60,64,67,.12)"
SHADOW = "0 2px 10px rgba(0,0,0,.45)" if DARK else "0 2px 10px rgba(60,64,67,.10)"
PAGE = "#14161A" if DARK else "#FFFFFF"
VGREEN = "#34D399" if DARK else "#0B7A3E"       # vault green (readable both ways)

st.markdown(f"""
<style>
  /* ---- page shell: looks like a phone app ---- */
  .stApp {{background: {PAGE};}}
  /* Streamlit's fixed toolbar is ~60px tall; push content clear of it */
  .block-container {{max-width: 620px; padding-top: 4.4rem !important;
                    padding-bottom: 3rem;}}
  [data-testid="stSidebar"] > div:first-child {{padding-top: 4rem !important;}}

  /* ---- header ---- */
  .vault-head {{display: block; padding: 4px 2px 16px; margin: 0; min-height: 44px;}}
  .vault-head .mark {{float: left; width: 40px; height: 40px; margin-right: 11px;
                     line-height: 0;}}
  .vault-head .mark svg {{display: block; width: 40px; height: 40px;}}
  .vault-head .name {{font-size: 1.16rem; font-weight: 800; color: {INK};
                     letter-spacing: -.35px; line-height: 1.25; margin: 0;}}
  .vault-head .tag {{font-size: .72rem; color: {SOFT}; margin: 0; line-height: 1.25;}}
  .vault-head::after {{content: ""; display: block; clear: both;}}

  /* ---- cards ---- */
  .v-card {{background: {CARD}; border: 1px solid {LINE}; border-radius: 22px;
           padding: 20px; margin-bottom: 14px; box-shadow: {SHADOW};}}
  .v-soft {{background: {CARD2}; border-radius: 18px; padding: 14px 16px;}}
  .v-label {{font-size: .72rem; font-weight: 700; letter-spacing: .07em;
            text-transform: uppercase; color: {SOFT};}}
  .v-hero {{font-size: 2.35rem; font-weight: 800; letter-spacing: -1.2px;
           color: {INK}; line-height: 1.1; margin: 2px 0 0;}}
  .v-sub {{font-size: .84rem; color: {SOFT}; margin-top: 4px;}}

  /* ---- vault (green accent) ---- */
  .v-vault {{background: linear-gradient(135deg, rgba(26,162,96,.15), rgba(52,211,153,.07));
            border: 1px solid rgba(26,162,96,.38); border-radius: 22px;
            padding: 18px 20px; margin-bottom: 14px; box-shadow: {SHADOW};}}
  .v-vault-amt {{font-size: 2rem; font-weight: 800; letter-spacing: -1px;
                color: {VGREEN}; line-height: 1.15; margin-top: 2px;}}
  .v-bar {{background: rgba(26,162,96,.20); border-radius: 999px; height: 10px;
          overflow: hidden; margin: 12px 0 6px;}}
  .v-bar-fill {{height: 100%; border-radius: 999px;
               background: linear-gradient(90deg, {GREEN}, #34D399);}}
  .v-tobadge {{display: inline-block; margin-top: 3px; padding: 1px 8px;
              border-radius: 999px; font-size: .64rem; font-weight: 800;
              background: rgba(26,162,96,.18); color: {VGREEN};}}
  .v-est {{background: rgba(26,162,96,.12); border: 1px solid rgba(26,162,96,.30);
          border-radius: 16px; padding: 14px 16px; margin: 6px 0 12px;}}
  .v-est .n {{font-size: 1.4rem; font-weight: 800; color: {VGREEN}; line-height: 1.2;}}

  /* ---- passcode gate ---- */
  .v-gate {{background: {CARD}; border: 1px dashed rgba(26,115,232,.45);
           border-radius: 22px; padding: 20px; text-align: center;
           margin-bottom: 14px; box-shadow: {SHADOW};}}
  .v-gate .ico {{font-size: 1.9rem; line-height: 1;}}
  .v-gate .t {{font-weight: 800; color: {INK}; font-size: .95rem; margin-top: 8px;}}
  .v-gate .d {{color: {SOFT}; font-size: .78rem; margin-top: 3px;}}

  /* ---- the vault panel sits under the icon row ---- */
  .st-key-vault_panel {{
      background: {CARD2};
      border: 1px solid {LINE};
      border-radius: 24px;
      padding: 14px 16px 6px;
      margin: 6px 0 18px;
      box-shadow: {SHADOW};}}

  /* ---- section titles ---- */
  .v-h {{font-size: 1.02rem; font-weight: 800; color: {INK}; margin: 22px 0 10px;}}

  /* ---- round icon buttons (Google Pay style) ---- */
  .v-actions {{display: grid; grid-template-columns: repeat(4, 1fr);
              gap: 8px; margin: 4px 0 2px;}}
  .v-act {{text-align: center;}}
  .v-circle {{width: 54px; height: 54px; border-radius: 50%; margin: 0 auto 6px;
             display: flex; align-items: center; justify-content: center;
             font-size: 1.35rem; color: #fff; box-shadow: {SHADOW};}}
  .v-act .lbl {{font-size: .68rem; font-weight: 700; color: {INK};
               line-height: 1.18;}}

  /* ---- transaction rows ---- */
  .v-row {{display: flex; align-items: flex-start; gap: 12px; padding: 11px 0;
          border-bottom: 1px solid {LINE};}}
  .v-row:last-child {{border-bottom: none;}}
  .v-avatar {{width: 42px; height: 42px; border-radius: 50%; flex: 0 0 42px;
             display: flex; align-items: center; justify-content: center;
             font-weight: 800; color: #fff; font-size: 1rem;}}
  .v-name {{font-size: .88rem; font-weight: 700; color: {INK};}}
  .v-date {{font-size: .72rem; color: {SOFT};}}
  .v-split {{font-size: .68rem; color: {SOFT}; margin-top: 3px; line-height: 1.45;}}
  .v-amt {{margin-left: auto; font-size: .92rem; font-weight: 800; white-space: nowrap;}}
  .v-day {{font-size: .72rem; font-weight: 800; letter-spacing: .05em;
          text-transform: uppercase; color: {SOFT}; margin: 14px 0 2px;}}

  /* ---- profile / misc ---- */
  .v-profile {{display: flex; align-items: center; gap: 14px;}}
  .v-bigav {{width: 64px; height: 64px; border-radius: 50%; flex: 0 0 64px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.5rem; font-weight: 800; color: #fff;}}
  .v-kv {{display: flex; justify-content: space-between; gap: 12px;
         padding: 9px 0; border-bottom: 1px solid {LINE}; font-size: .86rem;}}
  .v-kv:last-child {{border-bottom: none;}}
  .v-kv .k {{color: {SOFT};}}
  .v-kv .val {{color: {INK}; font-weight: 700; text-align: right;}}

  /* ---- our own buttons stay on-brand ---- */
  .stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {{
      background: {BLUE}; border-color: {BLUE}; color: #fff; font-weight: 700;
      border-radius: 999px;}}
  .stButton > button[kind="primary"]:hover,
  .stFormSubmitButton > button[kind="primary"]:hover {{
      background: #1765CC; border-color: #1765CC;}}
  .stFormSubmitButton > button {{border-radius: 999px;}}
  /* ---- round icon buttons: big coloured emoji button, no chrome ---- */
  [class*="st-key-ra_"] button {{
      width: 54px !important; height: 54px !important;
      min-height: 54px !important; padding: 0 !important;
      border-radius: 50% !important; border: none !important;
      font-size: 1.35rem !important; line-height: 1 !important;
      box-shadow: {SHADOW} !important; margin: 0 auto;}}
  [class*="st-key-ra_"] button kbd, [class*="st-key-ra_"] button p {{
      font-size: 1.35rem !important; margin: 0 !important;}}
  [class*="st-key-ra_"] [data-testid="stButton"] {{display: flex; justify-content: center;}}
  .st-key-ra_bal button {{background: {GREEN} !important;}}
  .st-key-ra_send button {{background: {BLUE} !important;}}
  .st-key-ra_hist button {{background: {YELLOW} !important;}}
  .st-key-ra_vault button {{background: {PURPLE} !important;}}
  [class*="st-key-ra_"] button:hover {{filter: brightness(1.08);}}
  .v-act-lbl {{text-align: center; font-size: .66rem; font-weight: 700;
               color: {INK}; line-height: 1.18; margin-top: 2px;}}

  /* captions sit quietly in grey instead of Streamlit's link blue */
  [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {{
      color: {SOFT} !important;}}
  [data-testid="stCaptionContainer"] b, [data-testid="stCaptionContainer"] strong {{
      color: {INK} !important; font-weight: 700;}}
  /* passcode boxes: no stray dots when empty */
  input[type="password"] {{letter-spacing: .18em;}}

  /* ---- feature cards ---- */
  .v-feat {{background: {CARD2}; border-radius: 18px; padding: 16px;
           text-align: center; height: 100%;}}
  .v-feat .ico {{font-size: 1.6rem;}}
  .v-feat .t {{font-weight: 800; font-size: .88rem; color: {INK}; margin-top: 6px;}}
  .v-feat .d {{font-size: .74rem; color: {SOFT}; margin-top: 3px;}}

  /* ---- the 4 action buttons must stay in one row, even on a phone ----
     Streamlit stacks sibling columns below ~640px, so pin the row itself. */
  [data-testid="stHorizontalBlock"]:has([class*="st-key-ra_"]) {{
      display: flex !important; flex-wrap: nowrap !important;
      gap: 4px !important; align-items: stretch !important;}}
  [data-testid="stHorizontalBlock"]:has([class*="st-key-ra_"])
      > [data-testid="stColumn"] {{
      flex: 1 1 0 !important; width: auto !important; min-width: 0 !important;}}
  [class*="st-key-ra_"] {{display: block !important; height: 54px !important;
                        min-height: 54px !important;}}
  [class*="st-key-ra_"] [data-testid="stButton"] {{
      height: 54px !important; min-height: 54px !important;
      display: flex !important; justify-content: center !important;}}
  [class*="st-key-ra_"] [data-testid="stElementContainer"] {{
      height: 54px !important; min-height: 54px !important;}}
  [class*="st-key-ra_"] button {{
      width: 54px !important; height: 54px !important;
      min-height: 54px !important; font-size: 1.35rem !important;}}
  @media (max-width: 480px) {{
    [class*="st-key-ra_"], [class*="st-key-ra_"] [data-testid="stButton"],
    [class*="st-key-ra_"] [data-testid="stElementContainer"] {{
        height: 44px !important; min-height: 44px !important;}}
    [class*="st-key-ra_"] button {{
        width: 44px !important; height: 44px !important;
        min-height: 44px !important; font-size: 1.1rem !important;}}
    [class*="st-key-ra_"] button p {{font-size: 1.1rem !important;}}
    .v-act-lbl {{font-size: .56rem;}}
  }}
  @media (max-width: 480px) {{
    .block-container {{padding-left: .9rem; padding-right: .9rem;}}
    .v-hero {{font-size: 1.95rem;}}
    .v-circle {{width: 46px; height: 46px; font-size: 1.15rem;}}
    .v-act .lbl {{font-size: .6rem;}}
    .v-card {{padding: 16px; border-radius: 18px;}}
    .v-split {{font-size: .64rem;}}
  }}
</style>
""", unsafe_allow_html=True)


# ================================================================ 2. helpers
def stretch():
    """Widgets fill the column (new Streamlit renamed this kwarg)."""
    sig = inspect.signature(st.plotly_chart).parameters
    return {"width": "stretch"} if "width" in sig else {"use_container_width": True}


def rupees(x):
    """48250 -> '₹48,250' ; 1200.5 -> '₹1,200.50'"""
    x = round(float(x), 2)
    return f"₹{x:,.0f}" if x.is_integer() else f"₹{x:,.2f}"


def logo(size=46):
    """Original SVG vault/shield mark: a shield with a keyhole."""
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 48 48" fill="none"
         style="display:block;flex:0 0 auto;overflow:visible"
         xmlns="http://www.w3.org/2000/svg" aria-label="Self Healing Vault logo">
      <defs>
        <linearGradient id="vgrad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="{BLUE}"/>
          <stop offset="55%" stop-color="{PURPLE}"/>
          <stop offset="100%" stop-color="{GREEN}"/>
        </linearGradient>
      </defs>
      <path d="M24 3.5 6.5 9.4v13.9c0 9.6 6.9 17.2 17.5 21.2 10.6-4 17.5-11.6 17.5-21.2V9.4L24 3.5Z"
            fill="url(#vgrad)"/>
      <circle cx="24" cy="20.5" r="5.1" fill="#fff"/>
      <path d="M21.7 23.5h4.6l1.5 8.2h-7.6l1.5-8.2Z" fill="#fff"/>
    </svg>"""


def head():
    """App header: logo + name + tagline."""
    st.markdown(f"""<div class="vault-head">
        <div class="mark">{logo(40)}</div>
        <div class="txt"><div class="name">Self Healing Vault</div>
             <div class="tag">Your money, quietly protected</div></div>
    </div>""", unsafe_allow_html=True)


def avatar_letter(name):
    """First letter of a name, for the round avatar."""
    return (re.sub(r"[^A-Za-z]", "", name) or "?")[0].upper()


def spare_change(amount, step=10):
    """Extra rupees needed to round UP to the next multiple of `step`.

    73 -> 2 (step 5)   73 -> 7 (step 10)   90 -> 0 (step 10)
    """
    return round((step - amount % step) % step, 2)


def txn_row(r):
    """One transaction line: avatar, name, date, the sent/spare/total split."""
    sign = "+" if r.Dir == "in" else "−"
    col = GREEN if r.Dir == "in" else RED
    avatar_col = BLUE if r.Dir == "in" else PURPLE

    if r.Kind == "vault":
        split = f'<div class="v-split">{r.Note}</div>'
    elif r.Dir == "in":
        split = f'<div class="v-split">Received {rupees(r.Amount)}</div>'
    elif float(r.Spare) > 0:
        # Sent ₹73 • Spare ₹2 (green) • Total debited ₹75
        split = (f'<div class="v-split">Sent {rupees(r.Amount)}'
                 f' <span style="color:{VGREEN};font-weight:800">• Spare '
                 f'{rupees(r.Spare)}</span>'
                 f' • Total debited {rupees(r.Amount + r.Spare)}</div>')
    else:
        split = f'<div class="v-split">Sent {rupees(r.Amount)} • No round-up</div>'

    return f"""<div class="v-row">
        <div class="v-avatar" style="background:{avatar_col}">{avatar_letter(r.Name)}</div>
        <div><div class="v-name">{r.Name}</div>
             <div class="v-date">{r.DateStr} · {'Received' if r.Dir == 'in' else 'Sent'}</div>
             {split}</div>
        <div class="v-amt" style="color:{col}">{sign}{rupees(r.Amount)}</div>
    </div>"""


def gate(icon, title, text):
    """The little 'locked' card shown above a passcode box."""
    st.markdown(f"""<div class="v-gate">
        <div class="ico">{icon}</div>
        <div class="t">{title}</div>
        <div class="d">{text}</div>
    </div>""", unsafe_allow_html=True)


def ask_passcode(section, icon, title, text):
    """Passcode box for one section.

    Returns True once that section is unlocked for this session.
    """
    if st.session_state[f"u_{section}"]:
        return True

    gate(icon, title, text)
    # clear the box before the widget is drawn (Streamlit forbids it afterwards)
    if st.session_state.pop(f"wipe_{section}", False):
        st.session_state[f"code_{section}"] = ""
    code = st.text_input("Passcode", type="password", placeholder="••••",
                         max_chars=4, key=f"code_{section}",
                         label_visibility="collapsed")
    if st.button("Unlock", type="primary", key=f"unlock_{section}", **stretch()):
        if code == PASSCODE:
            st.session_state[f"u_{section}"] = True
            st.session_state[f"wipe_{section}"] = True    # wiped on the next run
            st.session_state.flash = f"{title} unlocked 🔓"
            st.rerun()
        else:
            st.error("❌ Wrong passcode. Try again.")
    st.caption("Demo passcode: **0000**")
    return False


# ================================================================ 3. sample data + memory
ss = st.session_state

# ---- what the sidebar looks like before anyone unlocks anything
ss.setdefault("balance", 48250.0)     # bank account balance (hidden until unlocked)
ss.setdefault("vault", 120.0)         # round-off vault balance
ss.setdefault("roundup_step", 10)     # round up to the nearest ₹5 or ₹10
ss.setdefault("history", [])          # transfers + round-offs + vault actions
ss.setdefault("sips", [])             # demo SIPs
ss.setdefault("rd", [])               # demo recurring deposits
ss.setdefault("thanks", False)        # contact form submitted
ss.setdefault("show_account", False)  # reveal the account number?
ss.setdefault("vault_open", False)     # are the vault action tabs expanded?
ss.setdefault("show_history", False)  # did the History button get tapped?

# ---- one key per locked section, so each can be opened on its own
ss.setdefault("u_balance", False)     # Check balance
ss.setdefault("u_transfer", False)    # Bank transfer
ss.setdefault("u_vault", False)       # Vault (SIP / RD / transfer)
ss.setdefault("u_profile", False)     # Personal Details page

TODAY = dt.date.today()

# Sample bank transactions: (name, days ago, amount, direction, spare)
BASE_TXN = [
    ("Aarav Mehta", 0, 2500, "in", 0),
    ("Priya Sharma", 2, 1200, "out", 0),
    ("Zomato", 4, 482, "out", 8),
    ("Neha Kulkarni", 6, 3500, "in", 0),
    ("Rahul Verma", 9, 793, "out", 7),
    ("Salary · Nimbus Tech", 12, 15000, "in", 0),
    ("Metro Recharge", 15, 205, "out", 5),
    ("Ananya Iyer", 18, 2500, "in", 0),
    ("Blinkit", 21, 636, "out", 4),
    ("Karan Shah", 24, 1200, "out", 0),
    ("Electricity Board", 27, 1874, "out", 6),
    ("Café Coffee Day", 29, 448, "out", 2),
]

# Every sample round-up is also a vault deposit, so the history adds up.
SAMPLE_VAULT = [(name, days, spare) for name, days, _amt, dirn, spare in BASE_TXN
                if spare > 0]


def base_history():
    """Turn the sample lists above into dated history rows.

    Three kinds of row: received money, sent money, and vault deposits.
    """
    rows = []
    for name, days, amt, dirn, spare in BASE_TXN:
        rows.append({"Date": TODAY - dt.timedelta(days=days), "Name": name,
                     "Kind": "txn", "Dir": dirn, "Amount": float(amt),
                     "Spare": float(spare), "Note": "",
                     "DateStr": (TODAY - dt.timedelta(days=days)).strftime("%d %b %Y")})
    for name, days, spare in SAMPLE_VAULT:
        rows.append({"Date": TODAY - dt.timedelta(days=days), "Name": "Vault deposit 🛡️",
                     "Kind": "vault", "Dir": "in", "Amount": float(spare),
                     "Spare": 0.0, "Note": f"Round-off from {name}",
                     "DateStr": (TODAY - dt.timedelta(days=days)).strftime("%d %b %Y")})
    return rows


ss.setdefault("base_history", base_history())

PROFILE = {
    "Full name": "Aanya R. Kulkarni",
    "Account number": "50100 2847 3321",
    "IFSC code": "VLTB0000123",
    "Branch": "Bandra West, Mumbai",
    "Account type": "Savings (Demo)",
    "Phone": "+91 90000 12345",
    "Email": "aanya.demo@example.com",
}

# ================================================================ 4. toasts
flash = ss.pop("flash", None)
party = ss.pop("party", False)
if flash:
    st.toast(flash, icon="✅")
if party:
    st.balloons()

# ================================================================ 5. sidebar
with st.sidebar:
    st.markdown("**🛡️ Self Healing Vault**")
    st.caption("Demo banking · sample data")
    page = st.radio("Pages", ["🏠 Home", "👤 Personal Details",
                              "ℹ️ About Us", "🎧 Customer Care"],
                    label_visibility="collapsed")
    st.divider()
    if st.button("🔒 Lock again", **stretch()):
        for k in ("u_balance", "u_transfer", "u_vault", "u_profile"):
            ss[k] = False
        ss.show_account = False
        ss.vault_open = False
        ss.flash = "Vault locked again 🔒"
        st.rerun()
    st.caption("Demo only · no real payments")

head()

# ================================================================ 6. transaction history (no passcode)
def all_history():
    """Sample rows + everything the user did this session, newest first."""
    rows = ss.base_history + ss.history
    return sorted(rows, key=lambda r: r["Date"], reverse=True)


def show_history():
    st.markdown('<div class="v-h">🧾 Transaction history</div>', unsafe_allow_html=True)
    st.caption("No passcode needed — history is always open. Pick a date range below.")

    started = TODAY - dt.timedelta(days=29)      # sample data covers the last 30 days
    c1, c2 = st.columns(2)
    d_from = c1.date_input("From", value=started, min_value=started, max_value=TODAY,
                           key="h_from", format="DD/MM/YYYY")
    d_to = c2.date_input("To", value=TODAY, min_value=started, max_value=TODAY,
                         key="h_to", format="DD/MM/YYYY")

    if d_from > d_to:
        st.error("❌ The 'From' date is after the 'To' date. Swap them to see results.")
        return

    rows = [r for r in all_history() if d_from <= r["Date"] <= d_to]

    if not rows:
        st.info("🗓️ No transactions on these dates.")
        return

    # ---- summary for the selected range ----
    sent = sum(r["Amount"] for r in rows if r["Kind"] == "txn" and r["Dir"] == "out")
    spare = sum(r["Spare"] for r in rows if r["Kind"] == "txn")
    st.markdown(f"""<div class="v-est">
        <div class="v-label">Summary · {d_from.strftime('%d %b')} – {d_to.strftime('%d %b')}</div>
        <div style="display:flex;gap:18px;flex-wrap:wrap;margin-top:8px">
          <div><div class="v-sub">Total sent</div>
               <div style="font-weight:800;color:{RED}">{rupees(sent)}</div></div>
          <div><div class="v-sub">Spare change saved</div>
               <div style="font-weight:800;color:{VGREEN}">{rupees(spare)}</div></div>
          <div><div class="v-sub">Transactions</div>
               <div style="font-weight:800;color:{INK}">{len(rows)}</div></div>
        </div></div>""", unsafe_allow_html=True)

    # ---- grouped by day ----
    box = '<div class="v-card" style="padding:6px 18px">'
    day_now = None
    for r in rows:
        if r["Date"] != day_now:
            day_now = r["Date"]
            label = ("Today · " if day_now == TODAY else "") + day_now.strftime("%d %b %Y")
            box += f'<div class="v-day">{label}</div>'
        box += txn_row(pd.Series(r))
    st.markdown(box + "</div>", unsafe_allow_html=True)


# ================================================================ 7. the vault (SIP / RD / transfer)
def rd_interest(instalment, months, rate=RD_RATE):
    """Interest on a monthly deposit: instalment × n(n+1)/2 × rate / 12 / 100.

    The first instalment earns for `months` months, the last for one.
    """
    return round(instalment * months * (months + 1) / 2 * (rate / 12 / 100), 2)


def add_row(name, amount, direction="out", spare=0.0, note="", kind="txn"):
    """Append one dated row to the session history."""
    ss.history.append({"Date": TODAY, "Name": name, "Kind": kind, "Dir": direction,
                       "Amount": float(amount), "Spare": float(spare), "Note": note,
                       "DateStr": TODAY.strftime("%d %b %Y")})


def show_vault():
    """The three vault tabs: SIP, recurring deposit, transfer to bank."""
    st.caption("Demo only, no real investing or deposits.")

    tab_sip, tab_rd, tab_bank = st.tabs(["📈 SIP", "🔁 Recurring Deposit",
                                         "🏦 Transfer to bank"])

    # ------------------------------------------------------------ A. SIP
    with tab_sip:
        st.markdown(f'<div class="v-label">Vault balance</div>'
                    f'<div class="v-vault-amt">{rupees(ss.vault)}</div>',
                    unsafe_allow_html=True)
        fund = st.selectbox("Choose a sample fund",
                            ["Nimbus Index Fund", "Balanced Advantage Fund",
                             "Gold Savings Fund"], key="sip_fund")
        amount = st.number_input("Amount (₹)", 0.0, 200000.0, 0.0, step=100.0,
                                 key="sip_amt")
        freq = st.radio("How often?", ["One-time", "Monthly"], horizontal=True,
                        key="sip_freq")

        if st.button("Invest in SIP", type="primary", key="sip_go", **stretch()):
            if amount <= 0:
                st.error("❌ Enter an amount above ₹0.")
            elif amount > ss.vault:
                st.error(f"❌ That is more than your vault ({rupees(ss.vault)}).")
            else:
                ss.vault -= amount
                add_row(f"SIP · {fund}", amount, note=f"{freq} · demo investment")
                ss.sips.append({"Fund": fund, "Amount": float(amount), "Freq": freq,
                                "Date": TODAY})
                ss.flash = f"{rupees(amount)} invested in {fund} (demo)"
                st.rerun()

        if ss.sips:
            st.markdown('<div class="v-h">My SIPs</div>', unsafe_allow_html=True)
            for s in reversed(ss.sips):
                st.markdown(f"""<div class="v-soft" style="margin-bottom:8px">
                    <div style="font-weight:800;color:{INK}">{s['Fund']}</div>
                    <div class="v-sub">{s['Freq']} · {rupees(s['Amount'])} ·
                      started {s['Date'].strftime('%d %b %Y')}</div></div>""",
                            unsafe_allow_html=True)

    # ------------------------------------------------------------ B. recurring deposit
    with tab_rd:
        if ss.vault <= 0:
            st.info("Your vault is empty — uncheck nothing, just send a transfer "
                    "with round-off on to refill it.")

        instalment = st.number_input("Monthly instalment (₹)", 0.0, 200000.0, 0.0,
                                     step=100.0, key="rd_amt")
        months = st.selectbox("Tenure", [6, 12, 24], index=1, key="rd_months",
                              format_func=lambda m: f"{m} months")

        # live green estimate card
        deposit = instalment * months
        interest = rd_interest(instalment, months)
        maturity = deposit + interest
        st.markdown(f"""<div class="v-est">
            <div class="v-label">Estimated at {RD_RATE}% per year (demo)</div>
            <div class="n">{rupees(maturity)}</div>
            <div class="v-sub">Total deposit {rupees(deposit)} ·
              estimated interest <span style="color:{VGREEN};font-weight:800">
              {rupees(interest)}</span></div>
        </div>""", unsafe_allow_html=True)

        if st.button("Start RD", type="primary", key="rd_go", **stretch()):
            if instalment <= 0:
                st.error("❌ Enter an instalment above ₹0.")
            elif instalment > ss.vault:
                st.error(f"❌ That is more than your vault ({rupees(ss.vault)}).")
            else:
                ss.vault -= instalment
                add_row(f"RD · first instalment", instalment,
                        note=f"{months}-month RD, instalment 1 of {months}")
                ss.rd.append({"Instalment": float(instalment), "Months": months,
                              "Paid": 1, "Start": TODAY,
                              "Maturity": maturity, "Rate": RD_RATE})
                ss.flash = f"RD started — {rupees(instalment)} taken from your vault"
                st.rerun()

        if ss.rd:
            st.markdown('<div class="v-h">My recurring deposits</div>',
                        unsafe_allow_html=True)
            for i, rd in enumerate(ss.rd):
                paid, months_ = rd["Paid"], rd["Months"]
                pct = paid / months_ * 100
                done = paid >= months_
                st.markdown(f"""<div class="v-soft" style="margin-bottom:10px">
                    <div style="display:flex;justify-content:space-between">
                      <div style="font-weight:800;color:{INK}">
                        {rupees(rd['Instalment'])} × {months_} months</div>
                      <div class="v-sub">{rd['Rate']}% p.a.</div></div>
                    <div class="v-bar"><div class="v-bar-fill"
                         style="width:{pct:.0f}%"></div></div>
                    <div class="v-sub">{paid} of {months_} paid · started
                      {rd['Start'].strftime('%d %b %Y')} · maturity
                      <b style="color:{VGREEN}">{rupees(rd['Maturity'])}</b></div>
                </div>""", unsafe_allow_html=True)

                if done:
                    st.success("RD completed 🎉")
                    if st.button(f"Move {rupees(rd['Maturity'])} to bank account",
                                 key=f"rd_move_{i}", **stretch()):
                        ss.balance += rd["Maturity"]
                        add_row("RD maturity", rd["Maturity"], direction="in",
                                note="Recurring deposit completed")
                        ss.rd.pop(i)
                        ss.flash = f"{rupees(rd['Maturity'])} moved to your bank account"
                        ss.party = True
                        st.rerun()
                else:
                    if st.button(f"Pay next instalment ({rupees(rd['Instalment'])})",
                                 key=f"rd_pay_{i}", **stretch()):
                        if rd["Instalment"] > ss.vault:
                            st.error("❌ Not enough in vault.")
                        else:
                            ss.vault -= rd["Instalment"]
                            rd["Paid"] += 1
                            add_row("RD · instalment", rd["Instalment"],
                                    note=f"Instalment {rd['Paid']} of {rd['Months']}")
                            ss.flash = f"Instalment {rd['Paid']} of {rd['Months']} paid"
                            st.rerun()
                    if rd["Instalment"] > ss.vault:
                        st.caption(f"🔴 Not enough in vault — you have "
                                   f"{rupees(ss.vault)}.")

    # ------------------------------------------------------------ C. transfer to bank
    with tab_bank:
        st.markdown(f'<div class="v-label">Vault balance</div>'
                    f'<div class="v-vault-amt">{rupees(ss.vault)}</div>',
                    unsafe_allow_html=True)
        amount = st.number_input("Move to bank account (₹)", 0.0, 200000.0, 0.0,
                                 step=100.0, key="vbank_amt")
        b1, b2 = st.columns(2)
        move_all = b1.button("Move all", key="vbank_all", **stretch())
        confirm = b2.button("Confirm transfer", type="primary", key="vbank_go",
                            **stretch())

        def move_to_bank(target):
            """Shared by Confirm and Move all."""
            ss.vault -= target
            ss.balance += target
            add_row("Vault → bank account", target, direction="in",
                    note="Moved from vault to bank")
            ss.flash = f"{rupees(target)} moved from vault to your bank account"
            ss.party = True
            st.rerun()

        if move_all:
            if ss.vault <= 0:
                st.error("❌ Your vault is empty — nothing to move.")
            else:
                move_to_bank(ss.vault)
        elif confirm:
            if amount <= 0:
                st.error("❌ Enter an amount above ₹0.")
            elif amount > ss.vault:
                st.error(f"❌ That is more than your vault ({rupees(ss.vault)}).")
            else:
                move_to_bank(amount)


# ================================================================ 7b. the vault panel.
# Shown under the icon row only when session state `vault_open` is True.
# Streamlit has st.dialog, but it always draws in front of the whole page and
# needs widgets inside it to be wrapped in a function that cannot also render
# nested tabs and buttons reliably; an inline container matches "opens right
# below the icon row" better and keeps the history visible underneath.
def vault_panel():
    with st.container(key="vault_panel"):
        # ---- header row: title + the ✖ Close button
        t1, t2 = st.columns([3, 1])
        with t1:
            st.markdown('<div class="v-h" style="margin:6px 0 0">🛡️ Your vault</div>',
                        unsafe_allow_html=True)
        with t2:
            if st.button("✖ Close", key="vault_close", **stretch()):
                ss.vault_open = False
                st.rerun()

        # ---- passcode first, if this session has not opened the vault yet
        if not ss.u_vault:
            gate("🛡️", "Your vault is locked",
                 "Enter the passcode to open SIPs, deposits and transfers")
            if ss.pop("wipe_vault", False):
                ss.code_vault = ""
            code = st.text_input("Passcode", type="password", placeholder="••••",
                                 max_chars=4, key="code_vault",
                                 label_visibility="collapsed")
            if st.button("Unlock", type="primary", key="unlock_vault", **stretch()):
                if code == PASSCODE:
                    ss.u_vault = True
                    ss.wipe_vault = True          # wiped at the top of the next run
                    ss.flash = "Vault unlocked 🔓"
                    st.rerun()
                else:
                    st.error("❌ Wrong passcode. Try again.")
            st.caption("Demo passcode: **0000**")
            return

        # ---- big green card with the vault balance
        vault_pct = min(ss.vault / VAULT_TARGET * 100, 100)
        st.markdown(f"""<div class="v-vault">
            <div style="display:flex;justify-content:space-between;align-items:flex-start">
              <div>
                <div class="v-label">Round-off vault</div>
                <div class="v-vault-amt">{rupees(ss.vault)}</div>
                <div class="v-sub">{len([r for r in ss.history if r['Kind'] == 'vault'])}
                  round-ups saved</div>
              </div>
              <div style="font-size:1.8rem">🛡️</div>
            </div>
            <div class="v-bar"><div class="v-bar-fill" style="width:{vault_pct:.0f}%"></div></div>
            <div class="v-sub">{rupees(ss.vault)} of {rupees(VAULT_TARGET)} ·
              {vault_pct:.0f}%</div>
        </div>""", unsafe_allow_html=True)

        # ---- the three action tabs, each with its form and its list
        show_vault()


# ================================================================ 8. HOME
if page == "🏠 Home":

    # ---- action buttons: Check balance · Bank transfer · Transaction history · Vault
    def action(col, emoji, label, key, on_click):
        """One round icon button + its caption, Google Pay style."""
        with col:
            with st.container(key=f"ra_{key}"):
                st.button(emoji, key=f"go_{key}", on_click=on_click,
                          help=label)
            st.markdown(f'<div class="v-act-lbl">{label}</div>',
                        unsafe_allow_html=True)

    # these run *before* the page redraws, so the new state is already set
    def go_balance():
        ss.u_balance = True
        ss.flash = "Check balance unlocked 🔓"

    def go_transfer():
        ss.u_transfer = True

    def go_history():
        ss.show_history = True
        ss.flash = "Showing the transaction history"

    def go_vault():
        # only opens the panel — the panel itself asks for the passcode
        ss.vault_open = True

    a1, a2, a3, a4 = st.columns(4)
    action(a1, "💳", "Check balance", "bal", go_balance)
    action(a2, "📤", "Bank transfer", "send", go_transfer)
    action(a3, "🧾", "History", "hist", go_history)
    action(a4, "🛡️", "Vault", "vault", go_vault)

    # ---- the vault panel: sits right under the icon row, only when opened.
    # Everything below it (balance, transfer, history) simply moves down.
    if ss.vault_open:
        vault_panel()

    # ---- 1. CHECK BALANCE (needs the passcode) ----
    st.markdown('<div class="v-h">💳 Check balance</div>', unsafe_allow_html=True)
    if ask_passcode("balance", "💳", "Balance is locked",
                    "Enter the passcode to see your available balance"):
        st.markdown(f"""<div class="v-card">
            <div class="v-label">Available balance</div>
            <div class="v-hero">{rupees(ss.balance)}</div>
            <div class="v-sub">Aanya R. Kulkarni · A/c •••• 3321</div>
        </div>""", unsafe_allow_html=True)
        if st.button("🙈 Hide balance", key="hide_balance", **stretch()):
            ss.u_balance = False
            st.rerun()

        # small balance trend line (account balance only, no spending charts)
        bal = [52000, 49500, 51200, 50400, ss.balance]
        spark = go.Figure(go.Scatter(y=bal, mode="lines", line=dict(color=BLUE, width=3),
                                     fill="tozeroy", fillcolor="rgba(26,115,232,.14)"))
        spark.update_layout(height=110, margin=dict(l=0, r=0, t=0, b=0), showlegend=False,
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            xaxis=dict(visible=False), yaxis=dict(visible=False))
        st.plotly_chart(spark, config={"displayModeBar": False}, **stretch())

    # ---- 2. BANK TRANSFER (needs the passcode) ----
    st.markdown('<div class="v-h">📤 Bank transfer</div>', unsafe_allow_html=True)
    if ask_passcode("transfer", "📤", "Transfers are locked",
                    "Enter the passcode to send money"):
        # reset the fields before the widgets exist (Streamlit can't change a
        # widget key after the widget has been drawn)
        if ss.pop("clear_form", False):
            for k in ("t_name", "t_acc", "t_ifsc", "t_amount"):
                ss.pop(k, None)

        n1, n2 = st.columns(2)
        rec_name = n1.text_input("Recipient name", placeholder="e.g. Rohan Das",
                                 key="t_name")
        bank = n2.text_input("Bank name", placeholder="e.g. HDFC Bank", key="t_bank")
        a1, a2 = st.columns([1.4, 1])
        acc_no = a1.text_input("Account number", placeholder="9–18 digits",
                               max_chars=18, key="t_acc")
        ifsc = a2.text_input("IFSC code", placeholder="HDFC0001234", max_chars=11,
                             key="t_ifsc")
        amount = st.number_input("Amount (₹)", 1.0, 200000.0, step=1.0, key="t_amount")

        # round-up selector (default ₹10)
        ss.setdefault("step_pick", ss.roundup_step)
        ss.roundup_step = st.radio("Round up to nearest", [5, 10], horizontal=True,
                                   format_func=lambda v: f"₹{v}", key="step_pick")
        step = ss.roundup_step

        send = st.button("Send money", type="primary", key="send_go", **stretch())

        # ---- live breakdown, before pressing Send ----
        spare = spare_change(amount, step)
        total = amount + spare
        if spare > 0:
            split = (f'Sent {rupees(amount)} • <span style="color:{VGREEN};'
                     f'font-weight:800">Spare {rupees(spare)}</span>'
                     f' • Total debited {rupees(total)}')
        else:
            split = f'Sent {rupees(amount)} • No round-up • Total debited {rupees(total)}'
        st.markdown(f'<div class="v-soft" style="text-align:center;font-size:.84rem;'
                    f'color:{INK};margin-bottom:10px">{split}</div>',
                    unsafe_allow_html=True)

        if send:
            errors = []
            if not rec_name.strip():
                errors.append("recipient name")
            if not re.fullmatch(r"\d{9,18}", acc_no.replace(" ", "")):
                errors.append("a valid account number (9–18 digits)")
            if not re.fullmatch(r"[A-Za-z]{4}0[A-Za-z0-9]{6}", ifsc.strip()):
                errors.append("a valid IFSC code (e.g. HDFC0001234)")

            if total > ss.balance:                      # check the TOTAL, not just amount
                st.error(f"❌ Not enough balance. Sending {rupees(amount)} plus a "
                         f"{rupees(spare)} round-up needs {rupees(total)}, but you have "
                         f"{rupees(ss.balance)}.")
            elif errors:
                st.error("❌ Please check: " + ", ".join(errors) + ".")
            else:
                ss.balance -= total                     # debit amount + spare
                add_row(rec_name.strip(), amount, direction="out", spare=spare)
                if spare > 0:
                    ss.vault += spare                   # spare change joins the vault
                    add_row("Vault deposit 🛡️", spare, direction="in",
                            note=f"Round-off from {rec_name.strip()}", kind="vault")
                    ss.flash = f"{rupees(amount)} sent. {rupees(spare)} saved in your vault 🛡️"
                else:
                    ss.flash = f"{rupees(amount)} sent to {rec_name.strip()}"
                ss.party = True
                ss.clear_form = True
                st.rerun()
        st.caption("Demo transfer only — no money actually moves.")

    # ---- 3. TRANSACTION HISTORY (no passcode) ----
    show_history()


# ================================================================ 9. PERSONAL DETAILS (passcode)
elif page == "👤 Personal Details":
    st.markdown('<div class="v-h">👤 My personal details</div>', unsafe_allow_html=True)

    if not ss.u_profile:
        gate("👤", "Personal details are locked",
             "Enter the passcode to see your account information")
        if ss.pop("wipe_profile", False):
            ss.code_profile = ""
        code = st.text_input("Passcode", type="password", placeholder="••••",
                             max_chars=4, key="code_profile",
                             label_visibility="collapsed")
        if st.button("Unlock", type="primary", key="unlock_profile", **stretch()):
            if code == PASSCODE:
                ss.u_profile = True
                ss.wipe_profile = True
                ss.flash = "Personal details unlocked 🔓"
                st.rerun()
            else:
                st.error("❌ Wrong passcode. Try again.")
        st.caption("Demo passcode: **0000**")
    else:
        st.markdown(f"""<div class="v-card">
            <div class="v-profile">
              <div class="v-bigav" style="background:linear-gradient(135deg,{BLUE},{PURPLE})">
                AK</div>
              <div><div style="font-size:1.12rem;font-weight:800;color:{INK}">
                    Aanya R. Kulkarni</div>
                  <div class="v-sub">Savings account · verified ✅</div></div>
            </div></div>""", unsafe_allow_html=True)

        account_shown = "50100 2847 3321" if ss.show_account else "•••• •••• •••• 3321"
        st.markdown(f"""<div class="v-card">
            <div class="v-kv"><span class="k">Full name</span>
                 <span class="val">{PROFILE['Full name']}</span></div>
            <div class="v-kv"><span class="k">Account number</span>
                 <span class="val">{account_shown}</span></div>
            <div class="v-kv"><span class="k">IFSC code</span>
                 <span class="val">{PROFILE['IFSC code']}</span></div>
            <div class="v-kv"><span class="k">Branch</span>
                 <span class="val">{PROFILE['Branch']}</span></div>
            <div class="v-kv"><span class="k">Account type</span>
                 <span class="val">{PROFILE['Account type']}</span></div>
            <div class="v-kv"><span class="k">Phone</span>
                 <span class="val">{PROFILE['Phone']}</span></div>
            <div class="v-kv"><span class="k">Email</span>
                 <span class="val">{PROFILE['Email']}</span></div>
        </div>""", unsafe_allow_html=True)

        if st.button("🙈 Hide account number" if ss.show_account
                     else "👁️ Show account number", **stretch()):
            ss.show_account = not ss.show_account
            st.rerun()
        if st.button("🔒 Lock this page", **stretch()):
            ss.u_profile = False
            ss.show_account = False
            ss.flash = "Personal details locked 🔒"
            st.rerun()
        st.caption("All details above are fake sample data for this demo.")

# ================================================================ 10. ABOUT US
elif page == "ℹ️ About Us":
    st.markdown('<div class="v-h">ℹ️ About Self Healing Vault</div>',
                unsafe_allow_html=True)
    st.markdown(f"""<div class="v-card">
        <div style="font-size:1.02rem;color:{INK};line-height:1.55">
          Self Healing Vault is a friendly, no-fuss banking demo built for people
          who just want to know where their money is. Send a demo transfer, and the
          spare change from rounding it up slips into your vault automatically —
          then you decide whether it goes into a SIP, a recurring deposit, or back
          to your bank account.
        </div>
        <div class="v-sub" style="margin-top:10px">
          Transaction history stays open to everyone. Your balance, transfers,
          vault and personal details each ask for the passcode.</div>
    </div>""", unsafe_allow_html=True)

    feats = [("🛡️", "Secure", "Passcode on every private section", BLUE),
             ("🪙", "Round-off", "Spare change saved automatically", GREEN),
             ("⚡", "Quick", "Balances update instantly", YELLOW)]
    cols = st.columns(3)
    for c, (ico, t, d, _) in zip(cols, feats):
        with c:
            st.markdown(f"""<div class="v-feat">
                <div class="ico">{ico}</div>
                <div class="t">{t}</div>
                <div class="d">{d}</div></div>""", unsafe_allow_html=True)

    st.markdown(f"""<div class="v-card" style="margin-top:14px">
        <div class="v-label">Please note</div>
        <div class="v-sub" style="margin-top:6px">
          This is a college demo project. It uses sample data, has no real bank
          connection, and never moves real money. SIPs and deposits are pretend.</div>
    </div>""", unsafe_allow_html=True)

# ================================================================ 11. CUSTOMER CARE
else:
    st.markdown('<div class="v-h">🎧 Customer Care</div>', unsafe_allow_html=True)

    faqs = [("How do I send money?",
             "Tap 📤 Bank transfer on Home, enter the passcode, then fill in the "
             "recipient, account number, IFSC and amount. It is a demo — nothing "
             "leaves the app."),
            ("Why do you ask for a passcode again?",
             "Every private section (balance, transfer, vault, personal details) "
             "has its own lock. Transaction history and these help pages stay open."),
            ("Why was my transfer rejected?",
             "You can only send what you have. The check includes the round-up, so "
             "₹99 with a ₹1 round-up needs ₹100 in the bank."),
            ("Where does the spare change go?",
             "Straight into your vault. Open 🛡️ Vault to invest it in a demo SIP, "
             "start a recurring deposit, or move it back to your bank account."),
            ("Is my passcode stored anywhere?",
             "No. It lives in this app's session memory only, and the demo code is "
             "0000."),
            ("Can I use this with a real bank account?",
             "No. Every account, name and transaction here is fake sample data.")]

    for q, a in faqs:
        with st.expander(f"❓ {q}"):
            st.write(a)

    st.markdown('<div class="v-h">✉️ Contact us</div>', unsafe_allow_html=True)
    with st.form("contact"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Your name", placeholder="Aanya")
        issue = c2.selectbox("Issue type", ["Transfer problem", "Login / passcode",
                                            "Vault or SIP", "Something else"])
        msg = st.text_area("Message", placeholder="Tell us what happened…", height=90)
        sent_help = st.form_submit_button("Submit", type="primary", **stretch())
    if sent_help:
        if name.strip() and msg.strip():
            ss.thanks = True
            ss.flash = "Message sent — thank you!"
        else:
            st.error("❌ Please add your name and a short message.")

    if ss.thanks:
        st.success(f"✅ Thank you{' ' + name if name.strip() else ''}! Our demo team "
                   "will get back to you (well, pretend to).")

    st.markdown(f"""<div class="v-soft" style="margin-top:6px">
        <div class="v-label">Support</div>
        <div class="v-kv"><span class="k">Phone</span>
             <span class="val">1800 000 0000 (toll-free demo)</span></div>
        <div class="v-kv"><span class="k">Email</span>
             <span class="val">help@selfhealingvault.demo</span></div>
        <div class="v-kv"><span class="k">Hours</span>
             <span class="val">Mon–Sat · 9am to 7pm IST</span></div>
    </div>""", unsafe_allow_html=True)
