import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class DataManager:

    def __init__(self):
        self._user = os.environ["SHEETY_USERNAME"]
        self._password = os.environ["SHEETY_PASSWORD"]
        self._prices_endpoint = os.environ["SHEETY_PRICES_ENDPOINT"]
        self._users_endpoint = os.environ["SHEETY_USERS_ENDPOINT"]
        self._authorization = HTTPBasicAuth(self._user, self._password)
        self.destination_data = {}
        self.customer_data = {}

    def get_destination_data(self):
        # Use the Sheety API to GET all the data in that sheet and print it out.
        response = requests.get(url=self._prices_endpoint, auth=self._authorization)
        data = response.json()
        self.destination_data = data["prices"]
        # import 'pretty print' and print the data out again using pprint() to see it more clearly formatted
        # pprint(data)
        return self.destination_data

    # In the DataManager Class make PUT request and use row 'id' from 'sheet_data'
    # to update the Google Sheet with the IATA codes
    def update_destination_codes(self):
        for city in self.destination_data:
            new_data = {
                "price": {
                    "iataCode": city["iataCode"]
                }
            }
            response = requests.put(
                url=f"{self._prices_endpoint}/{city['id']}",
                auth=self._authorization,
                json=new_data
            )
            print(response.text)

    def get_customer_emails(self):
        response = requests.get(url=self._users_endpoint, auth=self._authorization)
        data = response.json()
        # Name of spreadsheet 'tab' with the customer emails is/should be "users"
        self.customer_data = data["users"]
        return self.customer_data
