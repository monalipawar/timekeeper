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

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
  html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }

  .stApp {
    background: linear-gradient(135deg, #0a0a1a 0%, #0d1b2a 40%, #0a0a1a 100%) !important;
    min-height: 100vh;
  }

  /* Starfield */
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
      radial-gradient(1px 1px at 50% 90%, rgba(255,255,255,0.5) 0%, transparent 100%);
    pointer-events: none;
    z-index: 0;
    animation: twinkle 8s ease-in-out infinite alternate;
  }
  @keyframes twinkle { 0% { opacity:0.5; } 100% { opacity:1.0; } }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: rgba(10,10,30,0.85) !important;
    backdrop-filter: blur(20px) !important;
    border-right: 1px solid rgba(255,255,255,0.10) !important;
  }

  /* All text white */
  body, p, span, div, label, li, h1, h2, h3, h4, h5, h6,
  .stMarkdown, [data-testid="stMarkdownContainer"],
  [data-testid="stSidebar"] * {
    color: #ffffff !important;
  }

  /* Streamlit widget labels */
  .stTextInput label, .stTextArea label, .stSelectbox label,
  .stDateInput label, .stTimeInput label, .stCheckbox label,
  .stRadio label, .stForm label, .stNumberInput label,
  [data-testid="stWidgetLabel"], .css-81oif8, .css-qrbaxs {
    color: #ffffff !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
  }

  /* Radio labels */
  .stRadio [role="radiogroup"] label { color: #ffffff !important; }

  /* Muted helper text */
  .stCaption, [data-testid="stCaptionContainer"] { color: rgba(200,210,255,0.6) !important; }

  /* Inputs */
  .stTextInput > div > div > input,
  .stTextArea > div > div > textarea,
  .stDateInput > div > div > input {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    font-family: 'Outfit', sans-serif !important;
  }
  .stTextInput > div > div > input::placeholder,
  .stTextArea > div > div > textarea::placeholder { color: rgba(200,210,255,0.4) !important; }

  /* Selectbox */
  [data-baseweb="select"] > div {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    border-radius: 10px !important;
    color: #ffffff !important;
  }
  [data-baseweb="select"] span, [data-baseweb="select"] div { color: #ffffff !important; }

  /* Buttons */
  .stButton > button {
    background: rgba(100,160,255,0.15) !important;
    color: #ffffff !important;
    border: 1px solid rgba(100,160,255,0.40) !important;
    border-radius: 10px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
  }
  .stButton > button:hover {
    background: rgba(100,160,255,0.30) !important;
    border-color: rgba(100,160,255,0.70) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(100,160,255,0.25) !important;
  }
  .stButton > button p { color: #ffffff !important; }

  /* Form submit button */
  .stForm [data-testid="stFormSubmitButton"] > button {
    background: rgba(100,160,255,0.25) !important;
    color: #ffffff !important;
    border: 1px solid rgba(100,160,255,0.55) !important;
    width: 100%;
  }

  /* Alert / info boxes */
  .stAlert, .stSuccess, .element-container .stAlert { border-radius: 12px !important; }

  /* Remove default white bg on main block */
  [data-testid="block-container"] {
    background: transparent !important;
  }

  /* Calendar card */
  .cal-card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 18px;
    padding: 1.4rem;
    margin-bottom: 1rem;
  }
  .cal-header {
    font-size: 1.5rem;
    font-weight: 700;
    color: #ffffff !important;
    letter-spacing: 0.02em;
    text-align: center;
    margin-bottom: 1rem;
  }
  .dow-row { display:grid; grid-template-columns:repeat(7,1fr); gap:4px; margin-bottom:6px; }
  .dow-cell {
    text-align:center; font-size:0.7rem; font-weight:700;
    color: rgba(140,180,255,0.9) !important;
    letter-spacing:0.08em; text-transform:uppercase; padding:4px 0;
  }
  .cal-grid { display:grid; grid-template-columns:repeat(7,1fr); gap:4px; }
  .day-cell {
    min-height:72px;
    background:rgba(255,255,255,0.03);
    border:1px solid rgba(255,255,255,0.08);
    border-radius:10px; padding:6px 8px; position:relative;
  }
  .day-cell.today { background:rgba(100,160,255,0.15); border-color:rgba(100,160,255,0.5); }
  .day-cell.other-month { opacity:0.3; }
  .day-num { font-size:0.82rem; font-weight:700; color:#ffffff !important; line-height:1; }
  .day-cell.today .day-num { color:#64a0ff !important; }
  .event-chip {
    font-size:0.67rem; font-weight:600; padding:2px 6px; border-radius:5px;
    margin-top:3px; white-space:nowrap; overflow:hidden;
    text-overflow:ellipsis; max-width:100%; display:block;
  }

  /* Event detail */
  .event-detail {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.13);
    border-radius: 14px;
    padding: 0.9rem 1.2rem;
    margin-bottom: 0.6rem;
  }
  .event-title { font-size:1rem; font-weight:700; color:#ffffff !important; }
  .event-meta  { font-size:0.78rem; color:rgba(180,200,255,0.8) !important; margin-top:3px; }

  /* Section heading */
  .section-heading {
    font-size:0.68rem; font-weight:700; letter-spacing:0.12em;
    text-transform:uppercase; color:rgba(140,180,255,0.75) !important;
    margin-bottom:0.6rem;
  }

  /* App title */
  .app-title {
    font-size:1.8rem; font-weight:700;
    background: linear-gradient(90deg, #64a0ff, #b060ff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; letter-spacing:0.04em;
  }
  .app-sub { font-size:0.72rem; color:rgba(180,200,255,0.5) !important; letter-spacing:0.1em; }

  hr { border-color:rgba(255,255,255,0.10) !important; }

  /* iframe wrapper */
  iframe { border-radius: 14px !important; }
</style>
""", unsafe_allow_html=True)

# ── Persistence ────────────────────────────────────────────────────────────────
DATA_FILE = "cosmo_events.json"

def load_events():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {}

def save_events(events):
    with open(DATA_FILE, "w") as f:
        json.dump(events, f, indent=2)

if "events"       not in st.session_state: st.session_state.events       = load_events()
if "view"         not in st.session_state: st.session_state.view         = "Month"
if "current_date" not in st.session_state: st.session_state.current_date = date.today()
if "selected_date"not in st.session_state: st.session_state.selected_date= date.today()
# Drag-to-create state
if "drag_start"   not in st.session_state: st.session_state.drag_start   = None
if "drag_end"     not in st.session_state: st.session_state.drag_end     = None
if "pending_evt"  not in st.session_state: st.session_state.pending_evt  = None

CATEGORY_COLORS = {
    "🔵 Work":      {"bg":"rgba(60,120,255,0.28)",  "border":"rgba(80,140,255,0.80)", "text":"#c0d8ff"},
    "🟣 Personal":  {"bg":"rgba(160,80,255,0.28)",  "border":"rgba(180,100,255,0.80)","text":"#e0c0ff"},
    "🟢 Health":    {"bg":"rgba(40,200,120,0.28)",  "border":"rgba(60,220,140,0.80)", "text":"#a0ffd0"},
    "🟡 Social":    {"bg":"rgba(255,200,40,0.22)",  "border":"rgba(255,210,60,0.80)", "text":"#fff0a0"},
    "🔴 Important": {"bg":"rgba(255,80,80,0.28)",   "border":"rgba(255,100,100,0.80)","text":"#ffc0c0"},
    "⚪ Other":     {"bg":"rgba(180,180,200,0.18)", "border":"rgba(200,200,220,0.60)","text":"#e0e0f0"},
}

def get_color(cat):
    return CATEGORY_COLORS.get(cat, CATEGORY_COLORS["⚪ Other"])

def events_for_date(d):
    return st.session_state.events.get(d.isoformat(), [])

def add_event(d, title, time_str, category, note=""):
    key = d.isoformat()
    st.session_state.events.setdefault(key, []).append({
        "title": title, "time": time_str,
        "category": category, "note": note,
        "id": datetime.now().timestamp(),
    })
    save_events(st.session_state.events)

def delete_event(d, idx):
    key = d.isoformat()
    if key in st.session_state.events:
        st.session_state.events[key].pop(idx)
        if not st.session_state.events[key]:
            del st.session_state.events[key]
        save_events(st.session_state.events)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="app-title">🌌 CosmoCal</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-sub">YOUR COSMIC CALENDAR</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown('<div class="section-heading">View</div>', unsafe_allow_html=True)
    view = st.radio("", ["Month","Week","Day","Agenda"],
                    index=["Month","Week","Day","Agenda"].index(st.session_state.view),
                    label_visibility="collapsed")
    st.session_state.view = view
    st.markdown("---")

    st.markdown('<div class="section-heading">✦ New Event</div>', unsafe_allow_html=True)
    with st.form("add_event_form", clear_on_submit=True):
        evt_date  = st.date_input("Date", value=st.session_state.selected_date)
        evt_title = st.text_input("Title", placeholder="Event name…")
        evt_time  = st.text_input("Time", placeholder="e.g. 14:00 or All day")
        evt_cat   = st.selectbox("Category", list(CATEGORY_COLORS.keys()))
        evt_note  = st.text_area("Notes", placeholder="Optional notes…", height=70)
        if st.form_submit_button("＋ Add Event", use_container_width=True) and evt_title.strip():
            add_event(evt_date, evt_title.strip(), evt_time or "All day", evt_cat, evt_note)
            st.session_state.selected_date = evt_date
            st.success("Event added! 🌠")
            st.rerun()

    st.markdown("---")
    st.markdown('<div class="section-heading">Navigate</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c1:
        if st.button("◀", use_container_width=True):
            d = st.session_state.current_date
            if view == "Month":
                m, y = d.month-1, d.year
                if m==0: m,y=12,y-1
                st.session_state.current_date = d.replace(year=y,month=m,day=1)
            elif view=="Week": st.session_state.current_date = d-timedelta(weeks=1)
            else:              st.session_state.current_date = d-timedelta(days=1)
            st.rerun()
    with c2:
        if st.button("Today", use_container_width=True):
            st.session_state.current_date  = date.today()
            st.session_state.selected_date = date.today()
            st.rerun()
    with c3:
        if st.button("▶", use_container_width=True):
            d = st.session_state.current_date
            if view == "Month":
                m, y = d.month+1, d.year
                if m==13: m,y=1,y+1
                st.session_state.current_date = d.replace(year=y,month=m,day=1)
            elif view=="Week": st.session_state.current_date = d+timedelta(weeks=1)
            else:              st.session_state.current_date = d+timedelta(days=1)
            st.rerun()

# ── Helpers ────────────────────────────────────────────────────────────────────
today = date.today()
cd    = st.session_state.current_date

# ═══════════════════════════════════════════════════════════════════════════════
# DRAGGABLE TIMELINE COMPONENT
# ═══════════════════════════════════════════════════════════════════════════════
def render_timeline(target_date, existing_events):
    """Render a 24-hour draggable timeline via HTML component.
    Returns (start_hour_float, end_hour_float) if user dragged, else None."""

    evts_json = json.dumps([
        {"title": e["title"], "time": e["time"],
         "category": e["category"],
         "color": get_color(e["category"])["border"],
         "bg":    get_color(e["category"])["bg"],
         "text":  get_color(e["category"])["text"]}
        for e in existing_events
    ])

    component_html = f"""
<!DOCTYPE html>
<html>
<head>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Outfit', sans-serif;
    background: transparent;
    color: #ffffff;
    user-select: none;
  }}
  #tl-wrap {{
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 14px;
    padding: 14px 16px;
    overflow: hidden;
  }}
  #tl-hint {{
    font-size: 11px;
    color: rgba(160,190,255,0.70);
    margin-bottom: 10px;
    font-weight: 500;
    letter-spacing: 0.05em;
  }}
  #tl-scroll {{
    overflow-y: auto;
    max-height: 520px;
    position: relative;
  }}
  #tl-inner {{
    position: relative;
    /* 24 hours × 52px per hour */
    height: 1248px;
  }}
  .hour-row {{
    position: absolute;
    left: 0; right: 0;
    height: 52px;
    display: flex;
    align-items: flex-start;
    border-top: 1px solid rgba(255,255,255,0.07);
  }}
  .hour-row.now-line {{
    border-top: 2px solid rgba(100,160,255,0.6);
  }}
  .hour-label {{
    font-size: 11px;
    font-weight: 600;
    color: rgba(140,180,255,0.75);
    min-width: 42px;
    padding-top: 3px;
    letter-spacing: 0.04em;
    flex-shrink: 0;
  }}
  .hour-stripe {{
    flex: 1;
    height: 100%;
    position: relative;
    cursor: crosshair;
  }}
  .half-line {{
    position: absolute;
    top: 50%; left: 0; right: 0;
    height: 1px;
    background: rgba(255,255,255,0.04);
    pointer-events: none;
  }}
  /* Existing event blocks */
  .evt-block {{
    position: absolute;
    left: 44px; right: 0;
    border-radius: 7px;
    padding: 4px 8px;
    font-size: 12px;
    font-weight: 600;
    pointer-events: none;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    z-index: 2;
    border-left: 3px solid;
  }}
  /* Drag selection overlay */
  #drag-sel {{
    position: absolute;
    left: 44px; right: 0;
    background: rgba(100,160,255,0.22);
    border: 2px solid rgba(100,160,255,0.75);
    border-radius: 8px;
    display: none;
    z-index: 10;
    pointer-events: none;
  }}
  #drag-label {{
    position: absolute;
    left: 44px;
    background: rgba(30,50,120,0.95);
    border: 1px solid rgba(100,160,255,0.7);
    border-radius: 7px;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 600;
    color: #c0d8ff;
    display: none;
    z-index: 20;
    pointer-events: none;
    white-space: nowrap;
  }}
  /* Current time line */
  #now-marker {{
    position: absolute;
    left: 42px; right: 0;
    height: 2px;
    background: rgba(255,120,120,0.9);
    z-index: 5;
    pointer-events: none;
  }}
  #now-dot {{
    position: absolute;
    left: 38px;
    width: 8px; height: 8px;
    background: rgba(255,120,120,0.9);
    border-radius: 50%;
    margin-top: -3px;
    z-index: 5;
    pointer-events: none;
  }}
</style>
</head>
<body>
<div id="tl-wrap">
  <div id="tl-hint">🖱 Drag to create an event — click &amp; hold, then drag down</div>
  <div id="tl-scroll">
    <div id="tl-inner">
      <div id="drag-sel"></div>
      <div id="drag-label"></div>
      <div id="now-marker"></div>
      <div id="now-dot"></div>
    </div>
  </div>
</div>

<script>
const HOUR_PX = 52;
const TOTAL_H = 1248; // 24 * 52

// ── Existing events ──
const events = {evts_json};

function timeStrToHour(t) {{
  if (!t || t === "All day") return null;
  const [h, m] = t.split(":").map(Number);
  return h + (m || 0) / 60;
}}

function hourToY(h) {{ return h * HOUR_PX; }}

// Build hour rows
const inner = document.getElementById("tl-inner");
for (let h = 0; h < 24; h++) {{
  const row = document.createElement("div");
  row.className = "hour-row";
  row.style.top = (h * HOUR_PX) + "px";
  const lbl  = document.createElement("div");
  lbl.className = "hour-label";
  lbl.textContent = h.toString().padStart(2,"0") + ":00";
  const stripe = document.createElement("div");
  stripe.className = "hour-stripe";
  stripe.dataset.hour = h;
  const half = document.createElement("div");
  half.className = "half-line";
  stripe.appendChild(half);
  row.appendChild(lbl);
  row.appendChild(stripe);
  inner.appendChild(row);
}}

// Draw existing event blocks
events.forEach(e => {{
  const h = timeStrToHour(e.time);
  if (h === null) return;
  const block = document.createElement("div");
  block.className = "evt-block";
  block.style.top = hourToY(h) + "px";
  block.style.height = HOUR_PX + "px";
  block.style.background = e.bg;
  block.style.borderLeftColor = e.color;
  block.style.color = e.text;
  block.textContent = e.time + "  " + e.title;
  inner.appendChild(block);
}});

// Current-time marker
function drawNow() {{
  const now = new Date();
  const frac = (now.getHours() + now.getMinutes()/60) * HOUR_PX;
  document.getElementById("now-marker").style.top = frac + "px";
  document.getElementById("now-dot").style.top    = frac + "px";
}}
drawNow();
setInterval(drawNow, 60000);

// Scroll to 8am on load
document.getElementById("tl-scroll").scrollTop = 8 * HOUR_PX - 20;

// ── Drag logic ──
const dragSel   = document.getElementById("drag-sel");
const dragLabel = document.getElementById("drag-label");
let dragging = false, startY = 0, dragStartH = 0;

function yFromEvent(e) {{
  const rect = inner.getBoundingClientRect();
  return (e.clientY - rect.top);
}}
function yToHour(y) {{
  return Math.max(0, Math.min(24, y / HOUR_PX));
}}
function formatH(h) {{
  const hh = Math.floor(h);
  const mm  = Math.round((h - hh) * 60);
  return hh.toString().padStart(2,"0") + ":" + mm.toString().padStart(2,"0");
}}

inner.addEventListener("mousedown", e => {{
  if (e.button !== 0) return;
  dragging  = true;
  startY    = yFromEvent(e);
  dragStartH = yToHour(startY);
  dragSel.style.display   = "block";
  dragLabel.style.display = "block";
  dragSel.style.top    = startY + "px";
  dragSel.style.height = "2px";
  dragLabel.style.top  = (startY - 24) + "px";
  dragLabel.textContent = formatH(dragStartH);
  e.preventDefault();
}});

document.addEventListener("mousemove", e => {{
  if (!dragging) return;
  const curY  = yFromEvent(e);
  const top   = Math.min(startY, curY);
  const bot   = Math.max(startY, curY);
  const startH = yToHour(Math.min(startY, curY));
  const endH   = yToHour(Math.max(startY, curY));
  dragSel.style.top    = top + "px";
  dragSel.style.height = (bot - top) + "px";
  dragLabel.style.top  = (top - 24) + "px";
  dragLabel.style.display = "block";
  dragLabel.textContent = formatH(startH) + " – " + formatH(endH);
}});

document.addEventListener("mouseup", e => {{
  if (!dragging) return;
  dragging = false;
  dragSel.style.display   = "none";
  dragLabel.style.display = "none";

  const curY   = yFromEvent(e);
  const startH = yToHour(Math.min(startY, curY));
  const endH   = yToHour(Math.max(startY, curY));

  // Only fire if drag was meaningful (> 5 min)
  if (endH - startH < 0.08) return;

  // Send to Streamlit
  const msg = {{ type:"drag_event", start: startH, end: endH }};
  window.parent.postMessage(JSON.stringify(msg), "*");
}});

// Touch support
inner.addEventListener("touchstart", e => {{
  const touch = e.touches[0];
  dragging = true;
  startY = yFromEvent(touch);
  dragStartH = yToHour(startY);
  dragSel.style.display   = "block";
  dragLabel.style.display = "block";
  dragSel.style.top    = startY + "px";
  dragSel.style.height = "2px";
  dragLabel.style.top  = (startY - 24) + "px";
  dragLabel.textContent = formatH(dragStartH);
  e.preventDefault();
}}, {{passive:false}});

document.addEventListener("touchmove", e => {{
  if (!dragging) return;
  const touch = e.touches[0];
  const curY  = yFromEvent(touch);
  const top   = Math.min(startY, curY);
  const bot   = Math.max(startY, curY);
  const startH = yToHour(top);
  const endH   = yToHour(bot);
  dragSel.style.top    = top + "px";
  dragSel.style.height = (bot - top) + "px";
  dragLabel.style.top  = (top - 24) + "px";
  dragLabel.textContent = formatH(startH) + " – " + formatH(endH);
}});

document.addEventListener("touchend", e => {{
  if (!dragging) return;
  dragging = false;
  dragSel.style.display   = "none";
  dragLabel.style.display = "none";
  const touch = e.changedTouches[0];
  const curY   = yFromEvent(touch);
  const startH = yToHour(Math.min(startY, curY));
  const endH   = yToHour(Math.max(startY, curY));
  if (endH - startH < 0.08) return;
  const msg = {{ type:"drag_event", start: startH, end: endH }};
  window.parent.postMessage(JSON.stringify(msg), "*");
}});

// Listen for ACK to clear
window.addEventListener("message", ev => {{
  try {{
    const d = JSON.parse(ev.data);
    if (d.type === "ack") {{
      dragSel.style.display = "none";
    }}
  }} catch(err) {{}}
}});
</script>
</body>
</html>
"""
    import streamlit.components.v1 as components
    components.html(component_html, height=560, scrolling=False)


# ═══════════════════════════════════════════════════════════════════════════════
# MONTH VIEW
# ═══════════════════════════════════════════════════════════════════════════════
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
            for e in events_for_date(day)[:2]:
                c = get_color(e["category"])
                html += (f'<span class="event-chip" style="background:{c["bg"]};'
                         f'color:{c["text"]};border-left:3px solid {c["border"]}">'
                         f'{e["title"]}</span>')
            evts_all = events_for_date(day)
            if len(evts_all) > 2:
                html += f'<span style="font-size:0.62rem;color:rgba(200,210,255,0.6)">+{len(evts_all)-2} more</span>'
            html += '</div>'
    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)

    st.markdown(f'<div class="section-heading">Events — {st.session_state.selected_date.strftime("%A, %B %-d, %Y")}</div>', unsafe_allow_html=True)
    sel_evts = events_for_date(st.session_state.selected_date)
    if sel_evts:
        for i, e in enumerate(sel_evts):
            c = get_color(e["category"])
            ce, cd_ = st.columns([8,1])
            with ce:
                st.markdown(
                    f'<div class="event-detail" style="border-left:4px solid {c["border"]}">'
                    f'<div class="event-title">{e["title"]}</div>'
                    f'<div class="event-meta">🕐 {e["time"]} &nbsp;·&nbsp; {e["category"]}'
                    f'{"<br>" + e["note"] if e["note"] else ""}</div></div>',
                    unsafe_allow_html=True)
            with cd_:
                if st.button("🗑", key=f"m_del_{st.session_state.selected_date}_{i}"):
                    delete_event(st.session_state.selected_date, i); st.rerun()
    else:
        st.markdown('<p style="color:rgba(200,210,255,0.4);font-size:0.85rem">No events — add one from the sidebar.</p>', unsafe_allow_html=True)

    pick = st.date_input("Jump to date", value=st.session_state.selected_date,
                         label_visibility="collapsed", key="jump_picker")
    if pick != st.session_state.selected_date:
        st.session_state.selected_date = pick
        st.session_state.current_date  = pick
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# WEEK VIEW
# ═══════════════════════════════════════════════════════════════════════════════
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
            bg = "rgba(100,160,255,0.15)" if is_today else "rgba(255,255,255,0.04)"
            bc = "rgba(100,160,255,0.50)" if is_today else "rgba(255,255,255,0.09)"
            st.markdown(
                f'<div style="background:{bg};border:1px solid {bc};border-radius:12px;'
                f'padding:10px 8px;min-height:180px;">'
                f'<div style="font-size:0.68rem;font-weight:700;letter-spacing:.08em;'
                f'color:rgba(140,180,255,0.85)">{day.strftime("%a").upper()}</div>'
                f'<div style="font-size:1.25rem;font-weight:700;'
                f'color:{"#64a0ff" if is_today else "#ffffff"}">{day.day}</div>',
                unsafe_allow_html=True)
            for e in events_for_date(day):
                c = get_color(e["category"])
                st.markdown(
                    f'<div style="font-size:0.68rem;font-weight:600;padding:3px 6px;border-radius:6px;'
                    f'background:{c["bg"]};color:{c["text"]};border-left:3px solid {c["border"]};'
                    f'margin-top:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">'
                    f'{e["time"]} {e["title"]}</div>', unsafe_allow_html=True)
            if not events_for_date(day):
                st.markdown('<div style="font-size:0.65rem;color:rgba(255,255,255,0.25);margin-top:8px">—</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# DAY VIEW  ←  draggable 24-hour timeline lives here
# ═══════════════════════════════════════════════════════════════════════════════
elif view == "Day":
    st.markdown(f'<div class="cal-header" style="text-align:left;font-size:1.4rem">'
                f'{cd.strftime("%A, %B %-d, %Y")}</div>', unsafe_allow_html=True)

    evts = events_for_date(cd)

    # ── Pending drag-to-create modal ────────────────────────────────────────
    if st.session_state.pending_evt:
        pe = st.session_state.pending_evt
        st.markdown(
            f'<div style="background:rgba(30,50,120,0.60);border:1px solid rgba(100,160,255,0.50);'
            f'border-radius:16px;padding:1.2rem 1.4rem;margin-bottom:1rem;">'
            f'<div style="font-size:0.95rem;font-weight:700;color:#c0d8ff;margin-bottom:0.6rem">'
            f'✨ New Event &nbsp; <span style="font-weight:400;font-size:0.8rem;'
            f'color:rgba(180,200,255,0.7)">{pe["start_str"]} – {pe["end_str"]}</span></div>',
            unsafe_allow_html=True)
        with st.form("drag_event_form", clear_on_submit=True):
            new_title = st.text_input("Event name", placeholder="What's happening?")
            new_cat   = st.selectbox("Category", list(CATEGORY_COLORS.keys()))
            new_note  = st.text_input("Notes (optional)", placeholder="Add details…")
            col_ok, col_cancel = st.columns(2)
            with col_ok:
                if st.form_submit_button("✓ Save", use_container_width=True) and new_title.strip():
                    add_event(cd, new_title.strip(), pe["start_str"], new_cat, new_note)
                    st.session_state.pending_evt = None
                    st.rerun()
            with col_cancel:
                if st.form_submit_button("✕ Cancel", use_container_width=True):
                    st.session_state.pending_evt = None
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Existing events list ─────────────────────────────────────────────────
    if evts:
        st.markdown('<div class="section-heading">Today\'s Events</div>', unsafe_allow_html=True)
        for i, e in enumerate(evts):
            c = get_color(e["category"])
            ce, cd_ = st.columns([10,1])
            with ce:
                st.markdown(
                    f'<div class="event-detail" style="border-left:5px solid {c["border"]}">'
                    f'<div class="event-title">{e["title"]}</div>'
                    f'<div class="event-meta">🕐 {e["time"]} &nbsp;·&nbsp; {e["category"]}'
                    f'{"<br>" + e["note"] if e["note"] else ""}</div></div>',
                    unsafe_allow_html=True)
            with cd_:
                if st.button("🗑", key=f"d_del_{i}"):
                    delete_event(cd, i); st.rerun()

    # ── 24-hour draggable timeline ───────────────────────────────────────────
    st.markdown('<div class="section-heading" style="margin-top:1.2rem">24-Hour Timeline — drag to create</div>', unsafe_allow_html=True)
    render_timeline(cd, evts)

    # ── Read drag result via query params ────────────────────────────────────
    # The JS posts a message to parent; we capture it via URL query param workaround
    # using st.query_params (Streamlit 1.30+)
    qp = st.query_params
    if "drag_start" in qp and "drag_end" in qp:
        try:
            ds = float(qp["drag_start"])
            de = float(qp["drag_end"])
            def fmt(h):
                hh = int(h)
                mm = round((h - hh) * 60 / 15) * 15
                if mm == 60: hh += 1; mm = 0
                return f"{hh:02d}:{mm:02d}"
            st.session_state.pending_evt = {"start": ds, "end": de,
                                            "start_str": fmt(ds), "end_str": fmt(de)}
            st.query_params.clear()
            st.rerun()
        except Exception:
            st.query_params.clear()

    # JS bridge: post → parent URL update
    import streamlit.components.v1 as components
    components.html("""
<script>
window.addEventListener("message", function(ev){
  try {
    var d = JSON.parse(ev.data);
    if(d.type === "drag_event"){
      var url = new URL(window.parent.location.href);
      url.searchParams.set("drag_start", d.start.toFixed(4));
      url.searchParams.set("drag_end",   d.end.toFixed(4));
      window.parent.history.replaceState(null,"",url.toString());
      // Trigger Streamlit rerun by dispatching a popstate
      window.parent.dispatchEvent(new PopStateEvent('popstate'));
    }
  } catch(e){}
});
</script>
""", height=0)

# ═══════════════════════════════════════════════════════════════════════════════
# AGENDA VIEW
# ═══════════════════════════════════════════════════════════════════════════════
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
                f'color:{"#64a0ff" if is_today else "rgba(140,180,255,0.85)"};'
                f'margin:1.2rem 0 0.4rem;letter-spacing:.07em;text-transform:uppercase">{label}</div>',
                unsafe_allow_html=True)
            for i, e in enumerate(evts):
                c = get_color(e["category"])
                ce, cd_ = st.columns([10,1])
                with ce:
                    st.markdown(
                        f'<div class="event-detail" style="border-left:4px solid {c["border"]}">'
                        f'<div class="event-title">{e["title"]}</div>'
                        f'<div class="event-meta">🕐 {e["time"]} &nbsp;·&nbsp; {e["category"]}'
                        f'{"<br>"+e["note"] if e["note"] else ""}</div></div>',
                        unsafe_allow_html=True)
                with cd_:
                    if st.button("🗑", key=f"ag_del_{check}_{i}"):
                        delete_event(check, i); st.rerun()
    if not found_any:
        st.markdown('<div style="text-align:center;padding:4rem 0;color:rgba(200,210,255,0.35);">'
                    '🌌 No upcoming events in the next 60 days.</div>', unsafe_allow_html=True)
