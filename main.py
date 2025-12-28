#!/usr/bin/env -S uv run --script

import argparse
import webbrowser
from pandas import DataFrame, read_excel, read_csv
from pathlib import Path
from pylabels import Sheet, Specification
from collections import namedtuple
from reportlab.graphics import shapes


def get_args(defaults: bool = False) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="address_label",
        description="Creates a pdf for printing address labels",
    )
    parser.add_argument("-i", "--input", default="addresses.csv")
    parser.add_argument("-o", "--output", default="labels.pdf")
    parser.add_argument("-f", "--filter", default="*", help="Ex: 'mary joe, 4-9, !5'")
    parser.add_argument("-b", "--bias", type=int, default=0, help="Count of labels to offset")
    parser.add_argument("-r", "--ret", action="store_true", help="Include the same number of return address labels")
    parser.add_argument("-t", "--test", action="store_true", help="Put box lines around each lablel")
    parser.add_argument("-l", "--launch", action="store_true", help="Launch the pdf in the browser")
    if defaults:
        return parser.parse_args([])
    return parser.parse_args()


def get_indices(filter: str, df: DataFrame, row_offset: int) -> set[int]:
    # example filter "1, 5-9, !6, John Doe"
    # note that this is dependent on each filter's order. you want to first include then exclude
    # TODO: refactor for cleaner code
    indices = set()
    filters = filter.split(",")
    for f in filters:
        invert = False
        # nums to add to indices
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
        # filter is a name
        elif all(c.isalpha() or c.isspace() for c in f):
            # we split the filter name and database name on spaces
            # all filter parts must match the database parts to be added
            parts_a = [x.strip().lower() for x in f.split()]
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

        # filter is number or number range
        elif all(c.isdigit() or c == "-" for c in f):
            # filter is range
            if "-" in f:
                parts = f.split("-")
                if len(parts) != 2 or not parts[0].strip().isdigit() or not parts[1].strip().isdigit():
                    raise Exception(f"Invalid index range: {f}")
                start, end = map(int, (parts[0], parts[1]))
                if start < row_offset or start >= len(df) + row_offset or end < row_offset or end >= len(df) + row_offset:
                    raise Exception(f"Invalid index: {f}, out of bounds {row_offset}-{len(df) + row_offset - 1}")
                if start > end:
                    raise Exception(f"Invalid range: start > end in {f}")
                nums.update(range(start - row_offset, end + 1 - row_offset))
            # filter is single number
            else:
                num = int(f)
                if num < row_offset or num >= len(df) + row_offset:
                    raise Exception(f"Invalid index: {f}, out of bounds {row_offset}-{len(df) + row_offset - 1}")
                nums.add(num - row_offset)

        # not a valid filter
        else:
            raise Exception(f"Not a valid filter: {f}")

        # update the indices
        if invert:
            indices.difference_update(nums)
        else:
            indices.update(nums)
    return indices


def get_dataframe(input_path: str) -> (DataFrame, int):
    # this funciton assumes that an excel file has a header
    # check if path is valid
    path = Path(input_path)
    if not path.is_file():
        raise FileNotFoundError(f"Input file not found at: {input_path}")
    # if is csv read csv without header
    if path.suffix.lower() == ".csv":
        return read_csv(path, header=None), 1
    # if excel then read excel
    elif path.suffix.lower() in [".xls", ".xlsx"]:
        return read_excel(path), 2
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}. Please use .csv, .xls, or .xlsx files.")


def get_sheet(test: bool) -> Sheet:
    PADDING = 1
    specs = Specification(
        215.9,
        279.4,
        3,
        10,
        # 64,
        66.7,
        25.4,
        corner_radius=2,
        left_margin=5,
        right_margin=5,
        top_margin=13,
        left_padding=PADDING,
        right_padding=PADDING,
        top_padding=PADDING,
        bottom_padding=PADDING,
        row_gap=0,
    )

    if test:
        return Sheet(specs, draw_address, border=True)
    return Sheet(specs, draw_address)


Address = namedtuple(
    "Address", ["name", "name2", "street1", "street2", "city", "state", "zip"]
)


def draw_address(label, width, height, address: Address | None):
    # If the address is None, we do nothing, resulting in a blank label.
    if address is None:
        return

    assert address.state, address  # nosec B101
    assert address.zip, address  # nosec B101

    # The order is flipped, because we're painting from bottom to top.
    # The sum of the lines get .upper(), because that's what the USPS likes.
    lines = [
        ("%s %s  %s" % (address.city, address.state, address.zip)).upper(),
        address.street2.upper(),
        address.street1.upper(),
        address.name2,
        address.name,
    ]

    group = shapes.Group()
    x, y = 0, 0
    for line in lines:
        if not line:
            continue
        shape = shapes.String(x, y, line, textAnchor="start")
        _, _, _, y = shape.getBounds()
        # Some extra spacing between the lines, to make it easier to read
        y += 3
        group.add(shape)
    _, _, lx, ly = label.getBounds()
    _, _, gx, gy = group.getBounds()

    # Make sure the label fits in a sticker
    assert gx <= lx, (address, gx, lx)  # nosec B101
    assert gy <= ly, (address, gy, ly)  # nosec B101

    # Move the content to the center of the sticker
    dx = (lx - gx) / 2
    dy = (ly - gy) / 2
    group.translate(dx, dy)

    label.add(group)


def save_pdf(args: argparse.Namespace, df: DataFrame, indices: set[int], sheet: Sheet):
    # Add blank labels if a bias is specified
    if args.bias > 0:
        sheet.add_label(None, count=args.bias)

    # sort indices to be in order
    for i in sorted(list(indices)):
        row = df.iloc[i].fillna("")
        address = Address(
            name=str(row.iloc[0]).strip(),
            name2=str(row.iloc[1]).strip(),
            street1=str(row.iloc[2]).strip(),
            street2=str(row.iloc[3]).strip(),
            city=str(row.iloc[4]).strip(),
            state=str(row.iloc[5]).strip(),
            zip=str(row.iloc[6]).strip(),
        )
        sheet.add_label(address)

    sheet.save(args.output)
    print(f"{sheet.label_count} label(s) output on {sheet.page_count} page(s).")


def run(args: argparse.Namespace):
    df, row_offset = get_dataframe(args.input)
    indices = get_indices(args.filter, df, row_offset)
    sheet = get_sheet(args.test)
    save_pdf(args, df, indices, sheet)
    if args.launch:
        webbrowser.open(args.output)


def main():
    try:
        run(get_args())
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
