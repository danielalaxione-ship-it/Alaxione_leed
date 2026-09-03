import streamlit as st
import subprocess
import pandas as pd
import os
import glob

# Installation automatique du navigateur Playwright au premier lancement sur le cloud
@st.cache_resource
def setup_playwright():
    try:
        subprocess.run(["playwright", "install", "chromium"], check=True)
    except Exception as e:
        print(f"Erreur d'installation Playwright: {e}")

setup_playwright()

st.set_page_config(page_title="Alaxione Lead Generator", layout="centered")

st.title("🎯 Alaxione - Générateur de Leads Médicaux")
st.markdown("Recherchez des professionnels de santé et extrayez leurs coordonnées en un clic.")

with st.form("search_form"):
    specialty = st.text_input("Spécialité médicale", value="ophtalmologue")
    location = st.text_input("Ville / Localisation", value="Cannes")
    submitted = st.form_submit_button("Lancer la recherche")

if submitted:
    with st.spinner(f"Recherche de {specialty}s à {location} en cours... (Patientez 1 minute)"):
        for f in glob.glob('*.csv'):
            try:
                os.remove(f)
            except:
                pass

        safe_spec = specialty.strip().replace(' ', '_').lower()
        safe_loc = location.strip().replace(' ', '_').lower()
        expected_file = f"leads_{safe_spec}_{safe_loc}.csv"

        cmd = f"python scraper.py --specialty \"{specialty}\" --location \"{location}\""
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)

    if os.path.exists(expected_file) and os.path.getsize(expected_file) > 10:
        try:
            df = pd.read_csv(expected_file)
            if not df.empty and len(df.columns) > 1:
                exact_count = len(df.dropna(how='all'))
                st.success(f"Recherche pour {location} terminée avec succès !")
                st.metric("Prospects trouvés", exact_count)
                st.dataframe(df)

                with open(expected_file, "rb") as file:
                    st.download_button(
                        label="Télécharger le fichier CSV",
                        data=file,
                        file_name=expected_file,
                        mime="text/csv",
                    )
            else:
                st.warning("Le fichier généré est vide.")
        except Exception as e:
            st.warning("Erreur lors de la lecture du fichier CSV.")
    else:
        st.error(f"Aucun résultat trouvé pour '{specialty}' à '{location}'.")
        with st.expander("🔍 Voir les détails techniques"):
            st.text(result.stdout)
            st.text(result.stderr)
