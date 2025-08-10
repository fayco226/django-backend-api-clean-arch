from config.base_repo import BaseRepository
from django.contrib.auth.models import User, Group, Permission
from datetime import datetime
from django.contrib.auth.hashers import make_password
from config.config import APPS_MODULE_NAMES

class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)
        self.base_store_data = { 'date_joined': datetime.now()}

    def before_store(self, inputs):
        inputs['password'] = make_password(inputs['password'])
        inputs.pop('password2')
        inputs.pop('created_by')
        inputs.pop('updated_by')
        return inputs
    
    def before_save(self, id, inputs):
        if 'password' in inputs:
            inputs['password'] = make_password(inputs['password'])
            inputs.pop('password2')
        inputs.pop('updated_by')
        return inputs

    def add_group(self, id, group_id):
        user = self.model.objects.filter(id=id).first()
        if user is None:
            return
        group = Group.objects.filter(id=group_id).first()
        user.groups.add(group)
    
    def remove_group(self, id, group_id):
        user = self.model.objects.filter(id=id).first()
        if user is None:
            return
        group = Group.objects.filter(id=group_id).first()
        user.groups.remove(group)
    
    def add_permission(self, id, permission_id):
        user = self.model.objects.filter(id=id).first()
        if user is None:
            return
        permission = Permission.objects.filter(id=permission_id).first()
        user.user_permissions.add(permission)
    
    def remove_permission(self, id, permission_id):
        user = self.model.objects.filter(id=id).first()
        if user is None:
            return
        permission = Permission.objects.filter(id=permission_id).first()
        user.user_permissions.remove(permission)

class GroupRepository(BaseRepository):
    def __init__(self):
        super().__init__(Group)

    def before_store(self, inputs):
        inputs.pop('created_by')
        inputs.pop('updated_by')
        return inputs
    
    def before_save(self, id, inputs):
        inputs.pop('updated_by')
        return inputs


    def add_permission(self, id, permission_id):
        group = self.model.objects.filter(id=id).first()
        if group is None:
            return
        permission = Permission.objects.filter(id=permission_id).first()
        group.permissions.add(permission)
    
    def remove_permission(self, id, permission_id):
        group = self.model.objects.filter(id=id).first()
        if group is None:
            return
        permission = Permission.objects.filter(id=permission_id).first()
        group.permissions.remove(permission)

    def add_user(self, id, user_id):
        group = self.model.objects.filter(id=id).first()
        if group is None:
            return
        user = User.objects.filter(id=user_id).first()
        group.user_set.add(user)
    
    def remove_user(self, id, user_id):
        group = self.model.objects.filter(id=id).first()
        if group is None:
            return
        user = User.objects.filter(id=user_id).first()
        group.user_set.remove(user)

class PermissionRepository(BaseRepository):
    def __init__(self):
        super().__init__(Permission)
    
    def add_group(self, id, group_id):
        permission = self.model.objects.filter(id=id).first()
        if permission is None:
            return
        group = Group.objects.filter(id=group_id).first()
        if group is None:
            return
        permission.group_set.add(group)
    
    def remove_group(self, id, group_id):
        permission = self.model.objects.filter(id=id).first()
        if permission is None:
            return
        group = Group.objects.filter(id=group_id).first()
        permission.group_set.remove(group)

class PermissionGroupRepository(BaseRepository):
    def __init__(self):
        super().__init__(Permission)
    
    def get_all(self, options=None):
        groups = Group.objects.all()
        permissions = Permission.objects.filter(content_type__app_label__in=APPS_MODULE_NAMES)

        # Préparer la réponse
        result = []

        for perm in permissions:
            row = {
                'id': perm.id,
                'code_name': perm.codename,
                'name': perm.name,
                'app_label': perm.content_type.app_label,
                'model': perm.content_type.model
            }

            for group in groups:
                has_permission = group.permissions.filter(id=perm.id).exists()
                key = f'{group.name}'
                row[key] = f"{perm.id};{group.id};1" if has_permission else f"{perm.id};{group.id};0"
            
            result.append(row)
        
        return result
    
    def get_one(self, options):
        groups = Group.objects.all()
        permissions = Permission.objects.filter(content_type__app_label__in=APPS_MODULE_NAMES).first()

        # Préparer la réponse
        result = {
                'id': permissions.id,
                'code_name': permissions.codename,
                'name': permissions.name,
                'app_label': permissions.content_type.app_label,
                'model': permissions.content_type.model
            }

        for group in groups:
            has_permission = group.permissions.filter(id=permissions.id).exists()
            key = f'{group.name}'
            result[key] = f"{permissions.id};{group.id};1" if has_permission else f"{permissions.id};{group.id};0"
        
        return result

class PermissionUserRepository(BaseRepository):
    def __init__(self):
        super().__init__(Permission)
    
    def get_all(self, options=None):
        users = User.objects.all()
        permissions = Permission.objects.filter(content_type__app_label__in=APPS_MODULE_NAMES)

        # Préparer la réponse
        result = []

        for perm in permissions:
            row = {
                'id': perm.id,
                'code_name': perm.codename,
                'name': perm.name,
                'app_label': perm.content_type.app_label,
                'model': perm.content_type.model
            }

            for user in users:
                has_permission = user.user_permissions.filter(id=perm.id).exists()
                key = f'{user.username}'
                row[key] = f"{perm.id};{user.id};1" if has_permission else f"{perm.id};{user.id};0"
            result.append(row)
        
        return result

    def get_one(self, options):
        users = User.objects.all()
        permissions = Permission.objects.all().first()

        # Préparer la réponse
        result = {
                'id': permissions.id,
                'code_name': permissions.codename,
                'name': permissions.name,
                'app_label': permissions.content_type.app_label,
                'model': permissions.content_type.model
            }

        for user in users:
            has_permission = user.user_permissions.filter(id=permissions.id).exists()
            key = f'{user.username}'
            result[key] = f"{permissions.id};{user.id};1" if has_permission else f"{permissions.id};{user.id};0"
        
        return result