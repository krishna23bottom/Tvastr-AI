"""TVASTR AI - Streamlit version.  Run:  streamlit run streamlit_app.py"""
import math
import os

import streamlit as st

import prompts
from engine import TvastrEngine, context_to_text
from llm_client import active_provider

st.set_page_config(page_title="TVASTR AI", page_icon="🔱", layout="wide")

# Let Streamlit secrets (for deployment) act as environment variables
try:
    for k in ("GEMINI_API_KEY", "ANTHROPIC_API_KEY"):
        if k in st.secrets:
            os.environ[k] = st.secrets[k]
except Exception:
    pass


@st.cache_resource
def get_engine():
    return TvastrEngine()


engine = get_engine()


# ---------------- Sudarshana chakra (static SVG built in Python) ----------------
def chakra_svg():
    P = lambda r, a: f"{r*math.sin(math.radians(a)):.2f},{-r*math.cos(math.radians(a)):.2f}"

    def zig(n, r0, r1, sweep):
        d = ""
        for i in range(n):
            a, w = i * 360 / n, 360 / n
            d += ("M" if i == 0 else "L") + P(r0, a) + "L" + P(r1, a + w * sweep) + "L" + P(r0, a + w)
        return d + "Z"

    petals = "".join(
        f'<path d="M0,-24 C11,-36 11,-52 0,-66 C-11,-52 -11,-36 0,-24Z" transform="rotate({i*30})"/>'
        for i in range(12))
    spokes = "".join(
        f'<line x1="{P(26 if i%2 else 18, i*15).split(",")[0]}" y1="{P(26 if i%2 else 18, i*15).split(",")[1]}" '
        f'x2="{P(62 if i%2 else 70, i*15).split(",")[0]}" y2="{P(62 if i%2 else 70, i*15).split(",")[1]}"/>'
        for i in range(24))
    return f"""
<svg class="chakra" viewBox="-120 -120 240 240" xmlns="http://www.w3.org/2000/svg">
 <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#f6d58a"/><stop offset=".55" stop-color="#e0a93e"/><stop offset="1" stop-color="#c8702a"/></linearGradient></defs>
 <g class="cw" fill="url(#g)" fill-opacity=".16" stroke="url(#g)" stroke-width="1"><path d="{zig(54,98,115,.62)}"/></g>
 <g class="ccw" fill="none" stroke="url(#g)" stroke-width=".9"><path d="{zig(36,84,95,.35)}" fill="url(#g)" fill-opacity=".1"/>
   <circle r="98" stroke-width="1.4"/><circle r="80" stroke-dasharray="1.5 4"/></g>
 <g class="cw" fill="none" stroke="url(#g)" stroke-width=".9"><circle r="70" stroke-width="1.3"/><circle r="64" stroke-dasharray="3 3"/>{spokes}</g>
 <g class="ccw" fill="url(#g)" fill-opacity=".14" stroke="url(#g)">{petals}</g>
 <g fill="none" stroke="url(#g)" stroke-width="1.2"><circle r="22"/><circle r="15" stroke-dasharray="2 2"/></g>
 <circle r="3.2" fill="#fff3c9"/></svg>"""


st.markdown(f"""
<style>
.stApp{{background:radial-gradient(1000px 600px at 80% -10%,#2a1710 0%,transparent 60%),#0a0810;color:#f4e8cb}}
[data-testid="stSidebar"]{{background:#110d19;border-right:1px solid #33283f}}
h1,h2,h3{{font-family:'Cinzel',Georgia,serif!important;color:#f6d58a!important;letter-spacing:3px}}
.chakra{{position:fixed;right:-160px;top:50%;width:700px;height:700px;transform:translateY(-50%);
  opacity:.25;pointer-events:none;z-index:0;filter:drop-shadow(0 0 24px rgba(255,150,50,.5))}}
.cw{{transform-origin:0 0;animation:spin 90s linear infinite}}
.ccw{{transform-origin:0 0;animation:spin 55s linear infinite reverse}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
[data-testid="stChatMessage"]{{background:linear-gradient(180deg,#1c1727,#15111d);border:1px solid #33283f;border-radius:14px;position:relative;z-index:1}}
.stButton>button{{width:100%;text-align:left;background:#1c1727;color:#f4e8cb;border:1px solid #33283f;border-radius:10px}}
.stButton>button:hover{{border-color:#e0a93e;color:#f6d58a}}
.seal{{display:inline-block;font-size:11px;padding:2px 10px;margin:2px 4px 0 0;border-radius:20px;border:1px solid #33283f;color:#a39ab3}}
.seal.i{{color:#f6d58a;border-color:#6b5222;background:rgba(224,169,62,.08)}}
</style>
{chakra_svg()}
""", unsafe_allow_html=True)

# ---------------- state ----------------
ss = st.session_state
ss.setdefault("msgs", [])      # what we display
ss.setdefault("history", [])   # what the LLM sees
ss.setdefault("ctx", {})       # remembered project context
ss.setdefault("queued", None)

# ---------------- sidebar: the workshop ----------------
TOOLS = {
    "Shot List": "Help me create a shot list for my scene",
    "Moodboard": "Suggest a mood and visual identity for my project",
    "Camera": "What camera settings should I use for cinematic video?",
    "Lighting": "How do I set up three point lighting?",
    "Color": "How do I get a cinematic color grade?",
    "Editing": "How do I make my cuts feel smoother?",
    "Sound": "How do I record clean dialogue?",
}
with st.sidebar:
    st.markdown("## TVASTR\n### त्वष्टा")
    st.caption("THE WORKSHOP")
    for name, q in TOOLS.items():
        if st.button(name, key=name):
            ss.queued = q
    st.info("**Tvastr** is the divine craftsman of the Vedas, who shaped forms and forged Indra's thunderbolt. Here, he shapes your story.")
    if st.button("BEGIN A NEW CREATION"):
        ss.msgs, ss.history, ss.ctx = [], [], {}
        st.rerun()
    st.caption(f"Forge: {active_provider()} | prompt {prompts.PROMPT_VERSION}")

# ---------------- main ----------------
st.markdown("# THE DIVINE CRAFTSMAN")
st.caption("Your AI co-pilot for visual storytelling")


def seals(meta):
    t = []
    if meta.get("intent"):
        t.append(f'<span class="seal i">✦ {meta["intent"].replace("_"," ")} · {meta["confidence"]:.0%}</span>')
    for v in meta.get("context", {}).values():
        t += [f'<span class="seal">{x.replace("_"," ")}</span>' for x in v]
    src = "built-in wisdom" if meta["source"] == "offline" else meta["source"].replace("llm:", "AI: ")
    t.append(f'<span class="seal">{src}</span>')
    return "".join(t)


if not ss.msgs:
    with st.chat_message("assistant", avatar="🔱"):
        st.markdown("**Namaste.** I am **Tvastr**, the divine craftsman. Tell me about your project "
                    "(type, mood, location, gear) and I will help you shape it, from the first idea to the final export.")

for m in ss.msgs:
    with st.chat_message(m["role"], avatar="🔱" if m["role"] == "assistant" else "⭐"):
        st.markdown(m["content"])
        if m.get("meta"):
            st.markdown(seals(m["meta"]), unsafe_allow_html=True)

prompt = st.chat_input("Describe your scene, shoot or problem...", max_chars=1000)
if ss.queued:
    prompt, ss.queued = ss.queued, None

if prompt:
    ss.msgs.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="⭐"):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar="🔱"):
        with st.spinner("Tvastr is forging your answer..."):
            r = engine.respond(prompt, ss.history, ss.ctx)
        st.markdown(r["reply"])
        st.markdown(seals(r), unsafe_allow_html=True)
    if r["source"] != "validation":
        ss.history += [{"role": "user", "content": prompt}, {"role": "assistant", "content": r["reply"]}]
        ss.history = ss.history[-24:]
    ss.ctx = r["context"]
    ss.msgs.append({"role": "assistant", "content": r["reply"], "meta": r})
    