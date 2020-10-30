"""Command-line interface for the program
"""
from argparse import ArgumentParser, Namespace
from .config import Config
import datetime
import sys


def _set_date(args) -> datetime.date:
    """Validates the date argument, parsing the date from the ISO format"""
    date: datetime.date
    try:
        date = datetime.date.fromisoformat(args)
    except ValueError:
        date = datetime.date.today()
    return date


def _are_dates_valid(date_start, date_end) -> bool:
    today = datetime.date.today()
    valid = True
    if date_start > today or date_end > today or date_start > date_end:
        valid = False
    return valid


def parse_and_get_arguments(config: Config) -> Namespace:
    parser: ArgumentParser = ArgumentParser(
        prog="invoices", description="Creates PDF invoices from CSV tables"
    )
    parser.add_argument(
        "-p",
        "--path",
        default=config.get("database_path"),
        help="Path to the invoices database to render.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    parser_config = subparsers.add_parser(
        "config",
        help="Commands related to the program's configuration."
        "Set, get values, or write the default configuration to the disk.",
    )
    parser_config.add_argument("-s", "--set", help="Set an option to a given value.")
    parser_config.add_argument("-g", "--get", help="Get the value of a given option")

    parser_generate = subparsers.add_parser(
        "generate", help="Generates invoices as html files, using an html template."
    )
    parser_generate.add_argument(
        "-o",
        "--out-path",
        help="Directory to generate html files into."
        "Overrides the value from your configuration file.",
    )
    parser_generate.add_argument(
        "-t",
        "--template-path",
        help="Path to an html file to use as a template for the invoices."
        "Overrides the value from your configuration file.",
    )

    parser_render = subparsers.add_parser("render", help="command render")
    parser_render.add_argument(
        "--as-pdf",
        help="Render the invoices as PDF files."
        "Requires the program wkhtmltopdf to render the files.",
    )
    parser_render.add_argument(
        "--as-png",
        help="Render the invoices as PNG files."
        "Requires the program wkhtmltopdf to render the files.",
    )
    parser_render.add_argument(
        "-s",
        "--start-date",
        type=_set_date,
        default=datetime.date(1900, 1, 1),
        help="Only render invoices after that date. The date format should be yyyy-mm-dd, for instance, 2020-10-05 for October 5, 2020.",
    )
    parser_render.add_argument(
        "-e",
        "--end-date",
        type=_set_date,
        default=datetime.date.today(),
        help="Only render invoices before that date.",
    )

    args = parser.parse_args()

    if hasattr(args, "start_date") and not _are_dates_valid(args.start_date, args.end_date):
        print("The start and end dates are invalid. Aborting.")
        sys.exit()
    return args
