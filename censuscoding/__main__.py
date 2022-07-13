import argparse
import censuscoding
import logging
import sys

def main():
    parser = argparse.ArgumentParser(description=censuscoding.__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    # Basic arguments
    parser.add_argument("-v", "--version",
                        action="version",
                        version="censuscoding {}".format(censuscoding.__version__))
    parser.add_argument("-q", "--quiet",
                        action="store_true",
                        help="suppress all logging messages except for errors")
    parser.add_argument("-d", "--debug",
                        action="store_true",
                        help="show all logging messages, including debugging output")
    parser.add_argument("-p", "--preserve",
                        action="store_true",
                        help="preserve unmatched records in CSV output file")
    parser.add_argument("--data",
                        help="path to an alternative censuscoding data directory")

    # Required arguments
    parser.add_argument("-i", "--input",
                        required=True,
                        help="input CSV file containing [record_id, zipcode, address]")
    parser.add_argument("-o", "--output",
                        required=True,
                        help="output CSV file containing ['id', 'zipcode', 'blkgrp', 'pobox', 'unsheltered']")

    # Optional arguments
    parser.add_argument("--record_id",
                        default="record_id",
                        help="field name corresponding to the record ID [default: 'record_id']")
    parser.add_argument("--zipcode",
                        default="zipcode",
                        help="field name corresponding to the zip code [default: 'zipcode']")
    parser.add_argument("--address",
                        default="address",
                        help="field name corresponding to the street address with street name and number [default: 'address']")

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    elif args.quiet:
        logging.basicConfig(stream=sys.stdout, level=logging.ERROR)
    else:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    if args.data:
        censuscoding.set_lookup_path(args.data)

    censuscoding.censuscode(
        args.input,
        args.output,
        record_id=args.record_id,
        zipcode=args.zipcode,
        address=args.address,
        preserve=args.preserve
    )

if __name__ == "__main__":
    sys.exit(main())
