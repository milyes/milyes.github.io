#!/bin/bash

echo "📦 Déploiement GitHub Pages pour NetSecurePro IA22"

rm -rf .git

git init
git checkout -b main
git add .

git commit -m "🚀 Publication officielle NetSecurePro IA22"
git remote add origin https://github.com/milyes/NetSecurePro-IA22.git
git push -f origin main

echo "✅ Push terminé. Connecte-toi à GitHub pour activer Pages."
xdg-open https://github.com/milyes/NetSecurePro-IA22/settings/pages
