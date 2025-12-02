from pprint import pprint
import csv
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
import marqo as mq

##
## Connect to Marqo
##

MARQO_URL = "http://92.112.48.13:8882"
marqoClient = mq.Client(url=MARQO_URL)
#pprint(marqoClient.get_indexes())

##
## Index settings for multimodal structured index
## follow instructions on https://docs.marqo.ai/2.11/other-resources/cookbook/indexes/creating-a-structured-index/multimodal-index/
##

settings = {
    "type": "structured",
    "model": "open_clip/ViT-B-32/laion2b_s34b_b79k", ## Run docker container with at least MARQO_MAX_CPU_MODEL_MEMORY=5 (ViT-H-14 models need more!)
    "allFields": [
        {"name": "uniqueID", "type": "text"},
        {"name": "document", "type": "text"},
        {"name": "page_bsb", "type": "text"},
        {"name": "volume", "type": "text", "features": ["lexical_search"]},
        {"name": "page", "type": "text", "features": ["lexical_search"]},
        {"name": "text_page", "type": "text", "features": ["lexical_search"]},
        {"name": "link", "type": "image_pointer"},
        {"name": "pairID", "type": "text"},
        {"name": "viewer_url", "type": "text"},
        {"name": "image_url", "type": "text"},
        {
            "name": "multimodal_field",
            "type": "multimodal_combination",
            "dependentFields": {"link": 1.0, "text_page": 0.0},
        },
    ],
    "tensorFields": ["multimodal_field"]
}


##
## Ask if index exists, if not create it
##

indexName = "camerarius_testIndex_full-imagesFINAL"
print("Indexname: ", indexName)
current_indexes = [d["indexName"] for d in marqoClient.get_indexes()["results"]]
if indexName in current_indexes:
    print(f"Index already exists: {indexName} ")
    # Set indexName as the current index
    print(f"Defaulting to index connection. Index connected: {indexName} ")
else:  # Create a new index
    print(f"Index does not exist: {indexName} ")
    print(f"Creating index: {indexName} ")
    marqoClient.create_index(indexName, settings_dict=settings)

## List of models integrated in Marqo: https://docs.marqo.ai/latest/models/marqo/list-of-models/
# camerarius_testIndex_full-imagesFINAL: open_clip/ViT-H-14/laion2b_s32b_b79k

pprint(marqoClient.get_indexes())

##
## Load dict of data
##


# Load list of dictionaries with each dictionary containing relevant keys
# CSV path
csv_file = 'C:/camerarius_rag/index/camerarius_index-full_imagesFINAL.csv'

# Read data from CSV file into a list of dictionaries
with open(csv_file, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    data = [row for row in reader]

# Function to clean text by replacing \n with spaces
def clean_text(text):
    return text.replace('\n', ' ').strip()

# Clean the 'text' field in each dictionary
for entry in data:
    entry['text_page'] = clean_text(entry['text_page'])

pprint(data[:3])

##
## Add documents to the index
##

print(f"Indexing data...")
# Define client_batch_size
client_batch_size = 128

# Indexing
result = marqoClient.index(indexName).add_documents(
    data,
    client_batch_size=client_batch_size
)

pprint(result)

print(f"Data has been indexed in {indexName}")