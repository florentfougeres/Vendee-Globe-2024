// Définir les styles disponibles
const styles = {
    dark: "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
    light: "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
  };

  // Créer la carte avec le style sombre par défaut
  let currentTheme = "dark";
  let map = new maplibregl.Map({
    container: "map",
    style: styles[currentTheme], // Thème sombre par défaut
    center: [-30, 40],
    zoom: 3,
  });

  // Pour stocker les trajectoires et points déjà affichés
  let displayedTrajectories = new Set(); // Set des codes de bateaux dont la trajectoire est affichée
  let displayedPoints = new Set(); // Set des points déjà affichés

  // Fonction pour afficher ou cacher une trajectoire de bateau
  function toggleBoatTrajectory(boat, data) {
    const button = document.querySelector(`button[data-boat="${boat}"]`);
    const lineColor = currentTheme === "dark" ? "#FF4136" : "#007bff"; // Choix de la couleur du trait (rouge ou bleu)

    if (displayedTrajectories.has(boat)) {
      displayedTrajectories.delete(boat);
      map.removeLayer(`trajectories-${boat}`);
      map.removeSource(`trajectories-${boat}`);
      button.classList.remove("btn-active");
      button.classList.add("btn-inactive");
    } else {
      displayedTrajectories.add(boat);
      map.addSource(`trajectories-${boat}`, {
        type: "geojson",
        data: {
          type: "FeatureCollection",
          features: data.features.filter((f) => f.properties.nom === boat),
        },
      });

      map.addLayer({
        id: `trajectories-${boat}`,
        type: "line",
        source: `trajectories-${boat}`,
        paint: {
          "line-width": 2,
          "line-color": lineColor, // Utiliser la couleur dynamique
        },
      });

      // Ajouter un événement de hover (mouseenter et mouseleave)
      map.on("mouseenter", `trajectories-${boat}`, () => {
        // Changer la couleur au survol
        map.setPaintProperty(`trajectories-${boat}`, "line-color", "#FF6347"); // Par exemple, rouge clair au survol
      });

      map.on("mouseleave", `trajectories-${boat}`, () => {
        // Réinitialiser la couleur lorsque la souris quitte
        map.setPaintProperty(`trajectories-${boat}`, "line-color", lineColor);
      });

      button.classList.remove("btn-inactive");
      button.classList.add("btn-active");
    }
  }

  // Fonction pour afficher ou cacher les points de "pointage"
  function togglePoint(boat, data) {
    const lineColor = currentTheme === "dark" ? "#FF4136" : "#007bff"; // Choix de la couleur du pointage

    if (displayedPoints.has(boat)) {
      displayedPoints.delete(boat);
      map.removeLayer(`points-${boat}`);
      map.removeSource(`points-${boat}`);
    } else {
      displayedPoints.add(boat);
      map.addSource(`points-${boat}`, {
        type: "geojson",
        data: {
          type: "FeatureCollection",
          features: data.features.filter((f) => f.properties.nom === boat),
        },
      });

      map.addLayer({
        id: `points-${boat}`,
        type: "circle",
        source: `points-${boat}`,
        paint: {
          "circle-radius": [
            "interpolate",
            ["linear"],
            ["zoom"],
            5, 4,
            10, 10,
          ],
          "circle-color": lineColor, // Utiliser la couleur dynamique
        },
      });

      // Ajouter un événement de hover (mouseenter et mouseleave) pour les points
      map.on("mouseenter", `points-${boat}`, () => {
        // Changer la couleur du pointage au survol
        map.setPaintProperty(`points-${boat}`, "circle-color", "#FFD700"); // Par exemple, jaune au survol
      });

      map.on("mouseleave", `points-${boat}`, () => {
        // Réinitialiser la couleur du pointage
        map.setPaintProperty(`points-${boat}`, "circle-color", lineColor);
      });
    }
  }

  // Fonction pour afficher toutes les trajectoires et points
  function showAll(data) {
    // Affiche toutes les trajectoires et tous les points
    const boats = [...new Set(data.features.map((f) => f.properties.nom))];
    boats.forEach((boat) => {
      if (!displayedTrajectories.has(boat)) {
        toggleBoatTrajectory(boat, data); // Afficher la trajectoire du bateau
      }
      if (!displayedPoints.has(boat)) {
        togglePoint(boat, data); // Afficher le pointage du bateau
      }
    });
  }

  // Fonction pour effacer toutes les trajectoires et points
  function clearAll() {
    displayedTrajectories.forEach((boat) => {
      map.removeLayer(`trajectories-${boat}`);
      map.removeSource(`trajectories-${boat}`);
    });
    displayedTrajectories.clear(); // Vider le Set des trajectoires

    displayedPoints.forEach((boat) => {
      map.removeLayer(`points-${boat}`);
      map.removeSource(`points-${boat}`);
    });
    displayedPoints.clear(); // Vider le Set des points

    // Réinitialiser l'état des boutons à non actif
    const allButtons = document.querySelectorAll('#boat-menu button');
    allButtons.forEach((button) => {
      button.classList.remove("btn-active");
      button.classList.add("btn-inactive");
    });
  }

  // Gestion du bouton de bascule de thème
  const themeToggleButton = document.getElementById("theme-toggle");
  const menu = document.getElementById("menu");
  themeToggleButton.addEventListener("click", () => {
    // Avant de changer de style, réinitialisez les boutons à l'état "non activé"
    const allButtons = document.querySelectorAll('#boat-menu button');
    allButtons.forEach((button) => {
      button.classList.remove("btn-active");
      button.classList.add("btn-inactive");
    });

    // Avant de changer de style, enregistrons les trajectoires existantes
    const currentTrajectories = [...displayedTrajectories];
    const currentPoints = [...displayedPoints];

    // Changez le thème de la carte
    currentTheme = currentTheme === "dark" ? "light" : "dark";
    map.setStyle(styles[currentTheme]);

    // Réajoutez les trajectoires et les points après le changement de style
    currentTrajectories.forEach((boat) => {
      fetch(trajectoriesGeoJSON)
        .then((response) => response.json())
        .then((data) => {
          toggleBoatTrajectory(boat, data);
        })
        .catch((error) => console.error("Erreur de chargement des données GeoJSON : ", error));
    });

    currentPoints.forEach((boat) => {
      fetch(pointsGeoJSON)
        .then((response) => response.json())
        .then((data) => {
          togglePoint(boat, data);
        })
        .catch((error) => console.error("Erreur de chargement des données GeoJSON des pointages : ", error));
    });

    menu.className = currentTheme; // Changer la classe du menu pour appliquer le thème
    themeToggleButton.textContent =
      currentTheme === "dark" ? "Basculer en thème clair" : "Basculer en thème sombre";
  });

  // URL des fichiers GeoJSON
  const trajectoriesGeoJSON =
    "https://raw.githubusercontent.com/florentfgrs/Vendee-Globe-2024/refs/heads/main/data/trajectoire.geojson";
  const pointsGeoJSON =
    "https://raw.githubusercontent.com/florentfgrs/Vendee-Globe-2024/refs/heads/main/data/pointages.geojson";

  map.on("style.load", () => {
    // Ajouter la source de trajectoire
    fetch(trajectoriesGeoJSON)
      .then((response) => response.json())
      .then((data) => {
        // Ajouter les événements aux boutons "Afficher toutes" et "Effacer toutes"
        document.getElementById("show-all").addEventListener("click", () => {
          showAll(data); // Afficher toutes les trajectoires et tous les points
        });

        document.getElementById("clear-all").addEventListener("click", () => {
          clearAll(); // Effacer toutes les trajectoires et tous les points
        });

        // Construire le menu dynamique pour les trajectoires des bateaux
        const boatMenu = document.getElementById("boat-menu");
        boatMenu.innerHTML = ""; // Réinitialiser le menu des bateaux
        const boats = [...new Set(data.features.map((f) => f.properties.nom))];

        boats.forEach((boat) => {
          const button = document.createElement("button");
          button.classList.add("btn", "btn-custom", "btn-inactive");
          button.textContent = boat;
          button.setAttribute("data-boat", boat); // Ajout d'un attribut personnalisé

          button.onclick = () => {
            toggleBoatTrajectory(boat, data);
            togglePoint(boat, data);
          };

          boatMenu.appendChild(button);
        });
      })
      .catch((error) => console.error("Erreur de chargement des données GeoJSON : ", error));
  });
