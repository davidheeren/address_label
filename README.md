# Personal Address Label Generator

This is a personal script designed to generate PDFs of address labels formatted for Avery 8160 sticky label sheets.

It is tailored to work with my specific address data, in an Excel spreadsheet. The script reads the address information, allows for filtering of specific addresses, and then creates a printable PDF file.

## Excel Format

The script expects an `.xlsx` file with the following columns in order. The first row is skipped as a header.

`last_name1, first_name1, last_name2, first_name2, address1, address2, city, state, zip, country`

## Usage

### Command Line

Use `python main.py -h` for help.

### GUI

There's also a GUI. Run it with:
`python gui.py`

It has all the same options and saves your settings between sessions.
