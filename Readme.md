# Django Backend API Clean Architecture

Ce projet est une API backend Django structurée selon les principes de la Clean Architecture. Il propose une gestion avancée des utilisateurs, groupes, permissions et profils, avec une séparation claire entre les couches métier, repository et présentation.

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Endpoints API](#endpoints-api)
- [Gestion des permissions](#gestion-des-permissions)
- [Tests](#tests)
- [Structure des dossiers](#structure-des-dossiers)
- [Contribuer](#contribuer)
- [Licence](#licence)

---

## Fonctionnalités

- Authentification et gestion des utilisateurs (login, logout, inscription)
- Gestion des groupes et profils
- Attribution et retrait de permissions aux utilisateurs et groupes
- API RESTful avec Django REST Framework
- Séparation des responsabilités via des repositories
- Protection CSRF et gestion des permissions API

## Architecture

Le projet suit la Clean Architecture :
- **Présentation** : Vues Django et API REST
- **Domaine** : Modèles et logique métier
- **Repository** : Accès aux données (UserRepository, GroupRepository, etc.)
- **Infrastructure** : Configuration Django, gestion des templates

## Installation

1. **Cloner le projet**
   ```bash
   git clone https://github.com/votre-utilisateur/django-backend-api-clean-arch.git
   cd django-backend-api-clean-arch
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Migrer la base de données**
   ```bash
   python manage.py migrate
   ```

5. **Créer un superutilisateur**
   ```bash
   python manage.py createsuperuser
   ```

## Configuration

- Modifier les paramètres dans `config/settings.py` selon votre environnement (base de données, email, etc.).
- Les templates HTML sont dans le dossier `templates/account/`.

## Utilisation

- **Lancer le serveur**
  ```bash
  python manage.py runserver
  ```

- Accéder à l’interface d’administration : `http://localhost:8000/admin/`
- Accéder aux endpoints API via Postman ou tout client HTTP.

## Endpoints API

| Méthode | URL                        | Description                      | Authentification |
|---------|----------------------------|----------------------------------|------------------|
| POST    | `/api/login/`              | Connexion utilisateur            | Non              |
| POST    | `/api/logout/`             | Déconnexion utilisateur          | Oui              |
| POST    | `/api/register/`           | Inscription utilisateur          | Non              |
| POST    | `/api/set_permission/`     | Ajouter/retirer une permission   | Oui              |
| POST    | `/api/set_profil/`         | Ajouter/retirer un profil/groupe | Oui              |

**Exemple de payload pour `/api/login/` :**
```json
{
  "username": "monuser",
  "password": "monmotdepasse"
}
```

## Gestion des permissions

- Les permissions sont attribuées aux utilisateurs ou groupes via les endpoints dédiés.
- Les repositories encapsulent la logique d’ajout/suppression de permissions et groupes.

## Tests

- Les tests unitaires sont à placer dans le dossier `tests/`.
- Pour lancer les tests :
  ```bash
  python manage.py test
  ```

## Structure des dossiers

```
account/
    views.py
    repository.py
    ...
config/
    settings.py
    urls.py
templates/
    account/
        login.html
        user/
        group/
        ...
Readme.md
requirements.txt
manage.py
```

## Contribuer

1. Forkez le projet
2. Créez votre branche de fonctionnalité (`git checkout -b feature/ma-fonctionnalite`)
3. Commitez vos modifications (`git commit -am 'Ajout de ma fonctionnalité'`)
4. Poussez la branche (`git push origin feature/ma-fonctionnalite`)
5. Ouvrez une Pull Request

## Licence

Ce projet est sous licence.

---

**Auteur** : Faical Lengane