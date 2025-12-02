###
### Index the text chunks and metadata to the Marqo index
###

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
## Index settings
##

settings = {
    "textPreprocessing": {
        "splitLength": 2,
        "splitOverlap": 0,
        "splitMethod": "sentence"
    }
}

##
## Ask if index exists, if not create it
##

indexName = "camerarius_testIndex_full-textsFINAL"
print("Indexname: ", indexName)
current_indexes = [d["indexName"] for d in marqoClient.get_indexes()["results"]]
if indexName in current_indexes:
    print(f"Index already exists: {indexName} ")
    # Set indexName as the current index
    print(f"Defaulting to index connection. Index connected: {indexName} ")
else:  # Create a new index
    print(f"Index does not exist: {indexName} ")
    print(f"Creating index: {indexName} ")
    marqoClient.create_index(
        indexName,
        model="flax-sentence-embeddings/all_datasets_v4_mpnet-base",
        #settings_dict=settings ## no preprocessing as texts are already chunked
    )

## List of models integrated in Marqo: https://docs.marqo.ai/latest/models/marqo/list-of-models/

pprint(marqoClient.get_indexes())

##
## Load dict of data
##


# Load list of dictionaries with each dictionary containing keys: "uniqueID", "document", "page_bsb", "volume", "page", 
# "line_indexes", "viewer_url", "image_url"
# "pairID" not added to the text index; might improve in future
csv_file = 'C:/camerarius_rag/index/camerarius_index-full_textFINAL.csv'

# Read data from CSV file into a list of dictionaries
with open(csv_file, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    data = [row for row in reader]

# Function to clean text by replacing \n with spaces
def clean_text(text):
    return text.replace('\n', ' ').strip()

# Clean the 'text' field in each dictionary
for entry in data:
    entry['text_chunk'] = clean_text(entry['text_chunk'])

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
    client_batch_size=client_batch_size,
    tensor_fields=["text_chunk"],
)

pprint(result)

print(f"Data has been indexed in {indexName}")