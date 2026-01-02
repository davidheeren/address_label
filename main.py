#!/usr/bin/env -S uv run --script

import argparse
from argparse import Namespace
from label_generator import LabelGenerator


def get_args(defaults: bool = False) -> Namespace:
    """Gets the command line args. If 'defaults' then return the default arguments"""
    parser = argparse.ArgumentParser(
        prog="address_label",
        description="Creates a pdf for printing address labels from an Excel file.",
    )
    parser.add_argument("-i", "--input", default="addresses.xlsx")
    parser.add_argument("-o", "--output", default="labels.pdf")
    parser.add_argument("-f", "--filter", default="*", help="Ex: 'mary joe, 4-9, !5'")
    parser.add_argument("-b", "--bias", type=int, default=0, help="Count of labels to offset")
    parser.add_argument("-n", "--name", default="", help="Your name to find return addresses row")
    parser.add_argument("-r", "--ret", action="store_true", help="Include the same number of return address labels")
    parser.add_argument("-t", "--test", action="store_true", help="Put box lines around each lablel")
    parser.add_argument("-l", "--launch", action="store_true", help="Launch the pdf in the browser")
    if defaults:
        return parser.parse_args([])
    return parser.parse_args()


def main():
    args = get_args()
    label_generator = LabelGenerator(args)
    label_generator.generate_pdf()


if __name__ == "__main__":
    main()
