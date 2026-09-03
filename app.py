import streamlit as st
import subprocess
import pandas as pd
import os
import glob

st.set_page_config(page_title="Alaxione Lead Generator", layout="centered")

st.title("🎯 Alaxione - Générateur de Leads Médicaux")
st.markdown("Recherchez des professionnels de santé et extrayez leurs coordonnées en un clic.")

with st.form("search_form"):
    specialty = st.text_input("Spécialité médicale", value="ophtalmologue")
    location = st.text_input("Ville / Localisation", value="Cannes")
    submitted = st.form_submit_button("Lancer la recherche")

if submitted:
    with st.spinner(f"Recherche de {specialty}s à {location} en cours... (Cela peut prendre 1 à 2 minutes)"):
        
        # On supprime TOUS les fichiers CSV existants pour repartir de zéro
        for f in glob.glob('*.csv'):
            try:
                os.remove(f)
            except:
                pass

        # Exécution du scraper
        safe_spec = specialty.strip().replace(' ', '_').lower()
        safe_loc = location.strip().replace(' ', '_').lower()
        expected_file = f"leads_{safe_spec}_{safe_loc}.csv"

        cmd = f"python scraper.py --specialty \"{specialty}\" --location \"{location}\""
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)

    # Vérification stricte : le fichier spécifique DOIT exister
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
        # Si le fichier n'a pas été créé, on affiche la vraie erreur technique
        st.error(f"Le scraper n'a pas pu générer les résultats pour {location}. Google Maps bloque souvent les requêtes sans interface graphique sur ce serveur cloud.")
        with st.expander("🔍 Voir les détails de l'erreur technique (Logs Playwright)"):
            st.text("--- STDOUT ---")
            st.text(result.stdout)
            st.text("--- STDERR ---")
            st.text(result.stderr)
