import os
import gzip
from Bio import SeqIO
import sys

# --- Configuration ---
data_directory = "data"  # Directory containing the files
file_extension = ".gpff.gz"  # File extension to filter files

# --- Initialization ---
top_level_attributes = {'id', 'name', 'description', 'seq', 'dbxrefs', 'letter_annotations'}
all_annotation_keys = set()
all_feature_types = set()
all_qualifier_keys = set()
total_records_processed = 0  # Counter for total records processed

print(f"Starting analysis of all files in directory: {data_directory}")

# --- Processing ---
try:
    for file_name in os.listdir(data_directory):
        if file_name.endswith(file_extension):
            file_path = os.path.join(data_directory, file_name)
            print(f"\nProcessing file: {file_path}")

            if file_path.endswith(".gz"):
                handle = gzip.open(file_path, "rt")
                print("Opened as gzipped file.")
            else:
                handle = open(file_path, "r")
                print("Opened as plain text file.")

            record_count = 0
            for record in SeqIO.parse(handle, "genbank"):
                record_count += 1
                total_records_processed += 1  # Increment total counter

                # Collect keys from the record.annotations dictionary
                all_annotation_keys.update(record.annotations.keys())

                # Collect feature types and qualifier keys from record.features
                for feature in record.features:
                    all_feature_types.add(feature.type)
                    all_qualifier_keys.update(feature.qualifiers.keys())

                if record_count % 1000 == 0:
                    print(f"Processed {record_count} records in {file_name}...")

            handle.close()
            print(f"Finished processing {file_name}. Total records found: {record_count}")

    # --- Combine and Output Results ---
    all_record_level_fields = top_level_attributes.union(all_annotation_keys)

    print("\n--- All Potential Record-Level Fields Found Across All Files ---")
    print(sorted(list(all_record_level_fields)))

    print("\n--- Unique Feature Types Found Across All Files ---")
    print(sorted(list(all_feature_types)))

    print("\n--- Unique Feature Qualifier Keys Found Across All Files ---")
    print(sorted(list(all_qualifier_keys)))

    print(f"\nTotal number of records processed across all files: {total_records_processed}")

except FileNotFoundError:
    print(f"\nError: The directory or a file was not found:")
    print(f"'{data_directory}'")
    print("Please check the directory path and try again.")
    sys.exit(1)

except Exception as e:
    print(f"\nAn unexpected error occurred:")
    print(e)
    print("This could be due to an issue with the file format or Biopython.")
    sys.exit(1)
