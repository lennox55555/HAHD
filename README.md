# Human-Aligned Hazardous Driving Detection Dataset

## Executive Summary:
The advancement of autonomous vehicles has primarily focused on object detection and road segmentation, yet there remains a crucial gap in understanding how human drivers process and respond to complex road scenarios. This project addresses this gap by creating a comprehensive dataset that captures human visual attention patterns during hazard detection in urban driving scenes. Through a web-based eye-tracking application, we collect detailed gaze data as participants analyze potential road hazards, providing insights into human decision-making processes that could inform more intuitive autonomous driving systems.

The dataset uniquely combines eye-tracking data with scenes from the Cityscapes dataset, creating a bridge between computer vision capabilities and human perception. This integration allows for the development of autonomous systems that not only detect objects but also prioritize attention in ways that align with human judgment. The data collection process has yielded over 1,000 viewing sessions, each containing up to 90 high-precision gaze coordinates with temporal information, providing a rich foundation for understanding human attention patterns in driving scenarios.

The potential impact of this research extends beyond autonomous vehicles into broader applications in transportation safety and human-computer interaction. The collected data can enhance driver monitoring systems, improve driver training programs, and contribute to the development of more intuitive driver assistance technologies. Furthermore, this dataset provides valuable insights for researchers studying human attention patterns and decision-making processes in critical situations.

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
The data collection utilizes a sophisticated web-based platform accessible at Hazardous Detection Web App. The application implements a careful protocol where each participant undergoes eye calibration before viewing urban driving scenes from the Cityscapes dataset. During each seven-second viewing period, the system records precise eye movements and gaze patterns, followed by participant feedback on perceived hazards.
The dataset encompasses comprehensive eye-tracking data including high-frequency X and Y gaze coordinates, precise timestamps, viewing durations, and hazard selection coordinates. This information is complemented by rich metadata containing test set identifiers, image references, and detailed session information. The image data consists of a carefully curated subset of the Cityscapes dataset, organized into nine distinct test sets that represent diverse urban driving scenarios.

All data is structured for research accessibility, with gaze data stored in CSV format and images maintained in high-quality JPG format. A dedicated mapping file provides clear relationships between original Cityscapes identifiers and the study's naming conventions, ensuring seamless integration with existing research frameworks.

## Power Analysis Results:
The data collection strategy aims to build a dataset sufficient for meaningful machine learning analysis to enventually trained. Initial targets were set at 15,000 gaze samples/questions to ensure adequate representation across all decision classes. Currently, the dataset includes 1,015 completed viewing sessions, with each session capturing up to 90 distinct gaze points. This data collection provides information about viewing patterns.

The dataset encompasses four primary decision classes representing common driving responses: stopping, slowing down, speeding up, and continuing at current speed. The current collection volume allows for detailed analysis of attention patterns within each decision category, while ongoing data collection continues to enhance the dataset's statistical power.

## Exploratory Data Analysis
The analysis reveals complex patterns in how participants visually process driving scenes. Through aggregate attention heatmaps, we've identified common focus areas that attract immediate attention across multiple viewers. These heatmaps highlight crucial zones where potential hazards are most frequently detected, providing insights into collective human perception of road safety.

Individual viewer pattern analysis reveals fascinating variations in how different participants approach hazard detection. Using color-coded visualization techniques, we can track unique gaze paths and attention patterns, showing how different viewers prioritize various elements within the same scene. This analysis helps identify both common patterns and individual variations in hazard detection strategies.
Temporal progression analysis demonstrates how attention shifts during the viewing period, from initial focus areas to subsequent points of interest. This timeline-based visualization helps understand the sequence of human attention in processing road scenes, crucial information for developing more intuitive autonomous systems.

## Ethics Statement
The research prioritizes ethical data collection and participant privacy. Every aspect of the data collection process adheres to strict ethical guidelines, beginning with voluntary participation and explicit consent for eye tracking. We maintain complete transparency about data usage purposes while collecting no personal identification information. Participants retain the right to withdraw at any time, and all data undergoes thorough anonymization before storage or analysis.

The data storage and handling procedures follow rigorous security protocols to ensure participant privacy and data integrity. Our primary goal remains the advancement of road safety and autonomous vehicle systems, conducted with unwavering respect for participant privacy and research ethics.

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

