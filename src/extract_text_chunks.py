###
### This code extracts text chunks of 5 lines of text from the full xml text pages
### and prepares the metadata to be added to the Marqo index
###

import os
import re
import csv
import xml.etree.ElementTree as ET
from tqdm import tqdm

# Helper: Collect all XML file paths
def collect_files(folder, extension=".xml"):
    file_paths = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(extension):
                file_paths.append(os.path.join(root, file))
    return file_paths

# Helper: Generate Digitale Sammlung URL
def generate_digital_sammlung_url(page_number) -> str:
    page_number = int(page_number)

    if page_number % 2 == 0:
        pages = f"{page_number},{page_number + 1}"
    else:
        pages = f"{page_number - 1},{page_number}"
    
    url = f"https://www.digitale-sammlungen.de/de/view/bsb10575861?page={pages}"
    return url

# Extract text chunks per region from a PAGE XML file
def extract_text_by_region(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    ns = {'pg': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}
    output = []

    for page in root.findall(".//pg:Page", ns):
        image_filename = page.attrib.get("imageFilename", "")
        text_id = re.sub(r'^\d{4}_', '', image_filename).replace('.jpg', '')  # remove .jpg + 4-digit prefix + underscore

        # Extract document_id from the filename
        match = re.search(r'bsb\d+', os.path.basename(file_path))
        document_id = match.group() if match else 'UNKNOWN'

        # Get page number from first 4 digits of XML filename
        page_number = os.path.basename(file_path)[:4].zfill(5)

        # Generate Digitale Sammlung preview link
        viewer_url = generate_digital_sammlung_url(page_number)

        # Create image download URL
        image_url = f"https://api.digitale-sammlungen.de/iiif/image/v2/{document_id}_{page_number}/full/full/0/default.jpg"

        # Iterate through regions in this page
        for region in page.findall("pg:TextRegion", ns):
            region_id = region.attrib.get("id", "unknown_region")
            lines = []

            # Collect lines with their readingOrder index
            lines_with_index = []
            for line in region.findall("pg:TextLine", ns):
                unicode_el = line.find("pg:TextEquiv/pg:Unicode", ns)
                if unicode_el is not None and unicode_el.text:
                    lines.append(unicode_el.text.strip())
                # Store full text of page
                text_page = "\n".join(lines)

                custom = line.attrib.get("custom", "")
                match_index = re.search(r'readingOrder\s*\{\s*index\s*:\s*(\d+)\s*;\s*\}', custom)
                index = int(match_index.group(1)) if match_index else -1

                if unicode_el is not None and unicode_el.text:
                    lines_with_index.append((index, unicode_el.text.strip()))

            # Sort lines by readingOrder index
            lines_with_index.sort(key=lambda x: x[0])

            # Split into chunks of 5
            for i in range(0, len(lines_with_index), 5):
                chunk = lines_with_index[i:i+5]
                text_chunk = "\n".join([line for _, line in chunk])
                index_list = [idx for idx, _ in chunk]

                output.append({
                    "uniqueID": text_id,
                    "document": document_id,
                    "page_bsb": page_number,
                    "volume": '',
                    "page": '',
                    "regionID": region_id,
                    "text_chunk": text_chunk,
                    "text_page": text_page,
                    "line_indexes": index_list,
                    "viewer_url": viewer_url,
                    "image_url": image_url
                })

    return output

# Folders to process
folders = [
    'C:/camerarius_rag/data/text/page/',
]

# Collect all XML files from folders
files = [file for folder in folders for file in collect_files(folder)]

# Process files
all_data = []

for file in tqdm(files, desc="Parsing XML files", unit="file"):
    all_data.extend(extract_text_by_region(file))

# Output CSV path
csv_file = 'C:/camerarius_rag/index/camerarius_index-full_text3.csv'
os.makedirs(os.path.dirname(csv_file), exist_ok=True)

# Write to CSV
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=["uniqueID", "document", "page_bsb", "volume", "page", "regionID", "text_chunk", "text_page", "line_indexes", "viewer_url", "image_url"])
    writer.writeheader()
    writer.writerows(all_data)