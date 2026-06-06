
import streamlit as st
import json
import calendar
import os
from datetime import datetime, date, timedelta

st.set_page_config(
    page_title="CosmoCal",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════════
# THEMES
# ═══════════════════════════════════════════════════════════════════════════════
THEMES = {
    "Default":  {"bg":"linear-gradient(160deg,#0a0a1a,#0d1b2a,#0a0a1a)","accent":"#64a0ff","accent2":"#b060ff","sidebar":"rgba(10,10,30,0.88)","today":"rgba(100,160,255,0.15)","today_b":"rgba(100,160,255,0.50)","btn_bg":"rgba(100,160,255,0.15)","btn_b":"rgba(100,160,255,0.40)","dow":"rgba(140,180,255,0.90)","star1":"rgba(140,200,255,0.3)","star2":"rgba(200,160,255,0.3)"},
    "Cyberpunk":{"bg":"linear-gradient(160deg,#1a0030,#0a0050,#001a33)","accent":"#00ffee","accent2":"#ff00cc","sidebar":"rgba(10,0,30,0.92)","today":"rgba(0,255,238,0.12)","today_b":"rgba(0,255,238,0.55)","btn_bg":"rgba(0,255,238,0.12)","btn_b":"rgba(0,255,238,0.40)","dow":"rgba(0,255,238,0.85)","star1":"rgba(0,255,238,0.25)","star2":"rgba(255,0,204,0.25)"},
    "Sunset":   {"bg":"linear-gradient(160deg,#1a0a05,#2a0a10,#1a0518)","accent":"#ff7e5f","accent2":"#ffcc70","sidebar":"rgba(30,8,5,0.92)","today":"rgba(255,126,95,0.15)","today_b":"rgba(255,126,95,0.55)","btn_bg":"rgba(255,126,95,0.15)","btn_b":"rgba(255,126,95,0.40)","dow":"rgba(255,180,120,0.90)","star1":"rgba(255,126,95,0.30)","star2":"rgba(255,204,112,0.30)"},
    "Ocean":    {"bg":"linear-gradient(160deg,#0a1628,#0a2035,#061420)","accent":"#38bdf8","accent2":"#2193b0","sidebar":"rgba(6,14,28,0.92)","today":"rgba(56,189,248,0.13)","today_b":"rgba(56,189,248,0.55)","btn_bg":"rgba(56,189,248,0.13)","btn_b":"rgba(56,189,248,0.40)","dow":"rgba(100,210,255,0.90)","star1":"rgba(56,189,248,0.25)","star2":"rgba(33,147,176,0.25)"},
    "Midnight": {"bg":"linear-gradient(160deg,#000000,#080808,#0f172a)","accent":"#a78bfa","accent2":"#6366f1","sidebar":"rgba(4,4,12,0.95)","today":"rgba(167,139,250,0.13)","today_b":"rgba(167,139,250,0.55)","btn_bg":"rgba(167,139,250,0.13)","btn_b":"rgba(167,139,250,0.40)","dow":"rgba(180,160,255,0.90)","star1":"rgba(167,139,250,0.25)","star2":"rgba(99,102,241,0.25)"},
}

CATEGORY_COLORS = {
    "🔵 Work":      {"bg":"rgba(60,120,255,0.28)",  "border":"rgba(80,140,255,0.80)", "text":"#c0d8ff"},
    "🟣 Personal":  {"bg":"rgba(160,80,255,0.28)",  "border":"rgba(180,100,255,0.80)","text":"#e0c0ff"},
    "🟢 Health":    {"bg":"rgba(40,200,120,0.28)",  "border":"rgba(60,220,140,0.80)", "text":"#a0ffd0"},
    "🟡 Social":    {"bg":"rgba(255,200,40,0.22)",  "border":"rgba(255,210,60,0.80)", "text":"#fff0a0"},
    "🔴 Important": {"bg":"rgba(255,80,80,0.28)",   "border":"rgba(255,100,100,0.80)","text":"#ffc0c0"},
    "⚪ Other":     {"bg":"rgba(180,180,200,0.18)", "border":"rgba(200,200,220,0.60)","text":"#e0e0f0"},
}

RECURRENCE_OPTIONS = ["None", "Daily", "Weekly", "Bi-weekly", "Monthly", "Yearly"]

# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════
DEFAULTS = {
    "events": {}, "view": "Month",
    "current_date": date.today(), "selected_date": date.today(),
    "theme": "Default", "pending_evt": None,
    "editing_evt": None,  # {"date_str": ..., "idx": ...}
    "search_query": "",
    "show_reminders": False,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ═══════════════════════════════════════════════════════════════════════════════
# PERSISTENCE
# ═══════════════════════════════════════════════════════════════════════════════
DATA_FILE = "cosmo_events.json"

def load_events():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {}

def save_events(events):
    with open(DATA_FILE, "w") as f:
        json.dump(events, f, indent=2)

if not st.session_state.events:
    st.session_state.events = load_events()

# ═══════════════════════════════════════════════════════════════════════════════
# EVENT HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def get_color(cat):
    return CATEGORY_COLORS.get(cat, CATEGORY_COLORS["⚪ Other"])

def events_for_date(d):
    """Return all events for a date, including recurring ones."""
    direct = st.session_state.events.get(d.isoformat(), [])
    recurring = []

    for date_str, evts in st.session_state.events.items():
        for e in evts:
            if e.get("recurrence", "None") == "None":
                continue
            try:
                origin = date.fromisoformat(date_str)
            except Exception:
                continue
            if origin == d:
                continue  # already in direct
            rec = e["recurrence"]
            delta = (d - origin).days
            if delta <= 0:
                continue
            match = False
            if rec == "Daily":
                match = True
            elif rec == "Weekly":
                match = (delta % 7 == 0)
            elif rec == "Bi-weekly":
                match = (delta % 14 == 0)
            elif rec == "Monthly":
                match = (d.day == origin.day)
            elif rec == "Yearly":
                match = (d.day == origin.day and d.month == origin.month)
            if match:
                recurring.append({**e, "_recurring": True, "_origin": date_str})

    return direct + recurring

def add_event(d, title, time_str, category, note="", recurrence="None", reminder_min=0):
    key = d.isoformat()
    st.session_state.events.setdefault(key, []).append({
        "title": title,
        "time": time_str,
        "category": category,
        "note": note,
        "recurrence": recurrence,
        "reminder_min": reminder_min,
        "id": datetime.now().timestamp(),
    })
    save_events(st.session_state.events)

def update_event(date_str, idx, title, time_str, category, note, recurrence, reminder_min):
    evts = st.session_state.events.get(date_str, [])
    if idx < len(evts):
        evts[idx].update({
            "title": title, "time": time_str,
            "category": category, "note": note,
            "recurrence": recurrence, "reminder_min": reminder_min,
        })
        save_events(st.session_state.events)

def delete_event(d, idx):
    key = d.isoformat()
    if key in st.session_state.events:
        st.session_state.events[key].pop(idx)
        if not st.session_state.events[key]:
            del st.session_state.events[key]
        save_events(st.session_state.events)

def search_events(query):
    """Search all events by title, note, or category."""
    results = []
    q = query.lower()
    for date_str, evts in st.session_state.events.items():
        for i, e in enumerate(evts):
            if (q in e["title"].lower() or
                q in e.get("note","").lower() or
                q in e.get("category","").lower()):
                results.append({"date_str": date_str, "idx": i, **e})
    results.sort(key=lambda x: x["date_str"])
    return results

def get_upcoming_reminders():
    """Return events with reminders due in the next 60 minutes."""
    now = datetime.now()
    due = []
    for date_str, evts in st.session_state.events.items():
        try:
            evt_date = date.fromisoformat(date_str)
        except Exception:
            continue
        for e in evts:
            reminder_min = e.get("reminder_min", 0)
            if reminder_min == 0 or e.get("time", "All day") == "All day":
                continue
            try:
                h, m = map(int, e["time"].split(":"))
                evt_dt = datetime(evt_date.year, evt_date.month, evt_date.day, h, m)
                remind_dt = evt_dt - timedelta(minutes=reminder_min)
                diff = (evt_dt - now).total_seconds() / 60
                if 0 <= diff <= reminder_min:
                    due.append({**e, "evt_dt": evt_dt, "remind_in_min": round(diff)})
            except Exception:
                continue
    return due

# ═══════════════════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════════════════
_th = THEMES[st.session_state.theme]
st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
  html, body, [class*="css"] {{ font-family: 'Outfit', sans-serif !important; }}

  .stApp {{
    background: {_th["bg"]} !important;
    min-height: 100vh;
  }}
  .stApp::before {{
    content: '';
    position: fixed; inset: 0;
    background-image:
      radial-gradient(1px 1px at 10% 20%, rgba(255,255,255,0.6) 0%, transparent 100%),
      radial-gradient(1px 1px at 25% 75%, rgba(255,255,255,0.4) 0%, transparent 100%),
      radial-gradient(1px 1px at 40% 10%, rgba(255,255,255,0.5) 0%, transparent 100%),
      radial-gradient(1px 1px at 60% 50%, rgba(255,255,255,0.3) 0%, transparent 100%),
      radial-gradient(1px 1px at 75% 30%, rgba(255,255,255,0.6) 0%, transparent 100%),
      radial-gradient(1px 1px at 85% 80%, rgba(255,255,255,0.4) 0%, transparent 100%),
      radial-gradient(2px 2px at 15% 55%, {_th["star1"]} 0%, transparent 100%),
      radial-gradient(2px 2px at 90% 15%, {_th["star2"]} 0%, transparent 100%),
      radial-gradient(1px 1px at 50% 90%, rgba(255,255,255,0.5) 0%, transparent 100%);
    pointer-events: none; z-index: 0;
    animation: twinkle 8s ease-in-out infinite alternate;
  }}
  @keyframes twinkle {{ 0% {{ opacity:0.5; }} 100% {{ opacity:1.0; }} }}

  [data-testid="stSidebar"] {{
    background: {_th["sidebar"]} !important;
    backdrop-filter: blur(20px) !important;
    border-right: 1px solid rgba(255,255,255,0.10) !important;
  }}

  body, p, span, div, label, li, h1,h2,h3,h4,h5,h6,
  .stMarkdown, [data-testid="stMarkdownContainer"],
  [data-testid="stSidebar"] * {{ color: #ffffff !important; }}

  .stTextInput label, .stTextArea label, .stSelectbox label,
  .stDateInput label, .stCheckbox label, .stRadio label,
  .stNumberInput label, [data-testid="stWidgetLabel"] {{
    color: #ffffff !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.82rem !important; font-weight: 500 !important;
  }}
  .stRadio [role="radiogroup"] label {{ color: #ffffff !important; }}
  .stCaption {{ color: rgba(200,210,255,0.6) !important; }}

  .stTextInput > div > div > input,
  .stTextArea > div > div > textarea,
  .stDateInput > div > div > input {{
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    border-radius: 10px !important; color: #ffffff !important;
    font-family: 'Outfit', sans-serif !important;
    caret-color: white !important;
  }}
  .stTextInput > div > div > input::placeholder,
  .stTextArea > div > div > textarea::placeholder {{ color: rgba(200,210,255,0.4) !important; }}

  [data-baseweb="select"] > div {{
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    border-radius: 10px !important; color: #ffffff !important;
  }}
  [data-baseweb="select"] span, [data-baseweb="select"] div {{ color: #ffffff !important; }}

  .stButton > button {{
    background: {_th["btn_bg"]} !important;
    color: #ffffff !important;
    border: 1px solid {_th["btn_b"]} !important;
    border-radius: 10px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
  }}
  .stButton > button:hover {{
    background: {_th["accent"]}33 !important;
    border-color: {_th["accent"]} !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px {_th["accent"]}33 !important;
  }}
  .stButton > button p {{ color: #ffffff !important; }}
  .stForm [data-testid="stFormSubmitButton"] > button {{
    background: {_th["accent"]}22 !important;
    border: 1px solid {_th["accent"]}88 !important; width: 100%;
  }}

  [data-testid="block-container"] {{ background: transparent !important; }}

  /* Calendar */
  .cal-card {{
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 18px; padding: 1.4rem; margin-bottom: 1rem;
  }}
  .cal-header {{
    font-size: 1.5rem; font-weight: 700; color: #ffffff !important;
    letter-spacing: 0.02em; text-align: center; margin-bottom: 1rem;
  }}
  .dow-row {{ display:grid; grid-template-columns:repeat(7,1fr); gap:4px; margin-bottom:6px; }}
  .dow-cell {{
    text-align:center; font-size:0.7rem; font-weight:700;
    color: {_th["dow"]} !important;
    letter-spacing:0.08em; text-transform:uppercase; padding:4px 0;
  }}
  .cal-grid {{ display:grid; grid-template-columns:repeat(7,1fr); gap:4px; }}
  .day-cell {{
    min-height:72px; background:rgba(255,255,255,0.03);
    border:1px solid rgba(255,255,255,0.08);
    border-radius:10px; padding:6px 8px; position:relative;
  }}
  .day-cell.today {{
    background: {_th["today"]} !important;
    border-color: {_th["today_b"]} !important;
  }}
  .day-cell.other-month {{ opacity:0.3; }}
  .day-num {{ font-size:0.82rem; font-weight:700; color:#ffffff !important; line-height:1; }}
  .day-cell.today .day-num {{ color: {_th["accent"]} !important; }}
  .event-chip {{
    font-size:0.67rem; font-weight:600; padding:2px 6px; border-radius:5px;
    margin-top:3px; white-space:nowrap; overflow:hidden;
    text-overflow:ellipsis; max-width:100%; display:block;
  }}
  .event-detail {{
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.13);
    border-radius: 14px; padding: 0.9rem 1.2rem; margin-bottom: 0.6rem;
  }}
  .event-title {{ font-size:1rem; font-weight:700; color:#ffffff !important; }}
  .event-meta  {{ font-size:0.78rem; color:rgba(180,200,255,0.8) !important; margin-top:3px; }}
  .section-heading {{
    font-size:0.68rem; font-weight:700; letter-spacing:0.12em;
    text-transform:uppercase; color:{_th["dow"]} !important;
    margin-bottom:0.6rem; opacity: 0.85;
  }}
  .app-title {{
    font-size:1.8rem; font-weight:700;
    background: linear-gradient(90deg, {_th["accent"]}, {_th["accent2"]});
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; letter-spacing:0.04em;
  }}
  .app-sub {{ font-size:0.72rem; color:rgba(180,200,255,0.5) !important; letter-spacing:0.1em; }}
  hr {{ border-color:rgba(255,255,255,0.10) !important; }}

  .recur-badge {{
    display:inline-block; font-size:0.6rem; font-weight:700;
    padding:1px 6px; border-radius:20px;
    background: {_th["accent"]}22;
    border: 1px solid {_th["accent"]}66;
    color: {_th["accent"]} !important;
    margin-left:6px; vertical-align:middle;
  }}
  .reminder-badge {{
    display:inline-block; font-size:0.6rem; font-weight:700;
    padding:1px 6px; border-radius:20px;
    background: rgba(255,200,40,0.18);
    border: 1px solid rgba(255,210,60,0.5);
    color: #fff0a0 !important;
    margin-left:4px; vertical-align:middle;
  }}
  .search-result {{
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 12px; padding: 0.75rem 1rem; margin-bottom: 0.5rem;
  }}
  .reminder-alert {{
    background: rgba(255,200,40,0.15);
    border: 1px solid rgba(255,210,60,0.5);
    border-radius: 14px; padding: 0.8rem 1rem; margin-bottom: 0.6rem;
  }}

  /* Number input */
  [data-testid="stNumberInput"] input {{
    background: rgba(15,23,42,0.85) !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    border-radius: 10px !important; color: white !important;
    font-family: 'Outfit', sans-serif !important; caret-color: white !important;
  }}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="app-title">🌌 CosmoCal</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-sub">YOUR COSMIC CALENDAR</div>', unsafe_allow_html=True)
    st.markdown("---")

    # Theme
    st.markdown('<div class="section-heading">🎨 Theme</div>', unsafe_allow_html=True)
    chosen_theme = st.selectbox("", list(THEMES.keys()),
                                index=list(THEMES.keys()).index(st.session_state.theme),
                                label_visibility="collapsed", key="theme_sel")
    if chosen_theme != st.session_state.theme:
        st.session_state.theme = chosen_theme
        st.rerun()

    st.markdown("---")

    # View
    st.markdown('<div class="section-heading">📅 View</div>', unsafe_allow_html=True)
    view = st.radio("", ["Month","Week","Day","Agenda","Search"],
                    index=["Month","Week","Day","Agenda","Search"].index(st.session_state.view),
                    label_visibility="collapsed")
    st.session_state.view = view
    st.markdown("---")

    # Reminders check
    reminders_due = get_upcoming_reminders()
    if reminders_due:
        st.markdown(f'<div style="background:rgba(255,200,40,0.15);border:1px solid rgba(255,210,60,0.4);border-radius:10px;padding:8px 12px;margin-bottom:8px;"><span style="font-size:0.85rem;font-weight:700;color:#fff0a0;">🔔 {len(reminders_due)} reminder{"s" if len(reminders_due)>1 else ""} due!</span></div>', unsafe_allow_html=True)
        for r in reminders_due:
            st.markdown(f'<div class="reminder-alert"><div style="font-size:0.82rem;font-weight:700;color:#fff0a0;">⏰ {r["title"]}</div><div style="font-size:0.72rem;color:rgba(255,240,160,0.8);">In {r["remind_in_min"]} min · {r["evt_dt"].strftime("%H:%M")}</div></div>', unsafe_allow_html=True)
        st.markdown("---")

    # Add Event Form
    st.markdown('<div class="section-heading">✦ New Event</div>', unsafe_allow_html=True)
    with st.form("add_event_form", clear_on_submit=True):
        evt_date      = st.date_input("Date", value=st.session_state.selected_date)
        evt_title     = st.text_input("Title", placeholder="Event name…")
        evt_time      = st.text_input("Time", placeholder="e.g. 14:00 or All day")
        evt_cat       = st.selectbox("Category", list(CATEGORY_COLORS.keys()))
        evt_note      = st.text_area("Notes", placeholder="Optional notes…", height=60)
        evt_recur     = st.selectbox("🔁 Recurrence", RECURRENCE_OPTIONS)
        evt_reminder  = st.selectbox("🔔 Reminder", [0, 5, 10, 15, 30, 60, 120],
                                     format_func=lambda x: "None" if x==0 else f"{x} min before")
        if st.form_submit_button("＋ Add Event", use_container_width=True) and evt_title.strip():
            add_event(evt_date, evt_title.strip(), evt_time or "All day",
                      evt_cat, evt_note, evt_recur, evt_reminder)
            st.session_state.selected_date = evt_date
            st.success("Event added! 🌠")
            st.rerun()

    st.markdown("---")

    # Navigate
    st.markdown('<div class="section-heading">Navigate</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c1:
        if st.button("◀", use_container_width=True):
            d = st.session_state.current_date
            if view=="Month":
                m,y=d.month-1,d.year
                if m==0: m,y=12,y-1
                st.session_state.current_date=d.replace(year=y,month=m,day=1)
            elif view=="Week": st.session_state.current_date=d-timedelta(weeks=1)
            else:              st.session_state.current_date=d-timedelta(days=1)
            st.rerun()
    with c2:
        if st.button("Today", use_container_width=True):
            st.session_state.current_date=date.today()
            st.session_state.selected_date=date.today()
            st.rerun()
    with c3:
        if st.button("▶", use_container_width=True):
            d=st.session_state.current_date
            if view=="Month":
                m,y=d.month+1,d.year
                if m==13: m,y=1,y+1
                st.session_state.current_date=d.replace(year=y,month=m,day=1)
            elif view=="Week": st.session_state.current_date=d+timedelta(weeks=1)
            else:              st.session_state.current_date=d+timedelta(days=1)
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# SHARED: Edit Event Modal
# ═══════════════════════════════════════════════════════════════════════════════
def render_edit_modal():
    ee = st.session_state.editing_evt
    if not ee:
        return
    date_str = ee["date_str"]
    idx      = ee["idx"]
    evts     = st.session_state.events.get(date_str, [])
    if idx >= len(evts):
        st.session_state.editing_evt = None
        return
    e = evts[idx]

    st.markdown(f"""
    <div style="background:rgba(20,30,70,0.75);border:1px solid {_th["accent"]}66;
    border-radius:18px;padding:1.4rem 1.6rem;margin-bottom:1.2rem;">
    <div style="font-size:1rem;font-weight:700;color:{_th["accent"]};margin-bottom:1rem;">
    ✏️ Edit Event — {date_str}</div>
    """, unsafe_allow_html=True)

    with st.form("edit_event_form", clear_on_submit=False):
        e_title    = st.text_input("Title",    value=e["title"])
        e_time     = st.text_input("Time",     value=e.get("time","All day"))
        e_cat      = st.selectbox("Category",  list(CATEGORY_COLORS.keys()),
                                  index=list(CATEGORY_COLORS.keys()).index(e.get("category","⚪ Other"))
                                  if e.get("category") in CATEGORY_COLORS else 0)
        e_note     = st.text_area("Notes",     value=e.get("note",""), height=70)
        e_recur    = st.selectbox("🔁 Recurrence", RECURRENCE_OPTIONS,
                                  index=RECURRENCE_OPTIONS.index(e.get("recurrence","None"))
                                  if e.get("recurrence") in RECURRENCE_OPTIONS else 0)
        e_reminder = st.selectbox("🔔 Reminder", [0,5,10,15,30,60,120],
                                  index=[0,5,10,15,30,60,120].index(e.get("reminder_min",0))
                                  if e.get("reminder_min",0) in [0,5,10,15,30,60,120] else 0,
                                  format_func=lambda x: "None" if x==0 else f"{x} min before")
        col_save, col_cancel = st.columns(2)
        with col_save:
            if st.form_submit_button("💾 Save Changes", use_container_width=True) and e_title.strip():
                update_event(date_str, idx, e_title.strip(), e_time or "All day",
                             e_cat, e_note, e_recur, e_reminder)
                st.session_state.editing_evt = None
                st.success("Saved! ✨")
                st.rerun()
        with col_cancel:
            if st.form_submit_button("✕ Cancel", use_container_width=True):
                st.session_state.editing_evt = None
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def event_row(e, date_str, idx, key_prefix):
    """Render one event detail card with Edit + Delete buttons."""
    c = get_color(e.get("category","⚪ Other"))
    recur = e.get("recurrence","None")
    reminder = e.get("reminder_min", 0)
    recur_badge = f'<span class="recur-badge">🔁 {recur}</span>' if recur != "None" else ""
    reminder_badge = f'<span class="reminder-badge">🔔 {reminder}m</span>' if reminder else ""
    recurring_tag = ' <span style="font-size:0.65rem;color:rgba(200,200,255,0.5);">(recurring)</span>' if e.get("_recurring") else ""

    col_e, col_edit, col_del = st.columns([9, 1, 1])
    with col_e:
        st.markdown(
            f'<div class="event-detail" style="border-left:4px solid {c["border"]}">'
            f'<div class="event-title">{e["title"]}{recur_badge}{reminder_badge}{recurring_tag}</div>'
            f'<div class="event-meta">🕐 {e.get("time","All day")} &nbsp;·&nbsp; {e.get("category","")}'
            f'{"<br>" + e["note"] if e.get("note") else ""}</div></div>',
            unsafe_allow_html=True)
    with col_edit:
        if not e.get("_recurring"):  # can't edit auto-generated recurring instances
            if st.button("✏️", key=f"{key_prefix}_edit_{date_str}_{idx}", help="Edit"):
                st.session_state.editing_evt = {"date_str": date_str, "idx": idx}
                st.rerun()
    with col_del:
        if not e.get("_recurring"):
            if st.button("🗑", key=f"{key_prefix}_del_{date_str}_{idx}", help="Delete"):
                delete_event(date.fromisoformat(date_str), idx)
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN VIEWS
# ═══════════════════════════════════════════════════════════════════════════════
today = date.today()
cd    = st.session_state.current_date

# ── Edit modal always shown if active ────────────────────────────────────────
if st.session_state.editing_evt:
    render_edit_modal()

# ─────────────────────────────────────────────────────────────────────────────
# MONTH VIEW
# ─────────────────────────────────────────────────────────────────────────────
if view == "Month":
    month_name = cd.strftime("%B %Y")
    html = f'<div class="cal-card"><div class="cal-header">{month_name}</div>'
    html += '<div class="dow-row">'
    for dow in ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]:
        html += f'<div class="dow-cell">{dow}</div>'
    html += '</div><div class="cal-grid">'

    cal = calendar.Calendar(firstweekday=6)
    for week in cal.monthdatescalendar(cd.year, cd.month):
        for day in week:
            is_today    = (day == today)
            other_month = (day.month != cd.month)
            css = "day-cell" + (" today" if is_today else "") + (" other-month" if other_month else "")
            html += f'<div class="{css}"><div class="day-num">{day.day}</div>'
            day_evts = events_for_date(day)
            for e in day_evts[:2]:
                c = get_color(e.get("category","⚪ Other"))
                recur_dot = " 🔁" if e.get("recurrence","None") != "None" or e.get("_recurring") else ""
                html += (f'<span class="event-chip" style="background:{c["bg"]};'
                         f'color:{c["text"]};border-left:3px solid {c["border"]}">'
                         f'{e["title"]}{recur_dot}</span>')
            if len(day_evts) > 2:
                html += f'<span style="font-size:0.62rem;color:rgba(200,210,255,0.6)">+{len(day_evts)-2} more</span>'
            html += '</div>'
    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)

    st.markdown(f'<div class="section-heading">Events — {st.session_state.selected_date.strftime("%A, %B %-d, %Y")}</div>', unsafe_allow_html=True)
    sel_evts = events_for_date(st.session_state.selected_date)
    if sel_evts:
        for i, e in enumerate(sel_evts):
            event_row(e, st.session_state.selected_date.isoformat(), i, "m")
    else:
        st.markdown('<p style="color:rgba(200,210,255,0.4);font-size:0.85rem">No events — add one from the sidebar.</p>', unsafe_allow_html=True)

    pick = st.date_input("Jump to date", value=st.session_state.selected_date,
                         label_visibility="collapsed", key="jump_picker")
    if pick != st.session_state.selected_date:
        st.session_state.selected_date = pick
        st.session_state.current_date  = pick
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# WEEK VIEW
# ─────────────────────────────────────────────────────────────────────────────
elif view == "Week":
    dow        = (cd.weekday() + 1) % 7
    week_start = cd - timedelta(days=dow)
    week_days  = [week_start + timedelta(days=i) for i in range(7)]
    week_label = f"{week_days[0].strftime('%b %-d')} – {week_days[-1].strftime('%b %-d, %Y')}"
    st.markdown(f'<div class="cal-header" style="text-align:left;font-size:1.3rem">{week_label}</div>', unsafe_allow_html=True)

    cols = st.columns(7)
    for i, day in enumerate(week_days):
        with cols[i]:
            is_today = (day == today)
            bg = f"{_th['today']}" if is_today else "rgba(255,255,255,0.04)"
            bc = f"{_th['today_b']}" if is_today else "rgba(255,255,255,0.09)"
            st.markdown(
                f'<div style="background:{bg};border:1px solid {bc};border-radius:12px;'
                f'padding:10px 8px;min-height:180px;">'
                f'<div style="font-size:0.68rem;font-weight:700;letter-spacing:.08em;'
                f'color:{_th["dow"]}">{day.strftime("%a").upper()}</div>'
                f'<div style="font-size:1.25rem;font-weight:700;'
                f'color:{""+_th["accent"] if is_today else "#ffffff"}">{day.day}</div>',
                unsafe_allow_html=True)
            for e in events_for_date(day):
                c = get_color(e.get("category","⚪ Other"))
                recur_dot = " 🔁" if e.get("recurrence","None") != "None" or e.get("_recurring") else ""
                st.markdown(
                    f'<div style="font-size:0.68rem;font-weight:600;padding:3px 6px;border-radius:6px;'
                    f'background:{c["bg"]};color:{c["text"]};border-left:3px solid {c["border"]};'
                    f'margin-top:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">'
                    f'{e.get("time","")} {e["title"]}{recur_dot}</div>', unsafe_allow_html=True)
            if not events_for_date(day):
                st.markdown('<div style="font-size:0.65rem;color:rgba(255,255,255,0.25);margin-top:8px">—</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f'<div class="section-heading">Edit Events This Week</div>', unsafe_allow_html=True)
    for day in week_days:
        day_evts = events_for_date(day)
        if day_evts:
            st.markdown(f'<div style="font-size:0.78rem;font-weight:700;color:{_th["accent"]};margin:0.6rem 0 0.3rem;">{day.strftime("%A, %b %-d")}</div>', unsafe_allow_html=True)
            for i, e in enumerate(day_evts):
                event_row(e, day.isoformat(), i, "w")

# ─────────────────────────────────────────────────────────────────────────────
# DAY VIEW
# ─────────────────────────────────────────────────────────────────────────────
elif view == "Day":
    st.markdown(f'<div class="cal-header" style="text-align:left;font-size:1.4rem">'
                f'{cd.strftime("%A, %B %-d, %Y")}</div>', unsafe_allow_html=True)

    evts = events_for_date(cd)

    if evts:
        st.markdown('<div class="section-heading">Today\'s Events</div>', unsafe_allow_html=True)
        for i, e in enumerate(evts):
            event_row(e, cd.isoformat(), i, "d")
    else:
        st.markdown('<p style="color:rgba(200,210,255,0.4);font-size:0.85rem;margin-bottom:1rem;">No events today — add one from the sidebar.</p>', unsafe_allow_html=True)

    # 24-hour timeline
    import streamlit.components.v1 as components
    evts_json = json.dumps([
        {"title": e["title"], "time": e.get("time","All day"),
         "category": e.get("category","⚪ Other"),
         "color": get_color(e.get("category","⚪ Other"))["border"],
         "bg":    get_color(e.get("category","⚪ Other"))["bg"],
         "text":  get_color(e.get("category","⚪ Other"))["text"]}
        for e in evts
    ])
    components.html(f"""
<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  *{{box-sizing:border-box;margin:0;padding:0;}}
  body{{font-family:'Outfit',sans-serif;background:transparent;color:#fff;user-select:none;}}
  #tl-wrap{{background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.10);border-radius:14px;padding:14px 16px;overflow:hidden;}}
  #tl-hint{{font-size:11px;color:rgba(160,190,255,0.70);margin-bottom:10px;font-weight:500;letter-spacing:0.05em;}}
  #tl-scroll{{overflow-y:auto;max-height:520px;position:relative;}}
  #tl-inner{{position:relative;height:1248px;}}
  .hour-row{{position:absolute;left:0;right:0;height:52px;display:flex;align-items:flex-start;border-top:1px solid rgba(255,255,255,0.07);}}
  .hour-label{{font-size:11px;font-weight:600;color:rgba(140,180,255,0.75);min-width:42px;padding-top:3px;letter-spacing:0.04em;flex-shrink:0;}}
  .hour-stripe{{flex:1;height:100%;position:relative;cursor:crosshair;}}
  .half-line{{position:absolute;top:50%;left:0;right:0;height:1px;background:rgba(255,255,255,0.04);pointer-events:none;}}
  .evt-block{{position:absolute;left:44px;right:0;border-radius:7px;padding:4px 8px;font-size:12px;font-weight:600;pointer-events:none;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;z-index:2;border-left:3px solid;}}
  #drag-sel{{position:absolute;left:44px;right:0;background:rgba(100,160,255,0.22);border:2px solid rgba(100,160,255,0.75);border-radius:8px;display:none;z-index:10;pointer-events:none;}}
  #drag-label{{position:absolute;left:44px;background:rgba(30,50,120,0.95);border:1px solid rgba(100,160,255,0.7);border-radius:7px;padding:4px 10px;font-size:12px;font-weight:600;color:#c0d8ff;display:none;z-index:20;pointer-events:none;white-space:nowrap;}}
  #now-marker{{position:absolute;left:42px;right:0;height:2px;background:rgba(255,120,120,0.9);z-index:5;pointer-events:none;}}
  #now-dot{{position:absolute;left:38px;width:8px;height:8px;background:rgba(255,120,120,0.9);border-radius:50%;margin-top:-3px;z-index:5;pointer-events:none;}}
</style></head><body>
<div id="tl-wrap">
  <div id="tl-hint">🖱 Drag to mark time blocks</div>
  <div id="tl-scroll"><div id="tl-inner">
    <div id="drag-sel"></div><div id="drag-label"></div>
    <div id="now-marker"></div><div id="now-dot"></div>
  </div></div>
</div>
<script>
const HOUR_PX=52;
const events={evts_json};
function timeStrToHour(t){{if(!t||t==="All day")return null;const[h,m]=t.split(":").map(Number);return h+(m||0)/60;}}
function hourToY(h){{return h*HOUR_PX;}}
const inner=document.getElementById("tl-inner");
for(let h=0;h<24;h++){{
  const row=document.createElement("div");row.className="hour-row";row.style.top=(h*HOUR_PX)+"px";
  const lbl=document.createElement("div");lbl.className="hour-label";lbl.textContent=h.toString().padStart(2,"0")+":00";
  const stripe=document.createElement("div");stripe.className="hour-stripe";stripe.dataset.hour=h;
  const half=document.createElement("div");half.className="half-line";stripe.appendChild(half);
  row.appendChild(lbl);row.appendChild(stripe);inner.appendChild(row);
}}
events.forEach(e=>{{
  const h=timeStrToHour(e.time);if(h===null)return;
  const block=document.createElement("div");block.className="evt-block";
  block.style.top=hourToY(h)+"px";block.style.height=HOUR_PX+"px";
  block.style.background=e.bg;block.style.borderLeftColor=e.color;block.style.color=e.text;
  block.textContent=e.time+"  "+e.title;inner.appendChild(block);
}});
function drawNow(){{const now=new Date();const frac=(now.getHours()+now.getMinutes()/60)*HOUR_PX;document.getElementById("now-marker").style.top=frac+"px";document.getElementById("now-dot").style.top=frac+"px";}}
drawNow();setInterval(drawNow,60000);
document.getElementById("tl-scroll").scrollTop=8*HOUR_PX-20;
</script></body></html>
""", height=560, scrolling=False)

# ─────────────────────────────────────────────────────────────────────────────
# AGENDA VIEW
# ─────────────────────────────────────────────────────────────────────────────
elif view == "Agenda":
    st.markdown('<div class="cal-header" style="text-align:left;font-size:1.4rem">Upcoming Events</div>', unsafe_allow_html=True)
    found_any = False
    for delta in range(60):
        check = today + timedelta(days=delta)
        evts  = events_for_date(check)
        if evts:
            found_any = True
            is_today  = (check == today)
            label = "Today" if is_today else check.strftime("%A, %B %-d")
            st.markdown(
                f'<div style="font-size:0.75rem;font-weight:700;'
                f'color:{""+_th["accent"] if is_today else _th["dow"]};'
                f'margin:1.2rem 0 0.4rem;letter-spacing:.07em;text-transform:uppercase">{label}</div>',
                unsafe_allow_html=True)
            for i, e in enumerate(evts):
                event_row(e, check.isoformat(), i, "ag")
    if not found_any:
        st.markdown('<div style="text-align:center;padding:4rem 0;color:rgba(200,210,255,0.35);">🌌 No upcoming events in the next 60 days.</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SEARCH VIEW
# ─────────────────────────────────────────────────────────────────────────────
elif view == "Search":
    st.markdown('<div class="cal-header" style="text-align:left;font-size:1.4rem">🔍 Search Events</div>', unsafe_allow_html=True)

    query = st.text_input("", placeholder="Search by title, notes, or category…",
                          label_visibility="collapsed", key="search_input")
    st.session_state.search_query = query

    if query.strip():
        results = search_events(query.strip())
        if results:
            st.markdown(f'<div class="section-heading">{len(results)} result{"s" if len(results)!=1 else ""} found</div>', unsafe_allow_html=True)
            for r in results:
                c = get_color(r.get("category","⚪ Other"))
                recur = r.get("recurrence","None")
                reminder = r.get("reminder_min",0)
                recur_badge  = f'<span class="recur-badge">🔁 {recur}</span>' if recur!="None" else ""
                remind_badge = f'<span class="reminder-badge">🔔 {reminder}m</span>' if reminder else ""
                col_e, col_edit, col_del = st.columns([9,1,1])
                with col_e:
                    st.markdown(
                        f'<div class="search-result" style="border-left:4px solid {c["border"]}">'
                        f'<div style="font-size:0.72rem;color:{_th["dow"]};margin-bottom:3px;">'
                        f'📅 {r["date_str"]}</div>'
                        f'<div class="event-title">{r["title"]}{recur_badge}{remind_badge}</div>'
                        f'<div class="event-meta">🕐 {r.get("time","All day")} · {r.get("category","")}'
                        f'{"<br>"+r["note"] if r.get("note") else ""}</div></div>',
                        unsafe_allow_html=True)
                with col_edit:
                    if st.button("✏️", key=f"sr_edit_{r['date_str']}_{r['idx']}", help="Edit"):
                        st.session_state.editing_evt = {"date_str": r["date_str"], "idx": r["idx"]}
                        st.rerun()
                with col_del:
                    if st.button("🗑", key=f"sr_del_{r['date_str']}_{r['idx']}", help="Delete"):
                        delete_event(date.fromisoformat(r["date_str"]), r["idx"])
                        st.rerun()
        else:
            st.markdown(f'<div style="color:rgba(200,210,255,0.4);padding:2rem 0;text-align:center;">🌌 No events found for "{query}"</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:rgba(200,210,255,0.35);padding:2rem 0;text-align:center;">Start typing to search your events…</div>', unsafe_allow_html=True)

        # Show summary stats
        total_events = sum(len(v) for v in st.session_state.events.values())
        if total_events:
            st.markdown("---")
            st.markdown(f'<div class="section-heading">📊 Calendar Stats</div>', unsafe_allow_html=True)
            cat_counts = {}
            for evts in st.session_state.events.values():
                for e in evts:
                    cat = e.get("category","⚪ Other")
                    cat_counts[cat] = cat_counts.get(cat,0) + 1
            cols = st.columns(min(len(cat_counts), 4))
            for i, (cat, count) in enumerate(sorted(cat_counts.items(), key=lambda x: -x[1])):
                c = get_color(cat)
                with cols[i % 4]:
                    st.markdown(
                        f'<div style="background:{c["bg"]};border:1px solid {c["border"]};'
                        f'border-radius:12px;padding:10px;text-align:center;">'
                        f'<div style="font-size:1.4rem;font-weight:800;color:{c["text"]}">{count}</div>'
                        f'<div style="font-size:0.7rem;color:{c["text"]};opacity:0.85">{cat}</div>'
                        f'</div>', unsafe_allow_html=True)

