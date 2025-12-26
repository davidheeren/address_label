#!/usr/bin/env -S uv run --script

import argparse
import pandas


def get_args() -> object:
    parser = argparse.ArgumentParser(
        prog="address_label",
        description="Creates a pdf for printing address labels",
    )
    parser.add_argument("-i", "--input", default="test.xlsx")
    parser.add_argument("-o", "--output", default="labels.pdf")
    parser.add_argument("-f", "--filter", default="*")
    parser.add_argument("-c", "--offset_count", default=0)
    parser.add_argument("-r", "--return", action="store_true")
    return parser.parse_args()


def get_indices(filter: str, df: pandas.DataFrame) -> set[int]:
    # example filter "1, 5-9, !6, John Doe"
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
        elif f[0].isdigit():
            if "-" in f:
                start, end = map(int, f.split("-"))
                if start > end:
                    raise Exception(f"Invalid range: start > end in {f}")
                nums.update(range(start, end + 1))
            else:
                nums.add(int(f))
        elif f[0].isalpha():
            # Ignores names and invalid ranges for now
            # for item in df.iloc[:, 0]:
            # if item ==
            nums.add(-1)
            pass
        else:
            raise Exception(f"Not a valid filter: {f}")
        if invert:
            indices.difference_update(nums)
        else:
            indices.update(nums)
    return indices


def main():
    # pandas row index is offset by 2. It starts at 0 and does not count headers
    args = get_args()
    df: pandas.DataFrame = pandas.read_excel(args.input)
    indices = get_indices(args.filter, df)
    # print(df.iloc[0, 0])
    print(indices)


if __name__ == "__main__":
    main()
