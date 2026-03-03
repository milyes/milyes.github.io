async function runIA() {
  const input = document.getElementById("inputIA").value;
  const result = document.getElementById("resultIA");
  result.innerHTML = "🧠 Réponse IA en cours...";
  setTimeout(() => {
    result.innerHTML = "✅ IA a analysé votre logique : '" + input + "'";
  }, 1500);
}

fetch("logic_data/netsecure_ai_modules.json")
  .then(response => response.json())
  .then(data => {
    const container = document.getElementById("module-cards");
    data.forEach(mod => {
      const card = document.createElement("div");
      card.style.background = "#1c1f26";
      card.style.padding = "15px";
      card.style.borderRadius = "10px";
      card.innerHTML = `<h3>${mod.name}</h3><p>${mod.description}</p><p>Status: ${mod.status}</p>`;
      container.appendChild(card);
    });
  });
