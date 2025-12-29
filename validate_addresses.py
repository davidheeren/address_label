#!/usr/bin/env -S uv run --script

import usaddress


def validate_address(address: str) -> str:
    pass


def main():
    # addr = "123 Main St. Suite 100, Chicago, IL"
    # addr = "1438 NW 11th St,Corvallis,OR,97330"
    addr = ",PO Box 86,Lennox,SD,57039,"

    # Tagging returns an OrderedDict and an address type string
    tagged_address, address_type = usaddress.tag(addr)
    print(address_type)

    f_address = f"{tagged_address['AddressNumber']} {tagged_address['StreetName']} {tagged_address['StreetNamePostType']}"
    print(f_address)


if __name__ == "__main__":
    main()
