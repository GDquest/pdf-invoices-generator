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

from modules.invoice import Invoice, InvoiceTemplate, InvoiceList
from modules.client import Client
from modules.products import Product
from modules.config import Config


DEBUG = True

def get_data_from_json(path):
    assert path.endswith('.json')
    with open(path) as data:
        return json.loads(data.read())


def set_up_output_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
    css_output_path = os.path.join(path, "style.css")
    if not os.path.exists(css_output_path):
        shutil.copy("template/style.css", css_output_path)
    img_output_path = os.path.join(path, "img")
    if not os.path.exists(img_output_path):
        shutil.copytree("img", img_output_path)


def generate_html_files(invoice_list, output_path, invoice_template):
    for invoice in invoice_list:
        invoice_html = convert_to_html(invoice, invoice_template)

        date = datetime.datetime.strptime(
            invoice["invoice"]["date"], config["date_format"]
        )
        date_string = date.strftime("%Y-%m-%d")
        client_name = invoice["client"]["name"].replace(" ", "-").lower()

        file_name = "{}-{}.html".format(invoice["invoice"]["index"], client_name)
        export_path = "{}/{}-{}".format(output_path, date_string, file_name)
        with codecs.open(export_path, "w", encoding="utf-8") as invoice_file:
            invoice_file.writelines(invoice_html)


def render_pdfs(html_output_folder, pdf_output_folder):
    if not os.path.exists(pdf_output_folder):
        os.makedirs(pdf_output_folder)

    for filename in os.listdir(html_output_folder):
        name = os.path.splitext(filename)[0]
        html_filepath = os.path.join(html_output_folder, filename)
        subprocess.run(
            "wkhtmltopdf {} {}.pdf".format(
                html_filepath, os.path.join(pdf_output_folder, name)
            )
        )


def main():
    locale.setlocale(locale.LC_ALL, "")
    config = Config('./data/config.json')
    company = get_data_from_json('./data/company.json')

    config.set("payment_paypal", "PayPal address: " + company["paypal"])
    with codecs.open("template/bank-details.html", "r", encoding="utf-8") as html_doc:
        config.set("payment_wire", html_doc.read())

    template = InvoiceTemplate(config.get("html_template_path"), company)
    if template.is_invalid():
        return


    invoice_list = InvoiceList(config.get("database_path"))
    invoice_list.parse_csv(config)
    print(invoice_list.db[0])
    # html = map(template.get_invoice_html, invoice_list)
    # print(next(html))

    # db_file_name = config.get("database_path")
    # assert(os.path.isfile(db_file_name))
    # db_file_name = os.path.splitext(os.path.basename())[0]
    # output_folder = os.path.join(config.get("output_path"), db_file_name)

    # html_output_folder = os.path.join(output_folder, "html")
    # pdf_output_folder = os.path.join(output_folder, "pdf")
    # set_up_output_directory(html_output_folder)
    # generate_html_files(invoice_list, html_output_folder, template)
    # render_pdfs(html_output_folder, pdf_output_folder)


if __name__ == "__main__":
    main()
