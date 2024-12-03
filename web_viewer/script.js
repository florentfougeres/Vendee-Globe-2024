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

function toggleBoatTrajectory(boat, data) {
  const button = document.querySelector(`button[data-boat="${boat}"]`);
  const lineColor = currentTheme === "dark" ? "#FF4136" : "#007bff";

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
        "line-color": lineColor,
      },
    });

    // Ajouter la popup dynamique au survol de la trajectoire
    const popup = new maplibregl.Popup({
      closeButton: false,
      closeOnClick: false,
    });

    map.on("mouseenter", `trajectories-${boat}`, (e) => {
      map.getCanvas().style.cursor = "pointer"; // Changer le curseur
      const coordinates = e.lngLat;
      const feature = e.features[0]; // Récupérer la première feature de la trajectoire (bateau)
      const name = feature.properties.nom;
      const cap = feature.properties["30m_cap"]; // Récupérer le cap
      const vitesse = feature.properties["30m_vitesse"]; // Récupérer la vitesse

      // Mettre à jour les informations dans le panneau latéral
      document.getElementById("boat-name").textContent = name;
      document.getElementById("boat-cap").textContent =
        cap !== undefined ? `${cap}` : "--";
      document.getElementById("boat-vitesse").textContent =
        vitesse !== undefined ? `${vitesse}` : "--";

      // Afficher le panneau d'informations
      document.getElementById("info-panel").style.display = "block";

      popup
        .setLngLat(coordinates)
        .setHTML(`<strong>${name}</strong>`)
        .addTo(map);

      // Changer la couleur de la ligne en vert au survol
      map.setPaintProperty(`trajectories-${boat}`, "line-color", "#00FF00"); // Vert
      // Augmenter la largeur de la ligne au survol
      map.setPaintProperty(`trajectories-${boat}`, "line-width", 4); // Plus épais
      // Ajouter un effet de diffusion (blur) pour rendre la ligne plus visible
      map.setPaintProperty(`trajectories-${boat}`, "line-blur", 1); // Effet de diffusion
    });

    map.on("mouseleave", `trajectories-${boat}`, () => {
      map.getCanvas().style.cursor = ""; // Réinitialiser le curseur
      popup.remove(); // Retirer la popup

      // Réinitialiser la couleur de la ligne à la couleur de base
      map.setPaintProperty(`trajectories-${boat}`, "line-color", lineColor);
      // Réinitialiser la largeur de la ligne à sa valeur d'origine
      map.setPaintProperty(`trajectories-${boat}`, "line-width", 2); // Largeur initiale
      // Réinitialiser l'effet de diffusion
      map.setPaintProperty(`trajectories-${boat}`, "line-blur", 0); // Annuler l'effet de diffusion
    });

    map.on("mouseleave", `trajectories-${boat}`, () => {
      map.getCanvas().style.cursor = ""; // Réinitialiser le curseur
      popup.remove(); // Retirer la popup

      // Réinitialiser la couleur de la ligne
      map.setPaintProperty(`trajectories-${boat}`, "line-color", lineColor);

      // Cacher le panneau d'informations
      document.getElementById("info-panel").style.display = "none";
    });

    map.on("mouseleave", `trajectories-${boat}`, () => {
      map.getCanvas().style.cursor = ""; // Réinitialiser le curseur
      popup.remove(); // Retirer la popup

      // Réinitialiser la couleur de la ligne
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
        "circle-radius": ["interpolate", ["linear"], ["zoom"], 5, 4, 10, 10],
        "circle-color": lineColor, // Utiliser la couleur dynamique
      },
    });
  }
}

// Fonction pour afficher toutes les trajectoires et points
function showAll(data) {
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
  const allButtons = document.querySelectorAll("#boat-menu button");
  allButtons.forEach((button) => {
    button.classList.remove("btn-active");
    button.classList.add("btn-inactive");
  });
}

// Gestion du bouton de bascule de thème
const themeToggleButton = document.getElementById("theme-toggle");
const menu = document.getElementById("menu");
themeToggleButton.addEventListener("click", () => {
  const allButtons = document.querySelectorAll("#boat-menu button");
  allButtons.forEach((button) => {
    button.classList.remove("btn-active");
    button.classList.add("btn-inactive");
  });

  const currentTrajectories = [...displayedTrajectories];
  const currentPoints = [...displayedPoints];

  currentTheme = currentTheme === "dark" ? "light" : "dark";
  map.setStyle(styles[currentTheme]);

  currentTrajectories.forEach((boat) => {
    fetch(trajectoriesGeoJSON)
      .then((response) => response.json())
      .then((data) => {
        toggleBoatTrajectory(boat, data);
      })
      .catch((error) =>
        console.error("Erreur de chargement des données GeoJSON : ", error)
      );
  });

  currentPoints.forEach((boat) => {
    fetch(pointsGeoJSON)
      .then((response) => response.json())
      .then((data) => {
        togglePoint(boat, data);
      })
      .catch((error) =>
        console.error(
          "Erreur de chargement des données GeoJSON des pointages : ",
          error
        )
      );
  });

  menu.className = currentTheme;
  themeToggleButton.textContent =
    currentTheme === "dark"
      ? "Basculer en thème clair"
      : "Basculer en thème sombre";
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

      // Récupérer les bateaux avec leur rang
      const boatsWithRangs = data.features
        .map((f) => ({
          nom: f.properties.nom,
          rang: f.properties.rang,
        }))
        .filter(
          (boat, index, self) =>
            self.findIndex((b) => b.nom === boat.nom) === index // Éliminer les doublons
        );

      // Séparer les bateaux avec rang null et non null
      const boatsWithValidRangs = boatsWithRangs.filter(
        (boat) => boat.rang !== null
      );
      const boatsWithAbandoned = boatsWithRangs.filter(
        (boat) => boat.rang === null
      );

      // Trier les bateaux ayant un rang non null (par rang croissant)
      boatsWithValidRangs.sort((a, b) => a.rang - b.rang);

      // Fusionner les bateaux avec rang valide et les bateaux abandonnés
      const sortedBoats = [...boatsWithValidRangs, ...boatsWithAbandoned];

      // Créer les boutons pour chaque bateau
      sortedBoats.forEach((boat) => {
        const button = document.createElement("button");
        button.classList.add("btn", "btn-custom", "btn-inactive");

        // Création de la structure HTML à l'intérieur du bouton
        const boatName = document.createElement("span");
        boatName.classList.add("boat-name");
        boatName.textContent = boat.nom; // Nom du bateau

        const boatRank = document.createElement("span");
        boatRank.classList.add("boat-rank");
        boatRank.textContent = boat.rang === null ? "Abandonné" : boat.rang; // Afficher "Abandonné" si rang est null

        // Ajouter les éléments au bouton
        button.appendChild(boatName);
        button.appendChild(boatRank);

        button.setAttribute("data-boat", boat.nom);

        // Fonction au clic
        button.onclick = () => {
          toggleBoatTrajectory(boat.nom, data);
          togglePoint(boat.nom, data);
        };

        boatMenu.appendChild(button);
      });
    })
    .catch((error) =>
      console.error("Erreur de chargement des données GeoJSON : ", error)
    );
});
