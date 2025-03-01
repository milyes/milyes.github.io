# Intégration de l'API OpenAI

Ce projet fournit une intégration complète de l'API OpenAI dans deux serveurs distincts : un serveur Flask (Python) et un serveur Express (Node.js) pour des tâches avancées de traitement du langage naturel et d'analyse de coûts d'utilisation.

## Structure du Projet

Le projet contient deux implémentations parallèles et équivalentes :

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

3. **Données partagées**
   - Dossier : `attached_assets/`
   - Données de coûts : `cost_2025-01-30_2025-03-01.csv`

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
- Réponse : La réponse générée par le modèle OpenAI

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

### Résumé de Texte (POST /api/summarize)
- Génère un résumé concis d'un texte long
- Corps de la requête JSON :
  ```json
  {
    "text": "Le texte long à résumer"
  }
  ```
- Réponse : Le résumé généré par le modèle OpenAI

### Analyse de Coûts (GET /api/analyze/costs)
- Analyse les coûts d'utilisation de l'API OpenAI sur différentes périodes
- Paramètres de requête :
  - `period` : Période d'analyse ('day', 'week', ou 'month'. Par défaut: 'month')
- Exemple de réponse :
  ```json
  {
    "summary": {
      "total_tokens": 374100,
      "total_cost_usd": 7.482,
      "days_analyzed": 31,
      "average_daily_cost_usd": 0.2414,
      "date_range": {
        "start": "2025-01-30",
        "end": "2025-03-01"
      }
    },
    "period": "month",
    "period_data": [
      {
        "month": "2025-01",
        "tokens": 27500,
        "cost_usd": 0.55
      },
      {
        "month": "2025-02",
        "tokens": 338300,
        "cost_usd": 6.766
      },
      {
        "month": "2025-03",
        "tokens": 8300,
        "cost_usd": 0.166
      }
    ]
  }
  ```

## Modes de Fonctionnement

Le système peut fonctionner dans deux modes :

1. **Mode API** : Utilise l'API OpenAI réelle pour traiter les requêtes (nécessite une clé API)
2. **Mode Simulation** : Génère des réponses simulées pour le développement et les tests (aucune clé API requise)

Le mode est automatiquement déterminé par la présence de la variable d'environnement `OPENAI_API_KEY`.

## Configuration

1. Configurez votre clé API OpenAI comme variable d'environnement :
   ```bash
   export OPENAI_API_KEY="votre-clé-api"
   ```

2. Pour démarrer le serveur Flask :
   ```bash
   cd python_flask
   python app.py
   ```

3. Pour démarrer le serveur Node.js :
   ```bash
   cd nodejs
   node server.js
   ```

## Utilisation

Exemples avec curl :

```bash
# Appel API de chat (Flask)
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Bonjour, comment ça va?"}'

# Appel API d'analyse de sentiment (Node.js)
curl -X POST http://localhost:8000/api/analyze/sentiment \
  -H "Content-Type: application/json" \
  -d '{"text": "Je suis très content de cette application!"}'

# Génération d'un résumé (Flask)
curl -X POST http://localhost:5000/api/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "Long texte à résumer..."}'

# Analyse des coûts par jour (Node.js)
curl -X GET "http://localhost:8000/api/analyze/costs?period=day"

# Analyse des coûts par semaine (Flask)
curl -X GET "http://localhost:5000/api/analyze/costs?period=week"

# Analyse des coûts par mois (par défaut)
curl -X GET http://localhost:5000/api/analyze/costs
```

## Analyse des Coûts

Le système permet d'analyser les coûts d'utilisation de l'API OpenAI sur différentes périodes :

- **Jour** : Affiche les coûts et tokens utilisés pour chaque jour
- **Semaine** : Agrège les coûts et tokens par semaine
- **Mois** : Agrège les coûts et tokens par mois (vue par défaut)

Les données sont extraites du fichier CSV `attached_assets/cost_2025-01-30_2025-03-01.csv` qui contient les enregistrements d'utilisation journalière.

## Note Importante

Le code utilise le modèle "gpt-4o" d'OpenAI, qui est le modèle le plus récent disponible à ce jour (Mai 2024). Ce modèle offre des capacités avancées de compréhension et de génération de texte.
