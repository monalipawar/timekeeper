import streamlit as st
import json
import calendar
import os
import csv
import io
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
    "Default":   {"bg":"linear-gradient(160deg,#020617,#0a0f2e,#0d1b2a)","accent":"#64a0ff","accent2":"#b060ff","sidebar":"rgba(5,8,28,0.92)","today":"rgba(100,160,255,0.13)","today_b":"rgba(100,160,255,0.55)","btn_bg":"rgba(100,160,255,0.13)","btn_b":"rgba(100,160,255,0.45)","dow":"rgba(140,180,255,0.85)","star1":"rgba(140,200,255,0.3)","star2":"rgba(200,160,255,0.3)","grid_bg":"rgba(255,255,255,0.025)","grid_b":"rgba(255,255,255,0.07)"},
    "Cyberpunk": {"bg":"linear-gradient(160deg,#0d0020,#0a0045,#001428)","accent":"#00ffee","accent2":"#ff00cc","sidebar":"rgba(6,0,22,0.94)","today":"rgba(0,255,238,0.10)","today_b":"rgba(0,255,238,0.60)","btn_bg":"rgba(0,255,238,0.10)","btn_b":"rgba(0,255,238,0.45)","dow":"rgba(0,255,238,0.80)","star1":"rgba(0,255,238,0.22)","star2":"rgba(255,0,204,0.22)","grid_bg":"rgba(0,255,238,0.02)","grid_b":"rgba(0,255,238,0.08)"},
    "Sunset":    {"bg":"linear-gradient(160deg,#150805,#220810,#180415)","accent":"#ff7e5f","accent2":"#ffcc70","sidebar":"rgba(20,5,4,0.94)","today":"rgba(255,126,95,0.13)","today_b":"rgba(255,126,95,0.60)","btn_bg":"rgba(255,126,95,0.13)","btn_b":"rgba(255,126,95,0.45)","dow":"rgba(255,180,120,0.85)","star1":"rgba(255,126,95,0.28)","star2":"rgba(255,204,112,0.28)","grid_bg":"rgba(255,126,95,0.02)","grid_b":"rgba(255,126,95,0.08)"},
    "Ocean":     {"bg":"linear-gradient(160deg,#060f1e,#091a2d,#040e18)","accent":"#38bdf8","accent2":"#2193b0","sidebar":"rgba(4,10,20,0.94)","today":"rgba(56,189,248,0.11)","today_b":"rgba(56,189,248,0.60)","btn_bg":"rgba(56,189,248,0.11)","btn_b":"rgba(56,189,248,0.45)","dow":"rgba(100,210,255,0.85)","star1":"rgba(56,189,248,0.22)","star2":"rgba(33,147,176,0.22)","grid_bg":"rgba(56,189,248,0.02)","grid_b":"rgba(56,189,248,0.07)"},
    "Midnight":  {"bg":"linear-gradient(160deg,#000000,#050508,#0a0d1a)","accent":"#a78bfa","accent2":"#6366f1","sidebar":"rgba(2,2,8,0.96)","today":"rgba(167,139,250,0.11)","today_b":"rgba(167,139,250,0.60)","btn_bg":"rgba(167,139,250,0.11)","btn_b":"rgba(167,139,250,0.45)","dow":"rgba(180,160,255,0.85)","star1":"rgba(167,139,250,0.22)","star2":"rgba(99,102,241,0.22)","grid_bg":"rgba(167,139,250,0.02)","grid_b":"rgba(167,139,250,0.07)"},
}

CATEGORY_COLORS = {
    "🔵 Work":      {"bg":"rgba(60,120,255,0.22)","border":"rgba(80,150,255,0.85)","text":"#c0d8ff","dot":"#4090ff"},
    "🟣 Personal":  {"bg":"rgba(160,80,255,0.22)","border":"rgba(185,110,255,0.85)","text":"#e0c0ff","dot":"#b060ff"},
    "🟢 Health":    {"bg":"rgba(40,200,120,0.22)","border":"rgba(60,225,145,0.85)","text":"#a0ffd0","dot":"#30cc90"},
    "🟡 Social":    {"bg":"rgba(255,200,40,0.18)","border":"rgba(255,215,65,0.85)","text":"#fff0a0","dot":"#ffcc30"},
    "🔴 Important": {"bg":"rgba(255,80,80,0.22)","border":"rgba(255,110,110,0.85)","text":"#ffc0c0","dot":"#ff5050"},
    "⚪ Other":     {"bg":"rgba(180,180,200,0.15)","border":"rgba(210,210,230,0.65)","text":"#e0e0f0","dot":"#a0a0c0"},
}

RECURRENCE_OPTIONS = ["None", "Daily", "Weekly", "Bi-weekly", "Monthly", "Yearly"]

MOOD_OPTIONS = ["", "😄", "😊", "😐", "😔", "😤", "🤩", "😴", "🥳", "😰", "❤️"]

US_HOLIDAYS = {
    "01-01": "🎆 New Year's Day",
    "01-15": "✊ MLK Day",
    "02-14": "💝 Valentine's Day",
    "03-17": "🍀 St. Patrick's Day",
    "04-22": "🌍 Earth Day",
    "05-27": "🇺🇸 Memorial Day",
    "06-19": "✊ Juneteenth",
    "07-04": "🎇 Independence Day",
    "09-02": "👷 Labor Day",
    "10-31": "🎃 Halloween",
    "11-11": "🎖️ Veterans Day",
    "11-28": "🦃 Thanksgiving",
    "12-25": "🎄 Christmas",
    "12-31": "🥂 New Year's Eve",
}

# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════
DEFAULTS = {
    "events": {}, "view": "Month",
    "current_date": date.today(), "selected_date": date.today(),
    "theme": "Default", "editing_evt": None,
    "search_query": "", "moods": {},
    "show_export": False,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ═══════════════════════════════════════════════════════════════════════════════
# PERSISTENCE
# ═══════════════════════════════════════════════════════════════════════════════
DATA_FILE  = "cosmo_events.json"
MOOD_FILE  = "cosmo_moods.json"

def load_events():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {}

def save_events(events):
    with open(DATA_FILE, "w") as f:
        json.dump(events, f, indent=2)

def load_moods():
    if os.path.exists(MOOD_FILE):
        with open(MOOD_FILE) as f:
            return json.load(f)
    return {}

def save_moods(moods):
    with open(MOOD_FILE, "w") as f:
        json.dump(moods, f, indent=2)

if not st.session_state.events:
    st.session_state.events = load_events()
if not st.session_state.moods:
    st.session_state.moods = load_moods()

# ═══════════════════════════════════════════════════════════════════════════════
# EVENT HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def get_color(cat):
    return CATEGORY_COLORS.get(cat, CATEGORY_COLORS["⚪ Other"])

def events_for_date(d):
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
                continue
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

def add_event(d, title, time_str, category, note="", recurrence="None", reminder_min=0, is_birthday=False):
    key = d.isoformat()
    st.session_state.events.setdefault(key, []).append({
        "title": title, "time": time_str, "category": category,
        "note": note, "recurrence": recurrence, "reminder_min": reminder_min,
        "is_birthday": is_birthday, "id": datetime.now().timestamp(),
    })
    save_events(st.session_state.events)

def update_event(date_str, idx, title, time_str, category, note, recurrence, reminder_min):
    evts = st.session_state.events.get(date_str, [])
    if idx < len(evts):
        evts[idx].update({"title": title, "time": time_str, "category": category,
                          "note": note, "recurrence": recurrence, "reminder_min": reminder_min})
        save_events(st.session_state.events)

def delete_event(d, idx):
    key = d.isoformat()
    if key in st.session_state.events:
        st.session_state.events[key].pop(idx)
        if not st.session_state.events[key]:
            del st.session_state.events[key]
        save_events(st.session_state.events)

def search_events(query):
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
                diff = (evt_dt - now).total_seconds() / 60
                if 0 <= diff <= reminder_min:
                    due.append({**e, "evt_dt": evt_dt, "remind_in_min": round(diff)})
            except Exception:
                continue
    return due

def export_events_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Title", "Time", "Category", "Note", "Recurrence", "Reminder (min)"])
    for date_str, evts in sorted(st.session_state.events.items()):
        for e in evts:
            writer.writerow([date_str, e.get("title",""), e.get("time",""), e.get("category",""),
                             e.get("note",""), e.get("recurrence","None"), e.get("reminder_min",0)])
    return output.getvalue()

def export_events_json():
    return json.dumps(st.session_state.events, indent=2)

def import_events_json(raw):
    try:
        data = json.loads(raw)
        for k, v in data.items():
            st.session_state.events.setdefault(k, [])
            existing_ids = {e.get("id") for e in st.session_state.events[k]}
            for e in v:
                if e.get("id") not in existing_ids:
                    st.session_state.events[k].append(e)
        save_events(st.session_state.events)
        return True
    except Exception:
        return False

# ═══════════════════════════════════════════════════════════════════════════════
# HOLIDAY HELPER
# ═══════════════════════════════════════════════════════════════════════════════
def get_holiday(d):
    key = d.strftime("%m-%d")
    return US_HOLIDAYS.get(key)

# ═══════════════════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════════════════
_th = THEMES[st.session_state.theme]

st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
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
      radial-gradient(1px 1px at 8%  18%, rgba(255,255,255,0.55) 0%, transparent 100%),
      radial-gradient(1px 1px at 22% 72%, rgba(255,255,255,0.38) 0%, transparent 100%),
      radial-gradient(1px 1px at 38% 8%,  rgba(255,255,255,0.48) 0%, transparent 100%),
      radial-gradient(1px 1px at 55% 48%, rgba(255,255,255,0.28) 0%, transparent 100%),
      radial-gradient(1px 1px at 72% 28%, rgba(255,255,255,0.55) 0%, transparent 100%),
      radial-gradient(1px 1px at 88% 82%, rgba(255,255,255,0.38) 0%, transparent 100%),
      radial-gradient(2px 2px at 14% 52%, {_th["star1"]} 0%, transparent 100%),
      radial-gradient(2px 2px at 92% 14%, {_th["star2"]} 0%, transparent 100%),
      radial-gradient(1px 1px at 48% 92%, rgba(255,255,255,0.45) 0%, transparent 100%),
      radial-gradient(1px 1px at 65% 65%, rgba(255,255,255,0.32) 0%, transparent 100%),
      radial-gradient(1px 1px at 32% 38%, rgba(255,255,255,0.42) 0%, transparent 100%);
    pointer-events: none; z-index: 0;
    animation: twinkle 9s ease-in-out infinite alternate;
}}
@keyframes twinkle {{ 0% {{ opacity:0.45; }} 100% {{ opacity:1.0; }} }}

[data-testid="stSidebar"] {{
    background: {_th["sidebar"]} !important;
    backdrop-filter: blur(24px) saturate(1.3) !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
}}

body, p, span, div, label, li, h1,h2,h3,h4,h5,h6,
.stMarkdown, [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] * {{ color: #ffffff !important; }}

.stTextInput label, .stTextArea label, .stSelectbox label,
.stDateInput label, .stCheckbox label, .stRadio label,
.stNumberInput label, [data-testid="stWidgetLabel"] {{
    color: rgba(200,215,255,0.75) !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.78rem !important; font-weight: 500 !important;
    letter-spacing: 0.04em !important; text-transform: uppercase !important;
}}
.stRadio [role="radiogroup"] label {{ color: #ffffff !important; text-transform: none !important; letter-spacing: normal !important; }}
.stCaption {{ color: rgba(180,200,255,0.5) !important; }}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stDateInput > div > div > input {{
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    border-radius: 10px !important; color: #ffffff !important;
    font-family: 'Outfit', sans-serif !important;
    caret-color: white !important; font-size: 0.9rem !important;
}}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
    border-color: {_th["accent"]}88 !important;
    box-shadow: 0 0 0 2px {_th["accent"]}22 !important;
}}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {{ color: rgba(180,200,255,0.3) !important; }}

[data-baseweb="select"] > div {{
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    border-radius: 10px !important; color: #ffffff !important;
}}
[data-baseweb="select"] span, [data-baseweb="select"] div {{ color: #ffffff !important; }}

.stButton > button {{
    background: {_th["btn_bg"]} !important;
    color: #ffffff !important;
    border: 1px solid {_th["btn_b"]} !important;
    border-radius: 10px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important; font-size: 0.85rem !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.02em !important;
}}
.stButton > button:hover {{
    background: {_th["accent"]}28 !important;
    border-color: {_th["accent"]} !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 24px {_th["accent"]}30 !important;
}}
.stButton > button p {{ color: #ffffff !important; }}
.stForm [data-testid="stFormSubmitButton"] > button {{
    background: linear-gradient(135deg, {_th["accent"]}30, {_th["accent2"]}20) !important;
    border: 1px solid {_th["accent"]}70 !important;
    width: 100%; font-size: 0.9rem !important;
}}
.stForm [data-testid="stFormSubmitButton"] > button:hover {{
    background: linear-gradient(135deg, {_th["accent"]}45, {_th["accent2"]}35) !important;
}}

[data-testid="block-container"] {{ background: transparent !important; }}
[data-testid="stNumberInput"] input {{
    background: rgba(15,23,42,0.85) !important;
    border: 1px solid rgba(255,255,255,0.20) !important;
    border-radius: 10px !important; color: white !important;
    font-family: 'Outfit', sans-serif !important; caret-color: white !important;
}}

/* ── Calendar grid ── */
.cal-card {{
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 20px; padding: 1.4rem 1.2rem 1.2rem; margin-bottom: 1rem;
    box-shadow: 0 8px 40px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.08);
}}
.cal-header {{
    font-size: 1.45rem; font-weight: 800; color: #ffffff !important;
    letter-spacing: 0.01em; text-align: center; margin-bottom: 1rem;
    background: linear-gradient(90deg, {_th["accent"]}, {_th["accent2"]});
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}}
.dow-row {{ display:grid; grid-template-columns:repeat(7,1fr); gap:5px; margin-bottom:7px; }}
.dow-cell {{
    text-align:center; font-size:0.65rem; font-weight:700;
    color: {_th["dow"]} !important;
    letter-spacing:0.10em; text-transform:uppercase; padding:5px 0;
}}
.cal-grid {{ display:grid; grid-template-columns:repeat(7,1fr); gap:5px; }}
.day-cell {{
    min-height:80px;
    background: {_th["grid_bg"]};
    border: 1px solid {_th["grid_b"]};
    border-radius: 12px; padding: 7px 8px 5px; position:relative;
    transition: background 0.15s ease, border-color 0.15s ease;
    cursor: pointer;
}}
.day-cell:hover {{
    background: rgba(255,255,255,0.055) !important;
    border-color: rgba(255,255,255,0.18) !important;
}}
.day-cell.today {{
    background: {_th["today"]} !important;
    border-color: {_th["today_b"]} !important;
    box-shadow: 0 0 0 1px {_th["today_b"]}60, inset 0 1px 0 {_th["accent"]}20;
}}
.day-cell.other-month {{ opacity:0.25; pointer-events:none; }}
.day-num {{
    font-size:0.80rem; font-weight:700; color:#ffffff !important;
    line-height:1; margin-bottom:3px; display:flex; align-items:center; justify-content:space-between;
}}
.day-cell.today .day-num-inner {{
    color: {_th["accent"]} !important;
    background: {_th["accent"]}22;
    border-radius: 6px; padding: 1px 5px; display:inline-block;
}}
.event-chip {{
    font-size:0.62rem; font-weight:600; padding:2px 7px 2px 5px; border-radius:6px;
    margin-top:3px; white-space:nowrap; overflow:hidden;
    text-overflow:ellipsis; max-width:100%; display:flex; align-items:center; gap:4px;
    border-left: 3px solid; line-height: 1.4;
}}
.event-chip-dot {{ width:5px; height:5px; border-radius:50%; flex-shrink:0; }}
.holiday-chip {{
    font-size:0.60rem; font-weight:500; color:rgba(255,230,150,0.85) !important;
    margin-top:2px; display:block; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;
}}
.mood-pip {{
    font-size:0.78rem; float:right; margin-top:-1px;
}}

/* ── Event detail cards ── */
.event-detail {{
    background: rgba(255,255,255,0.055);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 14px; padding: 0.85rem 1.1rem 0.85rem 1.2rem; margin-bottom: 0.55rem;
    transition: background 0.15s ease;
    box-shadow: 0 2px 12px rgba(0,0,0,0.25);
}}
.event-detail:hover {{ background: rgba(255,255,255,0.075); }}
.event-title {{
    font-size: 0.97rem; font-weight: 700; color: #ffffff !important;
    line-height: 1.3; margin-bottom: 4px;
}}
.event-meta {{ font-size:0.76rem; color:rgba(180,200,255,0.75) !important; line-height:1.5; }}

/* ── Badges ── */
.recur-badge {{
    display:inline-flex; align-items:center; gap:3px;
    font-size:0.58rem; font-weight:700; padding:2px 7px;
    border-radius:20px; background:{_th["accent"]}1a;
    border:1px solid {_th["accent"]}55; color:{_th["accent"]} !important;
    margin-left:6px; vertical-align:middle; letter-spacing:0.04em;
}}
.reminder-badge {{
    display:inline-flex; align-items:center;
    font-size:0.58rem; font-weight:700; padding:2px 7px;
    border-radius:20px; background:rgba(255,200,40,0.15);
    border:1px solid rgba(255,210,60,0.45); color:#fff0a0 !important;
    margin-left:4px; vertical-align:middle;
}}
.birthday-badge {{
    display:inline-flex; align-items:center;
    font-size:0.58rem; font-weight:700; padding:2px 7px;
    border-radius:20px; background:rgba(255,120,200,0.15);
    border:1px solid rgba(255,150,200,0.45); color:#ffc0e8 !important;
    margin-left:4px; vertical-align:middle;
}}

/* ── Section heading ── */
.section-heading {{
    font-size:0.65rem; font-weight:700; letter-spacing:0.13em;
    text-transform:uppercase; color:{_th["dow"]} !important;
    margin-bottom:0.65rem; opacity:0.80;
}}

/* ── App title ── */
.app-title {{
    font-size:1.75rem; font-weight:800;
    background: linear-gradient(90deg, {_th["accent"]}, {_th["accent2"]});
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; letter-spacing:0.03em; line-height:1.1;
}}
.app-sub {{
    font-size:0.65rem; color:rgba(180,200,255,0.45) !important;
    letter-spacing:0.13em; text-transform:uppercase; margin-top:2px;
}}

/* ── Misc ── */
hr {{ border:none; border-top:1px solid rgba(255,255,255,0.08) !important; margin:0.9rem 0 !important; }}
.search-result {{
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 13px; padding: 0.75rem 1rem; margin-bottom: 0.5rem;
}}
.reminder-alert {{
    background: rgba(255,200,40,0.12);
    border: 1px solid rgba(255,210,60,0.45);
    border-radius: 13px; padding: 0.75rem 1rem; margin-bottom: 0.55rem;
}}
.stat-card {{
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 16px; padding: 1.1rem; text-align:center;
    transition: transform 0.2s ease;
}}
.stat-card:hover {{ transform: translateY(-2px); }}
.stat-number {{
    font-size: 2.2rem; font-weight: 800;
    background: linear-gradient(90deg, {_th["accent"]}, {_th["accent2"]});
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; line-height: 1;
}}
.stat-label {{
    font-size: 0.72rem; font-weight: 600; color: rgba(180,200,255,0.65) !important;
    letter-spacing: 0.08em; text-transform: uppercase; margin-top: 5px;
}}
.export-card {{
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 16px; padding: 1.2rem 1.4rem; margin-bottom: 1rem;
}}
.mood-row {{
    display: flex; gap: 6px; flex-wrap: wrap; margin: 0.4rem 0;
}}
.mood-btn-selected {{
    background: {_th["accent"]}33 !important;
    border: 2px solid {_th["accent"]} !important;
    border-radius: 8px; padding: 2px 8px; font-size: 1.2rem; cursor:pointer;
}}
.mood-btn {{
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 8px; padding: 2px 8px; font-size: 1.2rem; cursor:pointer;
}}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="app-title">🌌 CosmoCal</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-sub">Your Cosmic Calendar</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown('<div class="section-heading">🎨 Theme</div>', unsafe_allow_html=True)
    chosen_theme = st.selectbox("", list(THEMES.keys()),
                                index=list(THEMES.keys()).index(st.session_state.theme),
                                label_visibility="collapsed", key="theme_sel")
    if chosen_theme != st.session_state.theme:
        st.session_state.theme = chosen_theme
        st.rerun()

    st.markdown("---")

    st.markdown('<div class="section-heading">📅 View</div>', unsafe_allow_html=True)
    view = st.radio("", ["Month","Week","Day","Agenda","Search","📊 Stats","📤 Export"],
                    index=["Month","Week","Day","Agenda","Search","📊 Stats","📤 Export"].index(st.session_state.view)
                    if st.session_state.view in ["Month","Week","Day","Agenda","Search","📊 Stats","📤 Export"] else 0,
                    label_visibility="collapsed")
    st.session_state.view = view

    st.markdown("---")

    # Reminders
    reminders_due = get_upcoming_reminders()
    if reminders_due:
        st.markdown(f'<div style="background:rgba(255,200,40,0.13);border:1px solid rgba(255,210,60,0.40);border-radius:11px;padding:8px 12px;margin-bottom:8px;"><span style="font-size:0.82rem;font-weight:700;color:#fff0a0;">🔔 {len(reminders_due)} reminder{"s" if len(reminders_due)>1 else ""} due!</span></div>', unsafe_allow_html=True)
        for r in reminders_due:
            st.markdown(f'<div class="reminder-alert"><div style="font-size:0.82rem;font-weight:700;color:#fff0a0;">⏰ {r["title"]}</div><div style="font-size:0.70rem;color:rgba(255,240,160,0.75);">In {r["remind_in_min"]} min · {r["evt_dt"].strftime("%H:%M")}</div></div>', unsafe_allow_html=True)
        st.markdown("---")

    # Add Event
    st.markdown('<div class="section-heading">✦ New Event</div>', unsafe_allow_html=True)
    with st.form("add_event_form", clear_on_submit=True):
        evt_date     = st.date_input("Date", value=st.session_state.selected_date)
        evt_title    = st.text_input("Title", placeholder="Event name…")
        evt_time     = st.text_input("Time", placeholder="e.g. 14:00 or All day")
        evt_cat      = st.selectbox("Category", list(CATEGORY_COLORS.keys()))
        evt_note     = st.text_area("Notes", placeholder="Optional notes…", height=55)
        evt_recur    = st.selectbox("🔁 Recurrence", RECURRENCE_OPTIONS)
        evt_reminder = st.selectbox("🔔 Reminder", [0,5,10,15,30,60,120],
                                    format_func=lambda x: "None" if x==0 else f"{x} min before")
        evt_birthday = st.checkbox("🎂 This is a birthday")
        if st.form_submit_button("＋ Add Event", use_container_width=True) and evt_title.strip():
            recur = "Yearly" if evt_birthday else evt_recur
            add_event(evt_date, evt_title.strip(), evt_time or "All day",
                      evt_cat, evt_note, recur, evt_reminder, evt_birthday)
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
            if view == "Month":
                m,y = d.month-1, d.year
                if m == 0: m,y = 12, y-1
                st.session_state.current_date = d.replace(year=y, month=m, day=1)
            elif view == "Week":
                st.session_state.current_date = d - timedelta(weeks=1)
            else:
                st.session_state.current_date = d - timedelta(days=1)
            st.rerun()
    with c2:
        if st.button("Today", use_container_width=True):
            st.session_state.current_date = date.today()
            st.session_state.selected_date = date.today()
            st.rerun()
    with c3:
        if st.button("▶", use_container_width=True):
            d = st.session_state.current_date
            if view == "Month":
                m,y = d.month+1, d.year
                if m == 13: m,y = 1, y+1
                st.session_state.current_date = d.replace(year=y, month=m, day=1)
            elif view == "Week":
                st.session_state.current_date = d + timedelta(weeks=1)
            else:
                st.session_state.current_date = d + timedelta(days=1)
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# EDIT MODAL
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
    <div style="background:rgba(15,22,55,0.80);border:1px solid {_th["accent"]}55;
    border-radius:18px;padding:1.4rem 1.6rem;margin-bottom:1.2rem;
    box-shadow:0 8px 40px rgba(0,0,0,0.5);">
    <div style="font-size:1rem;font-weight:700;
    background:linear-gradient(90deg,{_th["accent"]},{_th["accent2"]});
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    background-clip:text;margin-bottom:1rem;">✏️ Edit — {date_str}</div>
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
            if st.form_submit_button("💾 Save", use_container_width=True) and e_title.strip():
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
    c = get_color(e.get("category","⚪ Other"))
    recur = e.get("recurrence","None")
    reminder = e.get("reminder_min", 0)
    is_birthday = e.get("is_birthday", False)
    recur_badge    = f'<span class="recur-badge">🔁 {recur}</span>' if recur != "None" else ""
    reminder_badge = f'<span class="reminder-badge">🔔 {reminder}m</span>' if reminder else ""
    birthday_badge = f'<span class="birthday-badge">🎂 Birthday</span>' if is_birthday else ""
    recurring_tag  = ' <span style="font-size:0.63rem;color:rgba(200,200,255,0.4);">(recurring)</span>' if e.get("_recurring") else ""

    col_e, col_edit, col_del = st.columns([9, 1, 1])
    with col_e:
        st.markdown(
            f'<div class="event-detail" style="border-left:4px solid {c["border"]}">'
            f'<div class="event-title">{e["title"]}{recur_badge}{reminder_badge}{birthday_badge}{recurring_tag}</div>'
            f'<div class="event-meta">🕐 {e.get("time","All day")} &nbsp;·&nbsp; {e.get("category","")}'
            f'{"<br>" + e["note"] if e.get("note") else ""}</div></div>',
            unsafe_allow_html=True)
    with col_edit:
        if not e.get("_recurring"):
            if st.button("✏️", key=f"{key_prefix}_edit_{date_str}_{idx}", help="Edit"):
                st.session_state.editing_evt = {"date_str": date_str, "idx": idx}
                st.rerun()
    with col_del:
        if not e.get("_recurring"):
            if st.button("🗑", key=f"{key_prefix}_del_{date_str}_{idx}", help="Delete"):
                delete_event(date.fromisoformat(date_str), idx)
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════
today = date.today()
cd    = st.session_state.current_date

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
            holiday = get_holiday(day)
            mood_key = day.isoformat()
            mood = st.session_state.moods.get(mood_key, "")
            num_inner = f'<span class="day-num-inner">{day.day}</span>' if is_today else str(day.day)
            mood_pip = f'<span class="mood-pip">{mood}</span>' if mood else ""
            html += f'<div class="{css}"><div class="day-num">{num_inner}{mood_pip}</div>'
            if holiday:
                html += f'<span class="holiday-chip">{holiday}</span>'
            day_evts = events_for_date(day)
            for e in day_evts[:2]:
                c = get_color(e.get("category","⚪ Other"))
                icon = "🎂" if e.get("is_birthday") else ("🔁" if (e.get("recurrence","None") != "None" or e.get("_recurring")) else "")
                html += (f'<span class="event-chip" style="background:{c["bg"]};'
                         f'color:{c["text"]};border-left-color:{c["border"]}">'
                         f'<span class="event-chip-dot" style="background:{c["dot"]}"></span>'
                         f'{e["title"]}{" "+icon if icon else ""}</span>')
            if len(day_evts) > 2:
                html += f'<span style="font-size:0.60rem;color:rgba(200,210,255,0.5);margin-top:2px;display:block;">+{len(day_evts)-2} more</span>'
            html += '</div>'
    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)

    # Selected day panel
    sel = st.session_state.selected_date
    sel_label = "Today" if sel == today else sel.strftime("%A, %B %-d, %Y")
    st.markdown(f'<div class="section-heading">Events — {sel_label}</div>', unsafe_allow_html=True)

    # Mood tracker for selected date
    mood_key = sel.isoformat()
    current_mood = st.session_state.moods.get(mood_key, "")
    st.markdown(f'<div style="font-size:0.72rem;color:rgba(180,200,255,0.65);margin-bottom:6px;font-weight:500;">How are you feeling today?</div>', unsafe_allow_html=True)
    mood_cols = st.columns(len(MOOD_OPTIONS))
    for i, m in enumerate(MOOD_OPTIONS):
        if not m:
            continue
        with mood_cols[i]:
            selected = (current_mood == m)
            if st.button(m, key=f"mood_{mood_key}_{i}",
                         help=f"Set mood: {m}",
                         type="primary" if selected else "secondary"):
                if current_mood == m:
                    del st.session_state.moods[mood_key]
                else:
                    st.session_state.moods[mood_key] = m
                save_moods(st.session_state.moods)
                st.rerun()

    sel_evts = events_for_date(sel)
    if sel_evts:
        for i, e in enumerate(sel_evts):
            event_row(e, sel.isoformat(), i, "m")
    else:
        holiday = get_holiday(sel)
        if holiday:
            st.markdown(f'<div style="background:rgba(255,220,80,0.10);border:1px solid rgba(255,220,80,0.30);border-radius:12px;padding:10px 14px;margin-bottom:0.5rem;font-size:0.88rem;color:rgba(255,230,130,0.90);">{holiday}</div>', unsafe_allow_html=True)
        st.markdown('<p style="color:rgba(200,210,255,0.35);font-size:0.85rem">No events — add one from the sidebar.</p>', unsafe_allow_html=True)

    pick = st.date_input("Jump to date", value=sel, label_visibility="collapsed", key="jump_picker")
    if pick != sel:
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
    st.markdown(f'<div class="cal-header" style="text-align:left">{week_label}</div>', unsafe_allow_html=True)

    cols = st.columns(7)
    for i, day in enumerate(week_days):
        with cols[i]:
            is_today = (day == today)
            bg = f"{_th['today']}" if is_today else _th["grid_bg"]
            bc = f"{_th['today_b']}" if is_today else _th["grid_b"]
            holiday = get_holiday(day)
            mood = st.session_state.moods.get(day.isoformat(), "")
            st.markdown(
                f'<div style="background:{bg};border:1px solid {bc};border-radius:14px;'
                f'padding:10px 8px;min-height:190px;box-shadow:0 2px 12px rgba(0,0,0,0.2);">'
                f'<div style="font-size:0.62rem;font-weight:700;letter-spacing:.09em;'
                f'color:{_th["dow"]}">{day.strftime("%a").upper()}</div>'
                f'<div style="font-size:1.2rem;font-weight:800;margin-bottom:2px;'
                f'color:{""+_th["accent"] if is_today else "#ffffff"}">{day.day} {mood}</div>'
                f'{"<div style=\"font-size:0.58rem;color:rgba(255,220,100,0.80);margin-bottom:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;\">"+holiday+"</div>" if holiday else ""}',
                unsafe_allow_html=True)
            for e in events_for_date(day):
                c = get_color(e.get("category","⚪ Other"))
                icon = "🎂" if e.get("is_birthday") else ("🔁" if e.get("recurrence","None") != "None" or e.get("_recurring") else "")
                st.markdown(
                    f'<div style="font-size:0.66rem;font-weight:600;padding:3px 7px;border-radius:7px;'
                    f'background:{c["bg"]};color:{c["text"]};border-left:3px solid {c["border"]};'
                    f'margin-top:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">'
                    f'{e.get("time","")} {e["title"]} {icon}</div>', unsafe_allow_html=True)
            if not events_for_date(day):
                st.markdown('<div style="font-size:0.62rem;color:rgba(255,255,255,0.20);margin-top:8px">—</div>', unsafe_allow_html=True)
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
    holiday = get_holiday(cd)
    mood = st.session_state.moods.get(cd.isoformat(), "")
    title_suffix = f" {mood}" if mood else ""
    st.markdown(f'<div class="cal-header" style="text-align:left;font-size:1.4rem">'
                f'{cd.strftime("%A, %B %-d, %Y")}{title_suffix}</div>', unsafe_allow_html=True)
    if holiday:
        st.markdown(f'<div style="background:rgba(255,220,80,0.10);border:1px solid rgba(255,220,80,0.28);border-radius:11px;padding:8px 14px;margin-bottom:1rem;font-size:0.88rem;color:rgba(255,230,130,0.90);">{holiday}</div>', unsafe_allow_html=True)

    evts = events_for_date(cd)
    if evts:
        st.markdown('<div class="section-heading">Today\'s Events</div>', unsafe_allow_html=True)
        for i, e in enumerate(evts):
            event_row(e, cd.isoformat(), i, "d")
    else:
        st.markdown('<p style="color:rgba(200,210,255,0.35);font-size:0.85rem;margin-bottom:1rem;">No events today — add one from the sidebar.</p>', unsafe_allow_html=True)

    import streamlit.components.v1 as components
    evts_json = json.dumps([
        {"title": e["title"], "time": e.get("time","All day"),
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
body{{font-family:'Outfit',sans-serif;background:transparent;color:#fff;}}
#tl-wrap{{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.09);border-radius:16px;padding:14px 16px;}}
#tl-hint{{font-size:10px;color:rgba(160,190,255,0.60);margin-bottom:10px;font-weight:600;letter-spacing:0.07em;text-transform:uppercase;}}
#tl-scroll{{overflow-y:auto;max-height:520px;position:relative;}}
#tl-inner{{position:relative;height:1248px;}}
.hour-row{{position:absolute;left:0;right:0;height:52px;display:flex;align-items:flex-start;border-top:1px solid rgba(255,255,255,0.05);}}
.hour-label{{font-size:10px;font-weight:600;color:rgba(140,180,255,0.60);min-width:42px;padding-top:3px;letter-spacing:0.04em;flex-shrink:0;}}
.hour-stripe{{flex:1;height:100%;position:relative;}}
.half-line{{position:absolute;top:50%;left:0;right:0;height:1px;background:rgba(255,255,255,0.03);pointer-events:none;}}
.evt-block{{position:absolute;left:44px;right:0;border-radius:8px;padding:4px 10px;font-size:12px;font-weight:600;pointer-events:none;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;z-index:2;border-left:3px solid;}}
#now-marker{{position:absolute;left:42px;right:0;height:2px;background:rgba(255,100,100,0.85);z-index:5;pointer-events:none;}}
#now-dot{{position:absolute;left:37px;width:8px;height:8px;background:rgba(255,100,100,0.85);border-radius:50%;margin-top:-3px;z-index:5;pointer-events:none;box-shadow:0 0 8px rgba(255,100,100,0.6);}}
</style></head><body>
<div id="tl-wrap">
  <div id="tl-hint">24-Hour Timeline</div>
  <div id="tl-scroll"><div id="tl-inner">
    <div id="now-marker"></div><div id="now-dot"></div>
  </div></div>
</div>
<script>
const HOUR_PX=52;
const events={evts_json};
function timeStrToHour(t){{if(!t||t==="All day")return null;const[h,m]=t.split(":").map(Number);return h+(m||0)/60;}}
const inner=document.getElementById("tl-inner");
for(let h=0;h<24;h++){{
  const row=document.createElement("div");row.className="hour-row";row.style.top=(h*HOUR_PX)+"px";
  const lbl=document.createElement("div");lbl.className="hour-label";lbl.textContent=h.toString().padStart(2,"0")+":00";
  const stripe=document.createElement("div");stripe.className="hour-stripe";
  const half=document.createElement("div");half.className="half-line";stripe.appendChild(half);
  row.appendChild(lbl);row.appendChild(stripe);inner.appendChild(row);
}}
events.forEach(e=>{{
  const h=timeStrToHour(e.time);if(h===null)return;
  const block=document.createElement("div");block.className="evt-block";
  block.style.top=(h*HOUR_PX)+"px";block.style.height=HOUR_PX+"px";
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
    st.markdown('<div class="cal-header" style="text-align:left">Upcoming Events</div>', unsafe_allow_html=True)
    found_any = False
    for delta in range(60):
        check = today + timedelta(days=delta)
        evts  = events_for_date(check)
        holiday = get_holiday(check)
        if evts or holiday:
            found_any = True
            is_today  = (check == today)
            label = "Today" if is_today else check.strftime("%A, %B %-d")
            mood  = st.session_state.moods.get(check.isoformat(), "")
            st.markdown(
                f'<div style="font-size:0.72rem;font-weight:700;'
                f'color:{""+_th["accent"] if is_today else _th["dow"]};'
                f'margin:1.1rem 0 0.35rem;letter-spacing:.08em;text-transform:uppercase">'
                f'{label} {mood}</div>', unsafe_allow_html=True)
            if holiday:
                st.markdown(f'<div style="font-size:0.78rem;color:rgba(255,230,130,0.85);margin-bottom:4px;">{holiday}</div>', unsafe_allow_html=True)
            for i, e in enumerate(evts):
                event_row(e, check.isoformat(), i, "ag")
    if not found_any:
        st.markdown('<div style="text-align:center;padding:4rem 0;color:rgba(200,210,255,0.30);">🌌 No upcoming events in the next 60 days.</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SEARCH VIEW
# ─────────────────────────────────────────────────────────────────────────────
elif view == "Search":
    st.markdown('<div class="cal-header" style="text-align:left">🔍 Search Events</div>', unsafe_allow_html=True)
    query = st.text_input("", placeholder="Search by title, notes, or category…",
                          label_visibility="collapsed", key="search_input")
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
                        f'<div style="font-size:0.68rem;color:{_th["dow"]};margin-bottom:3px;">📅 {r["date_str"]}</div>'
                        f'<div class="event-title">{r["title"]}{recur_badge}{remind_badge}</div>'
                        f'<div class="event-meta">🕐 {r.get("time","All day")} · {r.get("category","")}'
                        f'{"<br>"+r["note"] if r.get("note") else ""}</div></div>', unsafe_allow_html=True)
                with col_edit:
                    if st.button("✏️", key=f"sr_edit_{r['date_str']}_{r['idx']}", help="Edit"):
                        st.session_state.editing_evt = {"date_str": r["date_str"], "idx": r["idx"]}
                        st.rerun()
                with col_del:
                    if st.button("🗑", key=f"sr_del_{r['date_str']}_{r['idx']}", help="Delete"):
                        delete_event(date.fromisoformat(r["date_str"]), r["idx"])
                        st.rerun()
        else:
            st.markdown(f'<div style="color:rgba(200,210,255,0.35);padding:2rem 0;text-align:center;">🌌 No events found for "{query}"</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:rgba(200,210,255,0.28);padding:2rem 0;text-align:center;">Start typing to search your events…</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# STATS VIEW  ✨ NEW
# ─────────────────────────────────────────────────────────────────────────────
elif view == "📊 Stats":
    st.markdown('<div class="cal-header" style="text-align:left">📊 Calendar Insights</div>', unsafe_allow_html=True)

    all_evts = [(ds, e) for ds, evts in st.session_state.events.items() for e in evts]
    total    = len(all_evts)

    if not total:
        st.markdown('<div style="text-align:center;padding:4rem 0;color:rgba(200,210,255,0.30);">🌌 No events yet. Add some to see your insights!</div>', unsafe_allow_html=True)
    else:
        # Top stats
        today_count   = len(events_for_date(today))
        week_start    = today - timedelta(days=(today.weekday()+1)%7)
        week_count    = sum(len(events_for_date(week_start + timedelta(days=i))) for i in range(7))
        birthday_count = sum(1 for _, e in all_evts if e.get("is_birthday"))
        recurring_count = sum(1 for _, e in all_evts if e.get("recurrence","None") != "None")

        c1, c2, c3, c4 = st.columns(4)
        for col, num, label in [
            (c1, total, "Total Events"),
            (c2, today_count, "Today"),
            (c3, week_count, "This Week"),
            (c4, birthday_count, "🎂 Birthdays"),
        ]:
            with col:
                st.markdown(f'<div class="stat-card"><div class="stat-number">{num}</div><div class="stat-label">{label}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Category breakdown
        st.markdown('<div class="section-heading">Events by Category</div>', unsafe_allow_html=True)
        cat_counts = {}
        for _, e in all_evts:
            cat = e.get("category","⚪ Other")
            cat_counts[cat] = cat_counts.get(cat,0) + 1
        sorted_cats = sorted(cat_counts.items(), key=lambda x: -x[1])
        max_count = sorted_cats[0][1] if sorted_cats else 1

        for cat, count in sorted_cats:
            c = get_color(cat)
            pct = count / max_count
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">'
                f'<div style="width:120px;font-size:0.78rem;font-weight:600;color:{c["text"]};white-space:nowrap;">{cat}</div>'
                f'<div style="flex:1;background:rgba(255,255,255,0.07);border-radius:8px;height:10px;overflow:hidden;">'
                f'<div style="width:{int(pct*100)}%;height:100%;background:{c["border"]};border-radius:8px;'
                f'transition:width 0.5s ease;"></div></div>'
                f'<div style="width:28px;font-size:0.78rem;font-weight:700;color:{c["text"]};text-align:right;">{count}</div>'
                f'</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Mood summary
        if st.session_state.moods:
            st.markdown('<div class="section-heading">Your Mood History</div>', unsafe_allow_html=True)
            mood_counts = {}
            for m in st.session_state.moods.values():
                if m:
                    mood_counts[m] = mood_counts.get(m,0) + 1
            sorted_moods = sorted(mood_counts.items(), key=lambda x: -x[1])
            mood_cols = st.columns(min(len(sorted_moods), 5))
            for i, (m, cnt) in enumerate(sorted_moods[:5]):
                with mood_cols[i]:
                    st.markdown(
                        f'<div class="stat-card"><div style="font-size:2rem">{m}</div>'
                        f'<div class="stat-number" style="font-size:1.5rem">{cnt}</div>'
                        f'<div class="stat-label">days</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Upcoming birthdays
        birthdays = [(ds, e) for ds, e in all_evts if e.get("is_birthday")]
        if birthdays:
            st.markdown('<div class="section-heading">🎂 Upcoming Birthdays</div>', unsafe_allow_html=True)
            upcoming = []
            for ds, e in birthdays:
                try:
                    orig = date.fromisoformat(ds)
                    next_bday = orig.replace(year=today.year)
                    if next_bday < today:
                        next_bday = next_bday.replace(year=today.year+1)
                    days_away = (next_bday - today).days
                    upcoming.append((days_away, next_bday, e["title"]))
                except Exception:
                    pass
            for days_away, bday_date, name in sorted(upcoming)[:5]:
                label = "Today! 🎉" if days_away == 0 else f"in {days_away} day{'s' if days_away!=1 else ''}"
                st.markdown(
                    f'<div class="event-detail" style="border-left:4px solid rgba(255,150,200,0.85)">'
                    f'<div class="event-title">🎂 {name}</div>'
                    f'<div class="event-meta">{bday_date.strftime("%B %-d")} · {label}</div>'
                    f'</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Busiest days
        st.markdown('<div class="section-heading">Busiest Days (Next 30 Days)</div>', unsafe_allow_html=True)
        day_loads = []
        for delta in range(30):
            d = today + timedelta(days=delta)
            count = len(events_for_date(d))
            if count > 0:
                day_loads.append((count, d))
        day_loads.sort(reverse=True)
        for count, d in day_loads[:5]:
            is_today = (d == today)
            label = "Today" if is_today else d.strftime("%A, %B %-d")
            st.markdown(
                f'<div style="display:flex;align-items:center;justify-content:space-between;'
                f'background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);'
                f'border-radius:10px;padding:8px 14px;margin-bottom:6px;">'
                f'<span style="font-size:0.85rem;font-weight:600;color:#fff">{label}</span>'
                f'<span style="font-size:0.78rem;font-weight:700;color:{_th["accent"]}">{count} event{"s" if count!=1 else ""}</span>'
                f'</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# EXPORT VIEW  ✨ NEW
# ─────────────────────────────────────────────────────────────────────────────
elif view == "📤 Export":
    st.markdown('<div class="cal-header" style="text-align:left">📤 Export & Import</div>', unsafe_allow_html=True)

    total_events = sum(len(v) for v in st.session_state.events.values())
    st.markdown(f'<div style="color:rgba(180,200,255,0.60);font-size:0.85rem;margin-bottom:1.2rem;">{total_events} event{"s" if total_events!=1 else ""} in your calendar</div>', unsafe_allow_html=True)

    # Export
    st.markdown('<div class="export-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">⬇️ Export Your Events</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        csv_data = export_events_csv()
        st.download_button(
            "📄 Download as CSV",
            data=csv_data,
            file_name=f"cosmo_events_{today.isoformat()}.csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.markdown('<div style="font-size:0.72rem;color:rgba(180,200,255,0.50);margin-top:4px;">Opens in Excel, Google Sheets, etc.</div>', unsafe_allow_html=True)
    with col2:
        json_data = export_events_json()
        st.download_button(
            "🗂 Download as JSON",
            data=json_data,
            file_name=f"cosmo_events_{today.isoformat()}.json",
            mime="application/json",
            use_container_width=True,
        )
        st.markdown('<div style="font-size:0.72rem;color:rgba(180,200,255,0.50);margin-top:4px;">For backup or re-import.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Import
    st.markdown('<div class="export-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">⬆️ Import Events (JSON)</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload a previously exported CosmoCal JSON file", type=["json"])
    if uploaded:
        raw = uploaded.read().decode("utf-8")
        if st.button("📥 Import Events", use_container_width=True):
            success = import_events_json(raw)
            if success:
                st.success(f"Events imported successfully! 🌠")
                st.rerun()
            else:
                st.error("Import failed — please check the file format.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Holiday presets
    st.markdown('<div class="export-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">🎉 Add Holiday Presets</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.82rem;color:rgba(180,200,255,0.60);margin-bottom:0.8rem;">Add US holidays for a specific year to your calendar.</div>', unsafe_allow_html=True)
    year_for_holidays = st.number_input("Year", min_value=2024, max_value=2030, value=today.year, step=1)
    if st.button("🎊 Add All US Holidays", use_container_width=True):
        added = 0
        for mmdd, name in US_HOLIDAYS.items():
            try:
                month, day = map(int, mmdd.split("-"))
                hdate = date(int(year_for_holidays), month, day)
                key = hdate.isoformat()
                existing_titles = [e["title"] for e in st.session_state.events.get(key, [])]
                if name not in existing_titles:
                    add_event(hdate, name, "All day", "🟡 Social", "", "None", 0)
                    added += 1
            except Exception:
                pass
        save_events(st.session_state.events)
        st.success(f"Added {added} holidays for {year_for_holidays}! 🎆")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
