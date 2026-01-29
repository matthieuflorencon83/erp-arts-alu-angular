-- =============================================================================
-- ANTIGRAVITY ERP - Database Schema
-- MySQL 8.0 Compatible
-- This file is loaded by Docker on first startup
-- =============================================================================

SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- =============================================================================
-- TABLES PRINCIPALES
-- =============================================================================

-- Clients
CREATE TABLE IF NOT EXISTS client (
    code_cli VARCHAR(50) PRIMARY KEY,
    nom_client VARCHAR(255),
    adresse TEXT,
    tel VARCHAR(50),
    mail VARCHAR(255),
    type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Fournisseurs
CREATE TABLE IF NOT EXISTS fournisseur (
    code_fournisseur VARCHAR(50) PRIMARY KEY,
    nom_fournisseur VARCHAR(255),
    adresse TEXT,
    tel VARCHAR(50),
    mail VARCHAR(255),
    contact VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Articles / Catalogue
CREATE TABLE IF NOT EXISTS article (
    code_art VARCHAR(50) PRIMARY KEY,
    designation VARCHAR(255),
    famille VARCHAR(100),
    sous_famille VARCHAR(100),
    type VARCHAR(100),
    fournisseur VARCHAR(50),
    prix_unitaire DECIMAL(10,4),
    unite VARCHAR(20),
    conditionnement VARCHAR(50),
    config_calcul JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (fournisseur) REFERENCES fournisseur(code_fournisseur) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Affaires / Projets
CREATE TABLE IF NOT EXISTS affaire (
    num_cde_vente VARCHAR(100) PRIMARY KEY,
    client_ref VARCHAR(50),
    titre VARCHAR(255),
    date_creation DATE,
    statut VARCHAR(50) DEFAULT 'en_cours',
    montant_total DECIMAL(12,2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (client_ref) REFERENCES client(code_cli) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Besoins (lignes d'affaire)
CREATE TABLE IF NOT EXISTS besoin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ref_affaire VARCHAR(100),
    code_article VARCHAR(50),
    quantite DECIMAL(10,2),
    prix_unitaire DECIMAL(10,4),
    total_ht DECIMAL(12,2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (ref_affaire) REFERENCES affaire(num_cde_vente) ON DELETE CASCADE,
    FOREIGN KEY (code_article) REFERENCES article(code_art) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Commandes (achats)
CREATE TABLE IF NOT EXISTS commande (
    num_cde VARCHAR(100) PRIMARY KEY,
    fournisseur_ref VARCHAR(50),
    affaire_ref VARCHAR(100),
    date_commande DATE,
    date_livraison_prev DATE,
    statut VARCHAR(50) DEFAULT 'brouillon',
    total_ht DECIMAL(12,2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (fournisseur_ref) REFERENCES fournisseur(code_fournisseur) ON DELETE SET NULL,
    FOREIGN KEY (affaire_ref) REFERENCES affaire(num_cde_vente) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- GED (Gestion Électronique de Documents)
CREATE TABLE IF NOT EXISTS ged (
    id VARCHAR(100) PRIMARY KEY,
    object_type VARCHAR(50),
    object_id VARCHAR(100),
    nom_fichier_org VARCHAR(255),
    nom_fichier_ged VARCHAR(255),
    chemin_complet TEXT,
    categorie_doc VARCHAR(100),
    tags TEXT,
    meta_donnee JSON,
    date_ajout DATE,
    ref_affaire VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ref_affaire) REFERENCES affaire(num_cde_vente) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- INDEX
-- =============================================================================

CREATE INDEX idx_article_famille ON article(famille);
CREATE INDEX idx_article_fournisseur ON article(fournisseur);
CREATE INDEX idx_affaire_client ON affaire(client_ref);
CREATE INDEX idx_affaire_statut ON affaire(statut);
CREATE INDEX idx_besoin_affaire ON besoin(ref_affaire);
CREATE INDEX idx_commande_affaire ON commande(affaire_ref);
CREATE INDEX idx_ged_ref ON ged(ref_affaire);

-- =============================================================================
-- DONNÉES DE TEST (à supprimer en production)
-- =============================================================================

INSERT IGNORE INTO fournisseur (code_fournisseur, nom_fournisseur, mail) VALUES
    ('INSTALLUX', 'Installux', 'contact@installux.fr'),
    ('ARCELOR', 'ArcelorMittal', 'contact@arcelor.com');

INSERT IGNORE INTO client (code_cli, nom_client, type) VALUES
    ('CLI001', 'Client Test', 'particulier'),
    ('CLI002', 'Entreprise Demo', 'professionnel');
