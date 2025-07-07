# this file will parse the data into json

import csv
import os

from biothings.utils.dataload import dict_sweep

# FILES = ["mouse_CCDS.current.txt", "mouse_CCDS_attributes.current.txt", "human_CCDS.current.txt", "human_CCDS_attributes.current.txt"]
FILES = ['CCDS.current.txt', 'CCDS_attributes.current.txt']

# Master map: actual column name (lowercase, stripped) -> desired internal key
MASTER_COLUMN_MAP = {
    "gene_id": "_id",
    "_id": "_id",  # Handles if original header is already the desired key
    "#ccds": "ccds_id",
    "ccds_id": "ccds_id", # Handles if original header is already the desired key
    "ccds_status": "status",
    "status": "status", # Handles if original header is already the desired key
    "match_type": "match_type", # Handles if original header is already the desired key
    "attribute": "attribute" # Handles if original header is already the desired key
}

DESIRED_ENTRY_KEYS = ["status", "match_type", "attribute"]
DESIRED_GENE_ID_KEY = "_id"
DESIRED_CCDS_ID_KEY = "ccds_id"


def parse_geneid_ccds_pair(data: dict):
    """Parsing data of a single ccds and gene id pair with its meta information

    Args:
        data: a dictionary of data series

    Return:
        - gene_id(str)
        - meta_info(tuple)
    """
    gene_id = data.get(DESIRED_GENE_ID_KEY).lower()
    ccds_id = data.get(DESIRED_CCDS_ID_KEY).lower()

    if ccds_id.startswith("ccds"):
        ccds_id = ccds_id[4:]


    if gene_id is None or ccds_id is None:
        raise ValueError('the input data has gene_id or ccds_id missing')
    
    meta_info = [ccds_id]
    for search_key in DESIRED_ENTRY_KEYS:
        search_result = data.get(search_key, "")
        if search_result is None:
            search_result = ""
        else:
            search_result = search_result.lower()
        meta_info.append(search_result)

    return gene_id, tuple(meta_info)

def make_ccds_dict(meta_infos: set) -> dict:
    """Takes in a set of ccds meta infomations. Transform the data to dictionary

    Args:
        - meta_infos: the meta informations

    Return: a cleaned dictionary
    """
    transformed_meta_infos = []

    for meta_info in meta_infos:
        transformed_meta_infos.append(dict_sweep({
            "ccds_id": meta_info[0],
            "status": meta_info[1],
            "match_type": meta_info[2],
            "attribute": meta_info[3]
        }))

    return transformed_meta_infos



def load_ccds(data_folder:str):
    processed_data = dict()

    for file_path in FILES:
        with open(os.path.join(data_folder, file_path), 'r', newline='', encoding='utf-8') as tsvfile:
            header_line = tsvfile.readline()
            
            # rename all the columns
            original_file_headers = [h.strip() for h in header_line.strip().split('\t')]
            renamed_headers_for_dictreader = []
            for original_h in original_file_headers:
                processed_h_for_lookup = original_h.lower() # MASTER_COLUMN_MAP keys are lowercase
                # Use the mapped desired key, or the original header if no mapping exists
                desired_key_for_header = MASTER_COLUMN_MAP.get(processed_h_for_lookup, original_h)
                renamed_headers_for_dictreader.append(desired_key_for_header)

            # initalize reader
            reader = csv.DictReader(tsvfile, fieldnames=renamed_headers_for_dictreader, delimiter='\t')

            for _, row in enumerate(reader, 1):
                gene_id, meta_info = parse_geneid_ccds_pair(row)


                if gene_id not in processed_data:
                    processed_data[gene_id] = set()

                processed_data[gene_id].add(meta_info)
            
    for _id, meta_infos in processed_data.items():
        yield {
            "_id": _id,
            "ccds_ids": make_ccds_dict(meta_infos)
        }

    
# if __name__ == "__main__":
#     result = list(load_ccds('data'))
#     print(result)
