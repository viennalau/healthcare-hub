import os
import sys
import pandas as pd
from bs4 import BeautifulSoup
import requests
import json

# Website from the FDA that provides information on drug shortages
url = "https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm"
medlineURL = "https://wsearch.nlm.nih.gov/ws/query?db=healthTopics&term="


def find_drug(drug_name):
    with open('Providers.json', 'r') as providers:
        provider_dict = json.load(providers)
    for provider in provider_dict.items():
        provider_name = provider[0]
        with open(provider[1]['drug_txt'], 'rb') as f:
            # The file is binary, so it needs to be decoded as UTF-8
            drug_text = f.read().decode('utf-8')
        drug_found = drug_text.find(drug_name.lower()) != -1 or drug_text.find(drug_name.upper()) != -1
        print(f"{drug_name} is{" " if drug_found else " not "}covered by {provider_name}")


# creates get request to FDA's API on drug shortages
def FDA_APIrequest(url):
    global file_path
    try:
        response = requests.get(url)

        if response.status_code == 200:
            print("response successful")
            file_path = 'Drug_Shortages.html'
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            return file_path

        else:
            print(f"request failed: code {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"request failed: {e}")
        return None


# The following code is based off the https://www.geeksforgeeks.org/convert-html-table-into-csv-file-in-python/ 
# website with some adjustments and error handling

# converts an html table to a csv file for data processing with pandas
def HTML_Table_to_CSV(file_path):
    data = []
    # Open and parse the HTML file
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # gets header from html file
    list_header = []
    header = soup.find_all("table")[0].find("tr")
    for items in header:
        list_header.append(items.get_text())

    # gets the data within the table
    HTML_data = soup.find_all("table")[0].find_all("tr")[1:]
    for element in HTML_data:
        sub_data = []
        for sub_element in element:
            sub_data.append(sub_element.get_text(strip=True, separator=' '))
        data.append(sub_data)

    # stores data into a dataframe
    df = pd.DataFrame(data=data, columns=list_header)

    # removes columns that dont have a value
    df.dropna(axis=1, inplace=True)
    df.columns = df.columns.str.strip()
    return df
    
# saves the csv file
def File_Saving():
    global cleaned_df
    global file_path
    file_path = FDA_APIrequest(url)  
    if file_path:
        cleaned_df = HTML_Table_to_CSV(file_path)
        if cleaned_df is not None:
            cleaned_df.to_csv('Clean_Drug_Shortage.csv', index=False)
            print("CSV file saved")
            # print(cleaned_df)
        else:
            print("error occurred with HTML parsing")
    else:
        print("failed to get the HTML file")


def medication_info(medication):
    # Calling the previously defined functions for making an API request to the FDA website, 
    # converting the request to a CSV file, and downloading the CSV file
    FDA_APIrequest(url)
    HTML_Table_to_CSV(file_path)
    File_Saving()

    filtered_df = cleaned_df[cleaned_df['Generic Name or Active Ingredient'].str.contains(medication, case=False)]
    print(f"Shortage Information for {medication}:")
    print(filtered_df)

# Provides various information of the medication
def info_of_med(medication):
    Medline_APIrequest(medlineURL, medication)

# Makes API reuqest to website asking for the a page on the medication
def Medline_APIrequest(medlineURL, medication):
    try:
        medlineURL = medlineURL + medication
        response = requests.get(medlineURL)
        if response.status_code == 200:
            print("response successful")

            # Define file path and name
            file_path = (f'{medication}.html')

            # Write response to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            return file_path

        else:
            print(f"request failed: code {response.status_code}")
            return None
        
    except requests.exceptions.RequestException as e:
        print(f"request failed: {e}")
        return None

def treatment():
    pass


def insurance():
    from Drug_Coverage import find_drug
    find_drug(input("What drug do you want to check for? "))


programOn = True
while programOn:
    print('-------------------------------------------------------------------------------')
    print("""
    Welcome to our comprehensive chatbot designed for your healthcare needs.
    What can we help you with today?
    """)
    print('-------------------------------------------------------------------------------')


    print("""
    Options:
    1. (TBA) Treatment of Common Sicknesses
    2. Displays availability for a certain medication (TBA: Descriptions and where to purchase)
    3. See who covers a certain medication
    4. Quit
        
    """)

    user_input = input("Type here: ")

    if user_input == '1':
        treatment()
    elif user_input == '2':
        print("What medication would you like information on? Enter the generic name or active ingredient.")
        medication = input("Type here: ")
        medication_info(medication)
    elif user_input == '3':
        find_drug(input("Which medication are you looking for? "))
    elif user_input == '4':
        programOn = False
