#!/usr/bin/env -S uv run --script

import argparse
from pandas import DataFrame, read_excel, read_csv
from pathlib import Path


def get_args() -> object:
    parser = argparse.ArgumentParser(
        prog="address_label",
        description="Creates a pdf for printing address labels",
    )
    parser.add_argument("-i", "--input", default="addresses.csv")
    parser.add_argument("-o", "--output", default="labels.pdf")
    parser.add_argument("-f", "--filter", default="*", help="Ex: 'mary joe, 4-9, !5'")
    parser.add_argument("-c", "--offset_count", default=0)
    parser.add_argument("-r", "--return", action="store_true", help="Include the same number of return address labels")
    return parser.parse_args()


def get_indices(filter: str, df: DataFrame) -> set[int]:
    # example filter "1, 5-9, !6, John Doe"
    # TODO: refactor for cleaner code
    indices = set()
    filters = filter.split(",")
    for f in filters:
        invert = False
        nums = set()
        f = f.strip()
        if not f:
            continue
        if f.startswith("!"):
            invert = True
            f = f[1:]
        if not f:
            raise Exception("Invalid filter: dangling '!'")

        if f == "*":
            nums.update(range(0, len(df)))
        elif all(c.isalpha() or c.isspace() for c in f):
            # we split the filter name and excel name on spaces
            # all filter parts must be in the database parts to be included
            parts_a = [x.strip().lower() for x in f.split()]
            if len(parts_a) == 0:
                continue
            added_count = 0
            for index, item in enumerate(df.iloc[:, 0]):
                parts_b = set([x.strip().lower() for x in item.split()])
                match_all = True
                for a in parts_a:
                    if a not in parts_b:
                        match_all = False
                if match_all:
                    nums.add(index)
                    added_count += 1
            print(f"Matched name: {f}, {added_count} times")
        elif all(c.isdigit() or c == "-" for c in f):
            if "-" in f:
                parts = f.split("-")
                if len(parts) != 2 or not parts[0].strip().isdigit() or not parts[1].strip().isdigit():
                    raise Exception(f"Invalid index range: {f}")
                start, end = map(int, (parts[0], parts[1]))
                if start > end:
                    raise Exception(f"Invalid range: start > end in {f}")
                nums.update(range(start - 1, end))
            else:
                nums.add(int(f) - 1)
        else:
            raise Exception(f"Not a valid filter: {f}")

        if invert:
            indices.difference_update(nums)
        else:
            indices.update(nums)
    return indices


def get_dataframe(input_path: str) -> DataFrame:
    # check if path is valid
    path = Path(input_path)
    if not path.is_file():
        raise FileNotFoundError(f"Input file not found at: {input_path}")
    # if is csv read csv without header
    if path.suffix.lower() == ".csv":
        return read_csv(path, header=None)
    # if excel then read excel
    elif path.suffix.lower() in [".xls", ".xlsx"]:
        return read_excel(path)
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}. Please use .csv, .xls, or .xlsx files.")


def main():
    args = get_args()
    df = get_dataframe(args.input)
    indices = get_indices(args.filter, df)
    # print(df.iloc[17, 0])
    print(indices)


if __name__ == "__main__":
    main()
