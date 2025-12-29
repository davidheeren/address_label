#!/usr/bin/env -S uv run --script

import argparse
import webbrowser
from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from pathlib import Path
from pylabels import Sheet, Specification
from collections import namedtuple
from reportlab.graphics import shapes


def get_args(defaults: bool = False) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="address_label",
        description="Creates a pdf for printing address labels from an Excel file.",
    )
    parser.add_argument("-i", "--input", default="addresses.xlsx")
    parser.add_argument("-o", "--output", default="labels.pdf")
    parser.add_argument("-f", "--filter", default="*", help="Ex: 'mary joe, 4-9, !5'")
    parser.add_argument("-b", "--bias", type=int, default=0, help="Count of labels to offset")
    parser.add_argument("-r", "--ret", action="store_true", help="Include the same number of return address labels")
    parser.add_argument("-t", "--test", action="store_true", help="Put box lines around each lablel")
    parser.add_argument("-l", "--launch", action="store_true", help="Launch the pdf in the browser")
    if defaults:
        return parser.parse_args([])
    return parser.parse_args()


def get_indices(filter_str: str, ws: Worksheet, row_offset: int) -> set[int]:
    # example filter "1, 5-9, !6, John Doe"
    # note that this is dependent on each filter's order. you want to first include then exclude
    indices = set()
    filters = filter_str.split(",")
    num_data_rows = ws.max_row - (row_offset - 1)

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
            nums.update(range(num_data_rows))
        # filter is a name
        elif all(c.isalpha() or c.isspace() for c in f):
            parts_a = [x.strip().lower() for x in f.split()]
            added_count = 0
            # Enumerate over data rows (skipping header if any)
            for index, row in enumerate(ws.iter_rows(min_row=row_offset, values_only=True)):
                item = str(row[0]) if row and len(row) > 0 and row[0] is not None else ""
                # remove all commas and split
                parts_b = set([x.strip().lower() for x in item.replace(",", "").split()])
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
                if start < row_offset or start > ws.max_row or end < row_offset or end > ws.max_row:
                    raise Exception(f"Invalid index: {f}, out of bounds {row_offset}-{ws.max_row}")
                if start > end:
                    raise Exception(f"Invalid range: start > end in {f}")
                # Convert to 0-based index relative to data start
                nums.update(range(start - row_offset, end + 1 - row_offset))
            # filter is single number
            else:
                num = int(f)
                if num < row_offset or num > ws.max_row:
                    raise Exception(f"Invalid index: {f}, out of bounds {row_offset}-{ws.max_row}")
                # Convert to 0-based index
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


def get_worksheet(input_path: str) -> tuple[Worksheet, int]:
    path = Path(input_path)
    if not path.is_file():
        raise FileNotFoundError(f"Input file not found at: {input_path}")

    if path.suffix.lower() not in [".xls", ".xlsx"]:
        raise ValueError(f"Unsupported file type: {path.suffix}. Only .xls or .xlsx files are supported.")

    wb = load_workbook(input_path)
    # Excels are assumed to have a header, so row offset is 2
    return wb.active, 2


def get_sheet(test: bool) -> Sheet:
    PADDING = 1
    specs = Specification(
        215.9,
        279.4,
        3,
        10,
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
        return Sheet(specs, draw_address_old, border=True)
    return Sheet(specs, draw_address_old)


Address = namedtuple(
    "Address", ["name", "street", "city", "state", "zip"]
)


def draw_address(label, width, height, address: Address | None):
    if address is None:
        return

    # Per USPS recommendations: ALL CAPS for readability.
    # User requested not to uppercase zip, and not to remove commas yet.
    # Lines are defined top-to-bottom for readability.
    lines = [
        address.name.upper(),
        address.street.upper(),
        f"{address.city.upper()} {address.state.upper()}  {address.zip}",
    ]

    group = shapes.Group()
    x_pos, y_pos = 0, 0

    # Draw from bottom to top.
    for line in reversed(lines):
        # Use a standard 10pt font as recommended by USPS.
        shape = shapes.String(x_pos, y_pos, line, textAnchor="start", fontName="Helvetica", fontSize=10)
        group.add(shape)
        # Correctly advance y_pos for the next line.
        _x1, y1, _x2, y2 = shape.getBounds()
        line_height = y2 - y1
        y_pos += line_height + 1.5  # Line height + 1.5pt leading

    _, _, lx, ly = label.getBounds()
    _, _, gx, gy = group.getBounds()

    # Calculate scale factor if text overflows.
    scale = 1.0
    if gx > lx:
        scale = lx / gx
    if gy > ly:
        scale = min(scale, ly / gy)

    if scale < 1.0:
        group.scale(scale, scale)
        # Recalculate bounds for centering after scaling.
        _, _, gx, gy = group.getBounds()

    # Center the group on the label.
    dx = (lx - gx) / 2
    dy = (ly - gy) / 2
    group.translate(dx, dy)

    label.add(group)


def draw_address_old(label, width, height, address: Address | None):
    if address is None:
        return

    lines = [
        (f"{address.city} {address.state}  {address.zip}").upper(),
        address.street.upper(),
        address.name,
    ]

    group = shapes.Group()
    x, y = 0, 0
    for line in lines:
        shape = shapes.String(x, y, line, textAnchor="start", fontSize=8)
        _, _, _, y = shape.getBounds()
        y += 3
        group.add(shape)
    _, _, lx, ly = label.getBounds()
    _, _, gx, gy = group.getBounds()

    if gx > lx:
        # raise Exception(f"Address too long, name: {address.name}")
        print(f"Warning: Address too long, name: {address.name}")
    if gy > ly:
        # raise Exception(f"Address too tall, name: {address.name}")
        print(f"Warning: Address too tall, name: {address.name}")

    dx = (lx - gx) / 2
    dy = (ly - gy) / 2
    group.translate(dx, dy)

    label.add(group)


def save_pdf(args: argparse.Namespace, ws: Worksheet, indices: set[int], sheet: Sheet, row_offset: int):
    if args.bias > 0:
        sheet.add_label(None, count=args.bias)

    def _get_cell(row_tuple, index):
        try:
            val = row_tuple[index]
            return str(val).strip() if val is not None else ""
        except IndexError:
            return ""

    for i in sorted(list(indices)):
        # Convert 0-based data index to 1-based worksheet row number
        worksheet_row_num = i + row_offset
        row_tuple = next(ws.iter_rows(min_row=worksheet_row_num, max_row=worksheet_row_num, values_only=True))

        address = Address(
            name=_get_cell(row_tuple, 0),
            street=_get_cell(row_tuple, 1),
            city=_get_cell(row_tuple, 2),
            state=_get_cell(row_tuple, 3),
            zip=_get_cell(row_tuple, 4),
        )

        if not any(address):
            # print("skipping blank row")
            continue

        if not all(address):
            name_for_warning = _get_cell(row_tuple, 0)
            print(f"Warning: Skipping row with name: '{name_for_warning}', index: '{i + row_offset}' due to one or more missing address fields.")
            continue

        sheet.add_label(address)

    sheet.save(args.output)
    print(f"{sheet.label_count} label(s) output on {sheet.page_count} page(s).")


def run(args: argparse.Namespace):
    ws, row_offset = get_worksheet(args.input)
    indices = get_indices(args.filter, ws, row_offset)
    sheet = get_sheet(args.test)
    save_pdf(args, ws, indices, sheet, row_offset)
    if args.launch:
        webbrowser.open(args.output)


def main():
    run(get_args())
    # try:
    #     run(get_args())
    # except Exception as e:
    #     print(f"Error: {e}")


if __name__ == "__main__":
    main()
