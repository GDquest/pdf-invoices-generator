# -*- coding: utf-8 -*-
import json
import subprocess
import os
import shutil
import csv
import re
import logging
import locale
import datetime
import codecs
import itertools

from modules.invoice import Invoice, InvoiceTemplate, InvoiceList
from modules.client import Client
from modules.products import Product
from modules.config import Config


DEBUG = True


def get_data_from_json(path):
    assert path.endswith(".json")
    with open(path) as data:
        return json.loads(data.read())


def set_up_output_directory(path):
    """Create output directory tree and copy the assets required to render the pdfs
    """
    if not os.path.exists(path):
        os.makedirs(path)
    css_output_path = os.path.join(path, "style.css")
    if not os.path.exists(css_output_path):
        shutil.copy("template/style.css", css_output_path)
    img_output_path = os.path.join(path, "img")
    if not os.path.exists(img_output_path):
        shutil.copytree("template/img", img_output_path)


def save_html_files(html_output_directory, htmls, filenames):
    for html, filename in zip(htmls, filenames):
        export_path = os.path.join(html_output_directory, filename + ".html")
        with codecs.open(export_path, "w", encoding="utf-8") as invoice_file:
            invoice_file.writelines(html)


def render_pdfs(html_output_directory, pdf_output_directory):
    if not os.path.exists(pdf_output_directory):
        os.makedirs(pdf_output_directory)

    for filename in os.listdir(html_output_directory):
        name = os.path.splitext(filename)[0]
        html_filepath = os.path.join(html_output_directory, filename)
        subprocess.run(
            "wkhtmltopdf {} {}.pdf".format(
                html_filepath, os.path.join(pdf_output_directory, name)
            )
        )


def main():
    locale.setlocale(locale.LC_ALL, "")
    config = Config("./data/config.json")
    company = get_data_from_json("./data/company.json")

    config.set("payment_paypal", "PayPal address: " + company["paypal"])
    with codecs.open("template/bank-details.html", "r", encoding="utf-8") as html_doc:
        config.set("payment_wire", html_doc.read())

    template = InvoiceTemplate(config.get("html_template_path"), company)
    if template.is_invalid():
        return

    invoice_list = InvoiceList(config.get("database_path"))
    invoice_list.parse_csv(config)
    htmls = map(template.get_invoices_as_html, invoice_list.db, itertools.repeat(config))
    filenames = (invoice.get_filename() for invoice in invoice_list.db)

    db_file_path = config.get("database_path")
    assert(os.path.isfile(db_file_path))
    db_file_name = os.path.splitext(os.path.basename(db_file_path))[0]
    output_directory = os.path.join(config.get("output_path"), db_file_name)

    html_output_directory = os.path.join(output_directory, "html")
    set_up_output_directory(html_output_directory)
    save_html_files(html_output_directory, htmls, filenames)
    return

    render_pdfs(html_output_directory, output_directory)


if __name__ == "__main__":
    main()
