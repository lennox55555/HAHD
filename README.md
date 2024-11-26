# Human-Aligned Hazardous Driving Detection Dataset

## Executive Summary:
The advancement of autonomous vehicles has primarily focused on object detection and road segmentation, yet there remains a crucial gap in understanding how human drivers process and respond to complex road scenarios. This project addresses this gap by creating a dataset that captures human visual attention patterns during hazard detection in urban driving scenes. Through a web based eyetracking application, we collect gaze data as participants analyze potential road hazards, providing insights into human decision-making processes that could inform more intuitive autonomous driving systems.

The dataset combines eyetracking data with scenes from the Cityscapes dataset, creating a bridge between computer vision capabilities and human perception. This allows for the development of autonomous systems that not only detect objects but also prioritize attention in ways that align with human judgment. The data collection process has yielded over 1,000 viewing sessions, each containing up to 90 gaze coordinates with temporal information, providing a foundation for understanding human attention patterns in driving scenarios.

## Prerequisites

Before getting started, you'll need:
1. A Hugging Face account and access token
   - Sign up at [Hugging Face](https://huggingface.co/)
   - Get your token from [Access Tokens](https://huggingface.co/settings/tokens)

2. A Cityscapes account
   - Register at [Cityscapes](https://www.cityscapes-dataset.com/)
   - You'll need credentials to download the dataset

3. Python 3.8 or higher

## Installation

1. Clone the repository:
```bash
git clone https://github.com/lennox55555/Human-Aligned-Hazardous-Detection.git
cd Human-Aligned-Hazardous-Detection
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

### 1. Data Setup
First, download and process the required datasets:

```bash
cd Data
python main.py
```

This script will:
- Download the eye-tracking data from Hugging Face
- Download necessary images from Cityscapes
- Process and organize the data

When prompted:
- Enter your Hugging Face token
- Enter your Cityscapes credentials

### 2. Visualization
After data setup is complete, generate visualizations:

```bash
cd ../DataAnalysis
python main.py
```

This will create three types of visualizations:
1. Aggregate heatmaps showing overall attention patterns
2. Viewer-separated heatmaps showing individual viewing patterns
3. Temporal heatmaps showing gaze progression over time

## File Structure:
```bash
|── Hazardous-Driving-Detection/
|   ├── Data/
|   │   ├── eye_gaze_research/
|   │   ├── __init__.py
|   │   ├── cityscapes_mapping.csv
|   │   └── main.py
|   │
|   ├── DataAnalysis/
|   │   ├── __init__.py
|   │   └── main.py
|   │
|   ├── DrivingWebApplication/
|   │   ├── images/
|   │   ├── app.js
|   │   ├── awsUploader.js
|   │   ├── index.html
|   │   ├── quiz.js
|   │   └── styles.css
|   │
|   ├── Cityscapes dataset.pdf
|   ├── README.md
|   └── requirements.txt
```

## Description of Data:
The data collection utilizes a full stack Hazardous Detection Web App. The application implements a careful protocol where each participant undergoes eye calibration before viewing urban driving scenes from the Cityscapes dataset. During each 10 second viewing period, the system records precise eye movements and gaze patterns, followed by participant feedback on perceived hazards.

The dataset contains eyetracking data including X and Y gaze coordinates, timestamps, viewing durations, and hazard servity selection. This information is complemented by metadata containing test set identifiers, image references, and detailed session information. The image data consists of a carefully curated subset of the Cityscapes dataset, organized into nine test sets that represent diverse urban driving scenarios.

All data is structured for research accessibility, with gaze data stored in CSV format and images maintained in JPG format. A dedicated mapping file provides clear relationships between original Cityscapes identifiers and the study's naming conventions, ensuring seamless integration with existing research frameworks.

## Power Analysis Results:
The data collection strategy aims to build a dataset sufficient for meaningful machine learning analysis to enventually trained. Initial targets were set at 15,000 gaze samples/questions to ensure adequate representation across all decision classes. Currently, the dataset includes 1,015 completed viewing sessions, with each session capturing up to 90 distinct gaze points. This data collection provides information about viewing patterns.

## Exploratory Data Analysis
The analysis reveals complex patterns in how participants visually process driving scenes. Through aggregate attention heatmaps, we've identified common focus areas that attract immediate attention across multiple viewers. These heatmaps highlight zones where potential hazards are most frequently detected. This provids insights the collective human perception of road safety.

Individual viewer pattern analysis reveals fascinating variations in how different participants approach hazard detection. Using visualization techniques, we can track unique gaze paths and attention patterns, showing how different viewers prioritize various elements within the same scene. This analysis helps identify both common patterns and individual variations in hazard detection strategies.

Temporal progression analysis demonstrates how attention shifts during the viewing period, from initial focus areas to subsequent points of interest. This timeline based visualization helps understand the sequence of human attention in processing road scenes, crucial information for developing more intuitive autonomous systems.

## Ethics Statement
This research collects anonymized eye-tracking data during simulated driving scenarios. Data collection is strictly limited to gaze coordinates (X and Y positions), timestamps, and hazard selection responses. No personal identifiers, demographic information, or biometric data beyond gaze positions are recorded or stored. The web application informs participants about data collection scope..

## Citations
For using this dataset:
```bibtex
@misc{hazardous_driving_gaze_2024,
    title={Hazardous Driving Eye Gaze Dataset},
    author={Anderson, Lennox},
    year={2024},
    publisher={Hugging Face},
    howpublished={\url{https://huggingface.co/datasets/Lennyox/hazardous_driving_eye_gaze}},
    note={Creative Commons Attribution-NonCommercial 4.0 International License}
}
```

For Cityscapes dataset:
```bibtex
@inproceedings{Cordts2016Cityscapes,
    title={The Cityscapes Dataset for Semantic Urban Scene Understanding},
    author={Cordts, Marius and Omran, Mohamed and Ramos, Sebastian and Rehfeld, Timo and Enzweiler, Markus and Benenson, Rodrigo and Franke, Uwe and Roth, Stefan and Schiele, Bernt},
    booktitle={Proc. of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR)},
    year={2016}
}
```

