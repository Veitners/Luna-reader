# Deformation Viewer

## Overview
The Deformation Viewer is an interactive application designed to visualize deformation data over distance. It provides tools for analyzing, manipulating, and exporting data, making it ideal for engineering and scientific applications.

## Features
- **Plotting Deformation Data**: Visualize deformation values against distances for selected ranges.
- **Playback Controls**: Play, pause, fast-forward, and reverse through timestamps automatically.
- **Zeroing Options**: Apply or remove tare values and zero data based on specific timestamps.
- **Locking Lines**: Lock specific deformation lines for persistent reference.
- **Exporting Data**: Export selected data to Excel files.
- **Saving Plots**: Save plots as image files (e.g., PNG).
- **Y-Axis Controls**: Set custom Y-axis limits or reset them to default.
- **Interactive Interface**: Includes zoom, pan, and hover tooltips for detailed analysis.

## File Structure
- **`main.py`**: Main application logic and GUI setup.
- **`window.py`**: Handles creation of plot windows and interactive controls.
- **`processing.py`**: Utility functions for data manipulation.
- **`player.py`**: Implements playback logic.
- **`plotter.py`**: Handles plotting logic.
- **`loader.py`**: Manages file loading and parsing.

## Installation
1. Ensure Python 3.11 or later is installed.
2. Install required dependencies:
   ```bash
   pip install matplotlib pandas numpy
   ```

## Usage
1. Run the application:
   - On Windows: Double-click `launch_windows.bat`.
   - On macOS: Right-click `launch_macos.command` and select "Open".
2. Load deformation data from `.tsv` or `.csv` files.
3. Use the interactive controls to analyze and manipulate data.
4. Export results or save plots as needed.

## Dependencies
- Python 3.11+
- Matplotlib
- Pandas
- NumPy
- Tkinter (bundled with Python)

## License
This project is licensed under the MIT License.

## Author
Edgars Veitners
