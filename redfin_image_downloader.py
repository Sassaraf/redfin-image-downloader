#!/usr/bin/env python3

# FINAL VERSION 2
import re
import json
import requests
from tqdm import tqdm
from PIL import Image
from redfin import Redfin
import logging
from datetime import datetime
import pandas as pd
import os


# Create the "Redefine images" folder if it doesn't exist
if not os.path.exists("Redefine images"):
    os.makedirs("Redefine images")

    
# Set up logging configuration
log_format = '%(asctime)s %(levelname)s %(lineno)d: %(message)s'
log_filename = 'redfin.log'
logging.basicConfig(filename=log_filename, level=logging.INFO, format=log_format)

# Initialize Redfin client
client = Redfin()

# Read the list of addresses from the CSV file
df_adr = pd.read_csv('Redfin formatted addresses.csv')

# Define the columns for the progress file
progress_columns = ['Address', 'Status', 'Error']

# Check if the progress file already exists
progress_file = 'redfin_progress.csv'
if os.path.isfile(progress_file):
    # If the progress file exists, load the progress DataFrame from the file
    df_progress = pd.read_csv(progress_file)
else:
    # If the progress file doesn't exist, create a new progress DataFrame
    df_progress = pd.DataFrame(columns=progress_columns)

for _, row in tqdm(df_adr.iterrows(), total=df_adr.shape[0]):
    # Check if the address has already been processed
    address = row['Address']
    if address in df_progress['Address'].values:
        # If the address has already been processed, skip it
        logging.info(f"Skipping address {address} (already processed)")
        continue

    # Process the address
    logging.info(f"Processing address: {address}")
    status = 'Success'
    error_message = ''

    try:
        # Search for the address and get the exact match URL from the response
        response = client.search(address)
        url = response['payload']['exactMatch']['url']

        # Use the initial_info method to get the property ID
        initial_info = client.initial_info(url)
        property_id = initial_info['payload']['propertyId']

        # Use the below_the_fold method to get the image URLs for the property
        below_the_fold_data = client.below_the_fold(property_id)

        # Convert the payload to a JSON string
        payload_json = json.dumps(below_the_fold_data['payload'])

        # Define the pattern to match desired URLs
        url_pattern = re.compile(r'fullScreenPhotoUrl": "(https://ssl\.cdn-redfin\.com/.*?\.(?:jpg|jpeg|png|gif|webp))"')

        # Find all URLs in the JSON string
        matches = re.findall(url_pattern, payload_json)
        urls = [match for match in matches]

        # Print the number of URLs found
        logging.info(f"Found {len(urls)} image URLs for address: {address}")

        # Download each image and save it to a file
        for i, image_url in tqdm(enumerate(urls), desc='Downloading images', total=len(urls)):
            response = requests.get(image_url)
            if response.status_code == 200:
                ext = image_url.split('.')[-1]
                filename = f'Redefine images/{address.replace(" ", "_")}_image_{i}.{ext}'
                with open(filename, 'wb') as f:
                    f.write(response.content)
                logging.info(f"Image saved: {filename}")
            else:
                logging.warning(f"Error downloading image {i+1} for address {address}: HTTP error {response.status_code}")
                status = 'Error'
                error_message = f"HTTP error {response.status_code}"
    except Exception as e:
        error_message = str(e)
        logging.error(f"Error processing address {address}: {error_message}")
        status = 'Error'
    df_progress = df_progress.append({'Address': address, 'Status': status, 'Error': error_message}, ignore_index=True)

# Save the progress DataFrame to the progress file
df_progress.to_csv(progress_file, index=False)
