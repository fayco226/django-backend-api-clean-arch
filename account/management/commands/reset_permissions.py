from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group, User

import importlib
from config.config import APPS_MODULE_NAMES

class Command(BaseCommand):
    help = "Supprime les permissions existantes et recrée celles définies dans les fichiers config.py des apps ciblées"

    # Liste des apps à cibler (par défaut)
    target_apps = APPS_MODULE_NAMES # Tu peux modifier cette liste ici

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("🔁 Synchronisation des permissions personnalisées..."))

        for app_label in self.target_apps:
            self.stdout.write(f"\n🧩 App: {app_label}")

            try:
                # Récupérer tous les ContentType de l'app
                content_types = ContentType.objects.filter(app_label=app_label)

                # Supprimer les permissions associées à ces content types
                perms_deleted = Permission.objects.filter(content_type__in=content_types)
                count = perms_deleted.count()
                perms_deleted.delete()
                self.stdout.write(f"🗑️  {count} permissions supprimées de l'app '{app_label}'.")

                # Supprimer aussi des groupes et users
                for group in Group.objects.all():
                    group.permissions.remove(*group.permissions.filter(content_type__in=content_types))
                for user in User.objects.all():
                    user.user_permissions.remove(*user.user_permissions.filter(content_type__in=content_types))

                # Importer le fichier config.py de l'app
                if app_label == 'auth':
                    continue
                config_module_path = f"{app_label}.config"
                config = importlib.import_module(config_module_path)

                if not hasattr(config, 'custom_permissions'):
                    self.stdout.write(self.style.WARNING(f"⚠️  Aucun 'custom_permissions' trouvé dans {config_module_path}"))
                    continue

                for perm in config.custom_permissions:
                    model = perm['model']
                    content_type = ContentType.objects.get_for_model(model)

                    Permission.objects.update_or_create(
                        codename=perm['codename'],
                        content_type=content_type,
                        defaults={'name': perm['name']}
                    )
                    self.stdout.write(self.style.SUCCESS(f"✅ Permission ajoutée: {perm['codename']} ({perm['name']})"))

            except ModuleNotFoundError:
                self.stdout.write(self.style.ERROR(f"❌ Module config.py introuvable dans '{app_label}'"))

        self.stdout.write(self.style.SUCCESS("\n🎉 Synchronisation terminée."))
