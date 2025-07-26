// Application JavaScript principale

document.addEventListener('DOMContentLoaded', function() {
    // Initialisation
    updateCurrentDate();
    loadStatistics();
    loadAnnonces();
    
    // Gestion du formulaire de recherche
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            loadAnnonces();
        });
    }
});

// Mettre à jour la date courante
function updateCurrentDate() {
    const now = new Date();
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        weekday: 'long'
    };
    const dateString = now.toLocaleDateString('fr-FR', options);
    const dateElement = document.getElementById('current-date');
    if (dateElement) {
        dateElement.textContent = dateString;
    }
}

// Charger les statistiques
function loadStatistics() {
    fetch('/api/statistiques')
        .then(response => response.json())
        .then(data => {
            const stats = data.statistiques;
            updateStatElement('total-annonces', stats.total_annonces);
            updateStatElement('annonces-aujourdhui', stats.annonces_aujourd_hui);
            updateStatElement('ventes', stats.ventes);
            updateStatElement('locations', stats.locations);
        })
        .catch(error => console.error('Erreur chargement statistiques:', error));
}

// Mettre à jour un élément de statistique
function updateStatElement(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = value;
    }
}

// Charger les annonces
function loadAnnonces() {
    showLoading();
    
    // Récupérer les paramètres de recherche
    const quartier = document.getElementById('quartier')?.value || '';
    const type = document.getElementById('type')?.value || '';
    const date = document.getElementById('date')?.value || 'today';
    
    // Construire l'URL avec les paramètres
    let url = '/api/annonces/du-jour';
    const params = new URLSearchParams();
    
    if (quartier) params.append('quartier', quartier);
    if (type) params.append('type', type);
    
    if (params.toString()) {
        url += '?' + params.toString();
    }
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            displayAnnonces(data.annonces);
            updateResultsInfo(data.annonces.length, quartier, type);
        })
        .catch(error => {
            console.error('Erreur chargement annonces:', error);
            showError();
        });
}

// Afficher les annonces
function displayAnnonces(annonces) {
    const container = document.getElementById('annonces-container');
    if (!container) return;
    
    if (annonces.length === 0) {
        container.innerHTML = `
            <div class="col-12 text-center py-5">
                <i class="fas fa-search fa-3x text-muted mb-3"></i>
                <h4 class="text-muted">Aucune annonce trouvée</h4>
                <p class="text-muted">Essayez de modifier vos critères de recherche</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    annonces.forEach(annonce => {
        html += createAnnonceCard(annonce);
    });
    
    container.innerHTML = html;
}

// Créer une carte d'annonce
function createAnnonceCard(annonce) {
    const prixFormate = formatPrice(annonce.prix);
    
    return `
        <div class="col-lg-4 col-md-6 col-12 mb-4 fade-in">
            <div class="card annonce-card">
                <div class="position-relative">
                    <img src="${annonce.image}" 
                         class="card-img-top annonce-image" 
                         alt="${annonce.titre}">
                    <span class="badge annonce-type type-${annonce.type}">
                        ${annonce.type === 'vente' ? 'À vendre' : 'À louer'}
                    </span>
                </div>
                <div class="card-body">
                    <h5 class="card-title">${annonce.titre}</h5>
                    <p class="card-text text-muted small">${annonce.description}</p>
                    
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="annonce-price">${prixFormate}</span>
                        <span class="badge bg-secondary">${annonce.surface}</span>
                    </div>
                    
                    <div class="d-flex justify-content-between mb-3">
                        <span class="badge badge-quartier">
                            <i class="fas fa-map-marker-alt me-1"></i>
                            ${annonce.quartier}
                        </span>
                        ${annonce.chambres > 0 ? 
                            `<span class="badge bg-info">
                                <i class="fas fa-bed me-1"></i>
                                ${annonce.chambres} ch.
                            </span>` : ''
                        }
                    </div>
                    
                    <!-- Section Contact -->
                    <div class="contact-section bg-light p-2 rounded mb-2">
                        <h6 class="mb-2 text-primary">
                            <i class="fas fa-user me-1"></i>
                            Contact
                        </h6>
                        <div class="contact-info">
                            <div class="mb-1">
                                <strong>${annonce.contact_nom || 'Propriétaire'}</strong>
                            </div>
                            <div class="contact-buttons">
                                ${annonce.contact_telephone ? 
                                    `<a href="tel:${annonce.contact_telephone}" 
                                       class="btn btn-sm btn-outline-primary me-1 mb-1">
                                        <i class="fas fa-phone me-1"></i>
                                        Appeler
                                    </a>` : ''
                                }
                                ${annonce.contact_whatsapp ? 
                                    `<a href="https://wa.me/${annonce.contact_whatsapp.replace(/\D/g, '')}" 
                                       target="_blank"
                                       class="btn btn-sm btn-outline-success me-1 mb-1">
                                        <i class="fab fa-whatsapp me-1"></i>
                                        WhatsApp
                                    </a>` : ''
                                }
                                ${annonce.contact_email ? 
                                    `<a href="mailto:${annonce.contact_email}" 
                                       class="btn btn-sm btn-outline-info mb-1">
                                        <i class="fas fa-envelope me-1"></i>
                                        Email
                                    </a>` : ''
                                }
                            </div>
                        </div>
                    </div>
                    
                    <div class="mt-3 small text-muted">
                        <i class="fas fa-calendar me-1"></i>
                        Publié le ${formatDate(annonce.date_publication)}
                    </div>
                </div>
            </div>
        </div>
    `;
}