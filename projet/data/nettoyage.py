import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
import joblib
from pathlib import Path

def nettoyer_et_preparer():
    try:
        # 1. Chargement des données
        df = pd.read_csv("data/all_plant_details.csv")

        # 2. Standardisation des colonnes
        df = df.rename(columns={
            'common_name': 'nom',
            'watering_encoded': 'humidite',
            'care_level_encoded': 'difficulte_encoded'
        })

        # 3. Conversion des caractéristiques
        df['difficulte'] = df['difficulte_encoded'].map({
            0: 'facile',
            1: 'moyen',
            2: 'difficile'
        })

        # 4. Catégorisation de la lumière
        sunlight_map = {
            'full_sun': 'plein soleil',
            'part_shade': 'mi-ombre',
            'full_shade': 'ombre'
        }
        df['lumiere'] = 'mi-ombre'
        for col in df.filter(like='sunlight_').columns:
            key = ''.join(col.split('_')[1:])
            if key in sunlight_map:
                df.loc[df[col] == 1, 'lumiere'] = sunlight_map[key]

        # 5. Préprocesseur
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), ['humidite']),
                ('cat', OneHotEncoder(
                    categories=[['plein soleil', 'mi-ombre', 'ombre'], ['facile', 'moyen', 'difficile']],
                    handle_unknown='ignore'
                ), ['lumiere', 'difficulte'])
            ]
        )

        # 6. Sauvegarde
        Path("model").mkdir(exist_ok=True)
        preprocessor.fit(df)
        joblib.dump(preprocessor, "model/preprocesseur.joblib")

        # 7. Sauvegarde des données
        df[['nom', 'humidite', 'lumiere', 'difficulte']].to_csv(
            "data/plantes_nettoyees.csv", index=False
        )

        print("✅ Nettoyage terminé avec succès")

    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        raise

if __name__ == "__main__":
    nettoyer_et_preparer()
