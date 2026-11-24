"""Self Healing Vault — a small demo banking app. Sample data only, no real payments."""

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
PASSCODE = "0000"          # the demo passcode


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
  .v-amount {{font-size: 1.02rem; font-weight: 700;}}
  .v-red {{color: {RED};}} .v-green {{color: {GREEN};}}

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
  .v-row {{display: flex; align-items: center; gap: 12px; padding: 11px 0;
          border-bottom: 1px solid {LINE};}}
  .v-row:last-child {{border-bottom: none;}}
  .v-avatar {{width: 42px; height: 42px; border-radius: 50%; flex: 0 0 42px;
             display: flex; align-items: center; justify-content: center;
             font-weight: 800; color: #fff; font-size: 1rem;}}
  .v-name {{font-size: .88rem; font-weight: 700; color: {INK};}}
  .v-date {{font-size: .72rem; color: {SOFT};}}
  .v-amt {{margin-left: auto; font-size: .92rem; font-weight: 800;}}

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

  /* ---- feature cards ---- */
  .v-feat {{background: {CARD2}; border-radius: 18px; padding: 16px;
           text-align: center; height: 100%;}}
  .v-feat .ico {{font-size: 1.6rem;}}
  .v-feat .t {{font-weight: 800; font-size: .88rem; color: {INK}; margin-top: 6px;}}
  .v-feat .d {{font-size: .74rem; color: {SOFT}; margin-top: 3px;}}

  /* ---- lock screen ---- */
  .v-lock {{background: {CARD}; border: 1px solid {LINE}; border-radius: 26px;
           padding: 34px 26px 26px; text-align: center; box-shadow: {SHADOW};
           margin-top: 8vh;}}
  .v-lock .big {{font-size: 3rem; line-height: 1;}}
  .v-lock h2 {{margin: 12px 0 4px; font-size: 1.35rem; color: {INK};}}
  .v-lock p {{margin: 0; color: {SOFT}; font-size: .86rem;}}

  /* ---- phones ---- */
  @media (max-width: 480px) {{
    .block-container {{padding-left: .9rem; padding-right: .9rem;}}
    .v-hero {{font-size: 1.95rem;}}
    .v-circle {{width: 46px; height: 46px; font-size: 1.15rem;}}
    .v-act .lbl {{font-size: .6rem;}}
    .v-card {{padding: 16px; border-radius: 18px;}}
  }}
</style>
""", unsafe_allow_html=True)


# ================================================================ 2. helpers
def stretch():
    """Charts fill the column (new Streamlit renamed this kwarg)."""
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


def actions(items):
    """Row of round icon buttons, Google Pay style."""
    cells = "".join(
        f'<div class="v-act"><div class="v-circle" style="background:{c}">{e}</div>'
        f'<div class="lbl">{t}</div></div>' for e, t, c in items)
    st.markdown(f'<div class="v-actions">{cells}</div>', unsafe_allow_html=True)


def avatar_letter(name):
    """First letter of a name, for the round avatar."""
    return (re.sub(r"[^A-Za-z]", "", name) or "?")[0].upper()


# ================================================================ 3. sample data + memory
ss = st.session_state

ss.setdefault("unlocked", False)
ss.setdefault("balance", 48250.0)
ss.setdefault("show_balance", True)
ss.setdefault("show_account", False)
ss.setdefault("sent", [])          # transfers made in this session
ss.setdefault("thanks", False)     # contact form submitted

# Sample transactions: (name, days ago, amount, direction)
BASE_TXN = [
    ("Aarav Mehta", 0, 2500, "in"),
    ("Priya Sharma", 1, 1200, "out"),
    ("Zomato", 2, 480, "out"),
    ("Neha Kulkarni", 3, 3500, "in"),
    ("Rahul Verma", 5, 800, "out"),
    ("Salary · Nimbus Tech", 7, 15000, "in"),
    ("Metro Recharge", 9, 200, "out"),
]

PROFILE = {
    "Full name": "Aanya R. Kulkarni",
    "Account number": "50100 2847 3321",
    "IFSC code": "VLTB0000123",
    "Branch": "Bandra West, Mumbai",
    "Account type": "Savings (Demo)",
    "Phone": "+91 90000 12345",
    "Email": "aanya.demo@example.com",
}

if not ss.unlocked:
    # ---------------- LOCK SCREEN ----------------
    st.markdown(f"""<div class="v-lock">
        <div class="big">{logo(66)}</div>
        <h2>Self Healing Vault</h2>
        <p>Enter your passcode to unlock</p>
    </div>""", unsafe_allow_html=True)

    with st.form("unlock"):
        code = st.text_input("Passcode", type="password", placeholder="••••",
                             max_chars=4, label_visibility="collapsed")
        ok = st.form_submit_button("Unlock", type="primary", **stretch())
    if ok:
        if code == PASSCODE:
            ss.unlocked = True
            ss.flash, ss.party = "🔓 Vault unlocked", True
            st.rerun()
        else:
            st.error("❌ Wrong passcode. Try again.")
    st.caption("Demo passcode: **0000**")

else:
    # ---------------- SIDEBAR (only after unlocking) ----------------
    with st.sidebar:
        # simple text brand (the sidebar doesn't need the SVG mark)
        st.markdown("**🛡️ Self Healing Vault**")
        st.caption("Demo banking · sample data")
        page = st.radio("Pages", ["🏠 Home", "👤 Personal Details",
                                  "ℹ️ About Us", "🎧 Customer Care"],
                        label_visibility="collapsed")
        st.divider()
        if st.button("🔒 Lock", **stretch()):
            ss.unlocked = False
            ss.flash = "Vault locked 🔒"
            st.rerun()
        st.caption("Demo only · no real payments")

    # toasts / balloons queued by the previous click
    flash = ss.pop("flash", None)
    party = ss.pop("party", False)
    if flash:
        st.toast(flash, icon="✅")
    if party:
        st.balloons()

    head()

    # transactions dataframe: sample rows + transfers made this session
    # (both are tuples, so pandas gets one clean shape)
    sent_rows = [(r["Name"], r["DaysAgo"], r["Amount"], r["Dir"]) for r in ss.sent]
    txn = pd.DataFrame(BASE_TXN + sent_rows, columns=["Name", "DaysAgo", "Amount", "Dir"])
    txn["DaysAgo"] = pd.to_numeric(txn["DaysAgo"]).astype(int)
    txn["Amount"] = pd.to_numeric(txn["Amount"]).astype(float)
    txn["Date"] = (pd.Timestamp.today().normalize()
                   - pd.to_timedelta(txn["DaysAgo"], unit="D")).dt.strftime("%d %b")

    # ================================================================ HOME
    if page == "🏠 Home":
        masked = not ss.show_balance
        shown = "₹ ••••••" if masked else rupees(ss.balance)

        st.markdown(f"""<div class="v-card">
            <div style="display:flex;justify-content:space-between;align-items:center">
              <div>
                <div class="v-label">Available balance</div>
                <div class="v-hero">{shown}</div>
                <div class="v-sub">Aanya R. Kulkarni · A/c •••• 3321</div>
              </div>
              <div style="font-size:1.9rem">🛡️</div>
            </div></div>""", unsafe_allow_html=True)

        # eye toggle + reset balance
        e1, e2 = st.columns(2)
        with e1:
            if st.button("🙈 Hide balance" if ss.show_balance else "👁️ Show balance",
                         **stretch()):
                ss.show_balance = not ss.show_balance
                st.rerun()
        with e2:
            if st.button("💳 Check balance", **stretch()):
                ss.flash = f"Balance is {rupees(ss.balance)}"
                st.rerun()

        # round icon row
        actions([("📤", "Send to bank", BLUE), ("💳", "Check balance", GREEN),
                 ("🧾", "History", YELLOW), ("🔳", "Scan QR", RED)])

        with st.expander("🧾 View history"):
            for _, r in txn.iterrows():
                sign = "+" if r.Dir == "in" else "−"
                col = GREEN if r.Dir == "in" else RED
                st.markdown(f"""<div class="v-row">
                    <div class="v-avatar" style="background:{BLUE if r.Dir=='in' else PURPLE}">
                      {avatar_letter(r.Name)}</div>
                    <div><div class="v-name">{r.Name}</div>
                         <div class="v-date">{r.Date} · {'Received' if r.Dir=='in' else 'Sent'}</div></div>
                    <div class="v-amt" style="color:{col}">{sign}{rupees(r.Amount)}</div>
                </div>""", unsafe_allow_html=True)
            st.caption("🔳 Scan QR is a demo button — nothing is scanned.")

        # ---- bank transfer
        st.markdown('<div class="v-h">📤 Send to bank</div>', unsafe_allow_html=True)
        with st.form("transfer", clear_on_submit=True):
            n1, n2 = st.columns(2)
            rec_name = n1.text_input("Recipient name", placeholder="e.g. Rohan Das")
            bank = n2.text_input("Bank name", placeholder="e.g. HDFC Bank")
            a1, a2 = st.columns([1.4, 1])
            acc_no = a1.text_input("Account number", placeholder="11–16 digits",
                                   max_chars=18)
            ifsc = a2.text_input("IFSC code", placeholder="HDFC0001234",
                                 max_chars=11)
            amount = st.number_input("Amount (₹)", 1.0, 200000.0, 500.0, step=100.0)
            send = st.form_submit_button("Send money", type="primary", **stretch())

        if send:
            errors = []
            if not rec_name.strip():
                errors.append("recipient name")
            if not re.fullmatch(r"\d{9,18}", acc_no.replace(" ", "")):
                errors.append("a valid account number (9–18 digits)")
            if not re.fullmatch(r"[A-Za-z]{4}0[A-Za-z0-9]{6}", ifsc.strip()):
                errors.append("a valid IFSC code (e.g. HDFC0001234)")
            if amount > ss.balance:
                st.error(f"❌ Not enough balance. You have {rupees(ss.balance)}, "
                         f"but tried to send {rupees(amount)}.")
            elif errors:
                st.error("❌ Please check: " + ", ".join(errors) + ".")
            else:
                ss.balance -= float(amount)
                ss.sent.append({"Name": rec_name.strip(), "DaysAgo": 0,
                                "Amount": float(amount), "Dir": "out"})
                ss.flash = f"Sent {rupees(amount)} to {rec_name.strip()}"
                ss.party = True
                st.rerun()

        st.caption("Demo transfer only — no money actually moves.")

        # ---- recent transactions
        st.markdown('<div class="v-h">🕘 Recent transactions</div>',
                    unsafe_allow_html=True)
        rows = ""
        for _, r in txn.sort_values("DaysAgo").iterrows():
            sign = "+" if r.Dir == "in" else "−"
            col = GREEN if r.Dir == "in" else RED
            rows += f"""<div class="v-row">
                <div class="v-avatar" style="background:{BLUE if r.Dir=='in' else PURPLE}">
                  {avatar_letter(r.Name)}</div>
                <div><div class="v-name">{r.Name}</div>
                     <div class="v-date">{r.Date} · {'Received' if r.Dir=='in' else 'Sent'}</div></div>
                <div class="v-amt" style="color:{col}">{sign}{rupees(r.Amount)}</div>
            </div>"""
        st.markdown(f'<div class="v-card" style="padding:6px 18px">{rows}</div>',
                    unsafe_allow_html=True)

        # small balance trend line (account balance only, no spending charts)
        bal = [52000, 49500, 51200, 50400, ss.balance]
        spark = go.Figure(go.Scatter(y=bal, mode="lines", line=dict(color=BLUE, width=3),
                                     fill="tozeroy",
                                     fillcolor="rgba(26,115,232,.14)"))
        spark.update_layout(height=120, margin=dict(l=0, r=0, t=0, b=0), showlegend=False,
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            xaxis=dict(visible=False), yaxis=dict(visible=False))
        st.markdown('<div class="v-h">📈 Balance trend</div>', unsafe_allow_html=True)
        st.plotly_chart(spark, config={"displayModeBar": False}, **stretch())

        if st.button("🔄 Restore demo balance", **stretch()):
            ss.balance = 48250.0
            ss.sent = []
            ss.flash = "Demo balance restored"
            st.rerun()

    # ================================================================ PERSONAL DETAILS
    elif page == "👤 Personal Details":
        st.markdown('<div class="v-h">👤 My personal details</div>', unsafe_allow_html=True)

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
        st.caption("All details above are fake sample data for this demo.")

    # ================================================================ ABOUT US
    elif page == "ℹ️ About Us":
        st.markdown('<div class="v-h">ℹ️ About Self Healing Vault</div>',
                    unsafe_allow_html=True)
        st.markdown(f"""<div class="v-card">
            <div style="font-size:1.02rem;color:{INK};line-height:1.55">
              Self Healing Vault is a friendly, no-fuss banking demo built for people
              who just want to know where their money is. Check your balance, send a
              demo transfer, and keep an eye on your account — all in one calm screen.
            </div>
            <div class="v-sub" style="margin-top:10px">
              “Self healing” is our idea of banking that quietly repairs itself:
              if something looks off, the vault gets locked first and asks questions
              later.</div>
        </div>""", unsafe_allow_html=True)

        feats = [("🛡️", "Secure", "Passcode lock on every visit", BLUE),
                 ("✨", "Simple", "Two taps to send money", GREEN),
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
              connection, and never moves real money.</div>
        </div>""", unsafe_allow_html=True)

    # ================================================================ CUSTOMER CARE
    else:
        st.markdown('<div class="v-h">🎧 Customer Care</div>', unsafe_allow_html=True)

        faqs = [("How do I send money?",
                 "Open Home, fill in the recipient, account number, IFSC and amount, "
                 "then tap Send money. It is a demo — nothing leaves the app."),
                ("Why was my transfer rejected?",
                 "You can only send what you have. If the amount is more than your "
                 "balance you will see a red message."),
                ("Is my passcode stored anywhere?",
                 "No. It lives in this app's session memory only, and the demo code "
                 "is 0000."),
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
                                                "Account details", "Something else"])
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
