from django.shortcuts import render
from acteur.models import Client, Fournisseur, Grossiste
from inventaire.models import Produit, Categorie
from mouvement.models import Mouvement, LigneMouvement
from notification.models import Alert, Historique
from django.contrib.auth.decorators import login_required

from mouvement.choices import TYPE_CHOICES

@login_required
def dashboard(request):
    # Récupérer des statistiques de base pour le dashboard
    client = Client.objects.all()
    fournisseur = Fournisseur.objects.all()
    grossiste = Grossiste.objects.all()
    produit = Produit.objects.all()
    categorie = Categorie.objects.all()
    mouvement = Mouvement.objects.all()
    ligne_mouvement = LigneMouvement.objects.all()
    alert = Alert.objects.all()
    historique = Historique.objects.all()
    
    # Compter le nombre d'éléments dans chaque catégorie
    stats = {
        'clients_count': client.count() if client else 0,
        'fournisseurs_count': fournisseur.count() if fournisseur else 0,
        'grossistes_count': grossiste.count() if grossiste else 0,
        'produits_count': produit.count() if produit else 0,
        'categories_count': categorie.count() if categorie else 0,
        'mouvements_count': mouvement.count() if mouvement else 0,
        'ligne_mouvements_count': ligne_mouvement.count() if ligne_mouvement else 0,
        'alerts_count': alert.count() if alert else 0,
        'historiques_count': historique.count() if historique else 0,
    }
    
    # Récupérer les dernières alertes
    recent_alerts = []
    if alert:
        recent_alerts = alert.order_by('-date')[:5]
    
    # Récupérer les derniers mouvements
    recent_mouvements = []
    if mouvement:
        recent_mouvements = mouvement.order_by('-date')[:5]
    
    # Récupérer les produits avec stock faible
    low_stock_products = []
    if produit:
        low_stock_products = produit.filter(stock__lte=5)[:5]
    
    # Données pour le graphique des mouvements par type (quantités)
    from django.db.models import Sum
    from django.utils import timezone
    import datetime
    
    # Obtenir le premier jour du mois courant
    today = timezone.now().date()
    first_day_of_month = datetime.date(today.year, today.month, 1)
    
    # Récupérer les mouvements du mois courant
    current_month_mouvements = mouvement.filter(date__gte=first_day_of_month)
    
    # Données pour le graphique des quantités par type de mouvement
    mouvements_quantite_data = {}
    if ligne_mouvement:
        for type_choice in dict(TYPE_CHOICES).keys():
            total_quantite = ligne_mouvement.filter(
                mouvement__type=type_choice,
                mouvement__date__gte=first_day_of_month
            ).aggregate(total=Sum('quantite'))['total'] or 0
            mouvements_quantite_data[type_choice] = total_quantite
    
    # Données pour le graphique des prix par type de mouvement
    mouvements_prix_data = {}
    if ligne_mouvement:
        for type_choice in dict(TYPE_CHOICES).keys():
            # Calculer le prix total en utilisant les champs réels (prix_unitaire * quantité - réduction)
            lignes = ligne_mouvement.filter(
                mouvement__type=type_choice,
                mouvement__date__gte=first_day_of_month
            )
            total_prix = 0
            for ligne in lignes:
                # Calculer le prix net pour chaque ligne (comme dans la propriété prix_net)
                prix_total_ligne = ligne.quantite * ligne.prix_unitaire
                prix_net_ligne = prix_total_ligne - ligne.reduction
                total_prix += prix_net_ligne
            
            mouvements_prix_data[type_choice] = float(total_prix)
    
    context = {
        'stats': stats,
        'recent_alerts': recent_alerts,
        'recent_mouvements': recent_mouvements,
        'low_stock_products': low_stock_products,
        'mouvements_quantite_data': mouvements_quantite_data,
        'mouvements_prix_data': mouvements_prix_data,
        'title': 'Tableau de bord'
    }
    
    return render(request, 'dashboard.html', context)
