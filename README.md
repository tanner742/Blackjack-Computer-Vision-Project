# Blackjack-Computer-Vision-Project
Blackjack analysis using computer vision and common deviations based on running count


## Blackjack Computer Vision & Decision Engine

This project implements a real-time blackjack analysis system that combines
computer vision and rule-based decision logic. A YOLOv8-based object detection 
model identifies playing cards from live screen capture, which are then used to 
maintain a shoe-level Hi-Lo count and estimate game state in real time.

The system integrates a deterministic strategy engine implementing
basic strategy alongside selected count-based deviations (Illustrious 18
and Fab 4) to recommend player actions under configurable game rules.
State is tracked across hands to preserve shoe-level information.

This project is intended for educational and analytical purposes and
demonstrates applied probability, computer vision, and systems design.


### Key Features
- Real-time playing-card detection using YOLOv8 and OpenCV
- Shoe-persistent Hi-Lo card counting assumes one deck
- Action recommendation engine implementing basic strategy with
  Illustrious 18 and Fab 4 deviations
- Modular architecture separating detection, counting, and strategy logic
- Interactive HUD displaying game state and recommendations


The model is trained on the kaggle dataset found at this link https://www.kaggle.com/datasets/hugopaigneau/playing-cards-dataset 


Below is an attatched video of how the finsihed product should perform:
https://youtube.com/shorts/KgrgYAl_lVY?si=aEKLl4Gh-6y1AjK- 
