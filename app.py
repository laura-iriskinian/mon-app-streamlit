import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

st.title("Recherche de Commerces Google Maps")

# Champs de saisie
ville = st.text_input("Ville", placeholder="Entrez une ville")
type_commerce = st.text_input("Type de commerce", placeholder="Ex: restaurant, pharmacie...")
rayon = st.number_input("Rayon de recherche (m)", min_value=100, max_value=50000, value=5000, step=100)

if st.button("Rechercher des Commerces"):
    if not ville or not type_commerce:
        st.error("Veuillez entrer une ville et un type de commerce.")
    else:
        try:
            # Géocodage (conversion ville en latitude/longitude)
            geo_url = "https://maps.googleapis.com/maps/api/geocode/json"
            geo_params = {"address": ville, "key": API_KEY}
            geo_response = requests.get(geo_url, params=geo_params)
            geo_data = geo_response.json()

            if geo_data["status"] != "OK":
                st.error("Ville introuvable. Essayez une autre ville.")
            else:
                lat = geo_data["results"][0]["geometry"]["location"]["lat"]
                lon = geo_data["results"][0]["geometry"]["location"]["lng"]

                # Recherche de commerces
                places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                places_params = {
                    "location": f"{lat},{lon}",
                    "radius": rayon,
                    "type": type_commerce,
                    "key": API_KEY
                }
                
                places_response = requests.get(places_url, params=places_params)
                places_data = places_response.json()

                commerces = []
                for place in places_data.get("results", []):
                    nom = place.get("name", "N/A")
                    adresse = place.get("vicinity", "Adresse non disponible")

                    # Obtenir les détails supplémentaires
                    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
                    details_params = {
                        "place_id": place.get("place_id"),
                        "fields": "formatted_phone_number,website",
                        "key": API_KEY
                    }
                    details_response = requests.get(details_url, params=details_params)
                    details_data = details_response.json()
                    
                    telephone = details_data.get("result", {}).get("formatted_phone_number", "Non disponible")
                    site_web = details_data.get("result", {}).get("website", "Non disponible")

                    commerces.append([nom, adresse, telephone, site_web])

                if commerces:
                    df = pd.DataFrame(commerces, columns=["Nom", "Adresse", "Téléphone", "Site Web"])
                    st.success(f"{len(commerces)} commerces trouvés !")
                    st.dataframe(df)

                    # Bouton de téléchargement CSV
                    csv = df.to_csv(index=False, sep=';', encoding='utf-8-sig')
                    st.download_button(label="Télécharger en CSV", data=csv, file_name="commerces.csv", mime="text/csv")
                else:
                    st.warning("Aucun commerce trouvé. Essayez un autre type ou élargissez la recherche.")

        except Exception as e:
            st.error(f"Une erreur est survenue : {str(e)}")
