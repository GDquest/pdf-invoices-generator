# -*- coding: utf-8 -*-
import codecs
import itertools
import json
import locale
import os
import shutil

from .modules.command_line import parse_and_get_arguments
from .modules.config import Config
from .modules.invoice import InvoiceList, InvoiceTemplate
from .modules.render import render

DEBUG = True
THIS_FILE_PATH = os.path.dirname(__file__)


def get_data_from_json(path):
    assert path.endswith(".json")
    with open(path) as data:
        return json.loads(data.read())


def set_up_output_directory(path):
    """Create output directory tree and copy the assets required to render the pdfs
    """
    html_path = os.path.join(path, "html")
    if not os.path.exists(html_path):
        os.makedirs(html_path)
    css_output_path = os.path.join(html_path, "style.css")
    css_file_path = os.path.join(THIS_FILE_PATH, "template/style.css")
    shutil.copy(css_file_path, css_output_path)
    img_output_path = os.path.join(html_path, "img")
    if not os.path.exists(img_output_path):
        img_file_path = os.path.join(THIS_FILE_PATH, "template/img")
        shutil.copytree(img_file_path, img_output_path)


def save_html_files(dir_out, htmls, filenames):
    """Saves each html stream from the htmls list as a file"""
    html_directory = os.path.join(dir_out, "html")
    for html, filename in zip(htmls, filenames):
        export_path = os.path.join(html_directory, filename + ".html")
        with codecs.open(export_path, "w", encoding="utf-8") as invoice_file:
            invoice_file.writelines(html)


def main():
    locale.setlocale(locale.LC_ALL, "")

    config_path = os.path.join(THIS_FILE_PATH, "./data/config.json")
    config = Config(config_path)
    json_path = os.path.join(THIS_FILE_PATH, "./data/company.json")
    company = get_data_from_json(json_path)

    config.set("payment_paypal", "PayPal address: " + company["paypal"])
    bank_details_path = os.path.join(THIS_FILE_PATH, "template/bank-details.html")
    with codecs.open(bank_details_path, "r", encoding="utf-8") as html_doc:
        config.set("payment_wire", html_doc.read())

    template = InvoiceTemplate(
        os.path.join(THIS_FILE_PATH, "template/invoice.html"), company
    )
    if template.is_invalid():
        return

    args = parse_and_get_arguments(config)
    db_file_path = args.path
    assert os.path.isfile(db_file_path)
    db_file_name = os.path.splitext(os.path.basename(db_file_path))[0]
    dir_out = os.path.join(config.get("output_path"), db_file_name)

    invoice_list = InvoiceList(db_file_path)
    invoice_list.parse_csv(config)
    htmls = map(
        template.get_invoices_as_html, invoice_list.db, itertools.repeat(config)
    )
    filenames = (invoice.get_filename() for invoice in invoice_list.db)

    set_up_output_directory(dir_out)
    if args.command == "generate":
        save_html_files(dir_out, htmls, filenames)
    if args.command == "render":
        render(dir_out, as_png=False)


if __name__ == "__main__":
    main()
