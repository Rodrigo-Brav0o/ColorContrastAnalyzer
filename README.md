# Color Contrast Analyzer

**Color Contrast Analyzer**
is a Python based desktop application designed to check the color contrast ratio between foreground and background colors for accessibility compliance with the **WCAG (Web Content Accessibility Guidelines)**.

# Features

- Input foreground and background colors via **hex codes** or **color pickers**.
- Calculate **contrast ratios** instantly.
- WCAG **AA** and **AAA** pass/fail indicators for normal and large text.
- Live **text preview** with selected colors.
- Recommendations for improving color contrast.
- Upload images and select colors from specific pixels (pipette functionality).
- Light mode and dark mode themes for user convenience.

# Prerequisites

- Python 3.6+ installed on your system.
- `pip` (Python package manager).
- Libraries: Either **PySide6**(Recommended) or **PyQt** (if you adapt the code for PyQt)


# Installation

1. Clone the repository:     git clone https://github.com/YourUsername/ColorContrastAnalyzer.git
   then
   cd ColorContrastAnalyzer
2. Install dependencies
   pip install -r requirements.txt
3. Run the application
   python ColorContrast.py
