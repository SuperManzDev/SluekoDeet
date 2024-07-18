import random
import string
import os
import csv
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
def save_addresses_to_txt(entries, folder_name):
    """
    Save generated fake names and addresses to text files under 'addresses' folder.

    Args:
    - entries (list): List of dictionaries containing fake name and address information
    - folder_name (str): Name of the folder to save the text files
    """
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    for idx, entry in enumerate(entries):
        filename = os.path.join(folder_name, f'address_{idx + 1}.txt')
        with open(filename, 'w') as f:
            f.write(f"Name: {entry['Name']}\n")
            f.write(f"Address:\n{entry['Address']}\n")
            f.write(f"City: {entry['City']}\n")
            f.write(f"State: {entry['State']}\n")
            f.write(f"Zipcode: {entry['Zipcode']}\n")
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
            print(Fore.GREEN + "Waited for submission")

    except NoSuchElementException as e:
        print(Fore.RED + f"Error: {e}")
    except TimeoutException as te:
        print(Fore.RED + f"Timeout error: {te}")
    finally:
        driver.quit()

# Function to check validity of generated credit cards (Luhn algorithm)
def check_card_validity(card_number):
    """
    Check the validity of a credit card number using the Luhn algorithm.

    Args:
    - card_number (str): Credit card number to validate

    Returns:
    - bool: True if the credit card number is valid, False otherwise
    """
    def luhn_algorithm(card_number):
        digits = [int(x) for x in card_number]
        odd_sum = sum(digits[-1::-2])
        even_sum = sum(sum(divmod(2 * d, 10)) for d in digits[-2::-2])
        return (odd_sum + even_sum) % 10 == 0

    return luhn_algorithm(card_number)

# Function to read card details from a file
def read_cards_from_file(filename):
    """
    Read credit card details from a text file.

    Args:
    - filename (str): Name of the text file containing credit card details

    Returns:
    - list: List of dictionaries containing credit card information
    """
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
    """
    Organize generated credit cards into folders and validate their validity.

    Args:
    - cards (list): List of dictionaries containing credit card information

    Returns:
    - tuple: Two lists of dictionaries containing working and trashed card information
    """
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
    """
    Display the main menu and handle user input.
    """
    github_link = "https://github.com/SuperManzDev"
    website_link = "https://manassingh.me"

    print(Fore.MAGENTA + r"""
  ____ ____ ____ ____ ____ ____ ____
 ||C |||r |||a |||p |||y |||G |||e ||
 ||__|||__|||__|||__|||__|||__|||__||
 |/__\|/__\|/__\|/__\|/__\|/__\|/__\|
""")
    print(Fore.GREEN + "Welcome to CrapyGen!")

    while True:
        print(Fore.YELLOW + "\nWhat would you like to do?")
        print(Fore.CYAN + "1. Generate Credit Cards")
        print("2. Generate Fake Names and Addresses")
        print("3. Interact with Stripe Checkout Link")
        print("4. Save Cards to Text File")
        print("5. Save Cards to CSV File")
        print("6. Read Card Details from File and Organize")
        print("7. Visit My Website (manassingh.me)")
        print(Fore.RED + "8. Exit")

        choice = input(Fore.YELLOW + "\nEnter the number of what you want to do (1-8): ")

        if choice == '1':
            card_types = ['amex', 'discover', 'mc', 'visa13', 'visa16']
            num_cards = int(input("Enter number of cards to generate: "))
            generated_cards = generate_cards(card_types, num_cards)
            organize_and_validate_cards(generated_cards)

        elif choice == '2':
            num_entries = int(input("Enter number of fake names and addresses to generate: "))
            fake_info = generate_fake_info(num_entries)
            save_addresses_to_txt(fake_info, 'addresses')

        elif choice == '3':
            checkout_link = input("Enter the Stripe checkout link: ")
            num_cards = int(input("Enter number of cards to use for checkout: "))
            cards = generate_cards(['visa16'], num_cards)
            interact_with_stripe_checkout(checkout_link, cards)

        elif choice == '4':
            filename = input("Enter the filename to save (e.g., generated_cards.txt): ")
            save_to_txt(generated_cards, filename)

        elif choice == '5':
            filename = input("Enter the filename to save (e.g., generated_cards.csv): ")
            save_to_csv(generated_cards, filename)

        elif choice == '6':
            filename = input("Enter the filename to read cards from (e.g., cards.txt): ")
            cards_to_organize = read_cards_from_file(filename)
            organize_and_validate_cards(cards_to_organize)

        elif choice == '7':
            print(Fore.BLUE + f"Opening {website_link}")
            os.system(f"start {website_link}")

        elif choice == '8':
            print(Fore.RED + "Exiting CrapyGen. Goodbye!")
            break

        else:
            print(Fore.RED + "Invalid choice. Please enter a number between 1 and 8.")

# Main function
def main():
    """
    Main function to start the CrapyGen application.
    """
    display_menu()

if __name__ == "__main__":
    main()
