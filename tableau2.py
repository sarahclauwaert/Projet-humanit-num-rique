import requests
from bs4 import BeautifulSoup
import json

# URL de la page Wikipedia de l'Oise
page = requests.get('https://fr.wikipedia.org/wiki/Liste_des_anciennes_communes_de_l%27Oise')
soup = BeautifulSoup(page.text, 'html.parser')

# Accéder au deuxième tableau
tables = soup.find_all('table')
if len(tables) >= 3:
    table = tables[2]  # Accès au deuxième tableau
else:
    print("Il n'y a pas de troisième tableau sur la page.")

rows = table.find_all('tr')
headers = [header.text.strip() for header in rows[0].find_all(['th', 'td'])]

data = []

prev_row_data = {}  # Stockage des données de la ligne précédente

for row in rows[1:]:
    cells = row.find_all(['th', 'td'])
    row_data = {}
    
    # Utiliser les données de la ligne précédente si la cellule n'a qu'une paire clé-valeur
    if len(cells) == 1:
        if prev_row_data:  # Vérifier s'il y a des données dans la ligne précédente
            for header, value in prev_row_data.items():
                if header == "Nom":
                    nom = cells[0].text.strip()
                    if nom not in value:
                        prev_row_data[header] = value + ", " + nom  # Concaténer les valeurs
                    else:
                        prev_row_data[header] = value
                else:
                    prev_row_data[header] = value
        else:
            continue
    else:
        for header, cell in zip(headers, cells):
            row_data[header] = cell.text.strip()
            
        # Vérifier si les nouvelles données sont identiques aux données précédentes
        if row_data != prev_row_data:
            # Vérifier si la clé "Décision" existe dans les données
            if "Décision" in row_data:
                # Si la date d'effet est manquante, assigner la valeur de la décision à la date d'effet
                if "Date d’effet" not in row_data:
                    row_data["Date d’effet"] = row_data["Décision"]
            data.append(row_data)
            
            # Si la longueur de la ligne est de 3 cellules, copier les deux dernières valeurs de la ligne précédente
            if len(cells) == 3 and prev_row_data:
                row_data["Décision"] = prev_row_data.get("Décision", "")
                row_data["Date d’effet"] = prev_row_data.get("Date d’effet", "")

    # Mise à jour des données de la ligne précédente
    prev_row_data = row_data if row_data else prev_row_data

with open('data_table_2.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
