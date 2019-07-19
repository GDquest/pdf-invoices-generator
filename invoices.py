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

DEBUG = True
# Placeholders, required for GDquest
EUROPE_COUNTRY_CODES = ['IRL']
MENTION_AUTOLIQUIDATION = 'Autoliquidation de la TVA, article 259 du Code Général des Impôts'
MENTION_EXONERATION = 'Éxonération de TVA, art. 262 I du Code Général des Impôts'

def get_config(path):
    with open(path) as data:
        return json.loads(data.read())

# Setting up main data variables
data = get_config('./data/config.json')
config = data['config']
company = data['company']
options = data['settings']


def parse_invoice_date(date_string):
    date, payment_date = None, None

    # PayPal csv date format: dd/mm/yyyy
    date = datetime.datetime.strptime(date_string, '%d/%m/%Y')
    payment_date = date + datetime.timedelta(days=options['payment_date_delay'])

    return date, payment_date


def parse_html_template(html_doc):
    invoice_template, re_matches = [], []

    line_id = 0
    for line in html_doc:
        match = re.match(r'.+{{ (.*) }}', line)
        if match:
            identifier = match.group(1)

            # Pre-replace company details
            if identifier.startswith('company'):
                category, key = identifier.split('_', maxsplit=1)
                string_template = '{{ ' + identifier + ' }}'
                line = line.replace(string_template, company[key], 1)
            else:
                re_matches.append((line_id, match.group(1)))
        invoice_template.append(line)
        line_id += 1

    return invoice_template, re_matches


# TODO: currently doesn't work, create a working product DB object
def get_product_from_id(product_id):
    return {}

    product = {}

    if product_id.isdigit():
        index = int(product_id)
        product = product_database[index]
    else:
        for index, name in enumerate(product_names):
            if product_id == name:
                product = product_database[index]

    if not product:
        logging.warning('Could not find product id {!s}, returning None'.format(product_id))
    return product


def convert_invoice_to_html(invoice_data, invoice_template, re_matches):
    invoice_template_copy = list(invoice_template)

    # PRODUCT
    # TODO: to support multiple products, parse products in a separate function
    # Use a separate html template (one <tr> per product)
    # return the full list of <tr> as a string to replace {{ product_rows }}
    total_tax_excl, total_VAT = 0, 0

    product_data = invoice_data['product']
    amount = invoice_data['product']['quantity']
    product = get_product_from_id(product_data['identifier'])
    if not product:
        product = {
            'name': invoice_data['product']['identifier'],
            'VAT_rate': 0,
            'unit_price': float(invoice_data['product']['price'].replace(',', '.'))
        }

    VAT_rate = 0 if options['no_VAT'] == True else product['VAT_rate']
    product_cost_tax_excl = product['unit_price'] * amount
    product_VAT = product_cost_tax_excl * VAT_rate

    total_tax_excl += product_cost_tax_excl
    total_VAT += product_VAT

    # TODO: refactor invoice into object
    invoice_data['product']['name'] = product['name']
    invoice_data['product']['unit_price'] = product['unit_price']
    invoice_data['product']['VAT_rate'] = VAT_rate
    invoice_data['product']['total_tax_excl'] = product_cost_tax_excl

    invoice_data['total'] = {}
    invoice_data['total']['discount'] = 0
    invoice_data['total']['excl_tax'] = total_tax_excl
    invoice_data['total']['tax'] = total_VAT
    invoice_data['total']['incl_tax'] = total_tax_excl + total_VAT

    # REPLACE VALUES
    for index, identifier in re_matches:
        string_template = '{{ ' + identifier + ' }}'
        category, key = identifier.split('_', maxsplit=1)
        try:
            replace_value = invoice_data[category][key]
        except:
            replace_value = identifier
            logging.warning('Could not find matching value for {!s}'.format(identifier))
        if identifier in ['product_unit_price', 'product_total_tax_excl', 'total_discount', 'total_excl_tax', 'total_tax', 'total_incl_tax']:
            replace_value = str(replace_value) + invoice_data['invoice']['currency']
        invoice_template_copy[index] = invoice_template_copy[index].replace(string_template, str(replace_value), 1)
    return invoice_template_copy


def get_currency_symbol(currency):
    # USE HTML NAME CODES
    currencies = {
        'EUR': '&euro;',
        'USD': '$',
        'JPY': ''
    }
    return currencies[currency]


def get_payment_details(option):
    option = option.lower()
    if not option in options['payment_options'].keys():
        return ''
    return options['payment_options'][option]


def prepare_invoice_data():
    db = []
    file_path = config['database_path']
    try:
        with codecs.open(file_path, 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            header = next(csv_reader)

            for index, row in enumerate(csv_reader):
                invoice_index = index + 1
                date, payment_date = parse_invoice_date(row[0])
                currency = row[1] if row[1] else options['default_currency']
                invoice_data = {
                    'client': {
                        'name': row[4],
                        'country_code': row[5],
                        'VAT_number': row[6],
                        'address': row[7]
                    },
                    'product': {
                        'identifier': row[2],
                        'price': row[3],
                        'quantity': 1
                    },
                    'invoice': {
                        'index': "{:04d}".format(invoice_index),
                        'date': date.strftime(config['date_format']),
                        'currency': get_currency_symbol(currency)
                    },
                    'mentions': {
                        'vat': MENTION_AUTOLIQUIDATION if row[5] in EUROPE_COUNTRY_CODES else MENTION_EXONERATION
                    },
                    'payment': {
                        'date': payment_date.strftime(config['date_format']),
                        'details': get_payment_details(row[8])
                    }
                }
                db.append(invoice_data)
                if DEBUG and invoice_index >= options['debug']['csv_max_parsed_rows']:
                    break
    except FileNotFoundError:
        logging.warning('File {} not found'.format(file_path))
    except OSError:
        logging.warning('Could not open the file')
    return db


def parse_product_database(path):
    products = []
    with open(path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader)

        product = {}
        for row in reader:
            product['name'] = row[0]
            product['unit_price'] = float(row[1])
            product['VAT_rate'] = float(row[2]) / 100
            products.append(product)
    return products


def set_up_output_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
    css_output_path = os.path.join(path, 'style.css')
    if not os.path.exists(css_output_path):
        shutil.copy('template/style.css', css_output_path)
    img_output_path = os.path.join(path, 'img')
    if not os.path.exists(img_output_path):
        shutil.copytree('img', img_output_path)


def generate_html_files(invoices_database, output_path, invoice_template, re_matches):
    for invoice in invoices_database:
        invoice_as_html = convert_invoice_to_html(invoice, invoice_template, re_matches)

        export_date = datetime.datetime.strptime(invoice['invoice']['date'], config['date_format'])
        export_date_string = export_date.strftime('%Y-%m-%d')
        client_name = invoice['client']['name'].replace(' ', '-').lower()

        file_name = '{}-{}.html'.format(invoice['invoice']['index'], client_name)
        export_path = '{}/{}-{}'.format(output_path, export_date_string, file_name)
        with codecs.open(export_path, 'w', encoding='utf-8') as invoice_file:
            invoice_file.writelines(invoice_as_html)


def render_pdfs(html_output_folder, pdf_output_folder):
    if not os.path.exists(pdf_output_folder):
        os.makedirs(pdf_output_folder)

    for filename in os.listdir(html_output_folder):
        name = os.path.splitext(filename)[0]
        html_filepath = os.path.join(html_output_folder, filename)
        subprocess.run('wkhtmltopdf {} {}.pdf'.format(html_filepath, os.path.join(pdf_output_folder, name)))


def main():
    options['payment_options']['paypal'] = 'PayPal address: ' + company['paypal']
    with codecs.open('template/bank-details.html', 'r', encoding='utf-8') as html_doc:
        options['payment_options']['wire'] = html_doc.read()

    db_file_name = os.path.splitext(os.path.basename(config['database_path']))[0]
    output_folder = os.path.join(config['output_path'], db_file_name)
    html_output_folder = os.path.join(output_folder, 'html')
    pdf_output_folder = os.path.join(output_folder, 'pdf')

    locale.setlocale(locale.LC_ALL, '')
    # product_database = parse_product_database('./data/products_database.csv')

    # TODO: turn InvoiceTemplate into an object you can pass around
    invoice_template, re_matches = [], []
    with codecs.open(config['html_template_path'], 'r', encoding='utf-8') as html_doc:
        invoice_template, re_matches = parse_html_template(html_doc)
        if not invoice_template:
            logging.error('Could not load the invoice template. Aborting operation.')
        if not re_matches:
            logging.error('Missing {{ indentifier }} templates to replace in the html template. Aborting operation.')
    if not invoice_template:
        return

    # Main logic
    invoices_database = prepare_invoice_data()
    set_up_output_directory(html_output_folder)
    generate_html_files(invoices_database, html_output_folder, invoice_template, re_matches)
    render_pdfs(html_output_folder, pdf_output_folder)

if __name__ == '__main__':
    main()
