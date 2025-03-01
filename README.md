# NixLanguageTool

Intégration de l'API OpenAI dans deux serveurs : Flask (Python) et Express (Node.js) pour des tâches de traitement du langage naturel.

## Structure du Projet

Le projet contient deux implémentations parallèles :

1. **Python Flask** (port 5000)
   - Dossier : `python_flask/`
   - Point d'entrée : `app.py`
   - Utilitaires OpenAI : `openai_utils.py`
   - Exemple d'utilisation : `example.py`

2. **Node.js Express** (port 8000)
   - Dossier : `nodejs/`
   - Point d'entrée : `server.js`
   - Utilitaires OpenAI : `openai_utils.js`
   - Exemple d'utilisation : `example.js`

## Points d'API

Les deux serveurs fournissent les mêmes points d'API :

### Racine (GET /)
- Affiche des informations générales sur l'API

### Chat Completion (POST /api/chat)
- Génère une réponse à l'aide du modèle GPT d'OpenAI
- Corps de la requête JSON :
  ```json
  {
    "prompt": "Votre message ou question",
    "model": "gpt-4o" (facultatif, par défaut: "gpt-4o")
  }
  ```

### Analyse de Sentiment (POST /api/analyze/sentiment)
- Analyse le sentiment d'un texte donné
- Corps de la requête JSON :
  ```json
  {
    "text": "Le texte à analyser"
  }
  ```
- Réponse :
  ```json
  {
    "rating": 4,        // Note de 1 à 5
    "confidence": 0.85  // Score de confiance entre 0 et 1
  }
  ```

## Configuration

1. Configurez votre clé API OpenAI comme variable d'environnement :
   ```
   export OPENAI_API_KEY="votre-clé-api"
   ```

2. Pour démarrer le serveur Flask :
   ```
   cd python_flask
   python app.py
   ```

3. Pour démarrer le serveur Node.js :
   ```
   cd nodejs
   node server.js
   ```

## Utilisation

Exemples avec curl :

```bash
# Appel API de chat (Flask)
curl -X POST http://localhost:5000/api/chat -H "Content-Type: application/json" -d '{"prompt": "Bonjour, comment ça va?"}'

# Appel API d'analyse de sentiment (Node.js)
curl -X POST http://localhost:8000/api/analyze/sentiment -H "Content-Type: application/json" -d '{"text": "Je suis très content de cette application!"}'
```

## Note Importante

Le code utilise le modèle "gpt-4o" d'OpenAI, qui est le modèle le plus récent disponible à ce jour.
