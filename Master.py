import random
import string
import time
from datetime import datetime, timedelta
import os
import csv
from faker import Faker  # Import Faker for generating random names and addresses
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Credit card generator class
class CreditCardGenerator:
    CCDATA = {
        'amex': {'len_num': 15, 'len_cvv': 4, 'pre': [34, 37], 'remaining': 13},
        'discover': {'len_num': 16, 'len_cvv': 3, 'pre': [6001], 'remaining': 12},
        'mc': {'len_num': 16, 'len_cvv': 3, 'pre': [51, 55], 'remaining': 14},
        'visa13': {'len_num': 13, 'len_cvv': 3, 'pre': [4], 'remaining': 12},
        'visa16': {'len_num': 16, 'len_cvv': 3, 'pre': [4], 'remaining': 15},
    }

    def __init__(self, card_type):
        if card_type.lower() not in self.CCDATA:
            raise ValueError("Invalid card type")
        self.cc_type = card_type.lower()
        self.cc_num = None
        self.cc_cvv = None
        self.cc_exp = None
        self.generate_card()

    def generate_card(self):
        self.generate_cc_num()
        self.generate_cc_cvv()
        self.generate_cc_exp()

    def generate_cc_exp(self):
        # Generate expiration date 1 to 5 years from now
        current_date = datetime.now()
        exp_date = current_date + timedelta(days=random.randint(365, 1825))
        self.cc_exp = exp_date

    def generate_cc_cvv(self):
        self.cc_cvv = ''.join(random.choices(string.digits, k=self.CCDATA[self.cc_type]['len_cvv']))

    def generate_cc_num(self):
        pre = random.choice(self.CCDATA[self.cc_type]['pre'])
        remaining_digits = ''.join(random.choices(string.digits, k=self.CCDATA[self.cc_type]['remaining']))
        self.cc_num = str(pre) + remaining_digits

    def get_card_info(self):
        return {
            'Type': self.cc_type,
            'Number': self.cc_num,
            'CVV': self.cc_cvv,
            'Exp': self.cc_exp.strftime("%m-%Y")
        }

# Function to generate multiple cards of selected types
def generate_cards(card_types, num_cards):
    cards = []
    for _ in range(num_cards):
        card_type = random.choice(card_types)
        card = CreditCardGenerator(card_type)
        cards.append(card.get_card_info())
    return cards

# Function to save cards to text file
def save_to_txt(cards, filename):
    with open(filename, 'w') as f:
        for card in cards:
            f.write(f"Type: {card['Type']}\n")
            f.write(f"Number: {card['Number']}\n")
            f.write(f"CVV: {card['CVV']}\n")
            f.write(f"Exp: {card['Exp']}\n")
            f.write("------------------------------\n")
    print(f"Cards saved to {filename}")

# Function to save cards to CSV file
def save_to_csv(cards, filename):
    keys = cards[0].keys() if cards else []
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(cards)
    print(f"Cards saved to {filename}")

# Function to generate fake names and addresses
def generate_fake_info(num_entries):
    fake = Faker()
    entries = []
    for _ in range(num_entries):
        entries.append({
            'Name': fake.name(),
            'Address': fake.address(),
            'City': fake.city(),
            'State': fake.state(),
            'Zipcode': fake.zipcode(),
        })
    return entries

# Function to interact with Stripe checkout link using Selenium
def interact_with_stripe_checkout(checkout_link, cards):
    # Setup Selenium
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    try:
        driver.get(checkout_link)
        print("Opened checkout link successfully")
        
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.NAME, "cardnumber")))
        print("Found card number field")

        # Fill in card details
        for card in cards:
            driver.find_element(By.NAME, "cardnumber").send_keys(card['Number'])
            driver.find_element(By.NAME, "exp-date").send_keys(card['Exp'])
            driver.find_element(By.NAME, "cvc").send_keys(card['CVV'])
            time.sleep(1)  # Add a small delay between entering each field
            print(f"Entered card details for {card['Type']}")

            # Submit the form (you may need to adjust this based on the specific Stripe form)
            driver.find_element(By.NAME, "submit-button").click()
            print("Submitted the form")
            time.sleep(5)  # Wait for submission, adjust as necessary
            print("Waited for submission")

    except NoSuchElementException as e:
        print(f"Error: {e}")
    except TimeoutException as te:
        print(f"Timeout error: {te}")
    finally:
        driver.quit()

# Function to check validity of generated credit cards (Luhn algorithm)
def check_card_validity(card_number):
    def luhn_algorithm(card_number):
        digits = [int(x) for x in card_number]
        odd_sum = sum(digits[-1::-2])
        even_sum = sum(sum(divmod(2 * d, 10)) for d in digits[-2::-2])
        return (odd_sum + even_sum) % 10 == 0

    return luhn_algorithm(card_number)

# Function to display the main menu and handle user input
def display_menu():
    github_link = "https://github.com/SuperManzDev"
    print(r"""
  ____ ____ ____ ____ ____ ____ ____
 ||C |||r |||a |||p |||y |||G |||e ||
 ||__|||__|||__|||__|||__|||__|||__||
 |/__\|/__\|/__\|/__\|/__\|/__\|/__\|

Made with love and cats 🐾

Welcome to CRAPYGEN - Your Crappy Credit Card Generator and Tester

WHAT CAN I DO?

1. Generate fake credit card details (number, CVV, expiration date) for testing purposes.
2. Save generated credit card information to a text file.
3. Save generated credit card information to a CSV file.
4. Interact with a provided Stripe checkout link to simulate payment form submissions.
5. Generate fake names and addresses.
6. Check validity of generated credit cards.
7. Read credit card details from a text file and check their validity.
8. Exit

About me: {}
""".format(github_link))
    choice = input("Enter the number of what you want to do (1-8): ").strip()
    return choice

# Function to handle card type selection
def select_card_types():
    card_types = []
    print("""
SELECT CARD TYPES:

1. AMEX
2. Discover
3. MC (MasterCard)
4. Visa13
5. Visa16
6. Mixed (Select random types)
""")
    while True:
        choice = input("Enter card type (1-6) or 'done' to finish: ").strip().lower()
        if choice == '1':
            card_types.append('amex')
        elif choice == '2':
            card_types.append('discover')
        elif choice == '3':
            card_types.append('mc')
        elif choice == '4':
            card_types.append('visa13')
        elif choice == '5':
            card_types.append('visa16')
        elif choice == '6':
            card_types = random.choices(['amex', 'discover', 'mc', 'visa13', 'visa16'], k=random.randint(1, 5))
        elif choice == 'done':
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 6 or 'done'.")
    return card_types

# Function to read credit card details from a text file
def read_cards_from_txt(filename):
    cards = []
    with open(filename, 'r') as f:
        card = {}
        for line in f:
            if "Type:" in line:
                card['Type'] = line.split(":")[1].strip()
            elif "Number:" in line:
                card['Number'] = line.split(":")[1].strip()
            elif "CVV:" in line:
                card['CVV'] = line.split(":")[1].strip()
            elif "Exp:" in line:
                card['Exp'] = line.split(":")[1].strip()
            elif "------------------------------" in line:
                cards.append(card)
                card = {}
    return cards

# Main function
def main():
    while True:
        choice = display_menu()

        if choice == '1':
            card_types = select_card_types()
            num_cards = int(input("Enter the total number of cards to generate: "))
            try:
                cards = generate_cards(card_types, num_cards)
                for card in cards:
                    print(card)  # Print generated card details
            except ValueError as ve:
                print(f"Error: {ve}")

        elif choice == '2':
            card_types = select_card_types()
            num_cards = int(input("Enter the total number of cards to generate: "))
            filename = input("Enter the filename to save (without extension): ").strip() + ".txt"
            try:
                cards = generate_cards(card_types, num_cards)
                save_to_txt(cards, filename)
            except ValueError as ve:
                print(f"Error: {ve}")

        elif choice == '3':
            card_types = select_card_types()
            num_cards = int(input("Enter the total number of cards to generate: "))
            filename = input("Enter the filename to save (without extension): ").strip() + ".csv"
            try:
                cards = generate_cards(card_types, num_cards)
                save_to_csv(cards, filename)
            except ValueError as ve:
                print(f"Error: {ve}")

        elif choice == '4':
            checkout_link = input("Enter the Stripe checkout link: ").strip()
            card_types = select_card_types()
            num_cards = int(input("Enter the number of cards to use for interaction: "))
            try:
                cards = generate_cards(card_types, num_cards)
                interact_with_stripe_checkout(checkout_link, cards)
            except ValueError as ve:
                print(f"Error: {ve}")

        elif choice == '5':
            num_entries = int(input("Enter the number of fake names and addresses to generate: "))
            entries = generate_fake_info(num_entries)
            for entry in entries:
                print(entry)  # Print generated fake name and address

        elif choice == '6':
            card_number = input("Enter the credit card number to check validity: ").strip()
            if check_card_validity(card_number):
                print("The credit card number is valid.")
            else:
                print("The credit card number is invalid.")

        elif choice == '7':
            filename = input("Enter the filename to read (with extension): ").strip()
            if not os.path.isfile(filename):
                print("File not found. Please check the filename and try again.")
            else:
                cards = read_cards_from_txt(filename)
                for card in cards:
                    validity = "valid" if check_card_validity(card['Number']) else "invalid"
                    print(f"Card {card['Number']} is {validity}.")

        elif choice == '8':
            print("Exiting CRAPYGEN. Goodbye!")
            break

        else:
            print("Invalid choice. Please enter a number from 1 to 8.")

if __name__ == "__main__":
    main()
