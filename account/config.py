from django.contrib.auth.models import User, Group, Permission

custom_permissions = [
            # User
            {'codename': 'view_user', 'name': 'Peut voir un utilisateur', 'model': User},
            {'codename': 'add_user', 'name': 'Peut ajouter un utilisateur', 'model': User},
            {'codename': 'change_user', 'name': 'Peut modifier un utilisateur', 'model': User},
            {'codename': 'activate_user', 'name': 'Peut activer un utilisateur', 'model': User},
            {'codename': 'delete_user', 'name': 'Peut supprimer un utilisateur', 'model': User},
            {'codename': 'admin_user', 'name': 'Peut administrer un utilisateur', 'model': User},
            {'codename': 'view_user_group', 'name': 'Peut voir les profils d\'un utilisateur', 'model': User},
            {'codename': 'change_user_group', 'name': 'Peut modifier les profils d\'un utilisateur', 'model': User},
            {'codename': 'delete_user_group', 'name': 'Peut supprimer un profil à un utilisateur', 'model': User},
            {'codename': 'add_user_group', 'name': 'Peut ajouter un profil à un utilisateur', 'model': User},

            # Group
            {'codename': 'view_group', 'name': 'Peut voir un profil', 'model': Group},
            {'codename': 'add_group', 'name': 'Peut ajouter un profil', 'model': Group},
            {'codename': 'change_group', 'name': 'Peut modifier un profil', 'model': Group},
            {'codename': 'delete_group', 'name': 'Peut supprimer un profil', 'model': Group},
            {'codename': 'view_group_user', 'name': 'Peut voir les utilisateurs d\'un profil', 'model': Group},
            {'codename': 'change_group_user', 'name': 'Peut modifier les utilisateurs d\'un profil', 'model': Group},
            {'codename': 'delete_group_user', 'name': 'Peut supprimer un utilisateur d\'un profil', 'model': Group},
            {'codename': 'add_group_user', 'name': 'Peut ajouter un utilisateur à un profil', 'model': Group},

            # Permission
            {'codename': 'view_user_permission', 'name': 'Peut voir les permissions des utilisateurs', 'model': Permission},
            {'codename': 'view_group_permission', 'name': 'Peut voir les permissions des groupes', 'model': Permission},
        ]