import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import gradio as gr

# === CONFIG ===
model_path = "marvel_model.pth"
class_names = ['phase_1', 'phase_2', 'phase_3', 'phase_4', 'phase_5', 'disney_plus', 'upcoming']
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# === TRANSFORMS ===
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# === MODEL LOADING ===
def load_model():
    model = models.resnet18(pretrained=False)
    model.fc = nn.Linear(model.fc.in_features, len(class_names))
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    return model.to(device)

model = load_model()

# === PREDICTION FUNCTION ===
def classify_poster(image):
    image = image.convert("RGB")
    img_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        output = model(img_tensor)
        probs = torch.softmax(output, dim=1)
        top_prob, top_idx = torch.max(probs, dim=1)

    pred_class = class_names[top_idx.item()].replace('_', ' ').title()
    confidence = top_prob.item()

    return f"Prediction: {pred_class}\nConfidence: {confidence:.2%}"

# === STYLED GRADIO APP ===
with gr.Blocks() as demo:
    # Inject custom CSS for the button
    gr.HTML("""
        <style>
            .custom-button button {
                background-color: #d32f2f !important;  /* Marvel red */
                color: white !important;
                font-weight: bold;
                border: none;
                padding: 10px 16px;
                font-size: 16px;
                border-radius: 6px;
                cursor: pointer;
            }

            .custom-button button:hover {
                background-color: #b71c1c !important;
            }
        </style>
    """)

    # Banner image
    gr.Image("mcu_banner.jpg", show_label=False, container=False, height=250)

    # Title and description
    gr.Markdown("<h1 style='text-align: center;'>Marvel Poster Phase Classifier</h1>")
    gr.Markdown(
        "<p style='text-align: center;'>Upload a Marvel movie or show poster to predict which MCU phase it belongs to.<br>"
        "Powered by ResNet-18 and transfer learning.</p>"
    )

    # Layout: Image input and prediction output side-by-side
    with gr.Row():
        with gr.Column(scale=1):
            image_input = gr.Image(type="pil", label="Upload Poster", height=300)
        with gr.Column(scale=1):
            result_output = gr.Textbox(label="Prediction", lines=2, interactive=False)

    # Styled classify button
    with gr.Row():
        submit_button = gr.Button("Classify", elem_classes=["custom-button"])

    # Connect button to function
    submit_button.click(fn=classify_poster, inputs=image_input, outputs=result_output)

if __name__ == "__main__":
    demo.launch()
