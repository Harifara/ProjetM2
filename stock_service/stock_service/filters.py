import django_filters
from .models import Magasin

class MagasinFilter(django_filters.FilterSet):
    """
    Permet de filtrer les magasins selon différents champs.
    Exemple : ?nom__icontains=central&district_id=UUID
    """
    class Meta:
        model = Magasin
        fields = {
            "nom": ["icontains"],
            "district_id": ["exact"],
            "is_active": ["exact"],
        }
