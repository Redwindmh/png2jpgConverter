# PNG to JPG Converter

A simple and user-friendly application to convert PNG files to JPG format with optional size adjustment.

## Features

- Convert single or multiple PNG files to JPG
- Adjust output image size (800x600, 1024x768, 1920x1080, or original size)
- Modern and intuitive user interface
- Progress tracking during conversion
- Handles transparent PNGs with white background
- High-quality output (95% JPEG quality)

## Prerequisites

- Python 3.11 or higher installed on your system

## Installation

1. Create and activate a virtual environment:
   ```bash
   # Create virtual environment
   python3.11 -m venv venv

   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   # venv\Scripts\activate
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Make sure your virtual environment is activated (you should see `(venv)` in your terminal prompt)

2. Run the application:
   ```bash
   python main.py
   ```

3. In the application:
   - Navigate to and select your PNG files using the file browser
   - Choose your desired output size from the dropdown menu
   - Specify the output directory (defaults to your Pictures folder)
   - Click "Convert" to start the conversion process

4. The converted JPG files will be saved in the specified output directory

## Notes

- The application automatically handles transparent PNGs by adding a white background
- All converted images maintain high quality (95% JPEG quality)
- The application supports batch processing of multiple files
- Progress is shown during conversion

## Deactivating the Virtual Environment

When you're done using the application, you can deactivate the virtual environment:
```bash
deactivate
``` 