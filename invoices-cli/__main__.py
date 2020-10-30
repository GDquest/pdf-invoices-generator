# -*- coding: utf-8 -*-
import codecs
import itertools
import json
import os
from os.path import join, exists, dirname, isfile, splitext, basename
import shutil

from .modules.command_line import parse_and_get_arguments
from .modules.config import Config
from .modules.invoice import InvoiceList, InvoiceTemplate
from .modules.render import render

DEBUG = True
THIS_FILE_PATH = dirname(__file__)


def get_data_from_json(path):
    assert path.endswith(".json")
    with open(path) as data:
        return json.loads(data.read())
    return ""


def set_up_output_directory(path):
    """Create output directory tree and copy the assets required to render the pdfs
    """
    html_path = join(path, "html")
    if not exists(html_path):
        os.makedirs(html_path)
    css_output_path = join(html_path, "style.css")
    css_file_path = join(THIS_FILE_PATH, "template/style.css")
    shutil.copy(css_file_path, css_output_path)
    img_output_path = join(html_path, "img")
    if not exists(img_output_path):
        img_file_path = join(THIS_FILE_PATH, "template/img")
        shutil.copytree(img_file_path, img_output_path)


def save_html_files(dir_out, htmls, filenames):
    """Saves each html stream from the htmls list as a file"""
    html_directory = join(dir_out, "html")
    for html, filename in zip(htmls, filenames):
        export_path = join(html_directory, filename + ".html")
        with codecs.open(export_path, "w", encoding="utf-8") as invoice_file:
            invoice_file.writelines(html)


def get_config():
    """
    Returns a Config object with information about the company and invoice settings.
    """
    config_path = join(THIS_FILE_PATH, "./data/config.json")
    config = Config(config_path)

    json_path = join(THIS_FILE_PATH, "./data/company.json")
    company = get_data_from_json(json_path)
    config.set("company", company)
    config.set("payment_paypal", "PayPal address: " + company["paypal"])
    bank_details_path = join(THIS_FILE_PATH, "template/bank-details.html")
    with codecs.open(bank_details_path, "r", encoding="utf-8") as html_doc:
        config.set("payment_wire", html_doc.read())
    return config


def main():
    config = get_config()

    template_path = join(THIS_FILE_PATH, "template/invoice.html")
    template = InvoiceTemplate(template_path, config.get("company"))
    if template.is_invalid():
        return

    args = parse_and_get_arguments(config)
    assert isfile(args.path)
    db_file_name = splitext(basename(args.path))[0]
    dir_out = join(config.get("output_path"), db_file_name)

    invoice_list = InvoiceList(args.path)
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
