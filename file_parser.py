import csv
import os

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

DESIRED_CCDS_ENTRY_KEYS = ["ccds_id", "status", "match_type", "attribute"]
DESIRED_MAIN_ID_KEY = "_id" # This must be one of the *values* in MASTER_COLUMN_MAP

def process_ccds_files(file_paths):
    """
    Processes multiple tab-separated CCDS files with varying headers
    and aggregates the data into a dictionary.
    It renames header columns to desired internal keys during processing.
    """
    processed_data = {}

    for file_path in file_paths:
        print(f"Processing file: {file_path}...")
        if not os.path.exists(file_path):
            print(f"  Warning: File not found at {file_path}. Skipping.")
            continue
            
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as tsvfile:
                # Manually read and transform the header
                header_line = tsvfile.readline()
                if not header_line:
                    print(f"  Warning: File {file_path} is empty or header is missing. Skipping.")
                    continue
                
                # rename all the columns
                original_file_headers = [h.strip() for h in header_line.strip().split('\t')]
                renamed_headers_for_dictreader = []
                for original_h in original_file_headers:
                    processed_h_for_lookup = original_h.lower() # MASTER_COLUMN_MAP keys are lowercase
                    # Use the mapped desired key, or the original header if no mapping exists
                    desired_key_for_header = MASTER_COLUMN_MAP.get(processed_h_for_lookup, original_h)
                    renamed_headers_for_dictreader.append(desired_key_for_header)

                # LOG problem
                if DESIRED_MAIN_ID_KEY not in renamed_headers_for_dictreader:
                    print(f"  Warning: Main ID key '{DESIRED_MAIN_ID_KEY}' not found in (renamed) header of {file_path} after mapping. Skipping file.")
                    continue

                # Initialize DictReader with the renamed headers; it will read from the next line (first data row)
                # as we've already consumed the header line with tsvfile.readline()
                reader = csv.DictReader(tsvfile, fieldnames=renamed_headers_for_dictreader, delimiter='\t')
                
                for row_number, row in enumerate(reader, 1): # row_number is 1-based for data rows
                    try:
                        # Access the main ID using DESIRED_MAIN_ID_KEY directly from the row
                        current_id_val_original = row.get(DESIRED_MAIN_ID_KEY, "")
                        
                        if not current_id_val_original:
                            print(f"  Warning: Row {row_number} (data row) in {file_path} has an empty value for ID key '{DESIRED_MAIN_ID_KEY}'. Skipping row.")
                            continue
                        
                        current_id_val = current_id_val_original.lower()

                        if current_id_val not in processed_data:
                            processed_data[current_id_val] = {"ccds_ids": []}
                        
                        # Prepare data from the current row first
                        data_from_current_row = {}
                        for key in DESIRED_CCDS_ENTRY_KEYS:
                            val_from_row = row.get(key) # key is already the desired internal key
                            processed_val = None # Default to None if val_from_row is None or becomes empty after processing
                            if val_from_row is not None: # Present in row (even if empty string)
                                processed_val_str = val_from_row.lower()
                                if key == "ccds_id":
                                    if processed_val_str.startswith("ccds"):
                                        processed_val_str = processed_val_str[4:]
                                processed_val = processed_val_str
                            data_from_current_row[key] = processed_val

                        processed_ccds_id_from_row = data_from_current_row.get("ccds_id")
                        
                        target_entry_to_update = None
                        # Only search for an existing entry if the current row yielded a valid (non-empty) ccds_id
                        if processed_ccds_id_from_row and processed_ccds_id_from_row.strip() != "":
                            for existing_entry in processed_data[current_id_val]["ccds_ids"]:
                                if existing_entry.get("ccds_id") == processed_ccds_id_from_row:
                                    target_entry_to_update = existing_entry
                                    break
                        
                        if target_entry_to_update:
                            # Match found: Update existing entry only where its fields are currently None
                            # and the new data offers a non-None value.
                            for key_to_fill in DESIRED_CCDS_ENTRY_KEYS:
                                if target_entry_to_update.get(key_to_fill) is None: # If existing field is truly None
                                    value_from_new_data = data_from_current_row.get(key_to_fill)
                                    if value_from_new_data is not None: # And new data offers a value (could be empty string)
                                        target_entry_to_update[key_to_fill] = value_from_new_data
                        else:
                            # No match found: Append new entry, but only if it has a valid (non-empty, non-whitespace) ccds_id
                            if processed_ccds_id_from_row and processed_ccds_id_from_row.strip() != "":
                                processed_data[current_id_val]["ccds_ids"].append(data_from_current_row)
                            else:
                                # Log if row had other data but no valid ccds_id to form a new entry
                                has_other_data = any(v is not None and v.strip() != "" for k, v in data_from_current_row.items() if k != "ccds_id")
                                if has_other_data:
                                     print(f"  Info: Row {row_number} for _id '{current_id_val}' in {file_path} had data but 'ccds_id' was empty/whitespace after processing. New entry not added: {data_from_current_row}")
                                    
                    except Exception as e:
                        print(f"  Error processing data row {row_number} in {file_path}: {e}. Row data: {row}")
                        continue

        except FileNotFoundError:
            print(f"  Error: File not found at {file_path}. Skipping.")
        except Exception as e:
            print(f"  An unexpected error occurred while processing {file_path}: {e}")
            
    print("Processing complete.")
    return processed_data

# --- Example Usage ---
if __name__ == "__main__":
    files_to_process = [
        "data/human_CCDS_attributes.current.txt",
        "data/human_CCDS.current.txt",
        "data/mouse_CCDS_attributes.current.txt",
        "data/mouse_CCDS.current.txt"
    ]

    final_data = process_ccds_files(files_to_process)

    print("\nSample of processed data (first 2 _id entries):")
    import json
    count = 0
    for key, value in final_data.items():
        if count < 2: # Print first 2 _id entries
            print(f"Data for _id: {key}")
            print(json.dumps(value, indent=2))
            print("-" * 20)
            count += 1
        else:
            break
    if not final_data:
        print("No data was processed, or no _id entries were found.")
    elif len(final_data) > 0 and count == 0 and len(final_data) <2 : # handles if items exist but loop didn't run (e.g. count limit 0)
        print("Data was processed. Less than 2 _id entries found.")
    elif len(final_data) > 0 and count < 2 and count > 0:
        print(f"Data was processed. Only {count} _id entry/entries found and printed.")
