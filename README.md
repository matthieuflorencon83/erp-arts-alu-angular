# 🚀 Antigravity ERP - Arts Alu

> **Version**: 3.0.0 (Angular + Node.js + Python)  
> **Stack**: Angular 21 + Node.js/Express + Python/FastAPI + MySQL 8.0  
> **Architecture**: Monorepo Full-Stack TypeScript

---

## 📋 Table des Matières

- [🏗️ Architecture](#️-architecture)
- [⚡ Démarrage Rapide](#-démarrage-rapide)
- [🐳 Docker](#-docker)
- [🛠️ Développement](#️-développement)
- [📁 Structure du Projet](#-structure-du-projet)
- [🔐 Variables d'Environnement](#-variables-denvironnement)
- [📊 CI/CD](#-cicd)
- [📚 Documentation](#-documentation)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Angular 21 + PrimeNG 21 + Tailwind CSS 4              │    │
│  │  NgRx SignalStore • Standalone Components              │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ REST API (Zod Validated)
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND ORCHESTRATOR                          │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Node.js + Express 5 + Prisma 7                        │    │
│  │  Business Logic • API Gateway • Auth JWT               │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
               │                              │
               ▼                              ▼ Internal HTTP
┌──────────────────────────┐    ┌──────────────────────────────────┐
│      DATABASE            │    │        AI SERVICE                │
│  ┌────────────────────┐  │    │  ┌────────────────────────────┐  │
│  │  MySQL 8.0        │  │    │  │  Python + FastAPI          │  │
│  │  + Redis Cache    │  │    │  │  Calculations • ML • OCR   │  │
│  └────────────────────┘  │    │  └────────────────────────────┘  │
└──────────────────────────┘    └──────────────────────────────────┘
```

### Technologies

| Layer | Stack |
|-------|-------|
| **Frontend** | Angular 21, PrimeNG 21 (Unstyled), Tailwind CSS 4, NgRx SignalStore |
| **Backend Node** | Node.js 20+, Express 5, Prisma 7, Zod |
| **Backend Python** | Python 3.11+, FastAPI, Ruff |
| **Database** | MySQL 8.0, Redis 7 |
| **DevOps** | Docker Compose, GitHub Actions |

---

## ⚡ Démarrage Rapide

### Prérequis

- **Node.js** 20+ (`node -v`)
- **npm** 10+ (`npm -v`)
- **Python** 3.11+ (`python --version`)
- **Docker** + Docker Compose (`docker --version`)

### Installation

```bash
# 1. Cloner le repo
git clone https://github.com/matthieuflorencon83/erp-arts-alu-angular.git
cd erp-arts-alu-angular

# 2. Copier le fichier d'environnement
cp .env.example .env

# 3. Lancer les services Docker (MySQL, Redis, Adminer)
docker-compose up -d

# 4. Installer les dépendances Frontend
cd frontend-angular
npm install

# 5. Installer les dépendances Backend Node
cd ../backend-node
npm install
npx prisma generate

# 6. Installer les dépendances Backend Python
cd ../backend-python
pip install -r requirements.txt

# 7. Lancer l'application
# Terminal 1 - Frontend
cd frontend-angular && npm start

# Terminal 2 - Backend Node
cd backend-node && npm run dev

# Terminal 3 - Backend Python
cd backend-python && uvicorn main:app --reload
```

### Accès

| Service | URL |
|---------|-----|
| **Frontend Angular** | <http://localhost:4200> |
| **Backend Node API** | <http://localhost:3000> |
| **Backend Python API** | <http://localhost:8000> |
| **Adminer (MySQL UI)** | <http://localhost:8080> |

---

## 🐳 Docker

### Lancer tous les services

```bash
# Démarrer MySQL, Redis, Adminer
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter les services
docker-compose down

# Reset complet (supprime les données)
docker-compose down -v
```

### Services Docker

| Service | Port | Description |
|---------|------|-------------|
| `mysql` | 3306 | Base de données MySQL 8.0 |
| `adminer` | 8080 | Interface web pour MySQL |
| `redis` | 6379 | Cache et files d'attente |

---

## 🛠️ Développement

### Scripts Frontend (Angular)

```bash
cd frontend-angular

npm start          # Serveur de développement
npm run build      # Build production
npm run lint       # Linter ESLint
npm run format     # Formatter Prettier
npm test           # Tests unitaires
```

### Scripts Backend (Node.js)

```bash
cd backend-node

npm run dev        # Serveur avec hot-reload
npm start          # Production
npx prisma studio  # Interface BDD Prisma
npx prisma migrate # Migrations
```

### Pre-commit Hooks (Husky)

Les hooks sont automatiquement installés. Ils bloquent les commits si :

- Le code n'est pas formatté (Prettier)
- Le linter renvoie des erreurs (ESLint)

```bash
# Installation manuelle si besoin
cd frontend-angular
npm run prepare
```

---

## 📁 Structure du Projet

```
erp-arts-alu-angular/
├── frontend-angular/        # 🅰️ Application Angular
│   ├── src/
│   │   ├── app/
│   │   │   ├── core/       # Services singleton, guards
│   │   │   ├── shared/     # Components réutilisables
│   │   │   ├── modules/    # Feature modules
│   │   │   └── app.config.ts
│   │   └── styles/         # Tailwind CSS
│   ├── eslint.config.mjs
│   └── package.json
│
├── backend-node/            # 🟢 API Node.js/Express
│   ├── prisma/
│   │   └── schema.prisma   # Modèles Prisma
│   ├── src/
│   │   ├── modules/        # Business logic
│   │   ├── routes/         # Express routes
│   │   └── services/       # Data access
│   └── package.json
│
├── backend-python/          # 🐍 Service Python/FastAPI
│   ├── main.py
│   └── requirements.txt
│
├── database/                # 📊 Scripts SQL
│   └── schema.sql
│
├── .github/
│   └── workflows/
│       └── ci-quality.yml  # GitHub Actions CI/CD
│
├── docker-compose.yml       # 🐳 Services Docker
├── .env.example             # Template variables
├── .gitignore
└── README.md
```

---

## 🔐 Variables d'Environnement

Copiez `.env.example` vers `.env` et configurez :

| Variable | Description | Exemple |
|----------|-------------|---------|
| `DB_HOST` | Hôte MySQL | `localhost` |
| `DB_PORT` | Port MySQL | `3306` |
| `DB_NAME` | Nom de la base | `erp_arts_alu` |
| `DB_USER` | Utilisateur MySQL | `erp_user` |
| `DB_PASSWORD` | Mot de passe | `***` |
| `JWT_SECRET` | Secret JWT (min 32 chars) | `***` |
| `REDIS_URL` | URL Redis | `redis://localhost:6379` |

⚠️ **Ne jamais commiter le fichier `.env` !**

---

## 📊 CI/CD

### GitHub Actions

Le pipeline CI s'exécute sur chaque push/PR vers `master` :

| Job | Description |
|-----|-------------|
| 🅰️ Angular Build | `npm ci && npm run build` |
| 🟢 Node Backend | Prisma generate + syntax check |
| 🐍 Python Lint | Ruff linter |

### Badges

[![CI Quality](https://github.com/matthieuflorencon83/erp-arts-alu-angular/actions/workflows/ci-quality.yml/badge.svg)](https://github.com/matthieuflorencon83/erp-arts-alu-angular/actions)

---

## 📚 Documentation

- [Architecture Rules (v2.0)](./rules.md)
- [Prisma Schema](./backend-node/prisma/schema.prisma)
- [Angular Module Structure](./frontend-angular/src/app/modules/)

---

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/amazing-feature`)
3. Commit avec Conventional Commits (`git commit -m 'feat(module): add amazing feature'`)
4. Push vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

---

## 📄 Licence

Propriétaire - © 2026 Antigravity / Arts Alu

---

> Built with ❤️ using Angular 21, Node.js, Python, and MySQL
