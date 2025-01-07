import argparse
from lankaNIC import NICParser, InvalidNICError
from lankaNIC.logger import get_logger, configure_logging
from datetime import datetime
import json
import csv
import os

logger = get_logger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Parse Sri Lankan NIC number and extract information.")
    parser.add_argument("nics", nargs="*", help="NIC number(s) to parse")
    parser.add_argument(
        "-i", "-f", "-file",
        dest="input_file",
        help="Input file(s) containing NIC numbers (one per line)",
        nargs="+"
    )

    allowedformats = {
            "csv" : "Comma Seperated Values",
            "json" : "JSON",
            "txt" : "Plain text"
        }

    parser.add_argument(
        "-in:format", "-openformat",
        dest="informat",
        help=f"Input file format (use with -i). Supported {allowedformats}",
        default="txt"
    )
    parser.add_argument(
        "-data", "-d",
        dest="data",
        help="Specify what data and order to display (e.g., 'bfa' for DOB, Format, Age)",
        default=""
    )
    parser.add_argument(
        "-plain", "-raw", "-nolabel",
        dest="plain",
        help="Display output without labels",
        action="store_true"
    )
    parser.add_argument(
        "-txt:separator", "-txt:sep", "-txt:delimit",
        dest="sep",
        help="Separator for output (default: newline). Use quotes for space (e.g., \" \")",
        default="\n"
    )
    parser.add_argument(
        "-no-nic", "-nonic",
        dest="no_nic",
        help="Suppress the display of the NIC number in output",
        action="store_true"
    )
    parser.add_argument(
        "-out:format", "-saveformat",
        dest="outformat",
        help=f"Output file format (use with -o). Supported {allowedformats}",
        default="txt"
    )

    parser.add_argument(
        "-p", "-print", "-show",
        dest="output_console",
        help="Show output (in console) default = True",
        default = True
    )
    parser.add_argument(
        "-o", "-out:file", "-save",
        dest="output_file",
        help="File path to save the output (e.g., result.csv or result.json)"
    )
    parser.add_argument(
        "-v", "--verbosity",
        type=int,
        choices=[0, 1, 2],
        default=0,
        help="Set verbosity level: 0=errors only, 1=info, 2=debug (default: 0)"
    )
    args = parser.parse_args()

    
    #configure_logging(logger, args.verbosity)

    # Check if NICs are provided
    if not args.nics and not args.file_paths:
        logger.error("No NIC numbers provided.")
        return
    
    # Valid output format
    if args.outformat:
        args.outformat = args.outformat.lower()
        if not args.outformat in allowedformats:
            logger.error("Unrecognized output format reqyested")
            return
    
    # Valid input format
    if args.informat:
        args.informat = args.informat.lower()
        if not args.informat in allowedformats:
            logger.error("Unrecognized input format supplied")
            return

    parser = NICParser()

    counter = 0
    file_nics = []
    
    for i in args.input_file:
        file_nics.append(load_file_nics(i, args.informat))

    for nic in args.nics:
        counter += 1
        try:
            parser.nic_number = nic

            content = extract(parser, args.data, args.sep, args.plain)
            
        except InvalidNICError as e:
            logger.error(e)
        
        # Output
        filename = args.output_file
        # Handle context where filename carries a file format but outformat is not specified
        if not args.outformat:
            args.outformat = get_fileextension(filename)
            

        block = ""
        match args.outformat:
            case "json":
                logger.info(f"Processing output as json")
                block = json.dumps(content)
            case "csv":
                logger.info(f"Processing output as csv")
                # Headers
                if counter == 1:
                    block = ",".join(content.keys()) + "\n"
                # Content
                block += ",".join(content.values()) + "\n"
            case _:
                logger.info(f"Processing output as txt")
                # Assume txt or any other format claim
                for key, value in content.items():
                    if type(key) != int:
                        block += key + " : "    
                    block += value + args.sep

        if filename:
            with open(filename, "w") as outfile:
                logger.info(f"Saving output to file {filename}")
                outfile.write(block)

        if args.output_console:
            print(block)

def get_fileextension(filename):
    """
    Get the extension of a given filename.
    """
    return os.path.splitext(filename)[1].lower()

def load_file_nics(filename, format):
    if not format:
        format = get_fileextension(filename)

    nics = []
    match format:
        case "csv":
            logging.info(f"Processing file {filename} as CSV")
            try:
                with open(filename, "r") as file:
                    reader = csv.reader(file)
                    header = next(reader)  # Get column names
                    data_preview = list(reader)[:10]  # Preview first 10 rows
                    
                    # Display column headers with potential NIC markers
                    display_headers_with_indices(header, data_preview)

                    # User selects columns
                    selected_indices = input("Enter column indices to extract NICs (comma-separated): ")
                    selected_indices = [int(idx.strip()) for idx in selected_indices.split(",")]

                    # Optionally preview rows
                    preview = input("Preview rows? (yes/no): ").strip().lower()
                    if preview == "yes":
                        start_row = int(input("Enter start row number: ")) - 1
                        end_row = int(input("Enter end row number: "))
                        preview_rows(data_preview, start_row, end_row)

                    # Extract NICs
                    nics.extend(extract_nics(data_preview, selected_indices, is_json=False))

            except FileNotFoundError:
                logging.warning(f"File {filename} not found. Skipping.")

        case "json":
            logging.info(f"Processing file {filename} as JSON")
            try:
                with open(filename, "r") as file:
                    data = json.load(file)

                    if isinstance(data, list):  # JSON array of objects
                        keys = list(data[0].keys())  # Assume all objects have the same keys

                        # Display keys with potential NIC markers
                        display_headers_with_indices(keys)

                        # User selects keys
                        selected_indices = input("Enter key indices to extract NICs (comma-separated): ")
                        selected_keys = [keys[int(idx.strip())] for idx in selected_indices.split(",")]

                        # Optionally preview rows
                        preview = input("Preview rows? (yes/no): ").strip().lower()
                        if preview == "yes":
                            start_row = int(input("Enter start row number: ")) - 1
                            end_row = int(input("Enter end row number: "))
                            preview_rows(data, start_row, end_row)

                        # Extract NICs
                        nics.extend(extract_nics(data, selected_keys, is_json=True))

            except FileNotFoundError:
                logging.warning(f"File {filename} not found. Skipping.")

        case _ :
            logger.info(f"Processing file {filename} as txt")
            # txt or other
            try:
                with open(filename, "r") as file:
                    # Read all lines, strip whitespace, and filter out empty lines
                    nics.extend([line.strip() for line in file.readlines() if line.strip()])
            except FileNotFoundError:
                logger.warn(f"File {filename} not found. Skipping.")

# Assume is_valid_nic() is defined elsewhere
def display_headers_with_indices(headers, data_preview=None):
    """
    Display headers (CSV columns or JSON keys) with optional data preview.
    """
    print("Headers/Keys in the file:")
    for idx, header in enumerate(headers):
        # Mark header if it seems to contain valid NICs
        if data_preview and any(NICParser.is_valid(row[idx]) for row in data_preview if idx < len(row)):
            print(f"{header}* [{idx}]")
        else:
            print(f"{header} [{idx}]")

def preview_rows(data, start, end):
    """
    Display rows/items from start to end.
    """
    print(f"Previewing rows {start + 1} to {end}:")
    for row in data[start:end]:
        print(row)

def extract_nics(data, indices_or_keys, is_json=False):
    """
    Extract NICs from selected columns/keys.
    """
    nics = []
    for row in data:
        for key_or_idx in indices_or_keys:
            value = row.get(key_or_idx) if is_json else (row[key_or_idx] if key_or_idx < len(row) else None)
            if value and is_valid_nic(value):
                nics.append(value)
    return nics


def extract(parser, data, sep, raw):
    data_keys = {
            "y": "Year of Birth",
            "d": "Day of Year",
            "b": "Date of Birth",
            "g": "Gender",
            "s": "Gender",
            "v": "Voting",
            "f": "Format",
            "a": "Age",
            "n": "Next Birthday",
        }

    block = {}
    if not data:
        data = "basf"
    for d in data:
        if raw:
            key = len(block)

        else:
            try:
                key = data_keys.get(d)
                if not key:
                    break
            except:
                logger.error(f"Unfamiliar data element request {d} skipped")
                break

        match d:
            case "y":
                value = parser.birth_day.strftime("%Y")
            case "d":
                value = parser.birth_day.strftime("%j")
            case "b":
                value = parser.birth_day.strftime("%Y-%m-%d")
            case "s" | "g":
                value = parser.sex
            case "v":
                value = parser.voting
            case "f":
                value = parser.format
            case "a":
                value = parser.age
            case "n":
                value = parser.next_birth_day
        block.update({key : value})
    return block

        # Print all
if __name__ == "__main__":
    main()
