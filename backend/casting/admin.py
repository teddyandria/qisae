"""Back-office casting.

En Phase 1 la saisie se fait à 100 % ici : les through models sont des inlines
pour qu'un profil se remplisse sans quitter sa fiche (docs/conventions-backend.md).
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Accent,
    Apparence,
    CompetenceArtistique,
    CompetenceConduite,
    CompetenceParticuliere,
    Costume,
    Departement,
    Instrument,
    Langue,
    Metier,
    Mineur,
    Permis,
    Photo,
    Profil,
    ProfilCompetenceArtistique,
    ProfilInstrument,
    ProfilLangue,
    ProfilSport,
    ProfilVehicule,
    Region,
    Registre,
    Sport,
    TypeExperience,
    TypePrestation,
    TypeVehicule,
    ZoneMobilite,
)

# =============================================================================
# Tables de référence
# `search_fields` est obligatoire ici : c'est ce qui alimente les
# `autocomplete_fields` de ProfilAdmin et des inlines.
# =============================================================================


class ReferenceAdmin(admin.ModelAdmin):
    list_display = ("nom",)
    search_fields = ("nom",)


for modele in (
    Region,
    Registre,
    Apparence,
    CompetenceConduite,
    CompetenceArtistique,
    Instrument,
    Langue,
    Accent,
    Metier,
    CompetenceParticuliere,
    Costume,
    ZoneMobilite,
    TypeExperience,
    TypePrestation,
    TypeVehicule,
):
    admin.site.register(modele, ReferenceAdmin)


@admin.register(Departement)
class DepartementAdmin(admin.ModelAdmin):
    list_display = ("code", "nom", "region")
    list_filter = ("region",)
    search_fields = ("code", "nom")
    autocomplete_fields = ("region",)


@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    list_display = ("nom", "categorie")
    list_filter = ("categorie",)
    search_fields = ("nom",)


@admin.register(Permis)
class PermisAdmin(admin.ModelAdmin):
    list_display = ("code", "libelle")
    search_fields = ("code", "libelle")


# =============================================================================
# Inlines — pattern 4 (through), pattern 5 (photos) et mineurs
# =============================================================================


class ProfilSportInline(admin.TabularInline):
    model = ProfilSport
    extra = 1
    autocomplete_fields = ("sport",)


class ProfilCompetenceArtistiqueInline(admin.TabularInline):
    model = ProfilCompetenceArtistique
    extra = 1
    autocomplete_fields = ("competence",)


class ProfilInstrumentInline(admin.TabularInline):
    model = ProfilInstrument
    extra = 1
    autocomplete_fields = ("instrument",)


class ProfilLangueInline(admin.TabularInline):
    model = ProfilLangue
    extra = 1
    autocomplete_fields = ("langue", "accent")


class ProfilVehiculeInline(admin.TabularInline):
    model = ProfilVehicule
    extra = 1
    autocomplete_fields = ("type_vehicule",)


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1
    fields = ("type", "image", "prise_le", "apercu")
    readonly_fields = ("apercu",)

    @admin.display(description="Aperçu")
    def apercu(self, obj):
        if not obj.image:
            return "—"
        return format_html('<img src="{}" style="height:80px;border-radius:4px;">', obj.image.url)


class MineurInline(admin.StackedInline):
    model = Mineur
    extra = 0
    max_num = 1
    fieldsets = (
        (
            "Responsable légal",
            {
                "fields": (
                    ("responsable_legal_prenom", "responsable_legal_nom"),
                    "responsable_legal_lien",
                    ("responsable_legal_telephone", "responsable_legal_email"),
                )
            },
        ),
        (
            "Autorisations",
            {
                "fields": (
                    ("autorisation_parentale_signee", "autorisation_parentale_le"),
                    "autorisation_travail_obtenue",
                    ("autorisation_travail_reference", "autorisation_travail_expire_le"),
                )
            },
        ),
        ("Disponibilité", {"fields": ("disponibilite_scolaire", "remarques")}),
    )


# =============================================================================
# Profil
# =============================================================================


@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "prenom",
        "nom",
        "age_affiche",
        "sexe",
        "ville",
        "departement",
        "actif",
    )
    list_filter = (
        "actif",
        "sexe",
        "departement__region",
        "departement",
        "composition",
        "disponibilite",
        "deja_figurant",
        "zones_mobilite",
        "apparences",
        "lunettes",
        "barbe",
        "tatouages_visibles",
        "peut_dormir_sur_place",
    )
    search_fields = ("nom", "prenom", "nom_artiste", "email", "reference", "ville")
    list_select_related = ("departement",)
    readonly_fields = ("cree_le", "date_derniere_maj")
    autocomplete_fields = (
        "departement",
        "registres",
        "apparences",
        "permis",
        "competences_conduite",
        "metiers",
        "competences_particulieres",
        "costumes",
        "zones_mobilite",
        "types_experience",
        "prestations_acceptees",
    )
    inlines = [
        ProfilLangueInline,
        ProfilSportInline,
        ProfilCompetenceArtistiqueInline,
        ProfilInstrumentInline,
        ProfilVehiculeInline,
        PhotoInline,
        MineurInline,
    ]
    fieldsets = (
        (
            "Identité",
            {
                "fields": (
                    "reference",
                    ("prenom", "nom"),
                    "nom_artiste",
                    "sexe",
                    "date_naissance",
                    ("age_apparent_min", "age_apparent_max"),
                )
            },
        ),
        ("Contact", {"fields": (("telephone", "email"), "reseaux_sociaux")}),
        (
            "Géographie & mobilité",
            {
                "fields": (
                    ("ville", "departement"),
                    "distance_max_km",
                    "zones_mobilite",
                    (
                        "peut_dormir_sur_place",
                        "vehicule_personnel_disponible",
                        "besoin_transport",
                    ),
                )
            },
        ),
        (
            "Physique",
            {
                "fields": (
                    ("taille_cm", "poids_kg", "pointure"),
                    ("taille_vetement", "taille_pantalon"),
                    ("tour_poitrine_cm", "tour_taille_cm", "tour_hanches_cm"),
                    "couleur_yeux",
                    ("couleur_cheveux", "type_cheveux", "longueur_cheveux", "cheveux_colores"),
                    ("barbe", "moustache", "calvitie"),
                    ("tatouages_visibles", "piercings", "lunettes", "lentilles"),
                )
            },
        ),
        (
            "Apparence & registres",
            {"fields": ("apparences", "registres", "profil_multiculturel", "autres_caracteristiques")},
        ),
        (
            "Compétences",
            {"fields": ("metiers", "competences_particulieres", "costumes")},
        ),
        (
            "Conduite",
            {"fields": ("permis", "competences_conduite")},
        ),
        (
            "Expérience & disponibilité",
            {
                "fields": (
                    "types_experience",
                    "prestations_acceptees",
                    ("deja_figurant", "nombre_tournages"),
                    "disponibilite",
                    "composition",
                )
            },
        ),
        (
            "RGPD",
            {
                "fields": (
                    ("consentement_obtenu_le", "source_consentement"),
                    "actif",
                    ("cree_le", "date_derniere_maj"),
                ),
                "description": (
                    "Base légale de la conservation du profil. Les apparences relèvent de "
                    "l'article 9 du RGPD : consentement explicite requis."
                ),
            },
        ),
        ("Notes internes", {"classes": ("collapse",), "fields": ("notes",)}),
    )

    @admin.display(description="Âge", ordering="date_naissance")
    def age_affiche(self, obj):
        age = obj.age
        if age is None:
            return "—"
        return f"{age} ans ⚠️" if obj.est_mineur else f"{age} ans"
