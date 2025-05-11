import streamlit as st
import pandas as pd
import joblib
from pathlib import Path
from datetime import datetime
import random
import os

# Configuration de l'application
st.set_page_config(page_title="🌿 Recommandation Plantes", layout="wide")

# Configuration du feedback
FEEDBACK_DIR = Path(__file__).parent / "feedback"
FEEDBACK_DIR.mkdir(exist_ok=True, parents=True)
FEEDBACK_FILE = FEEDBACK_DIR / "feedback_utilisateurs.csv"

@st.cache_resource
def charger_artefacts():
    """Charge le modèle, le préprocesseur et les données des plantes"""
    try:
        return {
            "model": joblib.load("model/modele_plantes.joblib"),
            "preprocessor": joblib.load("model/preprocesseur.joblib"),
            "df": pd.read_csv("data/plantes_nettoyees.csv")
        }
    except Exception as e:
        st.error(f"Erreur de chargement : {str(e)}")
        st.stop()

def get_plant_image(plant_name):
    """Trouve la meilleure image disponible pour la plante"""
    mapping_file = Path("data/plant_image_mapping.csv")
    if mapping_file.exists():
        mapping = pd.read_csv(mapping_file)
        matched = mapping[mapping["plant_name"].str.lower() == plant_name.lower()]
        if not matched.empty:
            img_path = Path("images") / matched.iloc[0]["image_file"]
            if img_path.exists():
                return img_path
    
    available_images = list(Path("images").glob("*.jpg")) + list(Path("images").glob("*.png"))
    if available_images:
        return random.choice(available_images)
    return Path("images/default.jpg") if Path("images/default.jpg").exists() else None

def enregistrer_feedback(note, commentaire, plante):
    """Enregistre le feedback dans un fichier CSV"""
    try:
        nouveau_feedback = pd.DataFrame([{
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "plante": plante,
            "note": note,
            "commentaire": commentaire
        }])
        
        nouveau_feedback.to_csv(
            FEEDBACK_FILE,
            mode='a',
            header=not FEEDBACK_FILE.exists(),
            index=False,
            encoding='utf-8'
        )
        return True
    except Exception as e:
        st.error(f"Erreur lors de l'enregistrement : {str(e)}")
        return False

def afficher_formulaire_feedback(prediction=None, key_suffix=""):
    """Affiche le formulaire de feedback avec des clés uniques"""
    with st.expander("💬 Donnez votre avis", expanded=False):
        if prediction:
            plante = st.text_input("Plante", value=prediction, disabled=True, key=f"plante_{key_suffix}")
        else:
            plante = st.text_input("Nom de la plante", key=f"plante_general_{key_suffix}")
        
        note = st.slider("Note (1-5)", 1, 5, 3, key=f"note_{key_suffix}")
        commentaire = st.text_area("Commentaire", key=f"comment_{key_suffix}")
        
        if st.button("Envoyer", key=f"btn_{key_suffix}"):
            if plante:
                if enregistrer_feedback(note, commentaire, plante):
                    st.success("Merci pour votre feedback !")
                    st.rerun()
                else:
                    st.error("Erreur lors de l'enregistrement")
            else:
                st.warning("Veuillez spécifier une plante")

def afficher_recommandation(prediction):
    """Affiche la recommandation avec gestion intelligente des images"""
    try:
        plante_data = artefacts["df"][artefacts["df"]["nom"] == prediction].iloc[0]
        img_path = get_plant_image(prediction)
        
        # Utilisation de colonnes pour un meilleur layout
        col_img, col_info = st.columns([1, 2])
        
        with col_img:
            if img_path and img_path.exists():
                st.image(str(img_path), width=300, caption=prediction)
            else:
                st.warning("Aucune image spécifique disponible")
                default_img = Path("images/default.jpg")
                if default_img.exists():
                    st.image(str(default_img), width=300, caption="Image générique")
        
        with col_info:
            st.markdown(f"""
            ### 🌿 {prediction}
            - ☀ **Luminosité:** {plante_data['lumiere']}
            - 💧 **Humidité:** {plante_data['humidite']}/5
            - 🛠 **Difficulté:** {plante_data['difficulte']}
            """)
        
        # Ajout du formulaire de feedback
        afficher_formulaire_feedback(prediction, key_suffix=prediction)
        
    except Exception as e:
        st.error(f"Erreur d'affichage: {str(e)}")

def diagnostiquer(symptomes):
    """Fonction de diagnostic des problèmes de plantes"""
    if symptomes.get("feuilles_jaunes") and symptomes.get("sol_humide"):
        return ("Excès d'arrosage", "Réduire les arrosages et vérifier le drainage", "⚠ Moyenne")
    elif symptomes.get("feuilles_jaunes"):
        return ("Manque de nutriments", "Appliquer un engrais équilibré", "🟢 Faible")
    elif symptomes.get("taches_noires"):
        return ("Maladie fongique", "Traiter avec un fongicide et isoler la plante", "🔴 Urgent")
    elif symptomes.get("flétrissement"):
        return ("Manque d'eau", "Arroser abondamment et surveiller", "⚠ Moyenne")
    else:
        return ("Aucun problème détecté", "Votre plante semble en bonne santé", "🟢 Faible")

def afficher_diagnostic():
    """Affiche l'interface de diagnostic"""
    st.header("🔍 Diagnostic des problèmes de plantes")
    
    with st.form("form_diagnostic"):
        st.subheader("Symptômes observés")
        col1, col2 = st.columns(2)
        
        with col1:
            feuilles_jaunes = st.checkbox("Feuilles jaunies", key="feuilles_jaunes")
            taches_noires = st.checkbox("Taches noires", key="taches_noires")
        
        with col2:
            sol_humide = st.checkbox("Sol constamment humide", key="sol_humide")
            fletrissement = st.checkbox("Flétrissement", key="fletrissement")
        
        submitted = st.form_submit_button("Effectuer le diagnostic")
    
    if submitted:
        symptomes = {
            "feuilles_jaunes": feuilles_jaunes,
            "taches_noires": taches_noires,
            "sol_humide": sol_humide,
            "flétrissement": fletrissement
        }
        
        diagnostic, conseils, urgence = diagnostiquer(symptomes)
        
        st.subheader("Résultats du diagnostic")
        col_res1, col_res2 = st.columns([1, 3])
        
        with col_res1:
            st.metric("Niveau d'urgence", urgence)
        
        with col_res2:
            st.info(f"*Diagnostic:* {diagnostic}")
            st.success(f"*Conseils:* {conseils}")

def afficher_statistiques_feedback():
    """Affiche les statistiques des feedbacks"""
    if not FEEDBACK_FILE.exists():
        st.warning("Aucun feedback n'a encore été enregistré")
        return
    
    try:
        df = pd.read_csv(FEEDBACK_FILE)
        
        st.subheader("📊 Statistiques des feedbacks")
        tab1, tab2 = st.tabs(["Résumé", "Données complètes"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Nombre de feedbacks", len(df))
                st.metric("Note moyenne", f"{df['note'].mean():.1f}/5")
            
            with col2:
                st.write("Derniers commentaires :")
                for _, row in df.tail(3).iterrows():
                    st.text(f"{row['date']} - {row['commentaire']}")
        
        with tab2:
            st.dataframe(df)
    
    except Exception as e:
        st.error(f"Erreur de lecture: {str(e)}")

def main():
    global artefacts
    artefacts = charger_artefacts()
    
    st.title("🌱 Trouvez Votre Plante Parfaite")
    
    # Création des onglets
    tab1, tab2, tab3, tab4 = st.tabs([
        "Recommandation",
        "Diagnostic",
        "Feedback Général",
        "Statistiques"
    ])
    
    with tab1:
        with st.form("main_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                lumiere = st.selectbox(
                    "🌞 Besoin en lumière",
                    ['plein soleil', 'mi-ombre', 'ombre'],
                    index=1,
                    key="lumiere_select"
                )
                humidite = st.slider("💧 Humidité (1-5)", 1, 5, 3, key="humidite_slider")
            
            with col2:
                difficulte = st.selectbox(
                    "🛠 Difficulté",
                    ['facile', 'moyen', 'difficile'],
                    index=0,
                    key="difficulte_select"
                )
            
            submitted = st.form_submit_button("Trouver ma plante")
        
        # Affichage des résultats immédiatement après soumission
        if submitted:
            try:
                X = pd.DataFrame([[humidite, lumiere, difficulte]], 
                                columns=['humidite', 'lumiere', 'difficulte'])
                X_trans = artefacts["preprocessor"].transform(X)
                prediction = artefacts["model"].predict(X_trans)[0]
                
                st.success(f"## Recommandation: {prediction}")
                afficher_recommandation(prediction)
            except Exception as e:
                st.error(f"Erreur: {str(e)}")
    
    with tab2:
        afficher_diagnostic()
    
    with tab3:
        st.header("Formulaire de Feedback Général")
        afficher_formulaire_feedback(key_suffix="general")
    
    with tab4:
        afficher_statistiques_feedback()

if __name__ == "__main__":
    main()