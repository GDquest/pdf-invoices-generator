import logging


class Product:
    def __init__(self, identifier, price, quantity=1, tax_rate=0.0):
        self.identifier = identifier
        self.price = price
        self.quantity = quantity
        self.tax_rate = tax_rate

        self.tax = self._calculate_tax()
        self.price_without_tax = self.price - self.tax

    def _calculate_tax(self) -> float:
        return round(self.price - (self.price / (1.0 + self.tax_rate)), 2)

    def calculate_total_without_tax(self) -> float:
        return self.calculate_total() - self.tax * self.quantity

    def calculate_total(self) -> float:
        return self.price * self.quantity

    def get_tax_rate_as_string(self) -> str:
        return "{}%".format(round(self.tax_rate * 100, 0))


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

    # # TODO: currently doesn't work, create a working product DB object
    # def get_product_from_id(product_id):
    #     return {}

    #     product = {}

    #     if product_id.isdigit():
    #         index = int(product_id)
    #         product = product_database[index]
    #     else:
    #         for index, name in enumerate(product_names):
    #             if product_id == name:
    #                 product = product_database[index]

    #     if not product:
    #         logging.warning(
    #             "Could not find product id {!s}, returning None".format(product_id)
    #         )
    #     return product
