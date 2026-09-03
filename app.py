import streamlit as st
import subprocess
import pandas as pd
import os
import glob

st.set_page_config(page_title="Alaxione Lead Generator", layout="centered")

st.title("🎯 Alaxione - Générateur de Leads Médicaux")
st.markdown("Recherchez des professionnels de santé et extrayez leurs coordonnées en un clic.")

# Formulaire de recherche
with st.form("search_form"):
    specialty = st.text_input("Spécialité médicale", value="ophtalmologue")
    location = st.text_input("Ville / Localisation", value="perpignan")
    submitted = st.form_submit_button("Lancer la recherche")

if submitted:
    with st.spinner(f"Recherche de {specialty}s à {location} en cours... Veuillez patienter."):
        # Lancement du scraper
        cmd = f"python scraper.py --specialty \"{specialty}\" --location \"{location}\""
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
        # Recherche du fichier CSV généré
        list_of_files = glob.glob('leads_*.csv')
        
        if list_of_files:
            latest_file = max(list_of_files, key=os.path.getctime)
            
            # Vérification si le fichier contient des données
            if os.path.exists(latest_file) and os.path.getsize(latest_file) > 10:
                try:
                    df = pd.read_csv(latest_file)
                    if not df.empty and len(df.columns) > 1:
                        st.success("Recherche terminée avec succès !")
                        st.metric("Prospects trouvés", len(df))
                        st.dataframe(df)
                        
                        with open(latest_file, "rb") as file:
                            st.download_button(
                                label="Télécharger le fichier CSV",
                                data=file,
                                file_name=latest_file,
                                mime="text/csv"
                            )
                    else:
                        st.warning("Le fichier trouvé est vide. Google Maps n'a renvoyé aucun résultat pour cette recherche.")
                except Exception as e:
                    st.warning("Le fichier CSV est vide ou mal formaté.")
            else:
                st.warning("Aucun résultat exploitable n'a été trouvé par le scraper pour cette ville.")
                with st.expander("Voir les détails techniques"):
                    st.text(result.stdout)
                    st.text(result.stderr)
        else:
            st.error("Aucun fichier de résultats n'a été créé.")