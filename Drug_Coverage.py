import json

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

if __name__ == "__main__":
    find_drug("penicillin")