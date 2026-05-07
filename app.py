import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

st.set_page_config(page_title="FaceArt — CV Style Studio", page_icon="🎨", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=Instrument+Sans:wght@400;500;600&family=DM+Mono:wght@300;400&display=swap');

:root {
    --ink:       #0a0b0d;
    --ink2:      #111318;
    --ink3:      #181c24;
    --amber:     #c9922a;
    --amber-lt:  #e0ab48;
    --amber-dim: rgba(201,146,42,0.10);
    --cream:     #e8e3d9;
    --muted:     rgba(232,227,217,0.38);
    --muted2:    rgba(232,227,217,0.16);
    --border:    rgba(255,255,255,0.06);
    --border2:   rgba(255,255,255,0.10);
    --teal:      #4db89a;
}

*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    font-family: 'Instrument Sans', sans-serif !important;
    background: var(--ink) !important;
    color: var(--cream) !important;
}

/* ── HIDE CHROME & ZERO ALL PADDING ── */
#MainMenu, footer, header { visibility: hidden !important; }

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* Zero out Streamlit column inner gaps */
[data-testid="column"] {
    padding: 0 !important;
    gap: 0 !important;
}
/* Remove the gap row Streamlit adds between columns */
[data-testid="stHorizontalBlock"] {
    gap: 0 !important;
    padding: 0 !important;
}
/* Zero stVerticalBlock padding inside columns */
[data-testid="stVerticalBlock"] {
    gap: 0 !important;
    padding: 0 !important;
}

/* ── MASTHEAD ── */
.masthead {
    background: var(--ink2);
    border-bottom: 1px solid var(--border2);
    padding: 0 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 56px;
}
.m-logo {
    font-family: 'Playfair Display', serif;
    font-size: 1.25rem;
    font-weight: 900;
    color: var(--cream);
    letter-spacing: -0.01em;
}
.m-logo em { color: var(--amber-lt); font-style: italic; }
.m-tag {
    font-family: 'DM Mono', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.20em;
    text-transform: uppercase;
    color: var(--muted);
    border: 1px solid var(--border2);
    padding: 4px 10px;
    border-radius: 2px;
}
.m-badge {
    display: flex; align-items: center; gap: 6px;
    font-family: 'DM Mono', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--teal);
}
.m-dot {
    width: 5px; height: 5px; border-radius: 50%;
    background: var(--teal);
    animation: blink 2.5s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.25} }

/* ── LEFT PANEL ── */
.left-panel {
    background: var(--ink2);
    border-right: 1px solid var(--border2);
    padding: 22px 16px;
    height: calc(100vh - 56px);
    overflow-y: auto;
    position: sticky;
    top: 56px;
}
.p-section {
    font-family: 'DM Mono', monospace;
    font-size: 0.56rem;
    font-weight: 600;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--amber);
    margin: 18px 0 8px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}
.p-section::after { content:''; flex:1; height:1px; background:var(--border2); }
.p-section:first-child { margin-top: 0; }

/* Style tiles */
.s-tile {
    background: var(--ink3);
    border: 1px solid var(--border2);
    border-radius: 7px;
    padding: 11px 13px;
    margin-bottom: 7px;
    display: flex;
    align-items: flex-start;
    gap: 11px;
}
.s-tile:hover {
    border-color: rgba(201,146,42,0.35);
    background: rgba(201,146,42,0.05);
}
.s-ico { font-size: 1.3rem; flex-shrink: 0; margin-top: 1px; }
.s-name {
    font-family: 'Instrument Sans', sans-serif;
    font-size: 0.84rem;
    font-weight: 600;
    color: var(--cream);
    margin-bottom: 2px;
}
.s-desc {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    color: var(--muted);
    line-height: 1.5;
}

/* Tip */
.tip {
    background: var(--amber-dim);
    border: 1px solid rgba(201,146,42,0.18);
    border-radius: 6px;
    padding: 10px 12px;
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: var(--muted);
    line-height: 1.7;
    margin-top: 8px;
}
.tip strong { color: var(--amber-lt); }

/* ── INPUTS ── */
.stFileUploader > div {
    background: var(--ink3) !important;
    border: 1px dashed var(--border2) !important;
    border-radius: 7px !important;
    padding: 12px !important;
}
.stSelectbox > div > div {
    background: var(--ink3) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 6px !important;
    color: var(--cream) !important;
    font-family: 'Instrument Sans', sans-serif !important;
    font-size: 0.84rem !important;
}
label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.58rem !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
    font-weight: 400 !important;
    margin-bottom: 4px !important;
}
.stTextInput > div > div > input,
.stFileUploader label { color: var(--muted) !important; }

/* ── APPLY BUTTON ── */
.stButton > button {
    font-family: 'Instrument Sans', sans-serif !important;
    font-size: 0.84rem !important;
    font-weight: 600 !important;
    background: var(--amber) !important;
    color: #0a0b0d !important;
    border: none !important;
    border-radius: 6px !important;
    height: 40px !important;
    width: 100% !important;
    letter-spacing: 0.03em !important;
    box-shadow: 0 2px 10px rgba(201,146,42,0.25) !important;
    transition: all 0.15s !important;
}
.stButton > button:hover {
    background: var(--amber-lt) !important;
    box-shadow: 0 4px 16px rgba(201,146,42,0.35) !important;
    transform: translateY(-1px) !important;
}

/* ── DOWNLOAD BUTTON ── */
.stDownloadButton > button {
    background: var(--ink3) !important;
    color: var(--teal) !important;
    border: 1px solid rgba(77,184,154,0.25) !important;
    border-radius: 6px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    font-weight: 400 !important;
    height: 36px !important;
    letter-spacing: 0.04em !important;
    box-shadow: none !important;
}
.stDownloadButton > button:hover {
    background: rgba(77,184,154,0.07) !important;
    border-color: rgba(77,184,154,0.45) !important;
    transform: none !important;
}

/* ── CANVAS (right side) ── */
.canvas {
    padding: 28px 36px;
    background: var(--ink);
    min-height: calc(100vh - 56px);
}
.c-header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    margin-bottom: 22px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border2);
}
.c-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.8rem;
    font-weight: 900;
    color: var(--cream);
    letter-spacing: -0.02em;
    line-height: 1;
}
.c-title em { color: var(--amber-lt); font-style: italic; }
.c-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.64rem;
    color: var(--muted);
    margin-top: 6px;
    letter-spacing: 0.03em;
}

/* ── IMAGE FRAME ── */
.img-frame {
    background: var(--ink2);
    border: 1px solid var(--border2);
    border-radius: 8px;
    overflow: hidden;
}
.f-label {
    display: flex; align-items: center; gap: 7px;
    padding: 8px 12px;
    border-bottom: 1px solid var(--border);
    font-family: 'DM Mono', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--muted);
}
.f-body { padding: 10px; }

/* Empty state */
.empty {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    min-height: 380px;
    border: 1px dashed rgba(201,146,42,0.18);
    border-radius: 10px;
    background: var(--ink2);
    text-align: center; padding: 40px;
}
.empty-ico { font-size: 2.8rem; opacity: 0.35; margin-bottom: 14px; }
.empty-ttl {
    font-family: 'Playfair Display', serif;
    font-size: 1.15rem; font-weight: 700;
    color: var(--cream); opacity: 0.45; margin-bottom: 7px;
}
.empty-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem; color: var(--muted2); line-height: 1.7;
}

/* Section label */
.sec-lbl {
    font-family: 'DM Mono', monospace;
    font-size: 0.56rem; font-weight: 600;
    letter-spacing: 0.22em; text-transform: uppercase;
    color: var(--muted2); margin: 22px 0 10px 0;
    display: flex; align-items: center; gap: 10px;
}
.sec-lbl::after { content:''; flex:1; height:1px; background:var(--border2); }

/* How it works */
.how-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 10px; }
.how-cell {
    background: var(--ink2); border: 1px solid var(--border2);
    border-radius: 8px; padding: 16px 14px;
    position: relative; overflow: hidden;
}
.how-cell::before {
    content: attr(data-n);
    position: absolute; top:-8px; right:8px;
    font-family: 'Playfair Display', serif;
    font-size: 3.5rem; font-weight: 900;
    color: rgba(201,146,42,0.04); line-height: 1;
    pointer-events: none;
}
.how-ico { font-size: 1.2rem; margin-bottom: 8px; }
.how-ttl { font-family:'Instrument Sans',sans-serif; font-size:0.85rem; font-weight:600; color:var(--cream); margin-bottom:7px; }
.how-txt { font-family:'DM Mono',monospace; font-size:0.62rem; color:var(--muted); line-height:1.8; }

/* Alerts */
.stAlert {
    background: var(--ink3) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 6px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
}
div[data-testid="stAlert"][kind="success"] {
    border-color: rgba(77,184,154,0.25) !important;
    color: var(--teal) !important;
}
.stSpinner > div { border-top-color: var(--amber) !important; }

::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: var(--ink); }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.07); border-radius: 2px; }

/* ── FOOTER ── */
.site-footer {
    padding: 14px 40px;
    border-top: 1px solid var(--border);
    display: flex; justify-content: space-between;
    font-family: 'DM Mono', monospace;
    font-size: 0.58rem; color: var(--muted2);
    letter-spacing: 0.08em;
    background: var(--ink2);
}
</style>
""", unsafe_allow_html=True)


# ─── EFFECTS ─────────────────────────────────────────────────
def pencil_sketch(img):
    b = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    g = cv2.cvtColor(b, cv2.COLOR_BGR2GRAY)
    inv = cv2.bitwise_not(g)
    blur = cv2.GaussianBlur(inv, (21,21), 0)
    return cv2.divide(g, cv2.bitwise_not(blur), scale=256.0)

def oil_painting(img):
    b = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return cv2.cvtColor(cv2.stylization(b, sigma_s=60, sigma_r=0.45), cv2.COLOR_BGR2RGB)

def cartoon_effect(img):
    b = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    smooth = cv2.bilateralFilter(b, 9, 300, 300)
    gray = cv2.cvtColor(b, cv2.COLOR_BGR2GRAY)
    edges = cv2.adaptiveThreshold(cv2.medianBlur(gray,7), 255,
                                   cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 2)
    return cv2.cvtColor(cv2.bitwise_and(smooth, cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)), cv2.COLOR_BGR2RGB)

def to_bytes(img):
    buf = io.BytesIO()
    if isinstance(img, np.ndarray):
        img = Image.fromarray(img).convert("L" if len(img.shape)==2 else "RGB")
    img.save(buf, format="PNG")
    return buf.getvalue()


# ─── MASTHEAD ────────────────────────────────────────────────
st.markdown("""
<div class="masthead">
    <div class="m-logo">Face<em>Art</em></div>
    <div class="m-tag">CV Style Studio</div>
    <div class="m-badge"><div class="m-dot"></div>OpenCV Powered</div>
</div>
""", unsafe_allow_html=True)


# ─── LAYOUT ──────────────────────────────────────────────────
left, right = st.columns([1, 2.8])

with left:
    st.markdown('<div class="left-panel">', unsafe_allow_html=True)

    st.markdown('<div class="p-section">Art Styles</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="s-tile"><div class="s-ico">✏️</div><div>
        <div class="s-name">Pencil Sketch</div>
        <div class="s-desc">Hand-drawn B&W via grayscale inversion + blur divide</div>
    </div></div>
    <div class="s-tile"><div class="s-ico">🎨</div><div>
        <div class="s-name">Oil Painting</div>
        <div class="s-desc">Painterly canvas via OpenCV stylization filter</div>
    </div></div>
    <div class="s-tile"><div class="s-ico">🎌</div><div>
        <div class="s-name">Cartoon</div>
        <div class="s-desc">Bold edges + flat colors via bilateral & adaptive threshold</div>
    </div></div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="p-section">Upload</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Photo", type=["jpg","jpeg","png","webp"],
                                 label_visibility="collapsed")

    st.markdown('<div class="p-section">Style</div>', unsafe_allow_html=True)
    style = st.selectbox("Style", ["✏️  Pencil Sketch","🎨  Oil Painting","🎌  Cartoon"],
                          label_visibility="collapsed")

    st.markdown("""
    <div class="tip">
        <strong>Best results</strong><br>
        Clear, well-lit face photo<br>
        Min 300×300 px · JPG or PNG
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    apply_btn = st.button("✦  Apply Style", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)


with right:
    st.markdown("""
    <div class="canvas">
        <div class="c-header">
            <div>
                <div class="c-title">Style <em>Studio</em></div>
                <div class="c-sub">Upload → Choose a style → Apply transformation</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    pad = "<div style='padding:0 36px'>"
    end = "</div>"

    if uploaded is None:
        st.markdown(f"""{pad}
        <div class="empty">
            <div class="empty-ico">🖼</div>
            <div class="empty-ttl">Canvas is empty</div>
            <div class="empty-sub">Upload a photo from the left panel<br>then select a style to begin</div>
        </div>{end}""", unsafe_allow_html=True)

    elif not apply_btn:
        img_array = np.array(Image.open(uploaded).convert("RGB"))
        st.markdown(pad, unsafe_allow_html=True)
        st.markdown('<div class="img-frame"><div class="f-label"><span>📷</span> Original Photo</div><div class="f-body">', unsafe_allow_html=True)
        st.image(img_array, use_column_width=True)
        st.markdown('</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="tip" style="margin-top:12px"><strong>Ready</strong> — click Apply Style to transform</div>{end}', unsafe_allow_html=True)

    else:
        img_array = np.array(Image.open(uploaded).convert("RGB"))
        with st.spinner("Rendering…"):
            if   "Pencil" in style: res, pil, gray, sname, sico = pencil_sketch(img_array), None, True,  "Pencil Sketch", "✏️"
            elif "Oil"    in style: res, pil, gray, sname, sico = oil_painting(img_array),  None, False, "Oil Painting",  "🎨"
            else:                   res, pil, gray, sname, sico = cartoon_effect(img_array), None, False, "Cartoon",       "🎌"
            result_pil = Image.fromarray(res).convert("L" if gray else "RGB")

        st.markdown(pad, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="img-frame"><div class="f-label"><span>📷</span> Original</div><div class="f-body">', unsafe_allow_html=True)
            st.image(img_array, use_column_width=True)
            st.markdown('</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="img-frame"><div class="f-label"><span>{sico}</span> {sname}</div><div class="f-body">', unsafe_allow_html=True)
            st.image(res, use_column_width=True, clamp=True)
            st.markdown('</div></div>', unsafe_allow_html=True)

        st.success(f"✓  {sico} {sname} applied")
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.download_button(f"⬇  Download {sname}", to_bytes(result_pil),
                           f"faceart_{sname.lower().replace(' ','_')}.png",
                           "image/png", use_container_width=True)

        # All 3 preview
        st.markdown('<div class="sec-lbl">All Styles Preview</div>', unsafe_allow_html=True)
        with st.spinner("Generating all three…"):
            s1, s2, s3 = pencil_sketch(img_array), oil_painting(img_array), cartoon_effect(img_array)

        pa, pb, pc, pd = st.columns(4)
        for col, ico, lbl, img, clamp in [
            (pa,"📷","Original", img_array, False),
            (pb,"✏️","Sketch",    s1,        True),
            (pc,"🎨","Oil Paint", s2,        False),
            (pd,"🎌","Cartoon",   s3,        False),
        ]:
            with col:
                st.markdown(f'<div class="img-frame"><div class="f-label"><span>{ico}</span> {lbl}</div><div class="f-body">', unsafe_allow_html=True)
                st.image(img, use_column_width=True, clamp=clamp)
                st.markdown('</div></div>', unsafe_allow_html=True)

        st.markdown(end, unsafe_allow_html=True)


# ─── HOW IT WORKS ────────────────────────────────────────────
st.markdown("""
<div style="padding:28px 40px 0 40px">
    <div class="sec-lbl">How It Works</div>
    <div class="how-grid">
        <div class="how-cell" data-n="01">
            <div class="how-ico">✏️</div>
            <div class="how-ttl">Pencil Sketch</div>
            <div class="how-txt">→ Grayscale conversion<br>→ Invert pixel values<br>→ Gaussian blur 21×21<br>→ Divide original ÷ blur<br>→ Sketch edges emerge</div>
        </div>
        <div class="how-cell" data-n="02">
            <div class="how-ico">🎨</div>
            <div class="how-ttl">Oil Painting</div>
            <div class="how-txt">→ cv2.stylization filter<br>→ sigma_s=60 spatial range<br>→ sigma_r=0.45 color range<br>→ Blends neighbor pixels<br>→ Canvas texture appears</div>
        </div>
        <div class="how-cell" data-n="03">
            <div class="how-ico">🎌</div>
            <div class="how-ttl">Cartoon Effect</div>
            <div class="how-txt">→ Bilateral filter smooths<br>→ Adaptive threshold edges<br>→ Median blur reduces noise<br>→ Combine smooth + edges<br>→ Bold outlines + flat colors</div>
        </div>
    </div>
</div>
<div style="height:32px"></div>
<div class="site-footer">
    <span>FaceArt CV Style Studio · Rahul Maurya</span>
    <span>OpenCV · Streamlit · PIL</span>
</div>
""", unsafe_allow_html=True)
