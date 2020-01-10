# -*- coding: utf-8 -*-
import codecs
import itertools
import json
import locale
import os
import shutil

from modules.config import Config
from modules.invoice import InvoiceList, InvoiceTemplate
from modules.render import render

DEBUG = True


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
    if not os.path.exists(css_output_path):
        shutil.copy("template/style.css", css_output_path)
    img_output_path = os.path.join(html_path, "img")
    if not os.path.exists(img_output_path):
        shutil.copytree("template/img", img_output_path)


def save_html_files(dir_out, htmls, filenames):
    """Saves each html stream from the htmls list as a file"""
    html_directory = os.path.join(dir_out, "html")
    for html, filename in zip(htmls, filenames):
        export_path = os.path.join(html_directory, filename + ".html")
        with codecs.open(export_path, "w", encoding="utf-8") as invoice_file:
            invoice_file.writelines(html)


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
    htmls = map(
        template.get_invoices_as_html, invoice_list.db, itertools.repeat(config)
    )
    filenames = (invoice.get_filename() for invoice in invoice_list.db)

    db_file_path = config.get("database_path")
    assert os.path.isfile(db_file_path)
    db_file_name = os.path.splitext(os.path.basename(db_file_path))[0]
    dir_out = os.path.join(config.get("output_path"), db_file_name)
    set_up_output_directory(dir_out)
    save_html_files(dir_out, htmls, filenames)
    render(dir_out, as_png=False)


if __name__ == "__main__":
    main()
