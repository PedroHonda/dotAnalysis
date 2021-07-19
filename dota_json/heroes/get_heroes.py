'''
OpenDota documentation for heroes queries:
https://docs.opendota.com/#tag/heroes
'''
import requests
import json
import pandas as pd

# Query OpenDota API for heroes
dota_heroes_api = 'https://api.opendota.com/api/heroes'
dota_heroes_response = requests.get(dota_heroes_api)

# Parse response into a json
dota_heroes = json.loads(dota_heroes_response.text)

# Convert to Pandas DataFrame
dota_heroes_df = pd.DataFrame(dota_heroes)

# Save to Pickle format
dota_heroes_df.to_pickle("heroes.pkl")

# Save to CSV format
dota_heroes_df.to_csv("heroes.csv", index=False, sep=';')

# Save to JSON format
with open('heroes.json', 'w', encoding='utf-8') as f:
    json.dump(dota_heroes, f, ensure_ascii=False, indent=4)

# Create dict with "id" as key and "localized_name" as value
heroes_dict = {}
for hero in dota_heroes:
    heroes_dict[hero["id"]] = hero["localized_name"]
with open('heroes_dict.json', 'w', encoding='utf-8') as f:
    json.dump(heroes_dict, f, ensure_ascii=False, indent=4)
