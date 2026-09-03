import streamlit as st
import subprocess
import pandas as pd
import os

st.set_page_config(page_title="Alaxione Lead Generator", layout="centered")

st.title("🎯 Alaxione - Générateur de Leads Médicaux")
st.markdown("Recherchez des professionnels de santé et extrayez leurs coordonnées en un clic.")

# Formulaire de recherche
with st.form("search_form"):
    specialty = st.text_input("Spécialité médicale", value="ophtalmologue")
    location = st.text_input("Ville / Localisation", value="Perpignan")
    submitted = st.form_submit_button("Lancer la recherche")

if submitted:
    with st.spinner(f"Recherche de {specialty}s à {location} en cours... Veuillez patienter."):
        # Nom de fichier unique basé sur la recherche pour éviter les mélanges
        safe_specialty = specialty.replace(" ", "_").lower()
        safe_location = location.replace(" ", "_").lower()
        output_filename = f"leads_{safe_specialty}_{safe_location}.csv"
        
        # Lancement du scraper en lui passant un nom de fichier si votre scraper le gère, 
        # ou en renommant le fichier généré par défaut.
        cmd = f"python scraper.py --specialty \"{specialty}\" --location \"{location}\""
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)

    # On cherche spécifiquement le dernier fichier généré ou celui correspondant
    if os.path.exists(output_filename) and os.path.getsize(output_filename) > 10:
        target_file = output_filename
    else:
        # Fallback sur le dernier fichier CSV créé si le nom personnalisé n'est pas géré par scraper.py
        import glob
        list_of_files = glob.glob('leads_*.csv')
        target_file = max(list_of_files, key=os.path.getctime) if list_of_files else None

    if target_file and os.path.exists(target_file) and os.path.getsize(target_file) > 10:
        try:
            df = pd.read_csv(target_file)
            if not df.empty and len(df.columns) > 1:
                exact_count = len(df.dropna(how='all'))
                
                st.success("Recherche terminée avec succès !")
                st.metric("Prospects trouvés", exact_count)
                st.dataframe(df)

                with open(target_file, "rb") as file:
                    st.download_button(
                        label="Télécharger le fichier CSV",
                        data=file,
                        file_name=target_file,
                        mime="text/csv",
                    )
            else:
                st.warning("Le fichier trouvé est vide. Google Maps n'a renvoyé aucun résultat pour cette recherche.")
        except Exception as e:
            st.warning("Le fichier CSV est vide ou mal formaté.")
    else:
        st.warning("Aucun résultat exploitable n'a été trouvé pour cette recherche.")
        with st.expander("Voir les détails techniques"):
            st.text(result.stdout)
            st.text(result.stderr)
