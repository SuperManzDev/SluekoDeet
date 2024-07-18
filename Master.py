import random
import string
import os
import csv
import time
from datetime import datetime, timedelta
from faker import Faker
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import init, Fore, Style
import shutil

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
        """
        Initialize a credit card generator object for a specific card type.

        Args:
        - card_type (str): Type of credit card ('amex', 'discover', 'mc', 'visa13', 'visa16')
        """
        if card_type.lower() not in self.CCDATA:
            raise ValueError("Invalid card type")
        self.cc_type = card_type.lower()
        self.cc_num = None
        self.cc_cvv = None
        self.cc_exp = None
        self.generate_card()

    def generate_card(self):
        """
        Generate a credit card number, CVV, and expiration date.
        """
        self.generate_cc_num()
        self.generate_cc_cvv()
        self.generate_cc_exp()

    def generate_cc_exp(self):
        """
        Generate a random expiration date for the credit card.
        """
        current_date = datetime.now()
        exp_date = current_date + timedelta(days=random.randint(365, 1825))
        self.cc_exp = exp_date

    def generate_cc_cvv(self):
        """
        Generate a CVV number for the credit card.
        """
        self.cc_cvv = ''.join(random.choices(string.digits, k=self.CCDATA[self.cc_type]['len_cvv']))

    def generate_cc_num(self):
        """
        Generate a valid credit card number based on the selected card type.
        """
        pre = random.choice(self.CCDATA[self.cc_type]['pre'])
        remaining_digits = ''.join(random.choices(string.digits, k=self.CCDATA[self.cc_type]['remaining']))
        self.cc_num = str(pre) + remaining_digits

    def get_card_info(self):
        """
        Return the generated credit card information.

        Returns:
        - dict: Dictionary containing 'Type', 'Number', 'CVV', 'Exp' keys.
        """
        return {
            'Type': self.cc_type,
            'Number': self.cc_num,
            'CVV': self.cc_cvv,
            'Exp': self.cc_exp.strftime("%m-%Y")
        }

# Function to generate multiple cards of selected types
def generate_cards(card_types, num_cards):
    """
    Generate multiple credit cards of specified types.

    Args:
    - card_types (list): List of card types to generate ('amex', 'discover', 'mc', 'visa13', 'visa16')
    - num_cards (int): Number of credit cards to generate

    Returns:
    - list: List of dictionaries containing credit card information
    """
    cards = []
    for _ in range(num_cards):
        card_type = random.choice(card_types)
        card = CreditCardGenerator(card_type)
        cards.append(card.get_card_info())
    return cards

# Function to save cards to text file
def save_to_txt(cards, filename):
    """
    Save generated credit card information to a text file.

    Args:
    - cards (list): List of dictionaries containing credit card information
    - filename (str): Name of the text file to save
    """
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
    """
    Save generated credit card information to a CSV file.

    Args:
    - cards (list): List of dictionaries containing credit card information
    - filename (str): Name of the CSV file to save
    """
    keys = cards[0].keys() if cards else []
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(cards)
    print(Fore.GREEN + f"Cards saved to {filename}")

# Function to generate fake names and addresses
def generate_fake_info(num_entries):
    """
    Generate fake names and addresses using the Faker library.

    Args:
    - num_entries (int): Number of fake names and addresses to generate

    Returns:
    - list: List of dictionaries containing fake name and address information
    """
    fake = Faker()
    entries = []
    for _ in range(num_entries):
        name = fake.name()
        street_address = fake.street_address()
        city = fake.city()
        state = fake.state_abbr()
        zipcode = fake.zipcode()

        # Format the address for readability
        address = f"{name}\n{street_address}\n{city}, {state} {zipcode}"

        entries.append({
            'Name': name,
            'Address': address,
            'City': city,
            'State': state,
            'Zipcode': zipcode,
        })

    return entries

# Function to save entries to text file under 'addresses' folder
def save_addresses_to_txt(entries, folder_name, single_file=False):
    """
    Save generated fake names and addresses to text files under 'addresses' folder.

    Args:
    - entries (list): List of dictionaries containing fake name and address information
    - folder_name (str): Name of the folder to save the text files
    - single_file (bool): Flag to determine if all addresses should be saved in a single file
    """
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    if single_file:
        filename = os.path.join(folder_name, 'all_addresses.txt')
        with open(filename, 'w') as f:
            for entry in entries:
                f.write(f"Name: {entry['Name']}\n")
                f.write(f"Address:\n{entry['Address']}\n")
                f.write(f"City: {entry['City']}\n")
                f.write(f"State: {entry['State']}\n")
                f.write(f"Zipcode: {entry['Zipcode']}\n")
                f.write("------------------------------\n")
        print(Fore.GREEN + f"Saved all addresses to {filename}")
    else:
        for idx, entry in enumerate(entries):
            filename = os.path.join(folder_name, f'address_{idx + 1}.txt')
            with open(filename, 'w') as f:
                f.write(f"Name: {entry['Name']}\n")
                f.write(f"Address:\n{entry['Address']}\n")
                f.write(f"City: {entry['City']}\n")
                f.write(f"State: {entry['State']}\n")
                f.write(f"Zipcode: {entry['Zipcode']}\n")
                f.write("------------------------------\n")
            print(Fore.GREEN + f"Saved address {idx + 1} to {filename}")

# Function to interact with Stripe checkout link using Selenium
def interact_with_stripe_checkout(checkout_link, cards):
    """
    Interact with a Stripe checkout link using Selenium WebDriver.

    Args:
    - checkout_link (str): URL of the Stripe checkout link
    - cards (list): List of dictionaries containing credit card information
    """
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

            try:
                driver.find_element(By.CLASS_NAME, "Message-title")
                print(Fore.GREEN + "Payment successful!")
            except NoSuchElementException:
                print(Fore.RED + "Payment failed")
            
            driver.refresh()
            time.sleep(5)

    except TimeoutException:
        print(Fore.RED + "Timeout occurred during interaction")
    
    finally:
        driver.quit()
        print(Fore.GREEN + "Browser closed")

# Function to check validity of credit card number using Luhn algorithm
def check_card_validity(card_number):
    """
    Check the validity of a credit card number using the Luhn algorithm.

    Args:
    - card_number (str): Credit card number to validate

    Returns:
    - bool: True if the card number is valid, False otherwise
    """
    def luhn_algorithm(card_number):
        digits = list(map(int, card_number))
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits + sum(divmod(2 * d, 10) for d in even_digits))
        return checksum % 10

    try:
        if luhn_algorithm(card_number) == 0:
            return True
        else:
            return False
    except ValueError:
        return False

# Function to organize card details from text file into folders
def organize_cards(filename):
    """
    Organize card details from a text file into folders.

    Args:
    - filename (str): Name of the text file containing card details
    """
    working_folder = 'WORKING_CARDS'
    trash_folder = 'TRASHED'
    unorganized_folder = 'UNORGANISED'

    if not os.path.exists(working_folder):
        os.makedirs(working_folder)
    if not os.path.exists(trash_folder):
        os.makedirs(trash_folder)
    if not os.path.exists(unorganized_folder):
        os.makedirs(unorganized_folder)

    with open(filename, 'r') as f:
        for line in f:
            if line.startswith("Number:"):
                card_number = line.split(":")[1].strip()
                if check_card_validity(card_number):
                    move_to_folder(filename, working_folder)
                else:
                    move_to_folder(filename, trash_folder)
            else:
                move_to_folder(filename, unorganized_folder)

# Function to move file to specified folder
def move_to_folder(filename, folder_name):
    """
    Move a file to the specified folder.

    Args:
    - filename (str): Name of the file to move
    - folder_name (str): Name of the folder to move the file to
    """
    base_name = os.path.basename(filename)
    new_path = os.path.join(folder_name, base_name)
    shutil.move(filename, new_path)
    print(Fore.GREEN + f"Moved {base_name} to {folder_name}")

# Function to display menu and handle user input
def display_menu():
    """
    Display menu options and handle user input.
    """
    print(Fore.CYAN + Style.BRIGHT + r'''
   ____ ____ ____ ____ ____ ____ ____
  ||C |||r |||a |||p |||y |||G |||e ||
  ||__|||__|||__|||__|||__|||__|||__||
  |/__\|/__\|/__\|/__\|/__\|/__\|/__\|
    ''')
    print(Fore.YELLOW + Style.BRIGHT + "Made with love and cats 🐾\n")
    print(Fore.CYAN + Style.BRIGHT + "Welcome to CRAPYGEN - Your Crappy Credit Card Generator and Tester\n")
    print(Fore.YELLOW + "WHAT CAN I DO?\n")
    print("1. Generate fake credit card details")
    print("2. Save generated credit card information to a text file")
    print("3. Save generated credit card information to a CSV file")
    print("4. Interact with a provided Stripe checkout link to simulate payment form submissions")
    print("5. Generate fake names and addresses (Google validated) and save to text file")
    print("6. Check validity of generated credit cards")
    print("7. Organize card details from a text file into folders")
    print("8. Delete all generated cards and addresses")
    print("9. Exit")

    while True:
        try:
            choice = int(input("\nEnter the number of what you want to do (1-9): "))
            if choice < 1 or choice > 9:
                raise ValueError("Invalid choice. Please enter a number between 1 and 9.")
            else:
                return choice
        except ValueError as e:
            print(Fore.RED + f"Error: {e}. Please enter a valid number.")

# Main function to run the program
def main():
    """
    Main function to run the program.
    """
    while True:
        choice = display_menu()

        if choice == 1:
            num_cards = int(input("\nEnter the number of credit cards to generate: "))
            card_types = ['amex', 'discover', 'mc', 'visa13', 'visa16']
            cards = generate_cards(card_types, num_cards)
            for card in cards:
                print(card)

        elif choice == 2:
            filename = input("\nEnter the filename to save credit card information (e.g., cards.txt): ")
            save_to_txt(cards, filename)

        elif choice == 3:
            filename = input("\nEnter the filename to save credit card information (e.g., cards.csv): ")
            save_to_csv(cards, filename)

        elif choice == 4:
            checkout_link = input("\nEnter the Stripe checkout link to interact with: ")
            num_cards = int(input("Enter the number of credit cards to use for submission: "))
            card_types = ['amex', 'discover', 'mc', 'visa13', 'visa16']
            cards = generate_cards(card_types, num_cards)
            interact_with_stripe_checkout(checkout_link, cards)

        elif choice == 5:
            num_entries = int(input("\nEnter the number of fake names and addresses to generate: "))
            single_file = input("Do you want to save all addresses in one file? (y/n): ").lower() == 'y'
            entries = generate_fake_info(num_entries)
            folder_name = 'addresses'
            save_addresses_to_txt(entries, folder_name, single_file)

        elif choice == 6:
            card_number = input("\nEnter the credit card number to check validity: ")
            if check_card_validity(card_number):
                print(Fore.GREEN + "Valid credit card number.")
            else:
                print(Fore.RED + "Invalid credit card number.")

        elif choice == 7:
            filename = input("\nEnter the filename containing card details to organize: ")
            organize_cards(filename)

        elif choice == 8:
            delete_generated_data()

        elif choice == 9:
            print(Fore.YELLOW + "Exiting CRAPYGEN. Have a nice day!")
            break

def delete_generated_data():
    """
    Delete all generated cards and addresses.
    """
    try:
        shutil.rmtree('WORKING_CARDS')
        shutil.rmtree('TRASHED')
        shutil.rmtree('UNORGANISED')
        shutil.rmtree('addresses')
        print(Fore.GREEN + "Deleted all generated cards and addresses.")
    except FileNotFoundError:
        print(Fore.YELLOW + "No generated cards or addresses found.")
