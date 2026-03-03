(function() {
    console.log("%c NOYAU IA22 : ACCÈS MAÎTRE DÉTECTÉ ", "background: #ff0000; color: #ffffff; font-weight: bold; font-size: 20px;");
    
    const welcomeMsg = "Salut, Zoubirou Mohammed Ilyes. L'empire dzrouge.com est en ligne et à vos ordres.";
    
    // Si nous sommes sur la page IA, on ajoute un message spécial
    if (window.location.pathname.includes('ia')) {
        alert("Noyau IA22 : Bienvenue chez vous, Maître.");
    }
})();

// Protocole Easter Egg Secret
let inputSecret = "";
window.addEventListener('keydown', (e) => {
    inputSecret += e.key.toUpperCase();
    if (inputSecret.includes("IA22")) {
        document.body.style.transition = "all 1s";
        document.body.style.background = "radial-gradient(circle, #ff0000, #000000)";
        alert("SOUVERAINETÉ DZROUGE CONFIRMÉE. BIENVENUE, MAÎTRE ZOUBIROU.");
        inputSecret = "";
    }
    if (inputSecret.length > 10) inputSecret = "";
});
