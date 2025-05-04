# Marvel Poster Classifier

[![Live Demo](https://img.shields.io/badge/Live%20Demo-HuggingFace-blue?style=for-the-badge)](https://huggingface.co/spaces/cfor224/mcu-poster-classifier)

This project classifies Marvel Cinematic Universe (MCU) posters by phase (Phase 1, Phase 2, etc.) using a deep learning model (ResNet-18). Built with PyTorch and deployed using Gradio.

---

## Project Overview

The goal is to classify movie and show posters from the MCU into their correct phase using transfer learning. The dataset is small (~217 images), but the model achieved around 70% validation accuracy.

---

## How It Works

### Data
- Posters were collected and manually labeled by MCU phase.
- Basic preprocessing and augmentation included resizing, normalization, flipping, and rotation.

### Model
- Architecture: ResNet-18 pretrained on ImageNet.
- Final classification layer was fine-tuned while freezing the rest of the network.
- Training used Adam optimizer and cross-entropy loss.

### Evaluation
- A confusion matrix was used to evaluate classification performance.
- Observed some common misclassifications, often between neighboring phases.
- Class imbalance was noted, which may have affected accuracy.

---

## Key Findings

- Transfer learning allows reasonable performance even with small datasets.
- Phase 3 was often confused with other phases due to poster similarities.
- Increasing dataset size or balancing classes may improve accuracy.

---

## How to Run Locally

1. Clone the repository:
   `git clone https://github.com/crystalmford/mcu-poster-classifier.git`
   `cd mcu-poster-classifier`

2. Install the required dependencies:
   `pip install -r requirements.txt`

3. Run the Gradio app:
   `python app.py`

---

## Additional Project Files

### Dataset Collection
The dataset of MCU posters was created using the TMDb API.
Posters were automatically searched, filtered, and deduplicated using:

- [`data_collection/fetch_movie_posters.py`](data_collection/fetch_movie_posters.py)

### Notebook (Model Training + Evaluation)
The entire modeling process is also available as a Jupyter notebook:

- [`data_collection/marvel.ipynb`](data_collection/marvel.ipynb)
