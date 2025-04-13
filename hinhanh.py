import streamlit as st
import numpy as np
import cv2
from PIL import Image

st.set_page_config(page_title="Ứng dụng chỉnh sửa ảnh", layout="wide")
st.title("📸 Ứng dụng chỉnh sửa ảnh đơn giản")

st.markdown("### 1. Tải ảnh lên")
uploaded_file = st.file_uploader("Chọn ảnh từ máy tính", type=["jpg", "jpeg", "png"])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    original_img = img.copy()

    # Giao diện chia 2 cột
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🖼 Ảnh gốc")
        st.image(original_img, use_container_width=True)

    # Các tùy chọn chỉnh sửa
    st.markdown("### 2. Tùy chỉnh ảnh")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        brightness = st.slider("🌞 Độ sáng", -100, 100, 0)
    with col_b:
        contrast = st.slider("🎛 Độ tương phản", -100, 100, 0)
    with col_c:
        sharpness = st.slider("🔍 Độ nét", -5, 5, 0)

    rotation = st.selectbox("🌀 Xoay ảnh", ["0°", "90°", "180°", "270°"])

    # Xử lý ảnh
    img_edit = original_img.astype(np.int16) + brightness
    img_edit = np.clip(img_edit, 0, 255)

    if contrast != 0:
        factor = (259 * (contrast + 255)) / (255 * (259 - contrast))
        img_edit = factor * (img_edit - 128) + 128
        img_edit = np.clip(img_edit, 0, 255)

    img_edit = img_edit.astype(np.uint8)

    # Độ nét
    if sharpness != 0:
        if sharpness > 0:
            kernel = np.array([[0, -1, 0],
                               [-1, 5 + sharpness, -1],
                               [0, -1, 0]])
            img_edit = cv2.filter2D(img_edit, -1, kernel)
        else:
            img_edit = cv2.GaussianBlur(img_edit, (3, 3), sigmaX=abs(sharpness))

    # Xoay ảnh
    if rotation == "90°":
        img_edit = cv2.rotate(img_edit, cv2.ROTATE_90_CLOCKWISE)
    elif rotation == "180°":
        img_edit = cv2.rotate(img_edit, cv2.ROTATE_180)
    elif rotation == "270°":
        img_edit = cv2.rotate(img_edit, cv2.ROTATE_90_COUNTERCLOCKWISE)

    # ✂️ Cắt ảnh
    st.markdown("### ✂️ 3. Cắt ảnh")
    h, w = img_edit.shape[:2]
    col_crop1, col_crop2 = st.columns(2)
    with col_crop1:
        x1 = st.slider("🔲 Trái (x1)", 0, w - 1, 0)
        x2 = st.slider("🔳 Phải (x2)", x1 + 1, w, w)
    with col_crop2:
        y1 = st.slider("🔲 Trên (y1)", 0, h - 1, 0)
        y2 = st.slider("🔳 Dưới (y2)", y1 + 1, h, h)
    img_edit = img_edit[y1:y2, x1:x2]

    with col2:
        st.subheader("🖼 Ảnh sau chỉnh sửa và cắt")
        st.image(img_edit, use_container_width=True)

    # Tách kênh màu
    st.markdown("### 4. Tách kênh màu RGB")
    channel = st.selectbox("🎨 Chọn kênh màu để tách", ["🔴 Đỏ (R)", "🟢 Lục (G)", "🔵 Lam (B)"])
    if st.button("👁 Hiển thị kênh đã chọn"):
        r, g, b = cv2.split(original_img)
        r_img = np.zeros_like(original_img)
        g_img = np.zeros_like(original_img)
        b_img = np.zeros_like(original_img)

        if channel == "🔴 Đỏ (R)":
            r_img[:, :, 0] = r
            st.image(r_img, caption="Kênh Đỏ (R)", use_container_width=True)
        elif channel == "🟢 Lục (G)":
            g_img[:, :, 1] = g
            st.image(g_img, caption="Kênh Lục (G)", use_container_width=True)
        elif channel == "🔵 Lam (B)":
            b_img[:, :, 2] = b
            st.image(b_img, caption="Kênh Lam (B)", use_container_width=True)

    # Tải ảnh
    st.markdown("### 5. Tải ảnh chỉnh sửa")
    result_pil = Image.fromarray(img_edit)
    st.download_button("💾 Tải ảnh", data=result_pil.tobytes(),
                       file_name="anh_chinh_sua.png", mime="image/png")
