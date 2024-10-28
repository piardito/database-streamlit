import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from cryptography.fernet import Fernet
import json

key = st.secrets['key']  # Remplacez par la clé générée

# Initialiser le chiffreur avec la clé
cipher_suite = Fernet(key)

# Lire le contenu chiffré de credentials_encrypted.json et le déchiffrer
with open("credentials_encrypted.json", "rb") as file:
    encrypted_data = file.read()

# Déchiffrer les données
decrypted_data = cipher_suite.decrypt(encrypted_data)

gcp_service_account_info = json.loads(decrypted_data)

# Configuration de l'authentification pour Google Sheets
def authenticate_gsheet():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file",
             "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_dict(gcp_service_account_info, scope)
    client = gspread.authorize(creds)
    return client


# Ouvrir la Google Sheet
def open_sheet(client, sheet_id):
    try:
        spreadsheet = client.open_by_key(sheet_id)
        sheet = spreadsheet.sheet1  # Utiliser la première feuille
        return sheet
    except Exception as e:
        st.error("Erreur d'ouverture de la feuille de calcul. Vérifiez l'ID de la feuille.")
        return None


# Fonction pour envoyer les données à Google Sheets
def envoyer_donnees(sheet, data):
    try:
        sheet.append_row(data)
        return True
    except Exception as e:
        st.error("Erreur lors de l'envoi des données à Google Sheets.")
        return False


# ID de la feuille Google (trouvé dans l'URL de la feuille de calcul Google)
SHEET_ID = "1pgCZ3S8gYlycTUlcuMlJJbyzzGWEbjCVufGr2uiBo6Q"

# Interface utilisateur avec Streamlit
st.title("Formulaire de saisie de données")
st.write("Veuillez entrer vos informations dans le formulaire ci-dessous.")

# Champs de saisie
nom = st.text_input("Nom")
email = st.text_input("Email")
age = st.number_input("Âge", min_value=1, max_value=100, step=1)

# Bouton de soumission
if st.button("Soumettre"):
    if nom and email and age:  # Vérification que tous les champs sont remplis
        # Authentification et ouverture de la feuille
        client = authenticate_gsheet()
        sheet = open_sheet(client, SHEET_ID)

        if sheet:
            # Préparer les données pour l'envoi
            data = [nom, email, int(age)]

            # Envoi des données dans Google Sheets
            success = envoyer_donnees(sheet, data)
            if success:
                st.success("Données envoyées avec succès dans Google Sheets !")
    else:
        st.error("Veuillez remplir tous les champs.")

