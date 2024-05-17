# Thinkific Media Downloader

Thinkific Media Downloader is a Python script designed to download audio and video files from Thinkific courses. Works fine for my needs but needs some polishing for wider use.

## Features

- Download audio files from Thinkific courses.
- Download video files from Thinkific courses.
- Easy-to-use command-line interface.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- You have Python 3.x installed on your computer.
- You have `pip` installed for managing Python packages.

## Installation

1. **Clone the repository**:

    ```sh
    git clone https://github.com/yourusername/thinkific-media-downloader.git
    cd thinkific-media-downloader
    ```

2. **Install the required dependencies**:

    ```sh
    pip install -r requirements.txt
    ```

3. **Configure local settings**:

    Copy the file `local_settings.default.py` to `local_settings.py` and replace the variables with the required website and course details.

## Usage

To download audio and video files, use the `download_videos.py` script.

### Command Line Interface

```sh
python download_videos.py
