#!/bin/env python3

import sys

from paginator import PagedUI, FileRowSource

def main():
    ui = PagedUI()
    try:
        ui.start()
        with open("/etc/locale.gen", "rt") as f:
            source = FileRowSource(f)
            ui.display(source)
    finally:
        ui.restore()

    return 0

if __name__ == "__main__":
    sys.exit(main())

