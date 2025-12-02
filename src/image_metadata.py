###
### This code prepares the metadata of the images to be indexed in Marqo
###

import os
import re
import csv

# Folders to process
folder = 'C:/camerarius_rag/data/image/clipped/'
csv_file_path = 'C:/camerarius_rag/index/camerarius_index-full_textFINAL.csv'

# Helper: Generate Digitale Sammlung URL
def generate_digital_sammlung_url(page_number) -> str:
    page_number = int(page_number)

    if page_number % 2 == 0:
        pages = f"{page_number},{page_number + 1}"
    else:
        pages = f"{page_number - 1},{page_number}"
    
    url = f"https://www.digitale-sammlungen.de/de/view/bsb10575861?page={pages}"
    return url

def get_pair_id(uniqueID):
    # Match document and page
    match = re.match(r"^(bsb\d+)_(\d+)(_full_full_0_default\.jpg)$", uniqueID)
    if match:
        document_id, page_str, suffix = match.groups()
        # Increment page
        next_page = str(int(page_str) + 1).zfill(len(page_str))
        # Build pair_ID
        pair_id = f"{document_id}_{next_page}{suffix}"
        return pair_id
    else:
        # Return None if format is unexpected
        return None

# Load CSV into a dict: page -> full row
page_rows = {}
with open(csv_file_path, mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        page_rows[row["page_bsb"].zfill(5)] = row  # ensure pages are zero-padded

# List to collect extracted results
extracted = []

## Image links are created for Docker to access the images via the mounted image repository
## Docker command:
## docker run --name marqo5GBim --mount type=bind,source=/michela_vignoli/camerarius_rag/data/
## clipped,target=/camerarius_rag/data/clipped -it -p 8882:8882 -e MARQO_MAX_CPU_MODEL_MEMORY=5 marqoai/marq
## o:latest

# Loop through all .jpg files
for filename in os.listdir(folder):
    if filename.endswith('.jpg'):
        #link = os.path.join("http://host.docker.internal:8222/", filename) ## When local image server is used
        link = "/michela_vignoli/camerarius_rag/data/clipped/" + filename ## Path to image folder mounted in Docker Marqo instance
        match = re.match(r"^(bsb\d+)_0*(\d+)_full_full_0_default", filename)
        image_id = os.path.splitext(filename)[0]
        pair_id = get_pair_id(image_id)
        if match:
            document_id, page_bsb = match.groups()
            page_bsb = page_bsb.zfill(5)

            # Generate Digitale Sammlung preview link
            viewer_url = generate_digital_sammlung_url(page_bsb)

            # Create image download URL
            image_url = f"https://api.digitale-sammlungen.de/iiif/image/v2/{document_id}_{page_bsb}/full/full/0/default.jpg"

            # Look up matching row in CSV
            row_data = page_rows.get(page_bsb)

            if row_data:
                text_page = row_data.get("text_page", "")
                volume = row_data.get("volume", "")
                page = row_data.get("page", "")
            else:
                print(f"Warning: No matching row in CSV for page {page_bsb} from file {filename}")
                text_page = ""
                volume = ""
                page = ""
            extracted.append({
                "_id": image_id,
                "uniqueID": image_id,
                "document": document_id,
                "page_bsb": page_bsb,
                "volume": volume,
                "page": page,
                "text_page": text_page,
                "link": link,
                "pairID": pair_id,
                "viewer_url": viewer_url,
                "image_url": image_url
            })

# Output CSV path
csv_file = 'C:/camerarius_rag/index/camerarius_index-full_imagesFINAL.csv'
os.makedirs(os.path.dirname(csv_file), exist_ok=True)

# Write to CSV
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=["_id", "uniqueID", "document", "page_bsb", "volume", "page", "text_page", "link", "pairID", "viewer_url", "image_url"])
    writer.writeheader()
    writer.writerows(extracted)