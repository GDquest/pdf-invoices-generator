import logging


class Product:
    def __init__(self, identifier, price, quantity=1, VAT_rate=0.0):
        self.identifier = identifier
        self.price = price
        self.quantity = quantity
        self.VAT_rate = VAT_rate


class ProductsDatabase:
    """
    Stores a list of products.
    Retrieves them by ID or by name.
    """

    def __init__(self):
        self.products = []
        self.product_names = []

    def find_product(self, identifier):
        product = None
        if identifier.isdigit():
            index = int(identifier)
            product = self.products[index]
        else:
            for index, name in enumerate(self.product_names):
                if identifier != name:
                    return
                product = self.products[index]
        if not product:
            logging.warning(
                "Could not find product id {!s}, returning None".format(identifier)
            )
        return product

    def parse_database(self, path):
        products = []
        with open(path, "r") as csv_file:
            reader = csv.reader(csv_file)
            next(reader)
            for row in reader:
                product = Product(row[0], float(row[1]))
                products.append(product)
        return products
