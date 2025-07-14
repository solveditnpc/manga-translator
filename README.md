**UNDER CONSTRUCTION**
**only for developers**

## Installation Guide

This guide will walk you through setting up the project for development only.

### Prerequisites

Make sure you have the following installed on your system:

- [Python 3.8+](https://www.python.org/downloads/) # prefer python 3.10.0
- [Node.js and npm](https://nodejs.org/en/download/)
- [Firefox](https://www.mozilla.org/en-US/firefox/new/)
- create a virtual environment using pyenv # for error free installation 

### Python Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd manga-translator
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Python dependencies:**
    A `requirements.txt` file is not yet available. Please install the following packages manually:
    ```bash
    pip install opencv-python paddleocr pdf2image python-docx docx2pdf selenium
    ```

4.  **Install OCR model and library:**
    Download the PaddleOCR model from [PaddleOCR](https://www.paddlepaddle.org.cn/en/install/quick?docurl=undefined)

    ```bash
    pip install paddleocr
    ```

### JavaScript Setup

1.  **Navigate to the API directory:**
    ```bash
    cd Translate/API_request
    ```

2.  **Install Node.js dependencies:**
    ```bash
    npm install dotenv express @google/generative-ai
    ```

### Configuration

1.  install Geckodriver

    ```bash
    python Translate/download_firefox_driver.py
    ```

2.  **`config.json`:**
    This file, located in the root directory, is used by the Python scripts. It requires paths to `geckodriver` and your Firefox profile.

    The GECKODRIVER is locted in this folder under config/tools directory 

    TO find the Firefox profile path, open Firefox, go to `about:profiles`, and copy the path of the profile you want to use.
    **Recommended to create a new profile for the bot to avoid any conflicts with your main profile**

    ```json
    {
        "GECKODRIVER_PATH": "/path/to/your/geckodriver",
        "FIREFOX_PROFILE_PATH": "/path/to/your/firefox/profile",
        "to_lan": "en"
    }
    ```