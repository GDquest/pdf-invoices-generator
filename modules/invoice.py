import logging
import re
import os
import datetime
import codecs
import csv

from .products import Product
from .client import Client
from .config import Config


class Invoice:
    def __init__(
        self,
        index,
        client,
        products,
        date_string,
        payment_delay,
        currency,
        payment_details="",
    ):
        self.date, self.payment_date = self.parse_date(date_string, payment_delay)
        self.index = index

        self.client = client
        self.products = products
        self.currency = self.get_currency_symbol(currency)
        self.payment_details = payment_details

        self.total = sum(map(lambda p: p.calculate_total(), products))
        self.tax = sum(map(lambda p: p.calculate_tax(), products))
        self.total_tax_excl = self.total - self.tax

    def parse_date(self, date_string, payment_delay=7):
        date = datetime.datetime.strptime(date_string, "%d/%m/%Y")
        payment_date = date + datetime.timedelta(days=payment_delay)
        return date, payment_date

    def get_currency_symbol(self, currency: str) -> str:
        currencies = {"EUR": "&euro;", "USD": "$", "JPY": "JPY"}
        return currencies[currency] if currency in currencies else ""

    def get_filename(self) -> str:
        """Returns a filename as a string without the extension"""
        return "{}-{:03d}-{}".format(self.date, self.index, self.client.name)

    def __repr__(self):
        return "Invoice {:03d} from {!s}".format(self.index, self.date)


class InvoiceList:
    """Generates and stores a list of Invoice objects parsed from csv"""

    def __init__(self, csv_file_path=""):
        self.csv_file_path = csv_file_path
        self.db = []

    def parse_csv(self, config):
        """Populates the db list with Invoice objects, parsed from self.csv_file_path"""
        self.db = []
        with codecs.open(self.csv_file_path, "r", encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")

            next(csv_reader)
            for id, row in enumerate(csv_reader):
                currency = row[1] if row[1] else config["default_currency"]

                client = Client(
                    name=row[4], address=row[7], country_code=row[5], tax_number=row[6]
                )
                products = [Product(identifier=row[2], price=float(row[3]), quantity=1)]
                invoice = Invoice(
                    id + 1,
                    client,
                    products,
                    row[0],
                    config.get("payment_delay_days"),
                    currency,
                )
                self.db.append(invoice)


class InvoiceTemplate:
    """
    Loads and stores an html template as a list.
    Parses the file and stores identifiers enclosed in double brackets: {{ identifier }}
    Finds, replaces template elements, parses and writes html to disk
    """

    def __init__(self, file_path, company_details):
        if not os.path.exists(file_path):
            raise AttributeError("File " + file_path + " does not exist")

        self.company = company_details
        with open(file_path, "r") as html_doc:
            self.html, self.regex_matches = self._parse(html_doc)

    def is_invalid(self):
        return not self.html or not self.company

    def get_invoices_as_html(self, invoice: Invoice, config: Config):
        """
        Returns a copy of the html data with template {{ identifiers }} replaced
        """
        html = list(self.html)
        client: Client = invoice.client
        # TODO: add support for multiple products
        product: Product = invoice.products[0]
        total_tax_excluded = product.calculate_total() - product.calculate_tax()
        data = {
            "client_name": client.name,
            "client_address": client.address,
            "client_VAT_number": client.tax_number,
            "invoice_index": invoice.index,
            "invoice_date": invoice.date,
            "product_name": product.identifier,
            "product_quantity": product.quantity,
            "product_unit_price": product.price,
            "product_VAT_rate": product.tax_rate,
            "product_total_tax_excl": total_tax_excluded,
            # TODO: add discount support
            "total_discount": 0,
            "total_excl_tax": total_tax_excluded,
            "total_tax": product.calculate_tax(),
            "total_incl_tax": product.calculate_total(),
            "mentions_vat": config.get("mention_fr_autoliquidation")
            if product.calculate_tax() == 0.0
            else "",
            "payment_date": invoice.payment_date,
            "payment_details": invoice.payment_details,
        }
        for index, identifier in self.regex_matches:
            string_template = "{{ " + identifier + " }}"
            html[index] = html[index].replace(string_template, str(data[identifier]), 1)
        return html

    def _parse(self, html_doc):
        """
        Bakes the company details in the document as every invoice is issues by the same company.
        Stores a list of found identifiers to replace in individual invoices.
        """
        html, regex_matches = [], []
        line_id = 0
        for line in html_doc:
            match = re.match(r".+{{ (.*) }}", line)
            if match:
                identifier = match.group(1)
                if identifier.startswith("company"):
                    key = identifier.split("_", maxsplit=1)[-1]
                    string_template = "{{ " + identifier + " }}"
                    line = line.replace(string_template, self.company[key], 1)
                else:
                    regex_matches.append((line_id, match.group(1)))
            html.append(line)
            line_id += 1
        return html, regex_matches
