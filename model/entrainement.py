import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

def entrainer_modele():
    try:
        # 1. Chargement
        df = pd.read_csv("data/plantes_nettoyees.csv")
        preprocessor = joblib.load("model/preprocesseur.joblib")
        
        # 2. Préparation
        X = preprocessor.transform(df)
        y = df['nom']
        
        # 3. Entraînement
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        model = RandomForestClassifier(
            n_estimators=150,
            class_weight='balanced',
            random_state=42
        )
        model.fit(X_train, y_train)
        
        # 4. Sauvegarde
        joblib.dump(model, "model/modele_plantes.joblib")
        
        # 5. Évaluation
        print(f"✅ Modèle entraîné avec succès")
        print(f"Score entraînement: {model.score(X_train, y_train):.2%}")
        print(f"Score test: {model.score(X_test, y_test):.2%}")
    
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        raise

if __name__ == "__main__":
    entrainer_modele()