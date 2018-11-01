import logging

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
            logging.warning('Could not find product id {!s}, returning None'.format(identifier))
        return product
