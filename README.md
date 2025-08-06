# 🎮 Flappy Bird Detection

![Python](https://img.shields.io/badge/python-v3.13+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

A real-time computer vision system that detects and tracks objects in Flappy Bird gameplay using color-based detection.

## ✨ Features

- **Real-time Bird Detection** - Tracks the bird using multi-color HSV filtering
- **Pipe Detection** - Identifies upper and lower pipes with shape validation
- **Game Over Detection** - Recognizes game over screen using color analysis
- **Score Tracking** - Counts pipes passed and games played
- **Visual Feedback** - Score lines in the gap between pipes
- **Statistics Display** - Live game statistics overlay

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Windows (for MSS screen capture)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/luangrezende/game-vision-python.git
   cd game-vision-python
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install opencv-python numpy mss
   ```

### Usage

1. **Open Flappy Bird in your browser**
2. **Run the detection script:**
   ```bash
   python flappy_bird_detector.py
   ```
3. **Press 'q' to quit**

## 🔧 How It Works

The script uses computer vision techniques to detect game elements:

1. **Screen Capture** - MSS library captures the game region (coordinates: 520, 275, 780, 475)
2. **Color Filtering** - HSV color space filtering isolates specific game elements
3. **Object Detection** - Contour analysis identifies and validates objects
4. **Score Tracking** - Pipe grouping and gap detection for scoring
5. **Visual Feedback** - Real-time overlay with bounding boxes and statistics

### Detection Methods

- **Bird**: Multi-color detection (blue, yellow, red, cyan) with size validation
- **Pipes**: Green color filtering with background exclusion and shape validation  
- **Game Over**: Enhanced color-based detection with area filtering

## 📊 Statistics

The system tracks:
- Pipes passed (score)
- Games played
- Real-time detection status

## 🎯 Configuration

The detection region is pre-configured for standard Flappy Bird browser games:
- **Region**: `(520, 275, 780, 475)` - 260x200 pixel capture area
- **Bird Colors**: Blue, yellow, red, cyan HSV ranges
- **Pipe Colors**: Green HSV ranges with background exclusion
- **Game Over**: White/light gray color detection

## 🔧 Technical Details

### Dependencies
- `opencv-python` - Computer vision operations
- `numpy` - Array operations and mathematical functions  
- `mss` - Fast cross-platform screen capture

### Key Functions
- `detect_bird()` - Multi-color bird detection with morphological operations
- `detect_pipes()` - Pipe detection with shape validation and grouping
- `detect_gameover_color_enhanced()` - Game over state detection
- Pipe scoring system with visual gap indicators

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎯 Future Enhancements

- Multi-resolution support
- Configurable detection regions
- Performance optimizations
- Additional game state detection


- `flappy_bird_detector.py` - Main detection script with bird, pipe, and OCR-based Game Over detection
- `config_helper.py` - Interactive configuration tool with comprehensive testing options
- `analyze_assets.py` - Asset color analyzer for calibrating detection ranges
- `test_ocr_gameover.py` - OCR testing tool for Game Over detection debugging
- `README.md` - This file
- `requirements.txt` - Python package dependencies

## Output

The script provides:
- **Visual feedback**: Real-time display with bounding boxes (red=bird, blue=pipes, yellow=Game Over)
- **Console output**: Coordinates and dimensions of detected objects
- **Game status**: Displays current game state (Playing/Game Over)
- **Detection counts**: Shows number of each object type detected per frame