
# Redfin Image Downloader

This script downloads images of properties listed on Redfin based on a list of property addresses provided in a CSV file.

## Requirements

- Python 3.6 or higher
- Libraries:
  - pandas
  - requests
  - Pillow
  - tqdm
  - redfin


## Installation

1. Clone the repository:

```
git clone https://github.com/yourusername/redfin-image-downloader.git
cd redfin-image-downloader
```

2. Install the required Python libraries:

```
pip install -r requirements.txt
```

## Usage

1. Add the list of property addresses to the `all_addresses.csv` file.
2. Run the script from the terminal:

```bash
python redfin_image_downloader.py
```

The script will log the progress to the `redfin.log` file and download the images to the `Redefine images` folder. The script will also save the progress to the `redfin_progress.csv` file, so it can be resumed if interrupted.

