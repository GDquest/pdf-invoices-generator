"""Command-line interface for the program
"""
from argparse import ArgumentParser, Namespace
from .config import Config


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

    return parser.parse_args()
