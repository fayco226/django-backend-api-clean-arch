from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django import forms


class BaseRepository:
    def __init__(self, model, fields='__all__', form=None):
        self.model = model
        self.base_filters = {}
        self.base_orders = [('id', 'asc')]
        self.base_store_data = {}
        self.base_save_data = {}
        self.fields = fields
        
        self.create_route = 'create'
        self.index_route = 'index'
        self.created_message = 'Créé !'
        self.updated_message = 'Mis à jour !'
        self.serializer = BaseSerializer(model=self.model, fields=self.fields)
        self.model_form = form if form is not None else BaseForm


    def get_all(self, options=None):
        if options is None:
            options = {}
        
        filters = {**self.base_filters, **options.get('filters', {})}
        orders = options.get('orders', self.base_orders)
        # fields = options.get('fields', ['*'])
        
        queryset = self.model.objects.filter(**filters)
        
        # Appliquer les tris
        for order in orders:
            queryset = queryset.order_by(f"{'-' if order[1] == 'desc' else ''}{order[0]}")
        
        # Compter le nombre total d'éléments si nécessaire
        total = queryset.count() if options.get('count', False) else 0
        
        # Appliquer les limites et offsets
        if 'offset' in options:
            queryset = queryset[options['offset']:]
        if 'limit' in options:
            queryset = queryset[:options['limit']]
        
        # Sérialiser les résultats
        result = self.serializer.serialize_list(queryset, model=self.model)
        
        return {'total': total, 'rows': result} if options.get('count', False) else result

    def get_one(self, options):
        filters = options.get('filters', {})
        
        try:
            # Récupérer l'objet
            instance = self.model.objects.filter(**filters).first()
            
            if instance is None:
                return None
            
            # Sérialiser l'instance
            serializer = BaseSerializer(instance=instance, model=self.model)
            return serializer.data
            
        except Exception as e:
            raise Exception(f"Erreur lors de la récupération : {str(e)}")

    def before_store(self, inputs):
        return inputs

    @transaction.atomic
    def store(self, inputs):
        # Créer un formulaire pour le modèle
        inputs = {**inputs, **self.base_store_data}
        inputs = self.before_store(inputs)
        print(inputs)
        
        isolated_data = inputs.pop('_isolated_', {})
        
        form = self.model_form.create_for_model(self.model, data=inputs)
        
        # validé les données
        if form.is_valid():
            
            # Enregistrer l'instance
            instance = form.save()
            
            if isolated_data:
                inputs['_isolated_'] = isolated_data
            
            # Sérialiser l'instance avec notre BaseSerializer
            serializer = BaseSerializer(instance=instance, model=self.model)
            instance_dict = serializer.data
            # print(instance_dict)
            inputs['_store_'] = instance_dict
            # model_instance = get_object_or_404(self.model, pk=instance_dict['pk'])
            
            # if model_instance:
            # inputs['_model_'] = model_instance
            
            
            return self.after_store(inputs)
        else:
            # Gérer les erreurs de validation
            raise ValueError(form.errors)
        
        
        
        # validé les données d'entrée
        # instance = self.model(**inputs)
        # instance.save()
           

    def after_store(self, inputs):
        return inputs['_store_']

    def before_save(self, id, inputs):
        return inputs

    @transaction.atomic
    def save(self, id, inputs):
        inputs = self.before_save(id, inputs)
        
        inputs = {**inputs, **self.base_save_data}
        
        # Récupérer l'instance existante
        instance = self.model.objects.filter(id=id).first()
        if not instance:
            raise ObjectDoesNotExist("Instance non trouvée")
        
        # Extraire les données isolées avant de créer le formulaire
        isolated_data = inputs.pop('_isolated_', {})
        
        try:
            # Créer un formulaire pour la mise à jour avec l'instance existante
            # Utiliser instance=instance pour indiquer qu'il s'agit d'une mise à jour
            # Utiliser data=inputs pour les nouvelles valeurs
            form = self.model_form.create_for_model(
                self.model,
                data=inputs,
                instance=instance,
                # Spécifier les champs à mettre à jour (uniquement ceux présents dans inputs)
                fields=list(inputs.keys())
            )
            
            # Vérifier si le formulaire est valide
            if form.is_valid():
                # Enregistrer les modifications
                updated_instance = form.save()
                
                # Restaurer les données isolées si nécessaire
                if isolated_data:
                    inputs['_isolated_'] = isolated_data
                
                # Sérialiser et retourner l'instance mise à jour
                serializer = BaseSerializer(instance=updated_instance, model=self.model, fields=self.fields)
                instance_dict = serializer.data
                
                inputs['_save_'] = instance_dict
                
                # model_instance = get_object_or_404(self.model, pk=instance_dict['id'])
                # print(model_instance.description)
                # if model_instance:
                # inputs['_model_instance_'] = model_instance
                
                return self.after_save(id, inputs)
            else:
                # Renvoyer les erreurs de validation du formulaire
                raise ValueError(form.errors)
        except Exception as e:
            # Capturer et renvoyer les autres erreurs
            raise ValueError(str(e))

    def after_save(self, id, inputs):
        return inputs['_save_']

    def before_delete(self, id, options):
        return options

    @transaction.atomic
    def delete(self, id):
        options = {'filters': {'id': id}, 'fields': ['*']}
        options = self.before_delete(id, options)
        
        instance = self.get_one(options)
        
        if not instance:
            raise ObjectDoesNotExist("Instance non trouvée")
        
        get_object_or_404(self.model, pk=id).delete()
        
        return self.after_delete(id, {'id': id}, options)

    def after_delete(self, id, output, options):
        return output

    def validate(self, id):
        self.model.objects.filter(id=id).update(etat='valide')  # Assurez-vous d'avoir un champ 'etat'

    def activate(self, id):
        self.model.objects.filter(id=id).update(statut='actif')  # Assurez-vous d'avoir un champ 'statut'

    def cancel(self, id):
        self.model.objects.filter(id=id).update(statut='inactif')  # Assurez-vous d'avoir un champ 'statut'


class BaseSerializer(serializers.ModelSerializer):
    """
    Sérialiseur de base dynamique qui peut être utilisé avec n'importe quel modèle Django.
    Les classes filles peuvent spécifier leurs propres champs en définissant une classe Meta.
    Inclut automatiquement les propriétés (@property) du modèle dans la sérialisation.
    """
    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model', None)
        self.fields_to_use = kwargs.pop('fields', None)
        
        if self.model:
            # Définir dynamiquement la classe Meta pour le modèle spécifié
            self.Meta.model = self.model
        
        # Si des champs spécifiques sont fournis, les utiliser
        if self.fields_to_use:
            self.Meta.fields = self.fields_to_use
            
        super().__init__(*args, **kwargs)

    class Meta:
        model = None
        fields = '__all__'
        
    def get_field_names(self, declared_fields, info):
        """
        Surcharge de la méthode get_field_names pour inclure les propriétés du modèle.
        """
        field_names = super().get_field_names(declared_fields, info)
        
        # Si le modèle est défini et que nous utilisons tous les champs ou si le champ est spécifiquement demandé
        if self.Meta.model and (self.Meta.fields == '__all__' or isinstance(self.Meta.fields, (list, tuple))):
            # Récupérer toutes les propriétés du modèle
            property_names = []
            for name in dir(self.Meta.model):
                # Vérifier si c'est une propriété
                if isinstance(getattr(self.Meta.model, name, None), property):
                    # Si nous utilisons tous les champs ou si la propriété est dans la liste des champs
                    if self.Meta.fields == '__all__' or name in self.Meta.fields:
                        property_names.append(name)
            
            # Ajouter les propriétés aux champs
            field_names = list(field_names) + property_names
        
        return field_names
        
    def to_representation(self, instance):
        """
        Convertit une instance de modèle en une représentation sérialisable.
        Inclut les propriétés du modèle.
        """
        # Utiliser l'implémentation de base pour la plupart des cas
        data = super().to_representation(instance)
        
        # Ajouter les propriétés du modèle
        if hasattr(instance, '__class__'):
            for name in dir(instance.__class__):
                if isinstance(getattr(instance.__class__, name, None), property):
                    # Si nous utilisons tous les champs ou si la propriété est dans la liste des champs
                    if self.Meta.fields == '__all__' or (isinstance(self.Meta.fields, (list, tuple)) and name in self.Meta.fields):
                        # Ajouter la valeur de la propriété
                        try:
                            data[name] = getattr(instance, name)
                        except Exception as e:
                            # En cas d'erreur, mettre None
                            print(e)
                            data[name] = None
        
        # Traitement spécial pour les relations
        for field_name, field in self.fields.items():
            if isinstance(field, serializers.RelatedField) and field_name in data and data[field_name] is not None:
                # Ajouter une représentation plus riche pour les relations
                related_obj = getattr(instance, field_name)
                if related_obj:
                    data[field_name] = data[field_name]
                    data[field_name + '_obj'] = {
                        'id': data[field_name],  # L'ID est déjà sérialisé
                        'str': str(related_obj)  # Ajouter la représentation en chaîne
                    }
        
        # Traitement spécial pour les champs de fichiers
        for field_name, field in self.fields.items():
            if isinstance(field, serializers.FileField) and field_name in data and data[field_name]:
                # S'assurer que l'URL complète est utilisée
                data[field_name] = self.context.get('request').build_absolute_uri(data[field_name]) if self.context.get('request') else data[field_name]
        
        return data

    @classmethod
    def serialize_list(cls, object_list, model=None):
        """
        Sérialise une liste d'objets ou un objet unique en utilisant le sérialiseur approprié.
        """
        if object_list is None:
            return None
            
        if isinstance(object_list, list):
            return object_list
        
        # Déterminer le modèle à utiliser
        if model is None and hasattr(object_list, '_meta'):
            model = object_list._meta.model
        elif model is None and hasattr(object_list, 'model'):
            model = object_list.model
        
        # Vérifier si c'est un objet unique ou une collection
        is_single_object = hasattr(object_list, '_meta') and not hasattr(object_list, '__iter__')
        
        # Créer une instance du sérialiseur avec le modèle approprié
        serializer = cls(instance=object_list, many=not is_single_object, model=model)
        return serializer.data


class BaseForm(forms.ModelForm):
    """Formulaire de base dynamique pour validé les données avant l'enregistrement ou la mise à jour"""
    
    def __init__(self, *args, **kwargs):
        self.model_class = kwargs.pop('model_class', None)
        super().__init__(*args, **kwargs)
        
        # Personnaliser les widgets et les validations si nécessaire
        for field_name, field in self.fields.items():
            # Ajouter des classes CSS pour le styling
            field.widget.attrs['class'] = 'form-control'
            
            # Ajouter des attributs data pour le JavaScript
            field.widget.attrs['data-field'] = field_name
    
    @classmethod
    def create_for_model(cls, model_class, *args, **kwargs):
        """Crée dynamiquement un formulaire pour le modèle spécifié"""
        
        # Créer une classe Meta dynamique
        meta_attrs = {
            'model': model_class,
            'fields': '__all__',  # Par défaut, inclure tous les champs
            # 'exclude': ['created_at', 'updated_at', 'created_by', 'updated_by']  # Exclure les champs automatiques
            'exclude': ['created_at', 'updated_at']  # Exclure les champs automatiques
        }
        
        # Personnaliser les champs à inclure si spécifiés
        if 'fields' in kwargs:
            meta_attrs['fields'] = kwargs.pop('fields')
        
        # Personnaliser les champs à exclure si spécifiés
        if 'exclude' in kwargs:
            meta_attrs['exclude'] = kwargs.pop('exclude')
        
        # Créer la classe Meta
        Meta = type('Meta', (), meta_attrs)
        
        # Créer la classe de formulaire dynamique
        form_class_name = f"{model_class.__name__}Form"
        form_class = type(form_class_name, (cls,), {'Meta': Meta})
        
        # Créer une instance du formulaire
        return form_class(*args, **kwargs, model_class=model_class)
    
    def clean(self):
        """Validation personnalisée pour le formulaire entier"""
        cleaned_data = super().clean()
        
        # Vous pouvez ajouter des validations personnalisées ici
        # Par exemple, vérifier que la date de début est antérieure à la date de fin
        
        return cleaned_data
    
    def save(self, commit=True):
        """Enregistre le formulaire et retourne l'instance du modèle"""
        instance = super().save(commit=False)
        
        # Vous pouvez ajouter des traitements personnalisés ici
        # Par exemple, définir des champs calculés ou des valeurs par défaut
        
        if commit:
            instance.save()
        
        return instance