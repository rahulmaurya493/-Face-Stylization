import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

st.set_page_config(
    page_title="FaceArt — CV Style Studio",
    page_icon="🎨",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=Instrument+Sans:wght@400;500;600&family=DM+Mono:wght@300;400&display=swap');

/* ── TOKENS ── */
:root {
    --ink:      #0a0b0d;
    --ink2:     #111318;
    --ink3:     #181c24;
    --ink4:     #1f2530;
    --amber:    #c9922a;
    --amber-lt: #e0ab48;
    --amber-dim: rgba(201,146,42,0.10);
    --cream:    #e8e3d9;
    --muted:    rgba(232,227,217,0.38);
    --muted2:   rgba(232,227,217,0.16);
    --border:   rgba(255,255,255,0.06);
    --border2:  rgba(255,255,255,0.10);
    --red:      #d45a5a;
    --teal:     #4db89a;
}

/* ── RESET ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    font-family: 'Instrument Sans', sans-serif !important;
    background: var(--ink) !important;
    color: var(--cream) !important;
}

#MainMenu, footer, header { visibility: hidden !important; }
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── TOP MASTHEAD ── */
.masthead {
    background: var(--ink2);
    border-bottom: 1px solid var(--border2);
    padding: 0 48px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 60px;
}
.masthead-logo {
    font-family: 'Playfair Display', serif;
    font-size: 1.3rem;
    font-weight: 900;
    color: var(--cream);
    letter-spacing: -0.01em;
}
.masthead-logo em {
    color: var(--amber-lt);
    font-style: italic;
}
.masthead-tag {
    font-family: 'DM Mono', monospace;
    font-size: 0.60rem;
    letter-spacing: 0.20em;
    text-transform: uppercase;
    color: var(--muted);
    border: 1px solid var(--border2);
    padding: 4px 12px;
    border-radius: 2px;
}
.masthead-badge {
    display: flex;
    align-items: center;
    gap: 6px;
    font-family: 'DM Mono', monospace;
    font-size: 0.60rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--teal);
}
.badge-dot {
    width: 5px; height: 5px;
    border-radius: 50%;
    background: var(--teal);
    animation: pulse 2.5s infinite;
}
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.3;transform:scale(0.8)} }

/* ── MAIN LAYOUT ── */
.page-body {
    display: grid;
    grid-template-columns: 300px 1fr;
    min-height: calc(100vh - 60px);
}

/* ── LEFT PANEL ── */
.left-panel {
    background: var(--ink2);
    border-right: 1px solid var(--border2);
    padding: 28px 22px;
    overflow-y: auto;
}
.panel-section {
    font-family: 'DM Mono', monospace;
    font-size: 0.58rem;
    font-weight: 600;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--amber);
    margin: 22px 0 10px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}
.panel-section::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border2);
}
.panel-section:first-child { margin-top: 0; }

/* ── STYLE TILES ── */
.style-tile {
    background: var(--ink3);
    border: 1px solid var(--border2);
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: all 0.18s;
    display: flex;
    align-items: flex-start;
    gap: 14px;
}
.style-tile:hover {
    border-color: rgba(201,146,42,0.35);
    background: rgba(201,146,42,0.05);
}
.tile-ico { font-size: 1.5rem; flex-shrink: 0; margin-top: 2px; }
.tile-name {
    font-family: 'Instrument Sans', sans-serif;
    font-size: 0.90rem;
    font-weight: 600;
    color: var(--cream);
    margin-bottom: 3px;
}
.tile-desc {
    font-family: 'DM Mono', monospace;
    font-size: 0.66rem;
    color: var(--muted);
    line-height: 1.5;
}

/* ── INPUTS ── */
.stFileUploader {
    margin-bottom: 0 !important;
}
.stFileUploader > div {
    background: var(--ink3) !important;
    border: 1px dashed var(--border2) !important;
    border-radius: 8px !important;
    padding: 16px !important;
}
.stFileUploader label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.62rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
    font-weight: 400 !important;
}
.stSelectbox > div > div {
    background: var(--ink3) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 6px !important;
    color: var(--cream) !important;
    font-family: 'Instrument Sans', sans-serif !important;
    font-size: 0.85rem !important;
}
label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.60rem !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
    font-weight: 400 !important;
    margin-bottom: 5px !important;
}

/* ── APPLY BUTTON ── */
.stButton > button {
    font-family: 'Instrument Sans', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    background: var(--amber) !important;
    color: var(--ink) !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 10px 20px !important;
    height: 42px !important;
    width: 100% !important;
    transition: all 0.18s !important;
    box-shadow: 0 2px 12px rgba(201,146,42,0.28) !important;
}
.stButton > button:hover {
    background: var(--amber-lt) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 18px rgba(201,146,42,0.38) !important;
}

/* ── DOWNLOAD BUTTON ── */
.stDownloadButton > button {
    background: var(--ink3) !important;
    color: var(--teal) !important;
    border: 1px solid rgba(77,184,154,0.28) !important;
    border-radius: 6px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    font-weight: 400 !important;
    letter-spacing: 0.06em !important;
    height: 38px !important;
    box-shadow: none !important;
}
.stDownloadButton > button:hover {
    background: rgba(77,184,154,0.08) !important;
    border-color: rgba(77,184,154,0.5) !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ── CANVAS AREA (right) ── */
.canvas-area {
    padding: 32px 40px;
    background: var(--ink);
}

/* ── PAGE HEADER ── */
.canvas-header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    margin-bottom: 28px;
    padding-bottom: 20px;
    border-bottom: 1px solid var(--border2);
}
.canvas-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.0rem;
    font-weight: 900;
    color: var(--cream);
    letter-spacing: -0.02em;
    line-height: 1;
}
.canvas-title em {
    color: var(--amber-lt);
    font-style: italic;
}
.canvas-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    color: var(--muted);
    margin-top: 7px;
    letter-spacing: 0.04em;
}

/* ── IMAGE FRAMES ── */
.img-frame {
    background: var(--ink2);
    border: 1px solid var(--border2);
    border-radius: 10px;
    overflow: hidden;
}
.frame-label {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 14px;
    border-bottom: 1px solid var(--border);
    font-family: 'DM Mono', monospace;
    font-size: 0.60rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--muted);
}
.frame-label span {
    font-size: 0.9rem;
}
.frame-body { padding: 14px; }

/* ── EMPTY CANVAS ── */
.empty-canvas {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 420px;
    border: 1px dashed rgba(201,146,42,0.20);
    border-radius: 10px;
    background: var(--ink2);
    text-align: center;
    padding: 40px;
}
.empty-canvas-ico {
    font-size: 3rem;
    margin-bottom: 16px;
    opacity: 0.4;
}
.empty-canvas-ttl {
    font-family: 'Playfair Display', serif;
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--cream);
    opacity: 0.5;
    margin-bottom: 8px;
}
.empty-canvas-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    color: var(--muted2);
    line-height: 1.7;
}

/* ── HOW IT WORKS ── */
.how-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-top: 12px;
}
.how-cell {
    background: var(--ink2);
    border: 1px solid var(--border2);
    border-radius: 8px;
    padding: 18px 16px;
    position: relative;
    overflow: hidden;
}
.how-cell::before {
    content: attr(data-n);
    position: absolute;
    top: -8px; right: 10px;
    font-family: 'Playfair Display', serif;
    font-size: 4rem;
    font-weight: 900;
    color: rgba(201,146,42,0.05);
    line-height: 1;
    pointer-events: none;
}
.how-ico { font-size: 1.3rem; margin-bottom: 10px; }
.how-ttl {
    font-family: 'Instrument Sans', sans-serif;
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--cream);
    margin-bottom: 8px;
}
.how-steps {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: var(--muted);
    line-height: 1.8;
}

/* ── TIP BOX ── */
.tip-box {
    background: rgba(201,146,42,0.06);
    border: 1px solid rgba(201,146,42,0.18);
    border-radius: 6px;
    padding: 12px 14px;
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    color: var(--muted);
    line-height: 1.7;
    margin-top: 10px;
}
.tip-box strong { color: var(--amber-lt); font-weight: 600; }

/* ── SEC LABEL ── */
.sec-lbl {
    font-family: 'DM Mono', monospace;
    font-size: 0.58rem;
    font-weight: 600;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--muted2);
    margin: 24px 0 10px 0;
    display: flex;
    align-items: center;
    gap: 10px;
}
.sec-lbl::after { content:''; flex:1; height:1px; background:var(--border2); }

/* ── SUCCESS / ALERTS ── */
.stAlert {
    background: var(--ink3) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 6px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
}
div[data-testid="stAlert"][kind="success"] {
    border-color: rgba(77,184,154,0.28) !important;
    color: var(--teal) !important;
}

/* ── SPINNER ── */
.stSpinner > div { border-top-color: var(--amber) !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--ink); }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 2px; }

/* ── FOOTER ── */
.site-footer {
    padding: 18px 48px;
    border-top: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-family: 'DM Mono', monospace;
    font-size: 0.60rem;
    color: var(--muted2);
    letter-spacing: 0.08em;
    background: var(--ink2);
}
</style>
""", unsafe_allow_html=True)


# ─── EFFECT FUNCTIONS ───────────────────────────────────────
def pencil_sketch(img_array):
    img = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    inverted = cv2.bitwise_not(gray)
    blurred = cv2.GaussianBlur(inverted, (21, 21), 0)
    inv_blur = cv2.bitwise_not(blurred)
    sketch = cv2.divide(gray, inv_blur, scale=256.0)
    return sketch

def oil_painting(img_array):
    img = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    oil = cv2.stylization(img, sigma_s=60, sigma_r=0.45)
    return cv2.cvtColor(oil, cv2.COLOR_BGR2RGB)

def cartoon_effect(img_array):
    img = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    smoothed = cv2.bilateralFilter(img, d=9, sigmaColor=300, sigmaSpace=300)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.adaptiveThreshold(
        cv2.medianBlur(gray, 7), 255,
        cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 2
    )
    edges_col = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    cartoon = cv2.bitwise_and(smoothed, edges_col)
    return cv2.cvtColor(cartoon, cv2.COLOR_BGR2RGB)

def pil_to_bytes(img, fmt="PNG"):
    buf = io.BytesIO()
    if isinstance(img, np.ndarray):
        img = Image.fromarray(img).convert("L" if len(img.shape) == 2 else "RGB")
    img.save(buf, format=fmt)
    return buf.getvalue()


# ─── MASTHEAD ───────────────────────────────────────────────
st.markdown("""
<div class="masthead">
    <div class="masthead-logo">Face<em>Art</em></div>
    <div class="masthead-tag">CV Style Studio</div>
    <div class="masthead-badge"><div class="badge-dot"></div>OpenCV Powered</div>
</div>
""", unsafe_allow_html=True)


# ─── TWO-COLUMN LAYOUT ──────────────────────────────────────
left_col, right_col = st.columns([1, 2.6], gap="small")

with left_col:
    st.markdown("""
    <div style="background:var(--ink2);border-right:1px solid var(--border2);
                padding:24px 18px;min-height:calc(100vh - 60px);">
    """, unsafe_allow_html=True)

    # Style tiles
    st.markdown('<div class="panel-section">Art Styles</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="style-tile">
        <div class="tile-ico">✏️</div>
        <div>
            <div class="tile-name">Pencil Sketch</div>
            <div class="tile-desc">Hand-drawn B&W sketch from grayscale inversion + blur divide</div>
        </div>
    </div>
    <div class="style-tile">
        <div class="tile-ico">🎨</div>
        <div>
            <div class="tile-name">Oil Painting</div>
            <div class="tile-desc">Painterly canvas feel via OpenCV stylization filter</div>
        </div>
    </div>
    <div class="style-tile">
        <div class="tile-ico">🎌</div>
        <div>
            <div class="tile-name">Cartoon</div>
            <div class="tile-desc">Bold edges + flat colors via bilateral filter & adaptive threshold</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Upload
    st.markdown('<div class="panel-section" style="margin-top:20px">Upload</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Photo", type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed"
    )

    # Style
    st.markdown('<div class="panel-section">Style</div>', unsafe_allow_html=True)
    style = st.selectbox(
        "Select style",
        ["✏️  Pencil Sketch", "🎨  Oil Painting", "🎌  Cartoon"],
        label_visibility="collapsed"
    )

    # Tip
    st.markdown("""
    <div class="tip-box">
        <strong>Best results</strong><br>
        Clear, well-lit face photo<br>
        Min 300 × 300 px<br>
        JPG or PNG format
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    apply_btn = st.button("✦  Apply Style", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


with right_col:
    st.markdown("""
    <div class="canvas-area">
        <div class="canvas-header">
            <div>
                <div class="canvas-title">Style <em>Studio</em></div>
                <div class="canvas-sub">Upload → Select a style → Apply transformation</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── EMPTY STATE ──
    if uploaded is None:
        st.markdown("""
        <div style="padding:0 40px">
        <div class="empty-canvas">
            <div class="empty-canvas-ico">🖼</div>
            <div class="empty-canvas-ttl">Your canvas is empty</div>
            <div class="empty-canvas-sub">
                Upload a photo from the left panel<br>
                then select an art style to begin
            </div>
        </div>
        </div>
        """, unsafe_allow_html=True)

    # ── UPLOADED, NOT APPLIED ──
    elif not apply_btn:
        img_array = np.array(Image.open(uploaded).convert("RGB"))
        st.markdown("<div style='padding:0 40px'>", unsafe_allow_html=True)
        st.markdown('<div class="img-frame"><div class="frame-label"><span>📷</span> Original Photo</div><div class="frame-body">', unsafe_allow_html=True)
        st.image(img_array, use_column_width=True)
        st.markdown("</div></div>", unsafe_allow_html=True)
        st.markdown("""
        <div class="tip-box" style="margin-top:14px">
            <strong>Photo ready</strong> — select a style in the left panel and click Apply Style
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── APPLIED ──
    else:
        img_array = np.array(Image.open(uploaded).convert("RGB"))

        with st.spinner("Rendering style…"):
            if "Pencil" in style:
                result = pencil_sketch(img_array)
                result_pil = Image.fromarray(result).convert("L")
                is_gray = True
                style_name = "Pencil Sketch"
                style_ico  = "✏️"
            elif "Oil" in style:
                result = oil_painting(img_array)
                result_pil = Image.fromarray(result)
                is_gray = False
                style_name = "Oil Painting"
                style_ico  = "🎨"
            else:
                result = cartoon_effect(img_array)
                result_pil = Image.fromarray(result)
                is_gray = False
                style_name = "Cartoon"
                style_ico  = "🎌"

        st.markdown("<div style='padding:0 40px'>", unsafe_allow_html=True)

        # Side by side
        c1, c2 = st.columns(2, gap="small")
        with c1:
            st.markdown('<div class="img-frame"><div class="frame-label"><span>📷</span> Original</div><div class="frame-body">', unsafe_allow_html=True)
            st.image(img_array, use_column_width=True)
            st.markdown("</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="img-frame"><div class="frame-label"><span>{style_ico}</span> {style_name}</div><div class="frame-body">', unsafe_allow_html=True)
            st.image(result, use_column_width=True, clamp=True)
            st.markdown("</div></div>", unsafe_allow_html=True)

        st.success(f"✓  {style_ico} {style_name} applied successfully")

        # Download
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        img_bytes = pil_to_bytes(result_pil)
        st.download_button(
            label=f"⬇  Download {style_name}",
            data=img_bytes,
            file_name=f"faceart_{style_name.lower().replace(' ','_')}.png",
            mime="image/png",
            use_container_width=True
        )

        # All 3 preview
        st.markdown('<div class="sec-lbl" style="margin-top:28px">All Styles Preview</div>', unsafe_allow_html=True)
        with st.spinner("Generating all three styles…"):
            s1 = pencil_sketch(img_array)
            s2 = oil_painting(img_array)
            s3 = cartoon_effect(img_array)

        pa, pb, pc, pd = st.columns(4, gap="small")
        frames = [
            (pa, "📷", "Original",      img_array, False),
            (pb, "✏️", "Sketch",         s1,        True),
            (pc, "🎨", "Oil Paint",      s2,        False),
            (pd, "🎌", "Cartoon",        s3,        False),
        ]
        for col, ico, lbl, img, gray in frames:
            with col:
                st.markdown(f'<div class="img-frame"><div class="frame-label"><span>{ico}</span> {lbl}</div><div class="frame-body">', unsafe_allow_html=True)
                st.image(img, use_column_width=True, clamp=gray)
                st.markdown("</div></div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


# ─── HOW IT WORKS ───────────────────────────────────────────
st.markdown("""
<div style="padding:36px 48px 0 48px">
    <div class="sec-lbl">How It Works</div>
    <div class="how-grid">
        <div class="how-cell" data-n="01">
            <div class="how-ico">✏️</div>
            <div class="how-ttl">Pencil Sketch</div>
            <div class="how-steps">
                → Convert to grayscale<br>
                → Invert pixel values<br>
                → Gaussian blur (21×21)<br>
                → Divide original ÷ blurred<br>
                → Sharp sketch edges emerge
            </div>
        </div>
        <div class="how-cell" data-n="02">
            <div class="how-ico">🎨</div>
            <div class="how-ttl">Oil Painting</div>
            <div class="how-steps">
                → cv2.stylization filter<br>
                → sigma_s = 60 (spatial range)<br>
                → sigma_r = 0.45 (color range)<br>
                → Blends neighboring pixels<br>
                → Canvas painterly texture
            </div>
        </div>
        <div class="how-cell" data-n="03">
            <div class="how-ico">🎌</div>
            <div class="how-ttl">Cartoon Effect</div>
            <div class="how-steps">
                → Bilateral filter smooths colors<br>
                → Adaptive threshold finds edges<br>
                → Median blur reduces noise<br>
                → Combine smooth + edges<br>
                → Bold outlines + flat colors
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─── FOOTER ─────────────────────────────────────────────────
st.markdown("""
<div style="height:36px"></div>
<div class="site-footer">
    <span>FaceArt CV Style Studio · Rahul Maurya</span>
    <span>OpenCV · Streamlit · PIL</span>
</div>
""", unsafe_allow_html=True)
