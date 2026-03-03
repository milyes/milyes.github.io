const statusText = [
    "> INITIALISATION DU NOYAU...",
    "> CONNEXION AU RÉSEAU SOUVERAIN...",
    "> MAÎTRE : ZOUBIROU M.I. IDENTIFIÉ.",
    "> PROTOCOLE IA22 ACTIF.",
    "> ANALYSE DES FLUX DE DONNÉES...",
    "> SYSTÈME OPÉRATIONNEL À 100%."
];

let line = 0;
const statusDiv = document.querySelector('.status');

function typeStatus() {
    if (line < statusText.length) {
        let p = document.createElement('p');
        p.textContent = statusText[line];
        p.style.color = "#00d4ff";
        statusDiv.appendChild(p);
        line++;
        setTimeout(typeStatus, 1200);
    }
}

window.onload = () => {
    // Efface le contenu statique et lance la simulation
    statusDiv.innerHTML = "";
    typeStatus();
};
