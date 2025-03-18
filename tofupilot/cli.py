import argparse
from importlib.metadata import (
    version,
)


def main():
    parser = argparse.ArgumentParser(prog="TofuPilot", add_help=True)
    current_version = version("tofupilot")
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {current_version}",
        help="TofuPilot package version",
    )
    parser.parse_args()


if __name__ == "__main__":
    main()
