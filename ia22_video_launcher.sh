#!/data/data/com.termux/files/usr/bin/bash
echo "🎥 [NetSecurePro IA] Chargement IA22 Video Launcher..."

FLUX=$(jq -r '.flux' config.json)

if [[ "$FLUX" == "youtube" ]]; then
  am start -a android.intent.action.VIEW -d "$(jq -r '.youtube_url' config.json)"
elif [[ "$FLUX" == "peertube" ]]; then
  am start -a android.intent.action.VIEW -d "$(jq -r '.peertube_url' config.json)"
else
  echo "⚠️ Flux non reconnu ou vide"
fi
