from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

import importlib
from config.config import APPS_MODULE_NAMES

class Command(BaseCommand):
    help = "Ajout des permissions manquantes"

    # Liste des apps à cibler (par défaut)
    target_apps = APPS_MODULE_NAMES # Tu peux modifier cette liste ici

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("🔁 Synchronisation des permissions ..."))

        for app_label in self.target_apps:
            self.stdout.write(f"\n🧩 App: {app_label}")

            try:
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

                    if Permission.objects.filter(codename=perm['codename'], content_type=content_type).exists():
                        self.stdout.write(self.style.WARNING(f"⚠️  Permission '{perm['codename']}' déjà existante dans {config_module_path}"))
                        continue

                    Permission.objects.update_or_create(
                        codename=perm['codename'],
                        content_type=content_type,
                        defaults={'name': perm['name']}
                    )
                    self.stdout.write(self.style.SUCCESS(f"✅ Permission ajoutée: {perm['codename']} ({perm['name']})"))

            except ModuleNotFoundError:
                self.stdout.write(self.style.ERROR(f"❌ Module config.py introuvable dans '{app_label}'"))

        self.stdout.write(self.style.SUCCESS("\n🎉 Synchronisation terminée."))
