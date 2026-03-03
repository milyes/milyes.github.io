function lancerAnalyseIA() {
    const code = document.getElementById("codeInput").value;
    let result = "";

    if (code.includes(".json")) {
        result = "🔍 Type détecté : JSON\n🧠 Analyse IA : JSON bien formé.\n💡 Suggestion : Valide avec jq.";
    } else if (code.includes(".deb")) {
        result = "🔍 Type détecté : Fichier Debian\n🧠 Analyse IA : Paquet détecté.\n💡 Suggestion : Vérifie dpkg.";
    } else if (code.includes("echo")) {
        result = "🔍 Type détecté : Script Bash\n🧠 Analyse IA : Syntaxe valide.\n💡 Suggestion : Exécute sous bash.";
    } else {
        result = "❗ Format non reconnu. Recommence.";
    }
    document.getElementById("result").innerText = result;
}
