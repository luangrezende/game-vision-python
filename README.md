# Flappy Bird Object Detection

A minimal Python script that captures a screen region and detects the bird, pipes, and Game Over screen in Flappy Bird using simple color filtering with OpenCV.

## Features

- **Screen Capture**: Uses `mss` library for fast screen capturing of a specific region
- **Color-based Detection**: Detects bird (blue/yellow), pipes (green), and Game Over screen using HSV color filtering
- **Real-time Visualization**: Draws bounding boxes around detected objects
- **Console Output**: Prints coordinates of detected objects each frame
- **Game State Detection**: Automatically detects when the game is over
- **Configuration Helper**: Interactive tool to help adjust detection parameters
- **Asset-based Calibration**: Uses real game assets for accurate color detection

## Requirements

- Python 3.7+
- OpenCV (`opencv-python`)
- MSS (`mss`)
- NumPy (`numpy`)
- Tesseract OCR (`pytesseract`)
- Pillow (`pillow`)

## Installation

1. Clone this repository
2. Install Tesseract OCR:
   - **Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki
   - **Mac**: `brew install tesseract`
   - **Linux**: `sudo apt install tesseract-ocr`
3. Install the required Python packages:
```bash
pip install opencv-python mss numpy pytesseract pillow
```

## Usage

### Quick Start
1. Open Flappy Bird in your browser or app
2. Run the detection script:
```bash
python flappy_bird_detector.py
```
3. Press 'q' to quit

### Configuration (Recommended)
Before running the main script, use the configuration helper to:
1. Find the correct screen coordinates for your game window
2. Determine the right HSV color ranges for your specific version of Flappy Bird
3. Test individual detection components (bird, pipes, Game Over)

```bash
python config_helper.py
```

**Menu Options:**
- **1. Color Picker** - Click on game objects to see HSV values
- **2. Test Capture Area** - Verify screen coordinates
- **3. Test Pipe Detection** - Preview pipe detection with filters
- **4. Test Bird Detection** - Preview bird detection specifically  
- **5. Test Game Over Detection** - Preview Game Over screen detection
- **6. Test Full Detection** - Preview all detections together
- **7. Exit**

## Configuration

You may need to adjust these parameters in `flappy_bird_detector.py`:

### Screen Region
```python
monitor = {"top": 100, "left": 100, "width": 600, "height": 800}
```

### Color Ranges
```python
# Bird (yellow) - adjust as needed
lower_yellow = np.array([20, 100, 100])
upper_yellow = np.array([30, 255, 255])

# Pipes (green) - adjust as needed
lower_green = np.array([40, 50, 50])
upper_green = np.array([80, 255, 255])
```

### Detection Thresholds
```python
# Minimum area for bird detection
if area > 100:

# Minimum area for pipe detection  
if area > 500:
```

## How It Works

1. **Screen Capture**: Captures a fixed region of the screen where the game is running
2. **Color Filtering**: Converts the image to HSV color space and filters for specific color ranges
3. **Asset-based Detection**: Uses color ranges derived from real game assets (bluebird-downflap.png, pipe-green.png, gameover.png)
4. **Contour Detection**: Finds contours in the filtered masks
5. **Object Classification**: Filters contours by area, aspect ratio, and size to distinguish between objects
6. **Game State Recognition**: Detects Game Over screen to determine game state
7. **Visualization**: Draws bounding rectangles and displays coordinates

## Detection Details

### Bird Detection
- **Blue body**: HSV range [95, 150, 100] to [125, 255, 255]
- **Yellow/Orange parts**: HSV range [95, 160, 200] to [105, 185, 255]  
- **Red beak**: HSV range [5, 200, 200] to [15, 255, 255]
- **Light blue areas**: HSV range [15, 100, 200] to [25, 130, 255]

### Pipe Detection  
- **Green pipes**: HSV range [36, 85, 84] to [75, 187, 253]
- **Background exclusion**: Removes background green automatically
- **Morphological operations**: Connects pipe body with caps

### Game Over Detection
- **OCR-based**: Uses Tesseract OCR to detect "GAME OVER" text directly
- **Color fallback**: HSV range [10, 100, 100] to [25, 255, 255] for orange text
- **Intelligent preprocessing**: Automatic image enhancement for better OCR accuracy
- **High accuracy**: No false positives from similar colored objects

## Tips

- Use the configuration helper to find the exact HSV values for your game
- Adjust the screen capture coordinates to focus on just the game area
- Modify color ranges if the default values don't work for your version of Flappy Bird
- Increase area thresholds if you're getting too much noise in detection

## Files

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