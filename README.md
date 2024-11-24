# Hazardous Driving Eye Gaze Dataset & Analysis

This repository contains tools for downloading, processing, and analyzing eye-tracking data collected during a hazardous driving detection study. The eye-tracking data was collected while participants viewed images from the Cityscapes dataset and identified potential hazards.

## Web Application
The eye-tracking data was collected using a custom web application available at:
[Hazardous Detection Web App](https://lennoxanderson.com/HazardousDetection/)

This application tracks users' gaze patterns as they identify potential hazards in urban driving scenarios from the Cityscapes dataset.

## Dataset
The eye-tracking dataset is hosted on Hugging Face:
[Hazardous Driving Eye Gaze Dataset](https://huggingface.co/datasets/Lennyox/hazardous_driving_eye_gaze)

The dataset contains:
- Gaze coordinates (X, Y positions)
- Timestamps for each gaze point
- Selected hazard locations
- Test set and image identifiers
- Session metadata

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
git clone https://github.com/YourUsername/hazardous-driving-analysis.git
cd hazardous-driving-analysis
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

Options:
```bash
python main.py --base-dir /custom/path --output-dir /output/path --debug
```

## Project Structure
```
project_root/
├── Data/
│   ├── main.py           # Data download and setup
│   └── __init__.py
├── DataAnalysis/
│   ├── main.py           # Visualization and analysis
│   └── __init__.py
└── requirements.txt
```

## Dataset Details

### Cityscapes Images
This study uses a subset of images from the Cityscapes dataset, focusing on urban driving scenarios. The images are organized into test sets (testSet01 through testSet09) and were selected based on their potential to contain hazardous situations.

### Eye-tracking Data
The gaze data includes:
- Fine-grained gaze coordinates (up to 90 points per viewing)
- Temporal information for each gaze point
- Viewer's hazard selections
- Session metadata and timestamps

## Output
Visualizations are saved to the `eye_gaze_research/visualizations` directory by default, including:
- High-resolution heatmaps (300 DPI)
- Multiple visualization types per image
- Detailed filename mapping to original Cityscapes images

## Contributing
Contributions are welcome! Please feel free to submit pull requests.

## License
This project is licensed under [Your License] - see the LICENSE file for details.

## Citation
If you use this dataset or code in your research, please cite:
```
@misc{hazardous_driving_gaze_2024,
    title={Hazardous Driving Eye Gaze Dataset},
    author={Anderson, Lennox},
    year={2024},
    publisher={Hugging Face},
    url={https://huggingface.co/datasets/Lennyox/hazardous_driving_eye_gaze}
}
```

## Acknowledgments
- [Cityscapes Dataset](https://www.cityscapes-dataset.com/) for providing the urban scene images
- All participants who contributed to the eye-tracking data collection