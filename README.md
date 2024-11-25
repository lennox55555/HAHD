# Human-Aligned Hazardous Driving Detection Dataset

## Executive Summary
This project collects and analyzes eye-tracking data to understand human perception and decision-making in driving scenarios. By tracking how humans visually process road hazards, we aim to improve autonomous vehicle systems to make decisions that better align with human judgment.

### Motivation
Current autonomous vehicle systems rely heavily on object detection but often lack human-like judgment in complex scenarios. While datasets like Cityscapes provide excellent visual data for urban scenes, they don't capture how humans process and react to these situations. This project bridges this gap by collecting human attention data through eye-tracking.

### Potential Applications
- Training autonomous vehicles to identify hazards in a human-like manner
- Improving driver monitoring systems
- Developing better driver assistance technologies
- Enhancing safety systems in semi-autonomous vehicles
- Studying human attention patterns in driving scenarios

## Description of Data

### Data Collection Method
Data is collected through a web-based application ([Hazardous Detection Web App](https://lennoxanderson.com/HazardousDetection/)) that:
1. Calibrates user's eyes to the screen
2. Shows urban driving scenes from Cityscapes dataset
3. Tracks eye movements for 7 seconds per image
4. Records user's hazard identification decisions

### Dataset Contents
1. Eye-tracking Data:
   - X, Y gaze coordinates (sampled at high frequency)
   - Timestamps for each gaze point
   - Viewing duration
   - Hazard selection coordinates

2. Metadata:
   - Test set identifiers
   - Image references
   - Session information
   - User response times

3. Image Data:
   - Modified subset of Cityscapes dataset
   - Organized into 9 test sets
   - Focus on urban driving scenarios

### Data Format
- Gaze data stored in CSV format
- Images stored in JPG format
- Mapping file links original Cityscapes names to study identifiers

## Power Analysis Results
Target Data Collection:
- Minimum 15,000 gaze samples/questions
- Current collection: 1,015 completed viewings
- Multiple gaze points per viewing (up to 90 points each)
- Four primary decision classes (stop, slow down, speed up, continue)

## Exploratory Data Analysis
Available visualizations include:
1. Aggregate Attention Heatmaps
   - Shows overall focus areas across all viewers
   - Identifies commonly perceived hazard zones

2. Individual Viewer Patterns
   - Different colors for each viewer's gaze path
   - Helps identify variation in attention patterns

3. Temporal Progression
   - Shows how attention moves over time
   - Indicates initial vs. subsequent focus areas

## Code Repository
The data collection and analysis code is available in two repositories:
1. [Data Collection Web Application](https://lennoxanderson.com/HazardousDetection/)
2. [Data Processing and Analysis Tools](https://github.com/YourUsername/hazardous-driving-analysis)

## Ethics Statement
This project adheres to ethical data collection practices:
- Voluntary participation
- Clear consent process before eye tracking
- No personal information collected
- Transparent data usage purposes
- Option to withdraw at any time
- Data anonymization
- Safe data storage and handling

The collected data aims to improve road safety and autonomous vehicle systems while respecting user privacy and consent.

## License
This project is licensed under Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0).

You are free to:
- Share and adapt the material for non-commercial purposes
- Must provide appropriate attribution

### Citations
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

## Acknowledgments
- Cityscapes Dataset for urban driving scenes
- All participants who contributed eye-tracking data
- Duke University for project support
