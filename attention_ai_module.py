
import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import torch
import torchvision.transforms as transforms
import cv2
import os

@st.cache_resource
def load_model():
    from torchvision.models import resnet50
    model = resnet50(pretrained=True)
    model.eval()
    return model

def get_saliency_map(image):
    model = load_model()
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor()
    ])
    img_tensor = transform(image).unsqueeze(0).requires_grad_()
    output = model(img_tensor)
    output_idx = output.argmax()
    output_max = output[0, output_idx]
    output_max.backward()

    saliency, _ = torch.max(img_tensor.grad.data.abs(), dim=1)
    saliency = saliency.reshape(224, 224).cpu().numpy()
    return saliency

def upscale_to_image(saliency, target_size):
    return cv2.resize(saliency, target_size, interpolation=cv2.INTER_CUBIC)

def run_attention_map():
    st.header("🧠 Attention Prediction (AI-based)")

    uploaded_image = st.file_uploader("📷 Загрузите макет интерфейса (JPG или PNG)", type=["png", "jpg", "jpeg"])

    if uploaded_image:
        image = Image.open(uploaded_image).convert("RGB")
        st.image(image, caption="Макет для анализа", use_container_width=True)

        with st.spinner("Анализ внимания..."):
            saliency = get_saliency_map(image)
            saliency_upscaled = upscale_to_image(saliency, image.size)

            fig, ax = plt.subplots(figsize=(8, 6))
            ax.imshow(image)
            ax.imshow(saliency_upscaled, cmap="hot", alpha=0.6)
            ax.axis("off")
            output_path = "output/attention_map_ai.png"
            os.makedirs("output", exist_ok=True)
            fig.savefig(output_path, bbox_inches='tight')
            plt.close()

        st.image(output_path, caption="Карта визуального внимания", use_container_width=True)

        with open(output_path, "rb") as img_file:
            st.download_button("📥 Скачать карту внимания", img_file, file_name="attention_map_ai.png", mime="image/png")
    else:
        st.info("Пожалуйста, загрузите изображение.")
