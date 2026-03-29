import streamlit as st
import streamlit.components.v1 as components
import requests

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="Emotional Abuse Detection",
    layout="centered",
    initial_sidebar_state="expanded"
)

# -------------------------------
# STYLING
# -------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,600;1,9..144,300;1,9..144,400&family=DM+Sans:wght@300;400;500&family=IBM+Plex+Mono:wght@300;400&display=swap');

/* ---- Base ---- */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #F5F0E8;
    font-family: 'DM Sans', sans-serif;
    color: #1A1410;
}

/* Subtle paper texture */
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    inset: 0;
    background-image:
        radial-gradient(ellipse at 20% 20%, rgba(180,140,100,0.07) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 80%, rgba(160,100,80,0.05) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
}

[data-testid="stMain"] { position: relative; z-index: 1; }

/* ---- Sidebar ---- */
[data-testid="stSidebar"] {
    background-color: #EDE8DC !important;
    border-right: 1px solid rgba(26,20,16,0.08) !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: rgba(26,20,16,0.4);
}

/* ---- Main container ---- */
.block-container {
    max-width: 680px !important;
    padding-top: 48px !important;
    padding-bottom: 80px !important;
}

/* ---- Header ---- */
.app-eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: rgba(26,20,16,0.35);
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.app-eyebrow::before {
    content: "";
    display: inline-block;
    width: 20px;
    height: 1px;
    background: rgba(26,20,16,0.3);
}

.app-title {
    font-family: 'Fraunces', serif;
    font-size: clamp(30px, 5vw, 46px);
    font-weight: 300;
    line-height: 1.15;
    color: #1A1410;
    margin-bottom: 10px;
    letter-spacing: -0.5px;
}

.app-title em {
    font-style: italic;
    color: #8B3A2A;
}

.app-desc {
    font-family: 'DM Sans', sans-serif;
    font-size: 13px;
    color: rgba(26,20,16,0.45);
    line-height: 1.7;
    margin-bottom: 36px;
    max-width: 480px;
}

.app-divider {
    width: 100%;
    height: 1px;
    background: linear-gradient(90deg, rgba(26,20,16,0.15) 0%, transparent 100%);
    margin: 32px 0;
}

/* ---- Input area ---- */
.input-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: rgba(26,20,16,0.4);
    margin-bottom: 8px;
}

[data-testid="stTextArea"] textarea {
    background: #FDFAF4 !important;
    border: 1px solid rgba(26,20,16,0.12) !important;
    border-radius: 4px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    color: #1A1410 !important;
    line-height: 1.7 !important;
    padding: 16px !important;
    transition: border-color 0.2s !important;
    box-shadow: inset 0 1px 3px rgba(26,20,16,0.04) !important;
}

[data-testid="stTextArea"] textarea:focus {
    border-color: rgba(139,58,42,0.4) !important;
    box-shadow: inset 0 1px 3px rgba(26,20,16,0.04), 0 0 0 3px rgba(139,58,42,0.06) !important;
}

[data-testid="stTextArea"] textarea::placeholder {
    color: rgba(26,20,16,0.25) !important;
    font-style: italic;
}

/* ---- Analyze button ---- */
.stButton > button {
    background: #1A1410 !important;
    color: #F5F0E8 !important;
    border: none !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    letter-spacing: 0.5px !important;
    border-radius: 3px !important;
    padding: 12px 28px !important;
    width: 100% !important;
    transition: all 0.2s !important;
}

.stButton > button:hover {
    background: #2D2420 !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(26,20,16,0.15) !important;
}

/* ---- Slider ---- */
[data-testid="stSlider"] > div > div > div > div {
    background: #8B3A2A !important;
}

[data-testid="stSlider"] label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: rgba(26,20,16,0.4) !important;
}

/* ---- Result cards ---- */
.result-wrap {
    margin-top: 32px;
    padding: 32px;
    background: #FDFAF4;
    border: 1px solid rgba(26,20,16,0.08);
    border-radius: 6px;
    box-shadow: 0 2px 24px rgba(26,20,16,0.06);
}

.result-verdict {
    font-family: 'Fraunces', serif;
    font-size: 36px;
    font-weight: 400;
    letter-spacing: -0.5px;
    margin-bottom: 4px;
}

.result-verdict.abusive   { color: #8B3A2A; }
.result-verdict.clean     { color: #2A5C3A; }

.result-confidence {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: rgba(26,20,16,0.4);
    margin-bottom: 28px;
}

.result-bar-wrap {
    margin-bottom: 24px;
}

.result-bar-label {
    display: flex;
    justify-content: space-between;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: rgba(26,20,16,0.4);
    margin-bottom: 6px;
}

.result-bar-track {
    width: 100%;
    height: 4px;
    background: rgba(26,20,16,0.08);
    border-radius: 2px;
    overflow: hidden;
}

.result-bar-fill-abusive {
    height: 100%;
    border-radius: 2px;
    background: #8B3A2A;
    transition: width 0.6s ease;
}

.result-bar-fill-clean {
    height: 100%;
    border-radius: 2px;
    background: #2A5C3A;
    transition: width 0.6s ease;
}

.result-divider {
    width: 100%;
    height: 1px;
    background: rgba(26,20,16,0.06);
    margin: 24px 0;
}

.flags-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: 4px;
}

.flag-chip {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 14px;
    border-radius: 4px;
    border: 1px solid rgba(26,20,16,0.08);
    background: rgba(26,20,16,0.02);
}

.flag-chip.active {
    background: rgba(139,58,42,0.06);
    border-color: rgba(139,58,42,0.18);
}

.flag-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: rgba(26,20,16,0.15);
    flex-shrink: 0;
}

.flag-dot.active { background: #8B3A2A; }

.flag-name {
    font-family: 'DM Sans', sans-serif;
    font-size: 12px;
    color: rgba(26,20,16,0.5);
}

.flag-name.active { color: #1A1410; font-weight: 500; }

.breakdown-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 9px;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: rgba(26,20,16,0.3);
    margin-bottom: 14px;
}

/* ---- Warning / error ---- */
.stAlert {
    background: rgba(139,58,42,0.06) !important;
    border: 1px solid rgba(139,58,42,0.2) !important;
    border-radius: 4px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    color: #8B3A2A !important;
}

/* ---- Footer ---- */
.app-footer {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 9px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: rgba(26,20,16,0.2);
    text-align: center;
    margin-top: 48px;
}

/* ---- Streamlit chrome ---- */
header[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stDecoration"]   { display: none; }
</style>
""", unsafe_allow_html=True)

# -------------------------------
# SIDEBAR
# -------------------------------
with st.sidebar:
    st.markdown("""
    <div style="padding: 24px 4px 16px;">
        <div style="font-family:IBM Plex Mono,monospace; font-size:9px; letter-spacing:3px;
                    text-transform:uppercase; color:rgba(26,20,16,0.35); margin-bottom:6px;">
            NLP System
        </div>
        <div style="font-family:Fraunces,serif; font-size:18px; font-weight:300;
                    color:#1A1410; line-height:1.3; margin-bottom:24px;">
            Detection<br><em style="color:#8B3A2A;">Controls</em>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p>Sensitivity Threshold</p>', unsafe_allow_html=True)
    threshold = st.slider(
        "",
        min_value=0.50,
        max_value=0.90,
        value=0.70,
        step=0.05,
        label_visibility="collapsed",
        help="Lower = more sensitive   |   Higher = more conservative"
    )

    st.markdown(f"""
    <div style="margin-top:4px; margin-bottom:32px;">
        <div style="font-family:IBM Plex Mono,monospace; font-size:20px; font-weight:400;
                    color:#1A1410; letter-spacing:-1px;">{threshold:.2f}</div>
        <div style="font-family:DM Sans,sans-serif; font-size:11px;
                    color:rgba(26,20,16,0.35); margin-top:2px;">
            {'More sensitive' if threshold < 0.65 else 'Balanced' if threshold < 0.80 else 'Conservative'}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="border-top:1px solid rgba(26,20,16,0.08); padding-top:20px;">
        <div style="font-family:IBM Plex Mono,monospace; font-size:9px; letter-spacing:2px;
                    text-transform:uppercase; color:rgba(26,20,16,0.3); margin-bottom:12px;">
            Model
        </div>
        <div style="font-family:DM Sans,sans-serif; font-size:12px; color:rgba(26,20,16,0.5);
                    line-height:1.6;">
            RoBERTa<br>Context-aware classification<br>Profanity + intent signals
        </div>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------
# HEADER
# -------------------------------
st.markdown("""
<div class="app-eyebrow">Text Analysis</div>
<div class="app-title">Emotional Abuse<br><em>Detection</em></div>
<div class="app-desc">
    Paste or type any text below. The system analyses linguistic patterns,
    profanity context, and emotional signals to classify the content.
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="app-divider"></div>', unsafe_allow_html=True)

# -------------------------------
# INPUT
# -------------------------------
st.markdown('<div class="input-label">Input Text</div>', unsafe_allow_html=True)

text_input = st.text_area(
    "",
    placeholder="Type or paste text here...",
    height=140,
    label_visibility="collapsed"
)

st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
run = st.button("Analyse Text")

# -------------------------------
# API + RESULTS
# -------------------------------
API_URL = "http://localhost:8000/api/predict"

if run:
    if not text_input.strip():
        st.warning("Please enter some text before analysing.")
    else:
        try:
            with st.spinner("Analysing..."):
                response = requests.post(API_URL, json={
                    "text": text_input,
                    "threshold": threshold
                })

            if response.status_code == 200:
                data = response.json()

                is_abusive       = data.get("is_abusive", False)
                confidence       = data.get("confidence", 0) * 100
                prob_abusive     = data.get("probability_abusive", 0) * 100
                prob_clean       = data.get("probability_non_abusive", 0) * 100
                threshold_used   = data.get("threshold_used", threshold)
                flags            = data.get("context_flags", {})

                verdict_text  = "Abusive Content" if is_abusive else "Non-Abusive Content"
                verdict_color = "#8B3A2A" if is_abusive else "#2A5C3A"

                flag_map = {
                    "Positive Context":   flags.get("has_positive_context", False),
                    "Attack Pattern":     flags.get("has_attack_pattern",   False),
                    "Emotional Emphasis": flags.get("has_emotional_emphasis", False),
                    "Profanity Detected": flags.get("has_profanity",         False),
                }

                def flag_html(name, active):
                    chip_bg     = "rgba(139,58,42,0.06)"   if active else "rgba(26,20,16,0.02)"
                    chip_border = "rgba(139,58,42,0.18)"   if active else "rgba(26,20,16,0.08)"
                    dot_bg      = "#8B3A2A"                if active else "rgba(26,20,16,0.15)"
                    txt_color   = "#1A1410"                if active else "rgba(26,20,16,0.5)"
                    txt_weight  = "500"                    if active else "400"
                    return f"""<div style="display:flex;align-items:center;gap:8px;padding:10px 14px;
                                border-radius:4px;border:1px solid {chip_border};background:{chip_bg};">
                        <div style="width:6px;height:6px;border-radius:50%;background:{dot_bg};flex-shrink:0;"></div>
                        <span style="font-family:DM Sans,sans-serif;font-size:12px;
                                     color:{txt_color};font-weight:{txt_weight};">{name}</span>
                    </div>"""

                flags_html = "".join(flag_html(n, a) for n, a in flag_map.items())

                prob_abusive_fmt = f"{prob_abusive:.1f}"
                prob_clean_fmt   = f"{prob_clean:.1f}"
                prob_abusive_w   = f"{prob_abusive:.1f}"
                prob_clean_w     = f"{prob_clean:.1f}"

                components.html(f"""<!DOCTYPE html>
<html>
<head>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;1,9..144,300&family=DM+Sans:wght@300;400;500&family=IBM+Plex+Mono:wght@300;400&display=swap" rel="stylesheet">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html, body {{ background: transparent; overflow: hidden; }}
</style>
</head>
<body style="padding:0;margin:0;">
<div style="padding:28px; background:#FDFAF4;
            border:1px solid rgba(26,20,16,0.08); border-radius:6px;
            box-shadow:0 2px 24px rgba(26,20,16,0.06);">

    <div style="font-family:Fraunces,serif; font-size:34px; font-weight:400;
                letter-spacing:-0.5px; margin-bottom:6px; color:{verdict_color};">
        {verdict_text}
    </div>
    <div style="font-family:IBM Plex Mono,monospace; font-size:11px; letter-spacing:2px;
                text-transform:uppercase; color:rgba(26,20,16,0.4);">
        Confidence: {confidence:.1f}% &nbsp;&middot;&nbsp; Threshold: {threshold_used}
    </div>
</div>
</body></html>""", height=130, scrolling=False)

            else:
                st.error(f"API returned status {response.status_code}. Check your backend.")

        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the backend. Ensure it is running at http://localhost:8000")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("""
<div class="app-footer">
    For educational and research purposes only &nbsp;·&nbsp; RoBERTa NLP Model
</div>
""", unsafe_allow_html=True)