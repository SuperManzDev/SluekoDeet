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
import platform
import psutil
import openpyxl
import configparser

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

def generate_cards(card_types, num_cards):
    cards = []
    for _ in range(num_cards):
        card_type = random.choice(card_types)
        card = CreditCardGenerator(card_type)
        cards.append(card.get_card_info())
    return cards

def save_to_txt(cards, filename):
    with open(filename, 'w') as f:
        for card in cards:
            f.write(f"Type: {card['Type']}\n")
            f.write(f"Number: {card['Number']}\n")
            f.write(f"CVV: {card['CVV']}\n")
            f.write(f"Exp: {card['Exp']}\n")
            f.write("------------------------------\n")
    print(Fore.GREEN + f"Cards saved to {filename}")

def save_to_csv(cards, filename):
    keys = cards[0].keys() if cards else []
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(cards)
    print(Fore.GREEN + f"Cards saved to {filename}")

def save_to_excel(cards, filename):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['Type', 'Number', 'CVV', 'Exp'])
    for card in cards:
        ws.append([card['Type'], card['Number'], card['CVV'], card['Exp']])
    wb.save(filename)
    print(Fore.GREEN + f"Cards saved to {filename}")

def save_to_ini(cards, filename):
    config = configparser.ConfigParser()
    for i, card in enumerate(cards):
        section = f'Card_{i + 1}'
        config.add_section(section)
        config.set(section, 'Type', card['Type'])
        config.set(section, 'Number', card['Number'])
        config.set(section, 'CVV', card['CVV'])
        config.set(section, 'Exp', card['Exp'])
    with open(filename, 'w') as configfile:
        config.write(configfile)
    print(Fore.GREEN + f"Cards saved to {filename}")

def generate_fake_info(num_entries):
    fake = Faker()
    entries = []
    for _ in range(num_entries):
        name = fake.name()
        street_address = fake.street_address()
        city = fake.city()
        state = fake.state_abbr()
        zipcode = fake.zipcode()

        address = f"{name}\n{street_address}\n{city}, {state} {zipcode}"

        entries.append({
            'Name': name,
            'Address': address,
            'City': city,
            'State': state,
            'Zipcode': zipcode,
        })

    return entries

def save_addresses_to_txt(entries, folder_name):
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
        print(Fore.GREEN + "Closed WebDriver")

def validate_card_number(card_number):
    def luhn_checksum(card_number):
        def digits_of(n):
            return [int(d) for d in str(n)]
        digits = digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            doubled = d * 2
            checksum += doubled if doubled < 10 else doubled - 9
        return checksum % 10

    return luhn_checksum(card_number) == 0

def organize_cards_by_validity(file_name):
    valid_folder = 'valid_cards'
    invalid_folder = 'invalid_cards'
    
    if not os.path.exists(valid_folder):
        os.makedirs(valid_folder)
    if not os.path.exists(invalid_folder):
        os.makedirs(invalid_folder)
    
    with open(file_name, 'r') as file:
        lines = file.readlines()
    
    current_file = None
    for line in lines:
        if line.startswith("Type: "):
            card_type = line.split(": ")[1].strip()
        elif line.startswith("Number: "):
            card_number = line.split(": ")[1].strip()
            valid = validate_card_number(card_number)
            folder = valid_folder if valid else invalid_folder
            if not current_file or current_file != folder:
                current_file = folder
                file_mode = 'w' if current_file == valid_folder else 'a'
                file_name = os.path.join(folder, f'{card_type}_cards.txt')
            with open(file_name, file_mode) as file:
                file.write(line)
                file.write(next(lines))
                file.write(next(lines))
                file.write(next(lines))
                file.write(next(lines))
            print(Fore.GREEN + f"Organized card details into {current_file}")

def delete_generated_data(folder_name):
    for file in os.listdir(folder_name):
        file_path = os.path.join(folder_name, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(Fore.GREEN + f"Deleted file {file_path}")
    print(Fore.GREEN + f"All files in {folder_name} have been deleted")

def display_system_info():
    print(Fore.YELLOW + f"System Info:")
    print(Fore.YELLOW + f"OS: {platform.system()} {platform.release()}")
    print(Fore.YELLOW + f"CPU: {platform.processor()}")
    print(Fore.YELLOW + f"CPU Speed: {psutil.cpu_freq().current} MHz")
    print(Fore.YELLOW + f"Total RAM: {round(psutil.virtual_memory().total / (1024 ** 3))} GB")
    print(Fore.YELLOW + f"IP Address: {psutil.net_if_addrs().get('Wi-Fi', [{'address': 'N/A'}])[0]['address']}")

def display_welcome_message():
    print(Fore.CYAN + """
     ____  _              _           ____              _
    / ___|| |_   _  ___ | | __  ___  |  _ \  ___   ___ | |_
    \___ \| | | | |/ _ \| |/ / / _ \ | | | |/ _ \ / _ \| __|
     ___) | | |_| |  __/|   < | (_) || |_| |  __/|  __/| |_
    |____/|_|\__,_|\___||_|\_\ \___/ |____/ \___/ \___| \__|
   
    """ + Fore.MAGENTA + """
    Welcome to SluekoDeet
    Instagram: @Manz.Luvs.U
    GitHub: https://github.com/SuperManzDev
    Website: ManasSingh.Me
    """)

def display_settings():
    print(Fore.YELLOW + """
    Settings Menu:
    1. Change Theme
    2. Toggle Development Mode
    3. Back to Main Menu
    """)

def change_theme():
    print(Fore.YELLOW + "Available Themes:")
    print(Fore.CYAN + "1. Default")
    print(Fore.CYAN + "2. Dark")
    print(Fore.CYAN + "3. Light")
    choice = input("Choose theme (1-3): ").strip()
    if choice == '1':
        print(Fore.GREEN + "Default theme selected")
    elif choice == '2':
        print(Fore.GREEN + "Dark theme selected")
        # Apply dark theme settings here
    elif choice == '3':
        print(Fore.GREEN + "Light theme selected")
        # Apply light theme settings here
    else:
        print(Fore.RED + "Invalid choice.")

def development_mode():
    print(Fore.YELLOW + "Development Mode:")
    print(Fore.CYAN + "Showing current line of code execution")

def main():
    display_welcome_message()
    
    while True:
        display_system_info()
        print(Fore.GREEN + """
        Main Menu:
        1. Generate Credit Cards
        2. Save Cards to TXT
        3. Save Cards to CSV
        4. Save Cards to Excel
        5. Save Cards to INI
        6. Generate Fake Addresses
        7. Save Addresses to TXT
        8. Interact with Stripe Checkout
        9. Organize Cards by Validity
        10. Delete Generated Data
        11. Change Format
        12. Settings
        e. Exit
        """)

        choice = input("Enter your choice: ").strip().lower()
        
        if choice == '1':
            card_types = ['amex', 'discover', 'mc', 'visa13', 'visa16']
            num_cards = int(input("Enter the number of cards to generate: "))
            cards = generate_cards(card_types, num_cards)
            print(Fore.GREEN + "Generated credit cards:")
            for card in cards:
                print(card)
        
        elif choice == '2':
            filename = input("Enter filename for TXT: ")
            save_to_txt(cards, filename)
        
        elif choice == '3':
            filename = input("Enter filename for CSV: ")
            save_to_csv(cards, filename)
        
        elif choice == '4':
            filename = input("Enter filename for Excel: ")
            save_to_excel(cards, filename)
        
        elif choice == '5':
            filename = input("Enter filename for INI: ")
            save_to_ini(cards, filename)
        
        elif choice == '6':
            num_entries = int(input("Enter the number of fake addresses to generate: "))
            entries = generate_fake_info(num_entries)
        
        elif choice == '7':
            folder_name = input("Enter folder name to save addresses: ")
            save_addresses_to_txt(entries, folder_name)
        
        elif choice == '8':
            checkout_link = input("Enter Stripe checkout link: ")
            interact_with_stripe_checkout(checkout_link, cards)
        
        elif choice == '9':
            file_name = input("Enter filename with card details: ")
            organize_cards_by_validity(file_name)
        
        elif choice == '10':
            folder_name = input("Enter folder name to delete data from: ")
            delete_generated_data(folder_name)
        
        elif choice == '11':
            print(Fore.YELLOW + "Changing format...")
            # Implement the format change option here
        
        elif choice == '12':
            display_settings()
            settings_choice = input("Enter your choice: ").strip()
            if settings_choice == '1':
                change_theme()
            elif settings_choice == '2':
                development_mode()
            elif settings_choice == '3':
                continue
            else:
                print(Fore.RED + "Invalid choice.")
        
        elif choice == 'e':
            print(Fore.RED + "Exiting...")
            break
        
        else:
            print(Fore.RED + "Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
