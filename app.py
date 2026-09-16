import streamlit as st
import subprocess
import pandas as pd
import os
import glob
import sys
import re

st.set_page_config(page_title="Alaxione Lead Generator", layout="centered")

st.title("🎯 Alaxione - Générateur de Leads Médicaux")
st.markdown("Recherchez des professionnels de santé et extrayez leurs coordonnées en un clic.")

with st.form("search_form"):
    specialty = st.text_input("Spécialité médicale", value="ophtalmologue")
    location = st.text_input("Ville / Localisation", value="Cannes")
    submitted = st.form_submit_button("Lancer la recherche")

if submitted:
    specialty_clean = specialty.strip()
    location_clean = location.strip()
    
    with st.spinner(f"Recherche de {specialty_clean}s à {location_clean} en cours... (Cela peut prendre un moment)"):
        # Nettoyage des anciens fichiers CSV pour éviter les confusions
        for f in glob.glob('leads_*.csv'):
            try:
                os.remove(f)
            except:
                pass

        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], capture_output=True)

        safe_spec = re.sub(r'[^a-zA-Z0-9]', '_', specialty_clean.lower())
        safe_loc = re.sub(r'[^a-zA-Z0-9]', '_', location_clean.lower())
        expected_file = f"leads_{safe_spec}_{safe_loc}.csv"

        cmd = [sys.executable, "scraper.py", "--specialty", specialty_clean, "--location", location_clean]
        result = subprocess.run(cmd, capture_output=True, text=True)

    if os.path.exists(expected_file) and os.path.getsize(expected_file) > 10:
        try:
            df = pd.read_csv(expected_file)
            if not df.empty and len(df.columns) > 1:
                exact_count = len(df.dropna(how='all'))
                st.success(f"Recherche pour {location_clean} terminée avec succès !")
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
            st.warning(f"Erreur lors de la lecture du fichier CSV : {e}")
    else:
        st.error(f"Aucun résultat trouvé pour '{specialty_clean}' à '{location_clean}'.")
        with st.expander("🔍 Voir les détails techniques"):
            st.text("STDOUT :")
            st.text(result.stdout)
            st.text("STDERR :")
            st.text(result.stderr)
