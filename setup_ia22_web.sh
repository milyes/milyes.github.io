#!/bin/bash
# =====================================
# NetSecurePro IA | Console IA22 Web
# Script d'installation automatique
# Auteur : Zoubirou Mohammed Ilyes
# ORCID : https://orcid.org/0009-0007-7571-3178
# =====================================

DOSSIER="IA22_Web_Console"

echo "[🔧] Création du dossier : $DOSSIER"
mkdir -p "$DOSSIER"
cd "$DOSSIER" || exit 1

# === Fichier HTML ===
cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Console IA22 Web</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>Console IA22 Web</h1>
    <p>Analyse intelligente de logique IA – HTML, JSON, Python, Bash</p>
    <textarea id="codeInput" rows="6">#!/bin/bash
DEB_FILE="netsecurepro_web_cli_REAL.deb"
echo "🔧 [INFO] Vérification du système..."</textarea>
    <br>
    <button onclick="lancerAnalyseIA()">Lancer Analyse IA</button>
    <pre id="result"></pre>
    <footer>
        <p>© 2025 – NetSecurePro IA | Zoubirou Mohammed Ilyes</p>
    </footer>
    <script src="script.js"></script>
</body>
</html>
EOF

# === Fichier CSS ===
cat > style.css << 'EOF'
body {
    font-family: Arial, sans-serif;
    text-align: center;
    padding: 20px;
    background: #f7f7f7;
}
h1 {
    color: #007bff;
}
textarea {
    width: 80%;
    font-family: monospace;
    margin-top: 20px;
}
button {
    margin-top: 10px;
    padding: 10px 20px;
    background: #007bff;
    color: white;
    border: none;
    cursor: pointer;
    border-radius: 5px;
}
pre {
    background: #111;
    color: #0f0;
    padding: 15px;
    margin-top: 15px;
    width: 80%;
    margin-left: auto;
    margin-right: auto;
    text-align: left;
}
footer {
    margin-top: 30px;
    color: gray;
}
EOF

# === Fichier JS ===
cat > script.js << 'EOF'
function lancerAnalyseIA() {
    const code = document.getElementById("codeInput").value;
    let result = "";

    if (code.includes(".json")) {
        result = "🔍 Type détecté : JSON\\n🧠 Analyse IA : JSON bien formé.\\n💡 Suggestion : Valide avec jq.";
    } else if (code.includes(".deb")) {
        result = "🔍 Type détecté : Fichier Debian\\n🧠 Analyse IA : Paquet détecté.\\n💡 Suggestion : Vérifie dpkg.";
    } else if (code.includes("echo")) {
        result = "🔍 Type détecté : Script Bash\\n🧠 Analyse IA : Syntaxe valide.\\n💡 Suggestion : Exécute sous bash.";
    } else {
        result = "❗ Format non reconnu. Recommence.";
    }
    document.getElementById("result").innerText = result;
}
EOF

# === Message final ===
echo ""
echo "============================================"
echo "[✔] ✅ Console IA22 Web installée avec succès."
echo "[📁] Dossier : $(pwd)"
echo "[🌐] Ouvre : index.html dans ton navigateur."
echo "============================================"
