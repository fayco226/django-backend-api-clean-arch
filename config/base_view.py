from django.db import transaction
from django.http import JsonResponse
import json
from rest_framework import viewsets
from django.contrib.auth.views import redirect_to_login

def set_default_options(options):
    results = {
        'filters': {},
        'fields': [],
        # 'count': False,
        # 'offset': 0,
        # 'limit': 100,
    }

    # Traitement des filtres (liste de "clé,valeur")
    if 'filters' in options and isinstance(options['filters'], list):
        for value in options['filters']:
            if isinstance(value, str) and ',' in value:
                key, val = value.split(',', 1)
                results['filters'][key.strip()] = val.strip()

    # Traitement des fields
    if 'fields' in options:
        if isinstance(options['fields'], str):
            results['fields'] = [f.strip() for f in options['fields'].split(',')]
        elif isinstance(options['fields'], list):
            results['fields'] = [f.strip() for f in options['fields']]
        else:
            results['fields'] = ['*']  # par défaut

    return results

        

def extract_form_data(request_data):
    """Extrait les données du formulaire au format data[field_name] en un dictionnaire"""
    data = {}
    for key, value in request_data.items():
        if key.startswith('data[') and key.endswith(']'):
            # Extraire le nom du champ de la clé 'data[nom_champ]'
            field_name = key[5:-1]  # Enlever 'data[' et ']'
            data[field_name] = value
    return data


class BaseView( viewsets.ViewSet):
    
    def get_repository(self, ressource):
        raise NotImplementedError("Cette méthode doit être implémentée dans les classes filles")
    
    def check_authentication(self, request):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        return None

    
    def get_url_element(self, request, element):
        return request.resolver_match.kwargs.get(element)

    def get_one(self, request, **kwargs):
        repository = self.get_repository(self.get_url_element(request,'ressource'))
        filters_raw = request.GET.get('filters[]', '[]')  # en tant que chaîne JSON
        options = {
            'filters': json.loads(filters_raw),  # <- ici, plus d'erreur
            'fields': request.GET.get('fields', '').split(',') if request.GET.get('fields') else ['*']
        }
        options = set_default_options(options)
        try:
            result = repository.get_one(options)
            return JsonResponse(result, safe=False)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': "Une erreur est survenue lors de la recuperation des donnees : "+str(e)}, status=500)

    def get_many(self, request, **kwargs):
        ressource = self.get_url_element(request,'ressource')
        repository = self.get_repository(ressource)
        
        options = {
            'filters': request.GET.getlist('filters[]', []),
            'fields': request.GET.getlist('fields', []),
            # 'count': request.GET.get('count') == 'true',
            # 'offset': int(request.GET.get('offset', 0)),
            # 'limit': int(request.GET.get('limit', 100))
        }
        options = set_default_options(options)
        try:
            result = repository.get_all(options)
            return JsonResponse(result, safe=False)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': "Une erreur est survenue lors de la recuperation des donnees : "+str(e)}, status=500)

    @transaction.atomic
    def store(self, request, ressource=None):
        ressource = request.resolver_match.kwargs.get('ressource')
        repository = self.get_repository(ressource)
        
        # Traitement des données du formulaire
        # data = extract_form_data(request.POST)
        data = request.POST.dict()
        data['created_by'] = request.user.username  # Ajoutez l'utilisateur courant aux données
        data['updated_by'] = request.user.username  # Ajoutez l'utilisateur courant aux données
        
        try:
            entity = repository.store(data)
            return JsonResponse({'status': 'success', ressource: entity})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': "Une erreur est survenue lors de la creation: "+str(e)}, status=500)

    @transaction.atomic
    def save(self, request, ressource=None, id=None):
        repository = self.get_repository(self.get_url_element(request,'ressource'))
        instance_id = self.get_url_element(request,'id')
        
        # Traitement des données du formulaire
        # data = extract_form_data(request.POST)
        data = request.POST.dict()  # Ajoutez l'utilisateur courant aux données
        data['updated_by'] = request.user.username 
        # data['_user'] = request.user  # Ajoutez l'utilisateur courant aux données
        
        try:
            entity = repository.save(instance_id, data)
            return JsonResponse({'status': 'success', self.get_url_element(request,'ressource'): entity})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': "Une erreur est survenue lors de la modification: "+str(e)}, status=500)

    @transaction.atomic
    def delete(self, request, ressource=None, id=None):
        repository = self.get_repository(self.get_url_element(request,'ressource'))
        instance_id = self.get_url_element(request,'id')
        
        try:
            repository.delete(instance_id)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': "Une erreur est survenue lors de la suppression(L'element que vous essayer de supprimer est peut etre utiliser dans le systeme): "+str(e)}, status=500)

    def get_criterias(self, ressource):
        return []