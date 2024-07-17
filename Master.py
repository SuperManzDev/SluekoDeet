import random
import string
import time
from datetime import datetime, timedelta
import os
import csv
from faker import Faker
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import init, Fore, Style

# Initialize colorama for cross-platform ANSI color support
init(autoreset=True)

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
    print(Fore.GREEN + f"Cards saved to {filename}")

# Function to save cards to CSV file
def save_to_csv(cards, filename):
    keys = cards[0].keys() if cards else []
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(cards)
    print(Fore.GREEN + f"Cards saved to {filename}")

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
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    try:
        driver.get(checkout_link)
        print(Fore.GREEN + "Opened checkout link successfully")
        
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.NAME, "cardnumber")))
        print(Fore.GREEN + "Found card number field")

        for card in cards:
            driver.find_element(By.NAME, "cardnumber").send_keys(card['Number'])
            driver.find_element(By.NAME, "exp-date").send_keys(card['Exp'])
            driver.find_element(By.NAME, "cvc").send_keys(card['CVV'])
            time.sleep(1)
            print(Fore.GREEN + f"Entered card details for {card['Type']}")

            driver.find_element(By.NAME, "submit-button").click()
            print(Fore.GREEN + "Submitted the form")
            time.sleep(5)
            print(Fore.GREEN + "Waited for submission")

    except NoSuchElementException as e:
        print(Fore.RED + f"Error: {e}")
    except TimeoutException as te:
        print(Fore.RED + f"Timeout error: {te}")
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

# Function to read card details from a file
def read_cards_from_file(filename):
    cards = []
    with open(filename, 'r') as f:
        card = {}
        for line in f:
            if line.startswith("Type:"):
                card['Type'] = line.split(": ")[1].strip()
            elif line.startswith("Number:"):
                card['Number'] = line.split(": ")[1].strip()
            elif line.startswith("CVV:"):
                card['CVV'] = line.split(": ")[1].strip()
            elif line.startswith("Exp:"):
                card['Exp'] = line.split(": ")[1].strip()
            elif line.strip() == "------------------------------":
                cards.append(card)
                card = {}
    return cards

# Function to organize cards into folders and validate them
def organize_and_validate_cards(cards):
    if not os.path.exists('UNORGANISED'):
        os.makedirs('UNORGANISED')
    if not os.path.exists('WORKING_CARDS'):
        os.makedirs('WORKING_CARDS')
    if not os.path.exists('TRASHED'):
        os.makedirs('TRASHED')

    working_cards = []
    trashed_cards = []

    for card in cards:
        if check_card_validity(card['Number']):
            working_cards.append(card)
        else:
            trashed_cards.append(card)

    save_to_txt(working_cards, 'WORKING_CARDS/working_cards.txt')
    save_to_txt(trashed_cards, 'TRASHED/trashed_cards.txt')
    save_to_txt(cards, 'UNORGANISED/unorganised_cards.txt')

    print(Fore.GREEN + f"Organized {len(cards)} cards into WORKING_CARDS and TRASHED folders.")
    print(Fore.CYAN + f"Number of working cards: {len(working_cards)}")
    print(Fore.RED + f"Number of trashed cards: {len(trashed_cards)}")

    return working_cards, trashed_cards

# Function to display the main menu and handle user input
def display_menu():
    github_link = "https://github.com/SuperManzDev"
    print(Fore.MAGENTA + r"""
  ____ ____ ____ ____ ____ ____ ____
 ||C |||r |||a |||p |||y |||G |||e ||
 ||__|||__|||__|||__|||__|||__|||__||
 |/__\|/__\|/__\|/__\|/__\|/__\|/__\|

Made with love and cats 🐾

Welcome to CRAPYGEN - Your Crappy Credit Card Generator and Tester

WHAT CAN I DO?

1. Generate fake credit card details
2. Save generated credit card information to a text file
3. Save generated credit card information to a CSV file
4. Interact with a provided Stripe checkout link to simulate payment form submissions
5. Generate fake names and addresses
6. Check validity of generated credit cards
7. Read card details from a text file and organize them
8. Exit
""")
    choice = input(Fore.YELLOW + "Enter the number of what you want to do (1-8): ").strip()
    return choice

# Function to handle card type selection
def select_card_types():
    card_types = []
    print(Fore.MAGENTA + r"""
SELECT CARD TYPES:

1. AMEX
2. Discover
3. MC (MasterCard)
4. Visa13 (Visa - 13 digits)
5. Visa16 (Visa - 16 digits)
6. All of the above

""")
    selection = input(Fore.YELLOW + "Enter card type(s) (comma separated numbers, e.g., 1,3): ").strip()
    if '6' in selection:
        card_types = list(CreditCardGenerator.CCDATA.keys())
    else:
        selections = selection.split(',')
        for sel in selections:
            if sel == '1':
                card_types.append('amex')
            elif sel == '2':
                card_types.append('discover')
            elif sel == '3':
                card_types.append('mc')
            elif sel == '4':
                card_types.append('visa13')
            elif sel == '5':
                card_types.append('visa16')
    return card_types

# Main function to run the program
def main():
    while True:
        choice = display_menu()

        if choice == '1':
            num_cards = int(input(Fore.YELLOW + "Enter number of cards to generate: ").strip())
            card_types = select_card_types()
            cards = generate_cards(card_types, num_cards)
            print(Fore.GREEN + f"Generated {len(cards)} credit card details.")

        elif choice == '2':
            if 'cards' in locals():
                save_to_txt(cards, 'generated_cards.txt')
            else:
                print(Fore.RED + "Please generate cards first (option 1).")

        elif choice == '3':
            if 'cards' in locals():
                save_to_csv(cards, 'generated_cards.csv')
            else:
                print(Fore.RED + "Please generate cards first (option 1).")

        elif choice == '4':
            checkout_link = input(Fore.YELLOW + "Enter the Stripe checkout link: ").strip()
            num_cards = int(input(Fore.YELLOW + "Enter number of cards to submit: ").strip())
            card_types = select_card_types()
            cards = generate_cards(card_types, num_cards)
            interact_with_stripe_checkout(checkout_link, cards)

        elif choice == '5':
            num_entries = int(input(Fore.YELLOW + "Enter number of fake names and addresses to generate: ").strip())
            fake_info = generate_fake_info(num_entries)
            for info in fake_info:
                print(Fore.GREEN + f"Name: {info['Name']}, Address: {info['Address']}, City: {info['City']}, State: {info['State']}, Zipcode: {info['Zipcode']}")

        elif choice == '6':
            card_number = input(Fore.YELLOW + "Enter card number to check validity: ").strip()
            if check_card_validity(card_number):
                print(Fore.GREEN + "Card number is valid.")
            else:
                print(Fore.RED + "Card number is invalid.")

        elif choice == '7':
            filename = input(Fore.YELLOW + "Enter the filename to read card details from: ").strip()
            cards = read_cards_from_file(filename)
            working_cards, trashed_cards = organize_and_validate_cards(cards)
            print(Fore.CYAN + f"Number of working cards: {len(working_cards)}")
            print(Fore.RED + f"Number of trashed cards: {len(trashed_cards)}")

            # Ask user if they want to delete the folders and create new cards
            delete_choice = input(Fore.YELLOW + "Do you want to delete the non-working/organized/working cards and remake new ones? (y/n): ").strip().lower()
            if delete_choice == 'y':
                if os.path.exists('UNORGANISED'):
                    os.remove('UNORGANISED/unorganised_cards.txt')
                    os.rmdir('UNORGANISED')
                if os.path.exists('WORKING_CARDS'):
                    os.remove('WORKING_CARDS/working_cards.txt')
                    os.rmdir('WORKING_CARDS')
                if os.path.exists('TRASHED'):
                    os.remove('TRASHED/trashed_cards.txt')
                    os.rmdir('TRASHED')
                print(Fore.GREEN + "Deleted existing cards.")

        elif choice == '8':
            print(Fore.MAGENTA + "Thank you for using CRAPYGEN. Goodbye!")
            break

        else:
            print(Fore.RED + "Invalid input. Please enter a number from 1 to 8.")

if __name__ == "__main__":
    main()
