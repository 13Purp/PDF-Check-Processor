# PDF Check Processor

This is a desktop application built with Python and CustomTkinter that uses OCR (Optical Character Recognition) to extract data from scanned PDF files containing Serbian bank checks. The application allows users to process PDFs, view the extracted data, manually edit or add information, and see the source images for verification. All data is saved locally to a `results.csv` file.

## Features

* **PDF Processing**: Select and process multi-page PDF files.
* **Data Extraction**: Uses EasyOCR to extract key information like bank name, account numbers, and serial numbers.
* **Interactive UI**: A modern, dark-themed interface built with CustomTkinter.
* **Data Editing**: All extracted and manually-entered fields are editable directly within the app.
* **Image Verification**: Buttons to display the cropped source images used for OCR, allowing for easy verification.
* **Persistent Storage**: All data is automatically saved to `results.csv` and loaded on startup.

---

## ⚙️ Setup and Installation

Follow these steps to set up the project on your local machine.

### 1. Prerequisites

This project requires **Python 3.8+** and the **Poppler** utility.

* **Python**: If you don't have it, download it from [python.org](https://www.python.org/downloads/).
* **Poppler**: This is a dependency for the `pdf2image` library.
    * **Windows**: Download the latest Poppler binaries. Unzip the folder, and add the `bin` subdirectory to your system's PATH.
    * **macOS**: `brew install poppler`
    * **Linux (Ubuntu/Debian)**: `sudo apt-get install poppler-utils`

### 2. Create a Virtual Environment

It is highly recommended to use a virtual environment to manage project dependencies.

```bash
# 1. Navigate to your project directory
cd path/to/your/project

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies

Install all the required libraries using pip:

```bash
pip install -r requirements.txt
```

The first time you run the application, `easyocr` will automatically download the necessary language models.

---

## ▶️ Running the Application

Once the setup is complete, you can run the application directly from the command line. Ensure your main script is named `main.py` (or adjust the command accordingly).

```bash
python main.py
```

The application window should appear, and it will automatically load any existing data from `results.csv`.

---
