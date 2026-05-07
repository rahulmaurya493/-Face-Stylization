import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

st.set_page_config(
    page_title="FaceArt Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,300;0,600;0,900;1,300;1,600&family=Outfit:wght@300;400;500;600&family=JetBrains+Mono:wght@300;400&display=swap');

/* ─── DESIGN TOKENS ─── */
:root {
    --bg:         #0e0e11;
    --surface:    #16171c;
    --surface2:   #1d1e25;
    --surface3:   #24262f;
    --gold:       #c8913f;
    --gold-light: #dba855;
    --gold-glow:  rgba(200,145,63,0.12);
    --gold-rim:   rgba(200,145,63,0.22);
    --white:      #f2ede6;
    --muted:      rgba(242,237,230,0.45);
    --subtle:     rgba(242,237,230,0.18);
    --hairline:   rgba(255,255,255,0.07);
    --hairline2:  rgba(255,255,255,0.12);
    --green:      #52a882;
    --green-dim:  rgba(82,168,130,0.10);
    --red:        #c26060;

    --font-display: 'Fraunces', Georgia, serif;
    --font-body:    'Outfit', sans-serif;
    --font-mono:    'JetBrains Mono', monospace;

    --space-1:  4px;
    --space-2:  8px;
    --space-3:  12px;
    --space-4:  16px;
    --space-5:  20px;
    --space-6:  24px;
    --space-8:  32px;
    --space-10: 40px;
    --space-12: 48px;

    --text-xs:  0.65rem;
    --text-sm:  0.78rem;
    --text-md:  0.90rem;
    --text-lg:  1.05rem;
    --text-xl:  1.25rem;
    --text-2xl: 1.6rem;
    --text-3xl: 2.2rem;

    --radius-sm: 6px;
    --radius:    10px;
    --radius-lg: 16px;
}

/* ─── GLOBAL RESET ─── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
    font-family: var(--font-body) !important;
    background:  var(--bg) !important;
    color:       var(--white) !important;
    font-size:   15px;
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
}

/* ─── STRIP STREAMLIT CHROME ─── */
#MainMenu, footer, header { visibility: hidden !important; }
.block-container             { padding: 0 !important; max-width: 100% !important; }
[data-testid="stHorizontalBlock"] { gap: 0 !important; padding: 0 !important; align-items: stretch !important; }
[data-testid="column"]            { padding: 0 !important; gap: 0 !important; }
[data-testid="stVerticalBlock"]   { gap: 0 !important; }
[data-testid="stSidebarCollapsedControl"] { display: none !important; }


/* ═══════════════════════════════
   TOPBAR
═══════════════════════════════ */
.topbar {
    height: 56px;
    background: var(--surface);
    border-bottom: 1px solid var(--hairline2);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 var(--space-10);
}
.topbar-brand {
    font-family: var(--font-display);
    font-size: var(--text-xl);
    font-weight: 900;
    color: var(--white);
    letter-spacing: -0.02em;
    line-height: 1;
}
.topbar-brand em {
    font-style: italic;
    color: var(--gold-light);
}
.topbar-center {
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    letter-spacing: 0.20em;
    text-transform: uppercase;
    color: var(--subtle);
    border: 1px solid var(--hairline2);
    padding: 5px 14px;
    border-radius: var(--radius-sm);
}
.topbar-right {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--green);
}
.status-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--green);
    animation: blink 2.5s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }


/* ═══════════════════════════════
   SIDEBAR PANEL (left column)
═══════════════════════════════ */
.sidebar-panel {
    background: var(--surface);
    border-right: 1px solid var(--hairline2);
    padding: var(--space-6) var(--space-5);
    height: calc(100vh - 56px);
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 0;
}

/* Section heading inside sidebar */
.panel-heading {
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    font-weight: 400;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--gold);
    margin-top: var(--space-6);
    margin-bottom: var(--space-3);
    padding-bottom: var(--space-2);
    border-bottom: 1px solid var(--hairline2);
    display: flex;
    align-items: center;
    gap: var(--space-2);
}
.panel-heading:first-child { margin-top: 0; }

/* Style preview cards */
.style-card {
    background: var(--surface2);
    border: 1px solid var(--hairline2);
    border-radius: var(--radius);
    padding: var(--space-3) var(--space-4);
    margin-bottom: var(--space-2);
    display: flex;
    align-items: flex-start;
    gap: var(--space-3);
    transition: border-color 0.15s, background 0.15s;
    cursor: default;
}
.style-card:hover {
    border-color: var(--gold-rim);
    background: var(--gold-glow);
}
.card-icon { font-size: 1.4rem; flex-shrink: 0; margin-top: 2px; }
.card-name {
    font-family: var(--font-body);
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--white);
    margin-bottom: 3px;
    line-height: 1.2;
}
.card-desc {
    font-family: var(--font-mono);
    font-size: 0.62rem;
    color: var(--muted);
    line-height: 1.55;
}

/* Info box */
.info-box {
    background: var(--gold-glow);
    border: 1px solid var(--gold-rim);
    border-radius: var(--radius-sm);
    padding: var(--space-3) var(--space-4);
    margin-top: var(--space-2);
}
.info-box-title {
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    letter-spacing: 0.10em;
    color: var(--gold-light);
    margin-bottom: var(--space-2);
    text-transform: uppercase;
}
.info-box-body {
    font-family: var(--font-mono);
    font-size: 0.62rem;
    color: var(--muted);
    line-height: 1.8;
}


/* ═══════════════════════════════
   FORM ELEMENTS
═══════════════════════════════ */
/* Labels */
label,
.stFileUploader label,
.stSelectbox label {
    font-family: var(--font-mono) !important;
    font-size: var(--text-xs) !important;
    font-weight: 400 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
    margin-bottom: var(--space-2) !important;
}

/* File uploader */
[data-testid="stFileUploader"] > div {
    background: var(--surface2) !important;
    border: 1px dashed var(--hairline2) !important;
    border-radius: var(--radius) !important;
    padding: var(--space-4) !important;
    transition: border-color 0.15s !important;
}
[data-testid="stFileUploader"] > div:hover {
    border-color: var(--gold-rim) !important;
}
[data-testid="stFileUploader"] > div p {
    font-family: var(--font-mono) !important;
    font-size: var(--text-xs) !important;
    color: var(--muted) !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background: var(--surface2) !important;
    border: 1px solid var(--hairline2) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--white) !important;
    font-family: var(--font-body) !important;
    font-size: var(--text-sm) !important;
}

/* Spacing */
.stFileUploader,
.stSelectbox { margin-bottom: var(--space-3) !important; }


/* ═══════════════════════════════
   BUTTONS
═══════════════════════════════ */

/* Apply button — primary gold */
.btn-apply .stButton > button {
    font-family: var(--font-body) !important;
    font-size: var(--text-sm) !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    background: var(--gold) !important;
    color: #0e0e11 !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    height: 42px !important;
    width: 100% !important;
    box-shadow: 0 2px 14px rgba(200,145,63,0.28) !important;
    transition: all 0.15s ease !important;
}
.btn-apply .stButton > button:hover {
    background: var(--gold-light) !important;
    box-shadow: 0 4px 20px rgba(200,145,63,0.40) !important;
    transform: translateY(-1px) !important;
}

/* Download button — ghost green */
.stDownloadButton > button {
    font-family: var(--font-mono) !important;
    font-size: var(--text-xs) !important;
    font-weight: 400 !important;
    letter-spacing: 0.08em !important;
    background: var(--green-dim) !important;
    color: var(--green) !important;
    border: 1px solid rgba(82,168,130,0.28) !important;
    border-radius: var(--radius-sm) !important;
    height: 38px !important;
    width: 100% !important;
    box-shadow: none !important;
    transition: all 0.15s !important;
}
.stDownloadButton > button:hover {
    background: rgba(82,168,130,0.16) !important;
    border-color: rgba(82,168,130,0.50) !important;
    transform: none !important;
    box-shadow: none !important;
}


/* ═══════════════════════════════
   CANVAS (right panel)
═══════════════════════════════ */
.canvas-panel {
    background: var(--bg);
    padding: var(--space-8) var(--space-10);
    min-height: calc(100vh - 56px);
}

/* Page header inside canvas */
.canvas-header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    padding-bottom: var(--space-5);
    margin-bottom: var(--space-6);
    border-bottom: 1px solid var(--hairline2);
}
.canvas-title {
    font-family: var(--font-display);
    font-size: var(--text-3xl);
    font-weight: 900;
    color: var(--white);
    letter-spacing: -0.03em;
    line-height: 1;
}
.canvas-title em {
    font-style: italic;
    color: var(--gold-light);
}
.canvas-subtitle {
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    color: var(--muted);
    margin-top: var(--space-2);
    letter-spacing: 0.04em;
    line-height: 1;
}

/* Section divider label */
.sec-label {
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--subtle);
    margin: var(--space-8) 0 var(--space-4) 0;
    display: flex;
    align-items: center;
    gap: var(--space-3);
}
.sec-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--hairline2);
}

/* Image frame card */
.img-frame {
    background: var(--surface);
    border: 1px solid var(--hairline2);
    border-radius: var(--radius);
    overflow: hidden;
}
.frame-bar {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-3) var(--space-4);
    border-bottom: 1px solid var(--hairline);
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--muted);
    background: var(--surface2);
}
.frame-content { padding: var(--space-3); }

/* Empty canvas placeholder */
.empty-canvas {
    border: 1px dashed rgba(200,145,63,0.20);
    border-radius: var(--radius-lg);
    background: var(--surface);
    min-height: 400px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: var(--space-12);
    gap: var(--space-4);
}
.empty-icon {
    font-size: 3rem;
    opacity: 0.30;
    line-height: 1;
}
.empty-title {
    font-family: var(--font-display);
    font-size: var(--text-xl);
    font-weight: 600;
    color: var(--white);
    opacity: 0.40;
    letter-spacing: -0.01em;
}
.empty-hint {
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    color: var(--subtle);
    line-height: 1.7;
    max-width: 280px;
}

/* Alert / status */
.stAlert {
    background: var(--surface2) !important;
    border: 1px solid var(--hairline2) !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--font-mono) !important;
    font-size: var(--text-xs) !important;
    letter-spacing: 0.02em !important;
}
div[data-testid="stAlert"][kind="success"] {
    border-color: rgba(82,168,130,0.30) !important;
    color: var(--green) !important;
}
.stSpinner > div { border-top-color: var(--gold) !important; }

/* ── How it works ── */
.how-grid {
    display: grid;
    grid-template-columns: repeat(3,1fr);
    gap: var(--space-3);
}
.how-card {
    background: var(--surface);
    border: 1px solid var(--hairline2);
    border-radius: var(--radius);
    padding: var(--space-5) var(--space-5);
    position: relative;
    overflow: hidden;
}
.how-card::after {
    content: attr(data-n);
    position: absolute;
    top: -6px; right: 10px;
    font-family: var(--font-display);
    font-size: 3.8rem;
    font-weight: 900;
    font-style: italic;
    color: rgba(200,145,63,0.06);
    line-height: 1;
    pointer-events: none;
}
.how-emoji { font-size: 1.3rem; margin-bottom: var(--space-3); display: block; }
.how-name {
    font-family: var(--font-body);
    font-size: var(--text-md);
    font-weight: 600;
    color: var(--white);
    margin-bottom: var(--space-3);
    line-height: 1.2;
}
.how-steps {
    font-family: var(--font-mono);
    font-size: 0.62rem;
    color: var(--muted);
    line-height: 1.85;
}

/* ── Footer ── */
.page-footer {
    padding: var(--space-4) var(--space-10);
    border-top: 1px solid var(--hairline);
    background: var(--surface);
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    color: var(--subtle);
    letter-spacing: 0.08em;
}

/* Scrollbar */
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# EFFECT FUNCTIONS
# ─────────────────────────────────────────────────────────────────
def pencil_sketch(img):
    b    = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(b, cv2.COLOR_BGR2GRAY)
    inv  = cv2.bitwise_not(gray)
    blur = cv2.GaussianBlur(inv, (21, 21), 0)
    return cv2.divide(gray, cv2.bitwise_not(blur), scale=256.0)

def oil_painting(img):
    b = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return cv2.cvtColor(cv2.stylization(b, sigma_s=60, sigma_r=0.45), cv2.COLOR_BGR2RGB)

def cartoon_effect(img):
    b      = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    smooth = cv2.bilateralFilter(b, 9, 300, 300)
    gray   = cv2.cvtColor(b, cv2.COLOR_BGR2GRAY)
    edges  = cv2.adaptiveThreshold(
        cv2.medianBlur(gray, 7), 255,
        cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 2
    )
    return cv2.cvtColor(
        cv2.bitwise_and(smooth, cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)),
        cv2.COLOR_BGR2RGB
    )

def to_bytes(arr, gray=False):
    buf = io.BytesIO()
    pil = Image.fromarray(arr).convert("L" if gray else "RGB")
    pil.save(buf, format="PNG")
    return buf.getvalue()


# ─────────────────────────────────────────────────────────────────
# TOPBAR
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
    <div class="topbar-brand">Face<em>Art</em></div>
    <div class="topbar-center">Computer Vision Style Studio</div>
    <div class="topbar-right"><div class="status-dot"></div>OpenCV · Ready</div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# MAIN LAYOUT  — left sidebar panel + right canvas
# ─────────────────────────────────────────────────────────────────
left, right = st.columns([1, 2.8])

# ═══════════════════════════════
# LEFT PANEL
# ═══════════════════════════════
with left:
    st.markdown('<div class="sidebar-panel">', unsafe_allow_html=True)

    # ── Style cards ──────────────────────
    st.markdown('<div class="panel-heading">Art Styles</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="style-card">
        <div class="card-icon">✏️</div>
        <div>
            <div class="card-name">Pencil Sketch</div>
            <div class="card-desc">Grayscale inversion + Gaussian blur divide — realistic hand-drawn look</div>
        </div>
    </div>
    <div class="style-card">
        <div class="card-icon">🎨</div>
        <div>
            <div class="card-name">Oil Painting</div>
            <div class="card-desc">OpenCV stylization filter — smooth canvas painterly texture</div>
        </div>
    </div>
    <div class="style-card">
        <div class="card-icon">🎌</div>
        <div>
            <div class="card-name">Cartoon</div>
            <div class="card-desc">Bilateral filter + adaptive threshold — bold edges, flat colors</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Upload ───────────────────────────
    st.markdown('<div class="panel-heading">Upload Photo</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Upload", type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed"
    )

    # ── Select style ─────────────────────
    st.markdown('<div class="panel-heading">Select Style</div>', unsafe_allow_html=True)
    style = st.selectbox(
        "Style", ["✏️  Pencil Sketch", "🎨  Oil Painting", "🎌  Cartoon"],
        label_visibility="collapsed"
    )

    # ── Tip box ──────────────────────────
    st.markdown("""
    <div class="info-box" style="margin-top:16px">
        <div class="info-box-title">Best Results</div>
        <div class="info-box-body">
            · Clear, well-lit photo<br>
            · Face should be visible<br>
            · Min 300 × 300 px<br>
            · JPG or PNG format
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Apply button ─────────────────────
    st.markdown('<div class="btn-apply">', unsafe_allow_html=True)
    apply_btn = st.button("✦  Apply Style", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # close sidebar-panel


# ═══════════════════════════════
# RIGHT CANVAS
# ═══════════════════════════════
with right:
    st.markdown("""
    <div class="canvas-panel">
        <div class="canvas-header">
            <div>
                <div class="canvas-title">Style <em>Canvas</em></div>
                <div class="canvas-subtitle">Upload a photo · Choose a style · Apply transformation</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # wrapping div for canvas content padding
    st.markdown('<div style="padding:0 40px">', unsafe_allow_html=True)

    # ── EMPTY STATE ──────────────────────
    if uploaded is None:
        st.markdown("""
        <div class="empty-canvas">
            <div class="empty-icon">🖼</div>
            <div class="empty-title">Nothing here yet</div>
            <div class="empty-hint">
                Upload a photo from the left panel,<br>
                pick an art style, then hit Apply Style
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── UPLOADED — preview ───────────────
    elif not apply_btn:
        img_arr = np.array(Image.open(uploaded).convert("RGB"))
        st.markdown('<div class="img-frame"><div class="frame-bar"><span>📷</span>&nbsp; Original Photo</div><div class="frame-content">', unsafe_allow_html=True)
        st.image(img_arr, use_column_width=True)
        st.markdown('</div></div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="margin-top:14px;padding:12px 16px;background:var(--surface2);
                    border:1px solid var(--hairline2);border-radius:var(--radius-sm);">
            <span style="font-family:var(--font-mono);font-size:0.65rem;
                         color:var(--muted);letter-spacing:0.06em;">
                Photo loaded — select a style in the left panel and click
                <strong style="color:var(--gold-light)">Apply Style</strong>
            </span>
        </div>
        """, unsafe_allow_html=True)

    # ── APPLIED — show result ────────────
    else:
        img_arr = np.array(Image.open(uploaded).convert("RGB"))

        with st.spinner("Rendering your style…"):
            if "Pencil" in style:
                res   = pencil_sketch(img_arr)
                gray  = True
                sname = "Pencil Sketch"
                sico  = "✏️"
            elif "Oil" in style:
                res   = oil_painting(img_arr)
                gray  = False
                sname = "Oil Painting"
                sico  = "🎨"
            else:
                res   = cartoon_effect(img_arr)
                gray  = False
                sname = "Cartoon"
                sico  = "🎌"

        # Before / After
        c1, c2 = st.columns(2, gap="small")
        with c1:
            st.markdown('<div class="img-frame"><div class="frame-bar"><span>📷</span>&nbsp; Original</div><div class="frame-content">', unsafe_allow_html=True)
            st.image(img_arr, use_column_width=True)
            st.markdown('</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="img-frame"><div class="frame-bar"><span>{sico}</span>&nbsp; {sname}</div><div class="frame-content">', unsafe_allow_html=True)
            st.image(res, use_column_width=True, clamp=True)
            st.markdown('</div></div>', unsafe_allow_html=True)

        st.success(f"✓  {sico}  {sname} applied successfully")

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.download_button(
            label=f"⬇  Download {sname}",
            data=to_bytes(res, gray),
            file_name=f"faceart_{sname.lower().replace(' ', '_')}.png",
            mime="image/png",
            use_container_width=True
        )

        # ── All 3 styles preview ──────────
        st.markdown('<div class="sec-label">All Styles Preview</div>', unsafe_allow_html=True)

        with st.spinner("Generating all three styles…"):
            s1 = pencil_sketch(img_arr)
            s2 = oil_painting(img_arr)
            s3 = cartoon_effect(img_arr)

        pa, pb, pc, pd = st.columns(4, gap="small")
        previews = [
            (pa, "📷", "Original",  img_arr, False),
            (pb, "✏️", "Sketch",     s1,      True),
            (pc, "🎨", "Oil Paint",  s2,      False),
            (pd, "🎌", "Cartoon",    s3,      False),
        ]
        for col, ico, label, img, clamp in previews:
            with col:
                st.markdown(f'<div class="img-frame"><div class="frame-bar"><span>{ico}</span>&nbsp; {label}</div><div class="frame-content">', unsafe_allow_html=True)
                st.image(img, use_column_width=True, clamp=clamp)
                st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # close padding wrapper


# ─────────────────────────────────────────────────────────────────
# HOW IT WORKS
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 40px 40px 0 40px">
    <div class="sec-label">How It Works</div>
    <div class="how-grid">
        <div class="how-card" data-n="1">
            <span class="how-emoji">✏️</span>
            <div class="how-name">Pencil Sketch</div>
            <div class="how-steps">
                1 · Convert image to grayscale<br>
                2 · Invert pixel values (bitwise_not)<br>
                3 · Apply Gaussian blur 21×21<br>
                4 · Divide original by inverted blur<br>
                5 · Sketch-like edges emerge
            </div>
        </div>
        <div class="how-card" data-n="2">
            <span class="how-emoji">🎨</span>
            <div class="how-name">Oil Painting</div>
            <div class="how-steps">
                1 · Pass image to cv2.stylization<br>
                2 · sigma_s = 60 (spatial smoothness)<br>
                3 · sigma_r = 0.45 (color range)<br>
                4 · Blends neighboring pixels together<br>
                5 · Painterly canvas texture appears
            </div>
        </div>
        <div class="how-card" data-n="3">
            <span class="how-emoji">🎌</span>
            <div class="how-name">Cartoon Effect</div>
            <div class="how-steps">
                1 · Bilateral filter smooths colors<br>
                2 · Median blur reduces noise<br>
                3 · Adaptive threshold detects edges<br>
                4 · Combine smooth image + edges<br>
                5 · Bold outlines + flat color regions
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style="height:40px"></div>
<div class="page-footer">
    <span>FaceArt Studio &nbsp;·&nbsp; Rahul Maurya</span>
    <span>Built with OpenCV &nbsp;·&nbsp; PIL &nbsp;·&nbsp; Streamlit</span>
</div>
""", unsafe_allow_html=True)
