import codecs
import csv
from .config import Config


class Client:
    def __init__(self, name, address, country_code, vat_number=""):
        self.name = name
        self.address = address
        self.country_code = country_code
        self.vat_number = vat_number


class ClientList(dict):
    """Generates and stores a dictionary of Client objects parsed from csv
    Stores each client as id: Client pairs, so you can get clients by key.
    """

    def __init__(self, csv_file_path="", *args, **kwargs):
        """
        Keyword Arguments:
        csv_file_path -- (default ""): path to the csv file that serves as the list of clients
        """
        super(ClientList, self).__init__(*args, **kwargs)
        self.csv_file_path = csv_file_path

    # TODO: Check named keywords from the CSV file header
    def parse_csv(self, config: Config) -> None:
        with codecs.open(self.csv_file_path, "r", encoding="utf-8") as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=",")
            for id, row in enumerate(csv_reader):
                self[row["name"]] = Client(
                    name=row["name"],
                    address=row["address"],
                    country_code=row["country_code"],
                    vat_number=row["vat_number"],
                )
