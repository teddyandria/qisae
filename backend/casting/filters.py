"""Recherche à facettes.

Deux règles structurent ce fichier (docs/conventions-backend.md) :

- contraindre **un même** lien (« tennis ET niveau ≥ confirmé ») ⇒ tout dans un
  **seul** `.filter()`, sinon Django peut satisfaire les deux conditions avec
  deux lignes différentes (tennis débutant + judo confirmé passerait) ;
- exiger **plusieurs** valeurs (« tennis ET judo ») ⇒ un `.filter()` **par valeur**.

D'où la forme des paramètres à niveau : `?sport=Tennis:3` (valeur ou `valeur:niveau_min`),
répétable pour cumuler les exigences — `?sport=Tennis:3&sport=Judo`.
"""

from datetime import date

import django_filters
from django.db.models import Q

from .models import Profil


def _date_pour_age(age):
    """Date de naissance d'une personne qui atteint exactement `age` aujourd'hui."""
    aujourdhui = date.today()
    try:
        return aujourdhui.replace(year=aujourdhui.year - age)
    except ValueError:  # né un 29 février
        return aujourdhui.replace(year=aujourdhui.year - age, day=28)


class ProfilFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filtre_texte", label="Nom, prénom ou nom d'artiste")

    # Identité / géographie
    sexe = django_filters.ChoiceFilter(choices=Profil.Sexe.choices)
    ville = django_filters.CharFilter(lookup_expr="icontains")
    departement = django_filters.CharFilter(field_name="departement__code")
    region = django_filters.CharFilter(field_name="departement__region__nom", lookup_expr="iexact")
    distance_max_km_min = django_filters.NumberFilter(
        field_name="distance_max_km", lookup_expr="gte"
    )

    # Âge réel (dérivé de la date de naissance) et âge apparent déclaré
    age_min = django_filters.NumberFilter(method="filtre_age_min")
    age_max = django_filters.NumberFilter(method="filtre_age_max")
    parait_age = django_filters.NumberFilter(
        method="filtre_parait_age", label="Âge apparent contenant cette valeur"
    )
    mineur = django_filters.BooleanFilter(method="filtre_mineur")

    # Physique
    taille_min = django_filters.NumberFilter(field_name="taille_cm", lookup_expr="gte")
    taille_max = django_filters.NumberFilter(field_name="taille_cm", lookup_expr="lte")
    couleur_yeux = django_filters.ChoiceFilter(choices=Profil.CouleurYeux.choices)
    couleur_cheveux = django_filters.ChoiceFilter(choices=Profil.CouleurCheveux.choices)
    type_cheveux = django_filters.ChoiceFilter(choices=Profil.TypeCheveux.choices)
    longueur_cheveux = django_filters.ChoiceFilter(choices=Profil.LongueurCheveux.choices)

    # Facettes à niveau — `valeur` ou `valeur:niveau_min`, répétable
    sport = django_filters.CharFilter(
        method="filtre_sport", label="Sport, éventuellement `Sport:niveau_min` (1→5)"
    )
    langue = django_filters.CharFilter(
        method="filtre_langue", label="Langue, éventuellement `Langue:niveau_min` (A1→C2, LM)"
    )
    instrument = django_filters.CharFilter(
        method="filtre_instrument", label="Instrument, éventuellement `Instrument:niveau_min` (1→4)"
    )
    competence_artistique = django_filters.CharFilter(
        method="filtre_competence_artistique",
        label="Compétence artistique, éventuellement `Compétence:niveau_min` (1→4)",
    )
    accent = django_filters.CharFilter(field_name="profillangue__accent__nom", lookup_expr="iexact")

    # Facettes sans attribut — répétables, cumulatives
    apparence = django_filters.CharFilter(method="filtre_m2m")
    registre = django_filters.CharFilter(method="filtre_m2m")
    metier = django_filters.CharFilter(method="filtre_m2m")
    competence_particuliere = django_filters.CharFilter(method="filtre_m2m")
    costume = django_filters.CharFilter(method="filtre_m2m")
    zone_mobilite = django_filters.CharFilter(method="filtre_m2m")
    type_experience = django_filters.CharFilter(method="filtre_m2m")
    prestation = django_filters.CharFilter(method="filtre_m2m")
    competence_conduite = django_filters.CharFilter(method="filtre_m2m")
    permis = django_filters.CharFilter(method="filtre_permis")

    avec_photo = django_filters.BooleanFilter(method="filtre_avec_photo")

    # Chaque facette « sans attribut » et son chemin de jointure.
    CHEMINS_M2M = {
        "apparence": "apparences__nom",
        "registre": "registres__nom",
        "metier": "metiers__nom",
        "competence_particuliere": "competences_particulieres__nom",
        "costume": "costumes__nom",
        "zone_mobilite": "zones_mobilite__nom",
        "type_experience": "types_experience__nom",
        "prestation": "prestations_acceptees__nom",
        "competence_conduite": "competences_conduite__nom",
    }

    class Meta:
        model = Profil
        fields = [
            "actif",
            "composition",
            "disponibilite",
            "deja_figurant",
            "barbe",
            "moustache",
            "calvitie",
            "tatouages_visibles",
            "piercings",
            "lunettes",
            "lentilles",
            "cheveux_colores",
            "profil_multiculturel",
            "peut_dormir_sur_place",
            "vehicule_personnel_disponible",
            "besoin_transport",
        ]

    def filter_queryset(self, queryset):
        # Les facettes traversent des M2M : sans distinct(), un profil remonte
        # autant de fois qu'il a de lignes jointes.
        return super().filter_queryset(queryset).distinct()

    # --- utilitaires ---------------------------------------------------------

    def _valeurs(self, nom):
        """Toutes les occurrences d'un paramètre répété (`?sport=A&sport=B`)."""
        donnees = self.data
        if hasattr(donnees, "getlist"):
            return [v.strip() for v in donnees.getlist(nom) if v and v.strip()]
        valeur = donnees.get(nom)
        return [valeur.strip()] if valeur and valeur.strip() else []

    def _filtre_a_niveau(self, queryset, param, chemin_valeur, chemin_niveau):
        """Un `.filter()` par valeur demandée ; valeur et niveau dans le même appel."""
        for brut in self._valeurs(param):
            valeur, _, niveau_min = brut.partition(":")
            contraintes = {f"{chemin_valeur}__iexact": valeur.strip()}
            if niveau_min.strip():
                contraintes[f"{chemin_niveau}__gte"] = niveau_min.strip()
            queryset = queryset.filter(**contraintes)
        return queryset

    # --- méthodes de filtrage ------------------------------------------------

    def filtre_texte(self, queryset, name, value):
        return queryset.filter(
            Q(nom__icontains=value)
            | Q(prenom__icontains=value)
            | Q(nom_artiste__icontains=value)
            | Q(reference__icontains=value)
        )

    def filtre_m2m(self, queryset, name, value):
        chemin = self.CHEMINS_M2M[name]
        for valeur in self._valeurs(name):
            queryset = queryset.filter(**{f"{chemin}__iexact": valeur})
        return queryset

    def filtre_permis(self, queryset, name, value):
        for code in self._valeurs("permis"):
            queryset = queryset.filter(permis__code__iexact=code)
        return queryset

    def filtre_sport(self, queryset, name, value):
        return self._filtre_a_niveau(
            queryset, "sport", "profilsport__sport__nom", "profilsport__niveau"
        )

    def filtre_langue(self, queryset, name, value):
        return self._filtre_a_niveau(
            queryset, "langue", "profillangue__langue__nom", "profillangue__niveau"
        )

    def filtre_instrument(self, queryset, name, value):
        return self._filtre_a_niveau(
            queryset,
            "instrument",
            "profilinstrument__instrument__nom",
            "profilinstrument__niveau",
        )

    def filtre_competence_artistique(self, queryset, name, value):
        return self._filtre_a_niveau(
            queryset,
            "competence_artistique",
            "profilcompetenceartistique__competence__nom",
            "profilcompetenceartistique__niveau",
        )

    def filtre_age_min(self, queryset, name, value):
        return queryset.filter(date_naissance__lte=_date_pour_age(int(value)))

    def filtre_age_max(self, queryset, name, value):
        return queryset.filter(date_naissance__gt=_date_pour_age(int(value) + 1))

    def filtre_parait_age(self, queryset, name, value):
        return queryset.filter(age_apparent_min__lte=value, age_apparent_max__gte=value)

    def filtre_mineur(self, queryset, name, value):
        limite = _date_pour_age(18)
        return queryset.filter(date_naissance__gt=limite) if value else queryset.filter(
            date_naissance__lte=limite
        )

    def filtre_avec_photo(self, queryset, name, value):
        return queryset.filter(photos__isnull=not value)
