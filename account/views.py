from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from acteur.views import BaseView
from .repository import UserRepository, GroupRepository, PermissionGroupRepository, PermissionUserRepository
from django.http import JsonResponse
from django.contrib.auth.models import User, Group
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login as dj_login, logout as dj_logout, authenticate
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def login(request):
    auth.logout(request)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'Connexion succès')
            return redirect('dashboard')
        else:
            messages.warning(request, 'Données invalides')
            return redirect('login')
    else:
        return render(request, 'account/login.html')

@login_required
def logout(request):
    auth.logout(request)
    messages.success(request, 'déconnexion réussie')
    return redirect('login')


class AccountView(BaseView):
    
    
    
    def index(self, request, ressource=None):
        auth = self.check_authentication(request)
        if auth:
            return auth
        data = {'current_page': ressource}

        if ressource == 'permissions_users':
            users = User.objects.all()
            data['users_names'] = ""
            for user in users:
                data['users_names'] += f"{user.username}" if user == users.last() else f"{user.username};"
        if ressource == 'permissions_groups':
            groups = Group.objects.all()
            data['groups_names'] = ""
            for group in groups:
                data['groups_names'] += f"{group.name}" if group == groups.last() else f"{group.name};"
        return render(request, self.get_index(self.get_url_element(request,'ressource')), data)
    
    
    def display(self, request, id=None):
        auth = self.check_authentication(request)
        if auth:
            return auth
        repository = self.get_repository(self.get_url_element(request,'ressource'))
        options = {
            'filters': {'id': self.get_url_element(request,'id')},
            'fields': ['*']
        }
        
        try:
            data = repository.get_one(options)
            return render(request, f'acteur/{self.get_index(request.GET.get("ressource"))}/display/index.html', {
                'id': self.get_url_element(request,'id'),
                'ressource': self.get_url_element(request,'ressource'),
                'data': data
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def set_permission(self, request, ressource=None):
        auth = self.check_authentication(request)
        if auth:
            return auth
        if(ressource == 'users'):
            try:
                user_id = request.POST.get('user_id')
                permission_id = request.POST.get('permission_id')
                statut = request.POST.get('statut')
                repository = self.get_repository('users')
                if(statut == 1 or statut == '1'):
                    repository.add_permission(user_id, permission_id)
                else:
                    repository.remove_permission(user_id, permission_id)
                return JsonResponse({'status': 'success', 'message': 'Permission ajoutée avec succès'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        
        if(ressource == 'groups'):
            try:
                group_id = request.POST.get('group_id')
                permission_id = request.POST.get('permission_id')
                statut = request.POST.get('statut')
                repository = self.get_repository('groups')
                if(statut == 1 or statut == '1'):
                    repository.add_permission(group_id, permission_id)
                else:
                    repository.remove_permission(group_id, permission_id)
                return JsonResponse({'status': 'success', 'message': 'Permission ajoutée avec succès'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    def set_profil(self, request, ressource=None):
        auth = self.check_authentication(request)
        if auth:
            return auth
        if(ressource == 'users'):
            try:
                user_id = request.POST.get('user_id')
                group_id = request.POST.get('group_id')
                statut = request.POST.get('statut')
                repository = self.get_repository('users')
                if(statut == 1 or statut == '1'):
                    repository.add_group(user_id, group_id)
                else:
                    repository.remove_group(user_id, group_id)
                return JsonResponse({'status': 'success', 'message': 'Profil ajoutée avec succès'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        
        if(ressource == 'groups'):
            try:
                group_id = request.POST.get('group_id')
                user_id = request.POST.get('user_id')
                statut = request.POST.get('statut')
                repository = self.get_repository('groups')
                if(statut == 1 or statut == '1'):
                    repository.add_user(group_id, user_id)
                else:
                    repository.remove_user(group_id, user_id)
                return JsonResponse({'status': 'success', 'message': 'Profil ajoutée avec succès'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        
    
    def get_repository(self, ressource):
        if ressource == 'users':
            return UserRepository()
        elif ressource == 'groups':
            return GroupRepository()
        elif ressource == 'profils':
            return GroupRepository()
        elif ressource == 'permissions_groups':
            return PermissionGroupRepository()
        elif ressource == 'permissions_users':
            return PermissionUserRepository()
        else:
            return None
        
    def get_index(self, ressource):
        if ressource == 'users':
            return 'account/user/index.html'
        elif ressource == 'groups':
            return 'account/group/index.html'
        elif ressource == 'profils':
            return 'account/profil/index.html'
        elif ressource == 'permissions_groups':
            return 'account/permission_group/index.html'
        elif ressource == 'permissions_users':
            return 'account/permission_user/index.html'
        else:
            return None
    
    @csrf_exempt
    @api_view(['POST'])
    @permission_classes([AllowAny])
    def api_login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            dj_login(request, user)
            return Response({'message': 'Connexion réussie'}, status=status.HTTP_200_OK)
        return Response({'error': 'Identifiants invalides'}, status=status.HTTP_401_UNAUTHORIZED)

    @csrf_exempt
    @api_view(['POST'])
    def api_logout(self, request):
        dj_logout(request)
        return Response({'message': 'Déconnexion réussie'}, status=status.HTTP_200_OK)

    @csrf_exempt
    @api_view(['POST'])
    @permission_classes([AllowAny])
    def api_register(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Nom d\'utilisateur déjà utilisé'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(username=username, password=password, email=email)
        user.save()
        return Response({'message': 'Utilisateur créé avec succès'}, status=status.HTTP_201_CREATED)
