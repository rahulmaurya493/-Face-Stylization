import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

# ─── Page Config ────────────────────────────────────────────
st.set_page_config(
    page_title="FaceArt AI — Style Your Face",
    page_icon="🎨",
    layout="wide"
)

# ─── Styling ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Raleway:wght@700;800;900&family=DM+Sans:wght@400;500;600&display=swap');

html, body, .stApp {
    font-family: 'DM Sans', sans-serif;
    background: linear-gradient(135deg, #0d0d0d 0%, #1a1a2e 50%, #0d0d0d 100%);
    color: #f0f0f0;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem; max-width: 1200px; }

.hero {
    background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
    border: 1px solid rgba(139,92,246,0.25);
    border-radius: 24px;
    padding: 48px 52px;
    margin-bottom: 32px;
    text-align: center;
}
.hero-title {
    font-family: 'Raleway', serif;
    font-size: 3.2rem;
    font-weight: 900;
    color: #fff;
    margin: 0 0 12px;
}
.hero-title span { 
    background: linear-gradient(90deg, #8b5cf6, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub {
    color: rgba(255,255,255,0.55);
    font-size: 1.05rem;
    margin: 0;
}

.style-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 24px;
    text-align: center;
    cursor: pointer;
    transition: all 0.25s;
    margin-bottom: 12px;
}
.style-card:hover {
    border-color: rgba(139,92,246,0.45);
    background: rgba(139,92,246,0.08);
    transform: translateY(-3px);
}
.style-icon { font-size: 2.8rem; margin-bottom: 10px; }
.style-name {
    font-weight: 700;
    font-size: 1.05rem;
    color: #fff;
    margin-bottom: 6px;
}
.style-desc {
    color: rgba(255,255,255,0.50);
    font-size: 0.83rem;
    line-height: 1.5;
}

.result-box {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(139,92,246,0.20);
    border-radius: 18px;
    padding: 20px;
    text-align: center;
}
.result-label {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: rgba(255,255,255,0.40);
    margin-bottom: 10px;
}

.tip {
    background: rgba(139,92,246,0.08);
    border-left: 3px solid #8b5cf6;
    border-radius: 0 12px 12px 0;
    padding: 12px 16px;
    font-size: 0.88rem;
    color: rgba(255,255,255,0.70);
    margin: 14px 0;
}
.tip strong { color: #a78bfa; }

.divider { 
    height: 1px; 
    background: rgba(255,255,255,0.07); 
    margin: 28px 0; 
}

label { 
    color: rgba(255,255,255,0.80) !important; 
    font-weight: 600 !important; 
}

.stButton > button {
    width: 100%;
    background: linear-gradient(90deg, #8b5cf6, #ec4899) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.75rem !important;
    letter-spacing: 0.8px !important;
    box-shadow: 0 4px 20px rgba(139,92,246,0.35) !important;
}
.stButton > button:hover {
    opacity: 0.90 !important;
    transform: translateY(-2px) !important;
}
.stDownloadButton > button {
    background: linear-gradient(90deg, #10b981, #059669) !important;
    box-shadow: 0 4px 20px rgba(16,185,129,0.30) !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Effects Functions ───────────────────────────────────────
def pencil_sketch(img_array):
    img = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    inverted = cv2.bitwise_not(gray)
    blurred = cv2.GaussianBlur(inverted, (21, 21), 0)
    inverted_blur = cv2.bitwise_not(blurred)
    sketch = cv2.divide(gray, inverted_blur, scale=256.0)
    return sketch

def oil_painting(img_array):
    img = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    oil = cv2.stylization(img, sigma_s=60, sigma_r=0.45)
    return cv2.cvtColor(oil, cv2.COLOR_BGR2RGB)

def cartoon_effect(img_array):
    img = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    smoothed = cv2.bilateralFilter(img, d=9,
                                    sigmaColor=300,
                                    sigmaSpace=300)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.adaptiveThreshold(
        cv2.medianBlur(gray, 7), 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY, 9, 2
    )
    edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    cartoon = cv2.bitwise_and(smoothed, edges_colored)
    return cv2.cvtColor(cartoon, cv2.COLOR_BGR2RGB)

def pil_to_bytes(img, fmt="PNG"):
    buf = io.BytesIO()
    if isinstance(img, np.ndarray):
        if len(img.shape) == 2:
            img = Image.fromarray(img).convert("L")
        else:
            img = Image.fromarray(img)
    img.save(buf, format=fmt)
    return buf.getvalue()

# ─── HERO ───────────────────────────────────────────────────
st.markdown("""
<div class='hero'>
    <div style='font-size:3rem;margin-bottom:12px;'>🎨</div>
    <h1 class='hero-title'>FaceArt <span>AI Styler</span></h1>
    <p class='hero-sub'>
        Upload any photo → transform it into Pencil Sketch, Oil Painting or Cartoon!
        Powered by OpenCV Computer Vision.
    </p>
</div>
""", unsafe_allow_html=True)

# ─── STYLE SELECTOR ─────────────────────────────────────────
st.markdown("### 🖼️ &nbsp; Choose Your Art Style")
st.markdown("<p style='color:rgba(255,255,255,0.45);font-size:0.85rem;margin-top:-10px;margin-bottom:20px;'>Pick the transformation you want to apply to your photo</p>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class='style-card'>
        <div class='style-icon'>✏️</div>
        <div class='style-name'>Pencil Sketch</div>
        <div class='style-desc'>Transforms your photo into a realistic hand-drawn pencil sketch in black & white</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='style-card'>
        <div class='style-icon'>🎨</div>
        <div class='style-name'>Oil Painting</div>
        <div class='style-desc'>Gives your photo a smooth artistic oil painting effect like a real canvas artwork</div>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='style-card'>
        <div class='style-icon'>🎌</div>
        <div class='style-name'>Cartoon</div>
        <div class='style-desc'>Turns your photo into a vibrant cartoon with bold edges and smooth flat colors</div>
    </div>""", unsafe_allow_html=True)

# ─── CONTROLS ───────────────────────────────────────────────
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

left, right = st.columns([1, 2], gap="large")

with left:
    st.markdown("### 📤 &nbsp; Upload Your Photo")
    uploaded = st.file_uploader(
        "Drop image here",
        type=["jpg", "jpeg", "png", "webp"],
        help="Best results with clear face photos!"
    )

    style = st.selectbox(
        "Select Art Style",
        ["✏️ Pencil Sketch", "🎨 Oil Painting", "🎌 Cartoon"],
        help="Choose which style to apply!"
    )

    st.markdown("""
    <div class='tip'>
        <strong>💡 Best Results:</strong><br>
        • Clear, well-lit photos<br>
        • Face should be visible<br>
        • Minimum 200x200px size<br>
        • JPG or PNG format
    </div>""", unsafe_allow_html=True)

    apply_btn = st.button("✨  Apply Style!", key="apply")

with right:
    if uploaded is None:
        st.markdown("""
        <div style='background:rgba(255,255,255,0.03);border:2px dashed rgba(139,92,246,0.25);
                    border-radius:18px;padding:60px;text-align:center;'>
            <div style='font-size:3rem;margin-bottom:14px;'>🖼️</div>
            <div style='font-weight:700;color:rgba(255,255,255,0.50);font-size:1.05rem;'>
                Upload a photo to get started!
            </div>
            <div style='color:rgba(255,255,255,0.30);font-size:0.85rem;margin-top:8px;'>
                Your transformed image will appear here
            </div>
        </div>""", unsafe_allow_html=True)

    elif uploaded and not apply_btn:
        img_array = np.array(Image.open(uploaded).convert("RGB"))
        st.markdown("<div class='result-box'>", unsafe_allow_html=True)
        st.markdown("<div class='result-label'>📷 Original Photo</div>", unsafe_allow_html=True)
        st.image(img_array, use_column_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='tip'>
            <strong>✅ Photo uploaded!</strong> 
            Now select your style and click <strong>Apply Style!</strong>
        </div>""", unsafe_allow_html=True)

    elif uploaded and apply_btn:
        img_array = np.array(Image.open(uploaded).convert("RGB"))

        with st.spinner("✨ Applying style... Please wait!"):
            if "Pencil" in style:
                result = pencil_sketch(img_array)
                result_pil = Image.fromarray(result).convert("L")
                is_gray = True
                style_name = "Pencil Sketch ✏️"
                style_emoji = "✏️"
            elif "Oil" in style:
                result = oil_painting(img_array)
                result_pil = Image.fromarray(result)
                is_gray = False
                style_name = "Oil Painting 🎨"
                style_emoji = "🎨"
            else:
                result = cartoon_effect(img_array)
                result_pil = Image.fromarray(result)
                is_gray = False
                style_name = "Cartoon 🎌"
                style_emoji = "🎌"

        # ── Show side by side ──────────────────────────────
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div class='result-box'>", unsafe_allow_html=True)
            st.markdown("<div class='result-label'>📷 Original</div>", unsafe_allow_html=True)
            st.image(img_array, use_column_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.markdown("<div class='result-box'>", unsafe_allow_html=True)
            st.markdown(f"<div class='result-label'>{style_emoji} {style_name}</div>", unsafe_allow_html=True)
            if is_gray:
                st.image(result, use_column_width=True, clamp=True)
            else:
                st.image(result, use_column_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.success(f"✅ {style_name} applied successfully!")

        # ── Download Button ────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        img_bytes = pil_to_bytes(result_pil)
        st.download_button(
            label=f"⬇️  Download {style_name}",
            data=img_bytes,
            file_name=f"faceart_{style.split()[1].lower()}.png",
            mime="image/png",
            use_container_width=True
        )

        # ── All 3 Preview ──────────────────────────────────
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.markdown("### 👀 &nbsp; Preview All 3 Styles")
        st.markdown("<p style='color:rgba(255,255,255,0.45);font-size:0.85rem;margin-top:-10px;'>See how your photo looks in every style!</p>", unsafe_allow_html=True)

        with st.spinner("Generating all styles..."):
            s1 = pencil_sketch(img_array)
            s2 = oil_painting(img_array)
            s3 = cartoon_effect(img_array)

        pa, pb, pc, pd = st.columns(4)
        with pa:
            st.markdown("<div class='result-box'>", unsafe_allow_html=True)
            st.markdown("<div class='result-label'>📷 Original</div>", unsafe_allow_html=True)
            st.image(img_array, use_column_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with pb:
            st.markdown("<div class='result-box'>", unsafe_allow_html=True)
            st.markdown("<div class='result-label'>✏️ Sketch</div>", unsafe_allow_html=True)
            st.image(s1, use_column_width=True, clamp=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with pc:
            st.markdown("<div class='result-box'>", unsafe_allow_html=True)
            st.markdown("<div class='result-label'>🎨 Oil Paint</div>", unsafe_allow_html=True)
            st.image(s2, use_column_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with pd:
            st.markdown("<div class='result-box'>", unsafe_allow_html=True)
            st.markdown("<div class='result-label'>🎌 Cartoon</div>", unsafe_allow_html=True)
            st.image(s3, use_column_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ─── HOW IT WORKS ───────────────────────────────────────────
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("### 🧠 &nbsp; How Does It Work?")

hw1, hw2, hw3 = st.columns(3)
with hw1:
    st.markdown("""
    <div class='style-card'>
        <div class='style-icon'>✏️</div>
        <div class='style-name'>Pencil Sketch</div>
        <div class='style-desc' style='text-align:left;'>
            1. Convert image to grayscale<br>
            2. Invert the colors<br>
            3. Apply Gaussian blur<br>
            4. Divide original by blurred<br>
            → Creates sketch-like edges!
        </div>
    </div>""", unsafe_allow_html=True)
with hw2:
    st.markdown("""
    <div class='style-card'>
        <div class='style-icon'>🎨</div>
        <div class='style-name'>Oil Painting</div>
        <div class='style-desc' style='text-align:left;'>
            1. Apply stylization filter<br>
            2. Sigma_s controls smoothness<br>
            3. Sigma_r controls color range<br>
            4. Blends nearby pixels together<br>
            → Creates painterly effect!
        </div>
    </div>""", unsafe_allow_html=True)
with hw3:
    st.markdown("""
    <div class='style-card'>
        <div class='style-icon'>🎌</div>
        <div class='style-name'>Cartoon</div>
        <div class='style-desc' style='text-align:left;'>
            1. Bilateral filter smooths colors<br>
            2. Adaptive threshold finds edges<br>
            3. Combine edges + smooth image<br>
            4. Bold outlines + flat colors<br>
            → Creates cartoon look!
        </div>
    </div>""", unsafe_allow_html=True)

# ─── FOOTER ─────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;padding:36px 0 20px;color:rgba(255,255,255,0.20);font-size:0.80rem;'>
    Built by <strong style='color:rgba(255,255,255,0.40);'>Rahul Maurya</strong> &nbsp;|&nbsp;
    Powered by <strong style='color:rgba(255,255,255,0.40);'>OpenCV + Streamlit</strong> &nbsp;|&nbsp;
    FaceArt AI v1.0 🎨
</div>""", unsafe_allow_html=True)
