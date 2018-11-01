import logging

# TODO: to support multiple products, parse products in a separate function
# Use a separate html template (one <tr> per product)
# return the full list of <tr> as a string to replace {{ product_rows }}
class Invoice:
    def __init__(self, html_template, index, client, product, date_string, currency, payment_option):
        self.html_template = html_template
        self.template_copy = self.html_template.get_copy()
        self.invoice_date, self.payment_date = self.parse_date(date_string)
        self.index = index
        self.data = {
            'client': {
                'name': client.name,
                'country_code': client.country_code,
                'VAT_number': client.VAT_number,
                'address': client.address
            },
            'product': {
                'name': product.name,
                'quantity': product.quantity,
                'unit_price': product.unit_price,
                'VAT_rate': product.VAT_rate,
                'total_tax_excl': product.total_tax_excl
            },
            'invoice': {
                'index': "{:04d}".format(self.index),
                'date': self.invoice_date,
                'currency': self.get_currency_symbol(currency)
            },
            'payment': {
                'date': self.payment_date,
                'details': self.get_payment_details(payment_option)
            },
            'total': {
                'discount': 0,
                'excl_tax': self.product.total_tax_excl,
                'tax': self.product,
                'incl_tax': self.product.total_tax_excl + self.product.total_tax
            }
        }

    def parse_date(self):
        # PayPal csv date format: mm/dd/yyyy
        self.data['date'] = datetime.datetime.strptime(date_string, '%m/%d/%Y')
        self.data['payment_date'] = date + datetime.timedelta(days=options['payment_date_delay'])

    def calculate_total(self):
        total_tax_excl += product_cost_tax_excl
        total_VAT += product_VAT

    def render_to_html(self, invoice_data, company):
        for index, identifier in self.html_template.regex_matches:
            string_template = '{{ ' + identifier + ' }}'
            category, key = identifier.split('_', maxsplit=1)
            try:
                replace_value = self.data[category][key]
            except:
                replace_value = identifier
                logging.warning('Could not find matching value for {!s}'.format(identifier))
            if identifier in ['product_unit_price', 'product_total_tax_excl', 'total_discount', 'total_excl_tax', 'total_tax', 'total_incl_tax']:
                replace_value = str(replace_value) + self.data['invoice']['currency']
            self.template_copy[index] = invoice_template_copy[index].replace(string_template, str(replace_value), 1)

    def get_currency_symbol(self, currency):
        currencies = {
            'EUR': '&euro;',
            'USD': '$',
            'JPY': 'JPY'
        }
        return currencies[currency]

    def get_payment_details(self, option):
        option_string = option.lower()
        if not option_string in options['payment_options'].keys():
            logging.warning('Unknown payment option "{!s}"'.format(option_string))
            return ''
        return options['payment_options'][option_string]


class InvoiceTemplate:
    """
    Parses an html template file and stores a list of
    regex-matched template elements {{ identifier }}
    Finds, replaces template elements, parses and writes html to disk
    """
    def __init__(self, template_path, company_details):
        self.company = company_details
        self.template_path = template_path
        self.regex_matches = []
        self.html_doc = []

    def parse_html_template(self):
        line_id = 0
        for line in self.invoice_as_html:
            match = re.match(r'.+{{ (.*) }}', line)
            if not match:
                continue
            identifier = match.group(1)

            # Pre-replace company details
            if identifier.startswith('company'):
                category, key = identifier.split('_', maxsplit=1)
                string_template = '{{ ' + identifier + ' }}'
                line = line.replace(string_template, company[key], 1)
            else:
                self.regex_matches.append((line_id, match.group(1)))
                self.html_doc.append(line)
                line_id += 1
