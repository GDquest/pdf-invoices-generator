import logging
import re
import os
import datetime
import options


class Invoice:
    def __init__(self, index, client, products, date_string, currency, payment_option):
        self.date, self.payment_date = self.parse_date(date_string)
        self.index = index

        self.client = client
        self.products = products
        self.currency = self.get_currency_symbol(currency)
        self.payment_details = self.get_payment_details(payment_option)

        self.total = sum(map(lambda p: p.calculate_total(), products))
        self.tax = sum(map(lambda p: p.calculate_tax(), products))
        self.total_tax_excl = self.total - self.tax

    def parse_date(self, date_string=""):
        # PayPal csv date format: mm/dd/yyyy
        date = datetime.datetime.strptime(date_string, "%m/%d/%Y")
        payment_date = date + datetime.timedelta(days=options.get("payment_date_delay"))
        return date, payment_date

    def get_currency_symbol(self, currency):
        currencies = {"EUR": "&euro;", "USD": "$", "JPY": "JPY"}
        return currencies[currency] if currency in currencies else ""

    def get_payment_details(self, option):
        key = option.lower()
        if key not in options["payment_options"]:
            logging.warning('Unknown payment option "{!s}"'.format(key))
            return ""
        return options["payment_options"][key]


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

    def get_invoice_html(self, invoice_data):
        """
        Returns a copy of the html data with template {{ identifiers }} replaced
        """
        html = list(self.html)
        for index, identifier in self.regex_matches:
            string_template = "{{ " + identifier + " }}"
            category, key = identifier.split("_", maxsplit=1)
            try:
                replace_value = invoice_data[category][key]
            except KeyError:
                replace_value = identifier
                logging.warning(
                    "Could not find matching value for {!s}".format(identifier)
                )
            if identifier in [
                "product_unit_price",
                "product_total_tax_excl",
                "total_discount",
                "total_excl_tax",
                "total_tax",
                "total_incl_tax",
            ]:
                replace_value = str(replace_value) + invoice_data["invoice"]["currency"]

            html[index] = html[index].replace(string_template, str(replace_value), 1)
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
