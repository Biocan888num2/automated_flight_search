import time
from datetime import datetime, timedelta
from data_manager import DataManager
from flight_search import FlightSearch
from flight_data import find_cheapest_flight
from notification_manager import NotificationManager
import smtplib

# Set your origin airport
ORIGIN_CITY_IATA = "YUL"
# Arrow symbol
UP_DOWN = "🔻"

# ==================== Set up the Flight Search ====================

data_manager = DataManager()
sheet_data = data_manager.get_destination_data()
flight_search = FlightSearch()
notification_manager = NotificationManager()

# ==================== Update the Airport Codes in Google Sheet ====================

for row in sheet_data:
    if row["iataCode"] == "":
        row["iataCode"] = flight_search.get_destination_code(row["city"])
        # slowing down requests to avoid rate limit
        time.sleep(2)
print(f"sheet_data:\n {sheet_data}")

data_manager.destination_data = sheet_data
data_manager.update_destination_codes()

# ==================== Retrieve your customer emails ====================

customer_data = data_manager.get_customer_emails()
# Verify the name of email column in sheet
customer_email_list = [row["whatIsYourEmail?"] for row in customer_data]
# print(f"Your email list includes {customer_email_list}")

# ==================== Search for direct flights  ====================
tomorrow = datetime.now() + timedelta(days=1)
six_month_from_today = datetime.now() + timedelta(days=(6 * 30))

for destination in sheet_data:
    print(f"\nGetting flights for {destination['city']}...")
    flights = flight_search.check_flights(
        ORIGIN_CITY_IATA,
        destination["iataCode"],
        from_time=tomorrow,
        to_time=six_month_from_today
    )
    cheapest_flight = find_cheapest_flight(flights)
    print(f"{destination['city']}: ${cheapest_flight.price} CAD")
    # Slowing down requests to avoid rate limit
    time.sleep(2)

    # ==================== Search for indirect flight if N/A ====================
    if cheapest_flight.price == "N/A":
        print(f"No direct flight to {destination['city']}. Looking for indirect flights...")
        stopover_flights = flight_search.check_flights(
            ORIGIN_CITY_IATA,
            destination["iataCode"],
            from_time=tomorrow,
            to_time=six_month_from_today,
            is_direct=False
        )
        cheapest_flight = find_cheapest_flight(stopover_flights)
        print(f"Cheapest indirect flight price is: ${cheapest_flight.price} CAD")

    # ==================== Send Notifications and Emails  ====================
    if cheapest_flight.price != "N/A" and cheapest_flight.price < destination["lowestPrice"]:
        print(f"Lower price flight found to {destination['city']}!")

        if cheapest_flight.stops == 0:
            message_body = (f"{UP_DOWN} Low price alert!! ONLY ${cheapest_flight.price} CAD, for a direct flight from "
                            f"{cheapest_flight.origin_airport} to {cheapest_flight.destination_airport}. "
                            f"Deal available from {cheapest_flight.out_date} until {cheapest_flight.return_date}.")

        else:
            message_body = (f"{UP_DOWN} Low price alert!! ONLY ${cheapest_flight.price} CAD, to fly from "
                            f"{cheapest_flight.origin_airport} to {cheapest_flight.destination_airport}. "
                            f"There will be a total of {cheapest_flight.stops} connecting flight(s)."
                            f"Deal available from {cheapest_flight.out_date} until {cheapest_flight.return_date}.")

        notification_manager.send_sms(
            message_body=message_body
        )

        # SMS not working? Try whatsapp instead.
        # notification_manager.send_whatsapp(
        #     message_body=f"Low price alert! Only £{cheapest_flight.price} to fly "
        #                  f"from {cheapest_flight.origin_airport} to {cheapest_flight.destination_airport}, "
        #                  f"on {cheapest_flight.out_date} until {cheapest_flight.return_date}."
        # )

        # Send emails to everyone on the list
        notification_manager.send_emails(
            email_list=customer_email_list,
            email_body=message_body
        )
