import streamlit as st
import json
import calendar
import os
from datetime import datetime, date, timedelta

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CosmoCal",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Glassmorphism dark theme ──────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
  /* ── Base ── */
  html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }

  .stApp {
    background: linear-gradient(135deg, #0a0a1a 0%, #0d1b2a 40%, #0a0a1a 100%);
    min-height: 100vh;
  }

  /* Animated starfield */
  .stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
      radial-gradient(1px 1px at 10% 20%, rgba(255,255,255,0.6) 0%, transparent 100%),
      radial-gradient(1px 1px at 25% 75%, rgba(255,255,255,0.4) 0%, transparent 100%),
      radial-gradient(1px 1px at 40% 10%, rgba(255,255,255,0.5) 0%, transparent 100%),
      radial-gradient(1px 1px at 60% 50%, rgba(255,255,255,0.3) 0%, transparent 100%),
      radial-gradient(1px 1px at 75% 30%, rgba(255,255,255,0.6) 0%, transparent 100%),
      radial-gradient(1px 1px at 85% 80%, rgba(255,255,255,0.4) 0%, transparent 100%),
      radial-gradient(2px 2px at 15% 55%, rgba(140,200,255,0.3) 0%, transparent 100%),
      radial-gradient(2px 2px at 90% 15%, rgba(200,160,255,0.3) 0%, transparent 100%),
      radial-gradient(1px 1px at 50% 90%, rgba(255,255,255,0.5) 0%, transparent 100%),
      radial-gradient(1px 1px at 70% 65%, rgba(255,255,255,0.4) 0%, transparent 100%);
    pointer-events: none;
    z-index: 0;
    animation: twinkle 8s ease-in-out infinite alternate;
  }

  @keyframes twinkle {
    0%   { opacity: 0.5; }
    100% { opacity: 1.0; }
  }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background: rgba(255,255,255,0.04) !important;
    backdrop-filter: blur(20px) !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
  }
  [data-testid="stSidebar"] * { color: rgba(255,255,255,0.9) !important; }

  /* ── Buttons ── */
  .stButton > button {
    background: rgba(100,160,255,0.12) !important;
    color: rgba(255,255,255,0.9) !important;
    border: 1px solid rgba(100,160,255,0.3) !important;
    border-radius: 10px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
  }
  .stButton > button:hover {
    background: rgba(100,160,255,0.25) !important;
    border-color: rgba(100,160,255,0.6) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(100,160,255,0.2) !important;
  }

  /* ── Inputs ── */
  .stTextInput > div > div > input,
  .stTextArea > div > div > textarea,
  .stSelectbox > div > div,
  .stDateInput > div > div > input,
  .stTimeInput > div > div > input {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: rgba(255,255,255,0.9) !important;
    font-family: 'Outfit', sans-serif !important;
  }

  /* ── Selectbox ── */
  [data-baseweb="select"] > div {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: white !important;
  }

  /* ── Labels ── */
  .stTextInput label, .stTextArea label, .stSelectbox label,
  .stDateInput label, .stTimeInput label, .stCheckbox label,
  .stRadio label, p, span, div {
    color: rgba(255,255,255,0.85) !important;
    font-family: 'Outfit', sans-serif !important;
  }

  /* ── Calendar grid glass card ── */
  .cal-card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 18px;
    padding: 1.5rem;
    margin-bottom: 1rem;
  }

  /* ── Calendar header ── */
  .cal-header {
    font-size: 1.6rem;
    font-weight: 700;
    color: rgba(255,255,255,0.95) !important;
    letter-spacing: 0.02em;
    text-align: center;
    margin-bottom: 1rem;
  }

  /* ── Day-of-week row ── */
  .dow-row {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 4px;
    margin-bottom: 6px;
  }
  .dow-cell {
    text-align: center;
    font-size: 0.72rem;
    font-weight: 600;
    color: rgba(140,180,255,0.7) !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 4px 0;
  }

  /* ── Day cells ── */
  .cal-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 4px;
  }
  .day-cell {
    min-height: 72px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 6px 8px;
    transition: background 0.2s;
    position: relative;
  }
  .day-cell:hover { background: rgba(100,160,255,0.08); }
  .day-cell.today {
    background: rgba(100,160,255,0.15);
    border-color: rgba(100,160,255,0.45);
  }
  .day-cell.other-month { opacity: 0.3; }
  .day-num {
    font-size: 0.82rem;
    font-weight: 600;
    color: rgba(255,255,255,0.7) !important;
    line-height: 1;
  }
  .day-cell.today .day-num {
    color: #64a0ff !important;
    font-weight: 700;
  }

  /* ── Event chips ── */
  .event-chip {
    font-size: 0.68rem;
    font-weight: 500;
    padding: 2px 6px;
    border-radius: 5px;
    margin-top: 3px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%;
    display: block;
  }

  /* ── Event detail card ── */
  .event-detail {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 14px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.6rem;
    position: relative;
  }
  .event-title {
    font-size: 1rem;
    font-weight: 600;
    color: rgba(255,255,255,0.95) !important;
  }
  .event-meta {
    font-size: 0.78rem;
    color: rgba(200,200,255,0.6) !important;
    margin-top: 2px;
  }

  /* ── Section heading ── */
  .section-heading {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(140,180,255,0.55) !important;
    margin-bottom: 0.6rem;
  }

  /* ── App title ── */
  .app-title {
    font-size: 1.9rem;
    font-weight: 700;
    background: linear-gradient(90deg, #64a0ff, #b060ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 0.04em;
  }
  .app-sub {
    font-size: 0.8rem;
    color: rgba(200,200,255,0.45) !important;
    letter-spacing: 0.08em;
  }

  /* ── Divider ── */
  hr { border-color: rgba(255,255,255,0.08) !important; }

  /* Fix Streamlit native elements in dark bg */
  [data-testid="stMarkdownContainer"] p { color: rgba(255,255,255,0.85) !important; }
  .stAlert { background: rgba(255,255,255,0.06) !important; border-radius: 12px !important; }
</style>
""", unsafe_allow_html=True)

# ── Data persistence ──────────────────────────────────────────────────────────
DATA_FILE = "cosmo_events.json"

def load_events():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {}

def save_events(events):
    with open(DATA_FILE, "w") as f:
        json.dump(events, f, indent=2)

if "events" not in st.session_state:
    st.session_state.events = load_events()

if "view" not in st.session_state:
    st.session_state.view = "Month"

if "current_date" not in st.session_state:
    st.session_state.current_date = date.today()

if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today()

# ── Colour palette for event categories ──────────────────────────────────────
CATEGORY_COLORS = {
    "🔵 Work":      {"bg": "rgba(60,120,255,0.25)",  "border": "rgba(60,120,255,0.7)",  "text": "#a0c0ff"},
    "🟣 Personal":  {"bg": "rgba(160,80,255,0.25)",  "border": "rgba(160,80,255,0.7)",  "text": "#d0a0ff"},
    "🟢 Health":    {"bg": "rgba(40,200,120,0.25)",  "border": "rgba(40,200,120,0.7)",  "text": "#80e8b0"},
    "🟡 Social":    {"bg": "rgba(255,200,40,0.20)",  "border": "rgba(255,200,40,0.7)",  "text": "#ffe080"},
    "🔴 Important": {"bg": "rgba(255,80,80,0.25)",   "border": "rgba(255,80,80,0.7)",   "text": "#ff9090"},
    "⚪ Other":     {"bg": "rgba(180,180,200,0.15)", "border": "rgba(180,180,200,0.5)", "text": "#c0c0d0"},
}

def get_color(cat):
    return CATEGORY_COLORS.get(cat, CATEGORY_COLORS["⚪ Other"])

# ── Helpers ───────────────────────────────────────────────────────────────────
def events_for_date(d: date):
    key = d.isoformat()
    return st.session_state.events.get(key, [])

def add_event(d: date, title, time_str, category, note):
    key = d.isoformat()
    if key not in st.session_state.events:
        st.session_state.events[key] = []
    st.session_state.events[key].append({
        "title": title,
        "time": time_str,
        "category": category,
        "note": note,
        "id": datetime.now().timestamp(),
    })
    save_events(st.session_state.events)

def delete_event(d: date, idx):
    key = d.isoformat()
    if key in st.session_state.events:
        st.session_state.events[key].pop(idx)
        if not st.session_state.events[key]:
            del st.session_state.events[key]
        save_events(st.session_state.events)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="app-title">🌌 CosmoCal</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-sub">YOUR COSMIC CALENDAR</div>', unsafe_allow_html=True)
    st.markdown("---")

    # View switcher
    st.markdown('<div class="section-heading">View</div>', unsafe_allow_html=True)
    view = st.radio("", ["Month", "Week", "Day", "Agenda"], index=["Month","Week","Day","Agenda"].index(st.session_state.view), label_visibility="collapsed")
    st.session_state.view = view

    st.markdown("---")

    # Add event form
    st.markdown('<div class="section-heading">✦ New Event</div>', unsafe_allow_html=True)
    with st.form("add_event_form", clear_on_submit=True):
        evt_date   = st.date_input("Date", value=st.session_state.selected_date)
        evt_title  = st.text_input("Title", placeholder="Event name…")
        evt_time   = st.text_input("Time", placeholder="e.g. 14:00 or All day")
        evt_cat    = st.selectbox("Category", list(CATEGORY_COLORS.keys()))
        evt_note   = st.text_area("Notes", placeholder="Optional notes…", height=80)
        submitted  = st.form_submit_button("＋ Add Event", use_container_width=True)
        if submitted and evt_title.strip():
            add_event(evt_date, evt_title.strip(), evt_time or "All day", evt_cat, evt_note)
            st.session_state.selected_date = evt_date
            st.success("Event added! 🌠")
            st.rerun()

    st.markdown("---")

    # Navigation
    st.markdown('<div class="section-heading">Navigate</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        if st.button("◀", use_container_width=True):
            d = st.session_state.current_date
            if view == "Month":
                m, y = d.month - 1, d.year
                if m == 0: m, y = 12, y - 1
                st.session_state.current_date = d.replace(year=y, month=m, day=1)
            elif view == "Week":
                st.session_state.current_date = d - timedelta(weeks=1)
            else:
                st.session_state.current_date = d - timedelta(days=1)
            st.rerun()
    with col2:
        if st.button("Today", use_container_width=True):
            st.session_state.current_date = date.today()
            st.session_state.selected_date = date.today()
            st.rerun()
    with col3:
        if st.button("▶", use_container_width=True):
            d = st.session_state.current_date
            if view == "Month":
                m, y = d.month + 1, d.year
                if m == 13: m, y = 1, y + 1
                st.session_state.current_date = d.replace(year=y, month=m, day=1)
            elif view == "Week":
                st.session_state.current_date = d + timedelta(weeks=1)
            else:
                st.session_state.current_date = d + timedelta(days=1)
            st.rerun()

# ── Main area ─────────────────────────────────────────────────────────────────
today = date.today()
cd    = st.session_state.current_date

# ════════════════════════════════════════════════════════════════════════════
# MONTH VIEW
# ════════════════════════════════════════════════════════════════════════════
if view == "Month":
    month_name = cd.strftime("%B %Y")

    html = f'<div class="cal-card">'
    html += f'<div class="cal-header">{month_name}</div>'

    # Day-of-week headers
    html += '<div class="dow-row">'
    for dow in ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]:
        html += f'<div class="dow-cell">{dow}</div>'
    html += '</div>'

    # Build calendar matrix
    cal = calendar.Calendar(firstweekday=6)  # Sunday first
    weeks = cal.monthdatescalendar(cd.year, cd.month)

    html += '<div class="cal-grid">'
    for week in weeks:
        for day in week:
            is_today     = (day == today)
            other_month  = (day.month != cd.month)
            css = "day-cell"
            if is_today:    css += " today"
            if other_month: css += " other-month"

            html += f'<div class="{css}">'
            html += f'<div class="day-num">{day.day}</div>'

            # Show up to 2 event chips
            evts = events_for_date(day)
            for e in evts[:2]:
                c = get_color(e["category"])
                html += (
                    f'<span class="event-chip" '
                    f'style="background:{c["bg"]};color:{c["text"]};'
                    f'border-left:3px solid {c["border"]}">'
                    f'{e["title"]}</span>'
                )
            if len(evts) > 2:
                html += f'<span style="font-size:0.62rem;color:rgba(200,200,255,0.5)">+{len(evts)-2} more</span>'

            html += '</div>'  # day-cell
    html += '</div>'  # cal-grid
    html += '</div>'  # cal-card
    st.markdown(html, unsafe_allow_html=True)

    # ── Selected-date events panel ──
    st.markdown(f'<div class="section-heading">Events — {st.session_state.selected_date.strftime("%A, %B %-d, %Y")}</div>', unsafe_allow_html=True)
    sel_evts = events_for_date(st.session_state.selected_date)
    if sel_evts:
        for i, e in enumerate(sel_evts):
            c = get_color(e["category"])
            col_e, col_d = st.columns([8, 1])
            with col_e:
                st.markdown(
                    f'<div class="event-detail" style="border-left:4px solid {c["border"]}">'
                    f'<div class="event-title">{e["title"]}</div>'
                    f'<div class="event-meta">🕐 {e["time"]} &nbsp;·&nbsp; {e["category"]}'
                    f'{"</div><div class=event-meta>" + e["note"] if e["note"] else ""}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            with col_d:
                if st.button("🗑", key=f"del_{st.session_state.selected_date}_{i}"):
                    delete_event(st.session_state.selected_date, i)
                    st.rerun()
    else:
        st.markdown('<p style="color:rgba(200,200,255,0.4);font-size:0.85rem">No events. Click ✦ New Event to add one.</p>', unsafe_allow_html=True)

    # Click a date (date picker shortcut)
    pick = st.date_input("Jump to date", value=st.session_state.selected_date, label_visibility="collapsed", key="jump_picker")
    if pick != st.session_state.selected_date:
        st.session_state.selected_date = pick
        st.session_state.current_date = pick
        st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# WEEK VIEW
# ════════════════════════════════════════════════════════════════════════════
elif view == "Week":
    # Find Sunday of the week
    dow = (cd.weekday() + 1) % 7  # 0=Sun
    week_start = cd - timedelta(days=dow)
    week_days  = [week_start + timedelta(days=i) for i in range(7)]

    week_label = f"{week_days[0].strftime('%b %-d')} – {week_days[-1].strftime('%b %-d, %Y')}"
    st.markdown(f'<div class="cal-header" style="text-align:left;font-size:1.3rem">{week_label}</div>', unsafe_allow_html=True)

    cols = st.columns(7)
    for i, day in enumerate(week_days):
        with cols[i]:
            is_today = (day == today)
            bg = "rgba(100,160,255,0.15)" if is_today else "rgba(255,255,255,0.04)"
            bc = "rgba(100,160,255,0.45)" if is_today else "rgba(255,255,255,0.09)"
            st.markdown(
                f'<div style="background:{bg};border:1px solid {bc};border-radius:12px;padding:10px 8px;min-height:180px;">'
                f'<div style="font-size:0.7rem;font-weight:600;letter-spacing:.08em;color:rgba(140,180,255,0.7)">{day.strftime("%a").upper()}</div>'
                f'<div style="font-size:1.3rem;font-weight:700;color:{"#64a0ff" if is_today else "rgba(255,255,255,0.85)"}">{day.day}</div>',
                unsafe_allow_html=True
            )
            evts = events_for_date(day)
            for e in evts:
                c = get_color(e["category"])
                st.markdown(
                    f'<div style="font-size:0.7rem;font-weight:500;padding:3px 6px;border-radius:6px;'
                    f'background:{c["bg"]};color:{c["text"]};border-left:3px solid {c["border"]};'
                    f'margin-top:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">'
                    f'{e["time"]} {e["title"]}</div>',
                    unsafe_allow_html=True
                )
            if not evts:
                st.markdown('<div style="font-size:0.68rem;color:rgba(255,255,255,0.2);margin-top:8px">—</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# DAY VIEW
# ════════════════════════════════════════════════════════════════════════════
elif view == "Day":
    st.markdown(f'<div class="cal-header" style="text-align:left;font-size:1.4rem">{cd.strftime("%A, %B %-d, %Y")}</div>', unsafe_allow_html=True)

    evts = events_for_date(cd)
    if evts:
        for i, e in enumerate(evts):
            c = get_color(e["category"])
            col_e, col_d = st.columns([10, 1])
            with col_e:
                st.markdown(
                    f'<div class="event-detail" style="border-left:5px solid {c["border"]};padding:1rem 1.5rem">'
                    f'<div style="font-size:1.1rem;font-weight:600;color:rgba(255,255,255,0.95)">{e["title"]}</div>'
                    f'<div style="font-size:0.8rem;color:rgba(200,200,255,0.6);margin-top:4px">🕐 {e["time"]} &nbsp;·&nbsp; {e["category"]}</div>'
                    f'{"<div style=font-size:0.82rem;color:rgba(200,200,255,0.7);margin-top:8px>" + e["note"] + "</div>" if e["note"] else ""}'
                    f'</div>',
                    unsafe_allow_html=True
                )
            with col_d:
                if st.button("🗑", key=f"day_del_{i}"):
                    delete_event(cd, i)
                    st.rerun()
    else:
        st.markdown(
            '<div style="text-align:center;padding:4rem 0;color:rgba(200,200,255,0.3);font-size:0.9rem">'
            '🌌 Nothing scheduled.<br>Add an event from the sidebar.</div>',
            unsafe_allow_html=True
        )

    # Hour timeline
    st.markdown('<div class="section-heading" style="margin-top:1.5rem">Timeline</div>', unsafe_allow_html=True)
    timed = {e["time"]: e for e in evts if e["time"] != "All day"}
    for h in range(7, 23):
        hstr  = f"{h:02d}:00"
        evt   = timed.get(hstr)
        color = "rgba(255,255,255,0.04)"
        label = ""
        if evt:
            c = get_color(evt["category"])
            color = c["bg"]
            label = f'<span style="color:{c["text"]};font-weight:600">{evt["title"]}</span>'
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:12px;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.04)">'
            f'<span style="font-size:0.72rem;color:rgba(140,180,255,0.5);min-width:42px">{hstr}</span>'
            f'<div style="flex:1;height:28px;background:{color};border-radius:6px;padding:0 10px;'
            f'display:flex;align-items:center;font-size:0.78rem">{label}</div></div>',
            unsafe_allow_html=True
        )

# ════════════════════════════════════════════════════════════════════════════
# AGENDA VIEW
# ════════════════════════════════════════════════════════════════════════════
elif view == "Agenda":
    st.markdown('<div class="cal-header" style="text-align:left;font-size:1.4rem">Upcoming Events</div>', unsafe_allow_html=True)

    # Next 30 days
    found_any = False
    for delta in range(60):
        check = today + timedelta(days=delta)
        evts  = events_for_date(check)
        if evts:
            found_any = True
            is_today  = (check == today)
            label = "Today" if is_today else check.strftime("%A, %B %-d")
            st.markdown(
                f'<div style="font-size:0.78rem;font-weight:600;color:{"#64a0ff" if is_today else "rgba(140,180,255,0.6)"};'
                f'margin:1.2rem 0 0.4rem;letter-spacing:.06em;text-transform:uppercase">{label}</div>',
                unsafe_allow_html=True
            )
            for i, e in enumerate(evts):
                c = get_color(e["category"])
                col_e, col_d = st.columns([10, 1])
                with col_e:
                    st.markdown(
                        f'<div class="event-detail" style="border-left:4px solid {c["border"]}">'
                        f'<div class="event-title">{e["title"]}</div>'
                        f'<div class="event-meta">🕐 {e["time"]} &nbsp;·&nbsp; {e["category"]}'
                        f'{"</div><div class=event-meta>" + e["note"] if e["note"] else ""}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                with col_d:
                    if st.button("🗑", key=f"ag_del_{check}_{i}"):
                        delete_event(check, i)
                        st.rerun()

    if not found_any:
        st.markdown(
            '<div style="text-align:center;padding:4rem 0;color:rgba(200,200,255,0.3);">'
            '🌌 No upcoming events in the next 60 days.</div>',
            unsafe_allow_html=True
        )
