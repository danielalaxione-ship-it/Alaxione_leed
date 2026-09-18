import streamlit as st
import subprocess
import pandas as pd
import os
import glob
import sys
import re
import io
import zipfile

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
                df = df.drop_duplicates(subset=['URL_Google_Maps'])
                exact_count = len(df.dropna(how='all'))
                st.success(f"Recherche pour {location_clean} terminée avec succès !")
                st.metric("Prospects trouvés", exact_count)
                cols = df.columns.tolist()
                preferred_order = ["Name", "Rating", "Reviews", "Phone", "Email", "Code Postal", "Ville", "Website", "URL_Google_Maps"]
                final_order = [c for c in preferred_order if c in cols] + [c for c in cols if c not in preferred_order]
                df = df[final_order]
                st.dataframe(df)

                # Création d'une archive ZIP en mémoire contenant des lots de 50 lignes maximum
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    chunk_size = 50
                    num_chunks = (len(df) // chunk_size) + (1 if len(df) % chunk_size > 0 else 0)
                    for i in range(num_chunks):
                        chunk = df.iloc[i * chunk_size : (i + 1) * chunk_size]
                        csv_data = chunk.to_csv(index=False).encode('utf-8')
                        zip_file.writestr(f"Leads_part{i + 1}.csv", csv_data)

                zip_buffer.seek(0)
                st.download_button(
                    label="Télécharger les résultats (ZIP)",
                    data=zip_buffer,
                    file_name=f"leads_{safe_spec}_{safe_loc}.zip",
                    mime="application/zip",
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
