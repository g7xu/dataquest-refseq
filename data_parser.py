# this file will parse the data into json

import csv
import os

# from biothings.utils.dataload import dict_convert, dict_sweep

FILES = ["mouse_CCDS.current.txt", "mouse_CCDS_attributes.current.txt", "human_CCDS.current.txt", "human_CCDS_attributes.current.txt"]

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

DESIRED_MAIN_ID_KEY = "_id" 

# def str_to_list(listLikeStr: str) -> list:
#     """Case str-like-list into actual list, nested list will be expand

#     Args:
#         listLikeStr (str): the list like str

#     Return:
#         the converted list

#     >>> str_to_list("A")
#     ['A']
#     >>> str_to_list("A, B")
#     ['A', 'B']
#     >>> str_to_list("A B")
#     ['A B']
#     >>> str_to_list("A, [A, B], C")
#     ['A', 'A', 'B', 'C']
#     >>> str_to_list("A, B, C, D, [E, F], [G, H I]")
#     ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H I']
#     """
#     parsed_str = re.sub(r"[\[\]]", "", listLikeStr)
#     parsed_str_list = parsed_str.split(",")
#     return [val.strip() for val in parsed_str_list]


# def make_uniqueMarker(cellMarkers: list) -> list:
#     """Make unique markers from a list of cell markers

#     Args:
#         cellMarkers (list): list of cell markers

#     Returns:
#         list: list of unique cell markers
#     """
#     cellMarkers = list({tuple(sorted(marker.items())) for marker in cellMarkers})
#     return [dict(marker) for marker in cellMarkers]


# def select_items(record, item_keys):
#     """Select specific items from a record

#     Args:
#         record (dict): the record to select items from
#         item_keys (list): the keys of the items to select

#     Returns:
#         dict: the selected items
#     """
#     return {key: record[key] for key in item_keys if key in record}


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

            for row_number, row in enumerate(reader, 1):
                current_id_val_original = row.get(DESIRED_MAIN_ID_KEY, "")
                ...
            
            for _id, related_info in processed_data.items():
                yield {
                    "_id": _id,
                }

            

# load_ccds('data')


# def load_data_files(data_folder: str, files: list) -> list:
#     """
#     Load data from a list of files in a specified folder.
#     Args:
#         data_folder (str): The path to the folder containing the data files.
#         files (list): A list of filenames to be loaded from the data folder.

#     Returns:
#         list[dict]: A list of dictionaries containing the data from the files.

#     Raises:
#         FileNotFoundError: If any of the specified files do not exist in the data folder.
#     """
#     data = []
#     for file in files:
#         file_path = os.path.join(data_folder, file)
#         if not os.path.exists(file_path):
#             raise FileNotFoundError(f"Missing file: {file_path}")
#         with open(file_path, mode="r", newline="", encoding='utf-8') as tsvfile:
#             # Manually read and transform the header
#             header_line = tsvfile.readline()

#             original_file_headers = [h.strip() for h in header_line.strip().split('\t')]
#             renamed_headers_for_dictreader = []
#             for original_h in original_file_headers:
#                 processed_h_for_lookup = original_h.lower() # MASTER_COLUMN_MAP keys are lowercase
#                 # Use the mapped desired key, or the original header if no mapping exists
#                 desired_key_for_header = MASTER_COLUMN_MAP.get(processed_h_for_lookup, original_h)
#                 renamed_headers_for_dictreader.append(desired_key_for_header)


#                 reader = csv.DictReader(tsvfile, fieldnames=renamed_headers_for_dictreader, delimiter="\t")
#             data.extend(reader)
#     return data


# def load_ccds(data_folder):
#     """Converting data into expected JSON format

#     Args:
#         data_folder (str): the relative data path to the data source

#     Return:
#         the yield JSON data
#     """
#     # load data
#     data = load_data_files(data_folder, FILES)

#     results = {}
#     for record in data:
#         # converting all the key to standard format
#         record = dict_convert(record, keyfn=lambda k: k.replace(" ", "_").lower())

#         # ignore geneID that is missing or contains non-numeric value
#         if (
#             record[GENE_ID].casefold() == "na"
#             or not record[GENE_ID].isnumeric()
#             or record[GENE_ID].casefold() == ""
#         ):
#             continue

#         # zip these elements together to get multiple copies
#         for gene_id in str_to_list(record[GENE_ID]):
#             _id = gene_id
#             if _id.casefold() == "na" or _id.casefold() == "":
#                 continue
#             results.setdefault(_id, {})
#             gene_id_dict = results[_id]

#             # identify source key
#             if record["markerresource"].casefold() != "company":
#                 resource_key = "pmid"
#                 record_resource_key = "pmid"
#             else:
#                 resource_key = "company"
#                 record_resource_key = "company"

#             # handle edge case
#             # if tissuetype is undefined, we will make it empty
#             if record["tissuetype"].casefold() == "undefined":
#                 record["tissuetype"] = ""

#             # check if any value in the dict is na, if so, make it empty
#             for key, value in record.items():
#                 # handle missing values
#                 if value.casefold() == "na":
#                     record[key] = ""

#                 if key == "cellontologyid" or key == "uberonontologyid":
#                     record[key] = record[key].replace("_", ":")
#                 else:
#                     record[key] = record[key].lower()

#             gene_id_dict.setdefault("cellmarker", []).append(
#                 dict_sweep(
#                     {
#                         "cellontology": record["cellontologyid"],
#                         "cellname": record["cellname"],
#                         "celltype": record["celltype"],
#                         "cancertype": record["cancertype"],
#                         "tissue": record["tissuetype"],
#                         "uberon": record["uberonontologyid"],
#                         "species": record["speciestype"],
#                         "marker_resource": record["markerresource"],
#                         f"{resource_key}": record[f"{record_resource_key}"],
#                     }
#                 )
#             )

#     # return each gene_id with yield and remove duplicate from the dictionary
#     for _id, related_info in results.items():
#         yield {
#             "_id": _id,
#             "cellmarker": make_uniqueMarker(related_info["cellmarker"]),
#         }


# # if __name__ == "__main__":
# #     import doctest

# #     doctest.testmod()
# #     x = load_cellMarkers("data")
# #     y = [i for i in x]

# #     breakpoint()
