"""Serializers de l'API.

Lecture : les champs sont listés explicitement — jamais `fields = "__all__"` sur un
profil, pour garder la main sur ce qui sort (données personnelles).

Écriture : ouverte au staff uniquement depuis l'ajout des formulaires côté front
(voir docs/decisions/0001-saisie-par-formulaires-front.md).
"""

from datetime import date

from rest_framework import serializers

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
    Registre,
    Sport,
    TypeExperience,
    TypePrestation,
    TypeVehicule,
    ZoneMobilite,
)


class ReferenceSerializer(serializers.ModelSerializer):
    """Alimente les listes du rail de filtres."""

    class Meta:
        model = None
        fields = ("id", "nom")


def _serializer_reference(modele):
    return type(
        f"{modele.__name__}Serializer",
        (ReferenceSerializer,),
        {"Meta": type("Meta", (ReferenceSerializer.Meta,), {"model": modele})},
    )


ApparenceSerializer = _serializer_reference(Apparence)
RegistreSerializer = _serializer_reference(Registre)
MetierSerializer = _serializer_reference(Metier)
CompetenceConduiteSerializer = _serializer_reference(CompetenceConduite)
CompetenceParticuliereSerializer = _serializer_reference(CompetenceParticuliere)
CostumeSerializer = _serializer_reference(Costume)
ZoneMobiliteSerializer = _serializer_reference(ZoneMobilite)
TypeExperienceSerializer = _serializer_reference(TypeExperience)
TypePrestationSerializer = _serializer_reference(TypePrestation)
TypeVehiculeSerializer = _serializer_reference(TypeVehicule)
InstrumentSerializer = _serializer_reference(Instrument)
LangueSerializer = _serializer_reference(Langue)
AccentSerializer = _serializer_reference(Accent)
CompetenceArtistiqueSerializer = _serializer_reference(CompetenceArtistique)


class SportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = ("id", "nom", "categorie")


class PermisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permis
        fields = ("id", "code", "libelle")


class DepartementSerializer(serializers.ModelSerializer):
    region = serializers.CharField(source="region.nom", read_only=True)

    class Meta:
        model = Departement
        fields = ("id", "code", "nom", "region")


class PhotoSerializer(serializers.ModelSerializer):
    # URL relative volontairement : le front est servi sur la même origine (proxy),
    # une URL absolue y réintroduirait une seconde origine dépendante du Host reçu.
    url = serializers.CharField(source="image.url", read_only=True)
    type_libelle = serializers.CharField(source="get_type_display", read_only=True)

    class Meta:
        model = Photo
        fields = ("id", "type", "type_libelle", "url", "prise_le")


# --- Liens à niveau (pattern 4) ------------------------------------------------


class ProfilSportSerializer(serializers.ModelSerializer):
    sport = serializers.CharField(source="sport.nom", read_only=True)
    niveau_libelle = serializers.CharField(source="get_niveau_display", read_only=True)

    class Meta:
        model = ProfilSport
        fields = ("sport", "niveau", "niveau_libelle")


class ProfilCompetenceArtistiqueSerializer(serializers.ModelSerializer):
    competence = serializers.CharField(source="competence.nom", read_only=True)
    niveau_libelle = serializers.CharField(source="get_niveau_display", read_only=True)

    class Meta:
        model = ProfilCompetenceArtistique
        fields = ("competence", "niveau", "niveau_libelle")


class ProfilInstrumentSerializer(serializers.ModelSerializer):
    instrument = serializers.CharField(source="instrument.nom", read_only=True)
    niveau_libelle = serializers.CharField(source="get_niveau_display", read_only=True)

    class Meta:
        model = ProfilInstrument
        fields = ("instrument", "niveau", "niveau_libelle")


class ProfilLangueSerializer(serializers.ModelSerializer):
    langue = serializers.CharField(source="langue.nom", read_only=True)
    niveau_libelle = serializers.CharField(source="get_niveau_display", read_only=True)
    accent = serializers.CharField(source="accent.nom", read_only=True, default=None)

    class Meta:
        model = ProfilLangue
        fields = ("langue", "niveau", "niveau_libelle", "accent")


class ProfilVehiculeSerializer(serializers.ModelSerializer):
    type_vehicule = serializers.CharField(source="type_vehicule.nom", read_only=True)

    class Meta:
        model = ProfilVehicule
        fields = ("type_vehicule", "marque", "modele", "annee")


# --- Profils -------------------------------------------------------------------


class LienNiveauEcritureSerializer(serializers.Serializer):
    """Une ligne de through model telle que la poste le formulaire."""

    niveau = serializers.CharField()


class SportEcritureSerializer(LienNiveauEcritureSerializer):
    sport = serializers.PrimaryKeyRelatedField(queryset=Sport.objects.all())


class LangueEcritureSerializer(LienNiveauEcritureSerializer):
    langue = serializers.PrimaryKeyRelatedField(queryset=Langue.objects.all())
    accent = serializers.PrimaryKeyRelatedField(
        queryset=Accent.objects.all(), required=False, allow_null=True
    )


class InstrumentEcritureSerializer(LienNiveauEcritureSerializer):
    instrument = serializers.PrimaryKeyRelatedField(queryset=Instrument.objects.all())


class CompetenceArtistiqueEcritureSerializer(LienNiveauEcritureSerializer):
    competence = serializers.PrimaryKeyRelatedField(queryset=CompetenceArtistique.objects.all())


class VehiculeEcritureSerializer(serializers.Serializer):
    type_vehicule = serializers.PrimaryKeyRelatedField(queryset=TypeVehicule.objects.all())
    marque = serializers.CharField(required=False, allow_blank=True)
    modele = serializers.CharField(required=False, allow_blank=True)
    annee = serializers.IntegerField(required=False, allow_null=True)


class ProfilListeSerializer(serializers.ModelSerializer):
    """Ce qu'affiche une comp card sur la planche : portrait, vitals, apparences.

    Volontairement sans coordonnées ni date de naissance : la liste sert à
    repérer un profil, pas à le contacter. L'âge est dérivé, la date reste au détail.
    """

    age = serializers.IntegerField(read_only=True)
    departement = serializers.CharField(source="departement.code", read_only=True, default=None)
    apparences = serializers.SlugRelatedField(slug_field="nom", many=True, read_only=True)
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Profil
        fields = (
            "id",
            "reference",
            "prenom",
            "nom",
            "nom_artiste",
            "sexe",
            "age",
            "ville",
            "departement",
            "taille_cm",
            "couleur_yeux",
            "couleur_cheveux",
            "apparences",
            "photos",
        )


class MineurSerializer(serializers.Serializer):
    """Présence d'un dossier mineur, sans exposer l'identité du responsable légal
    dans une réponse de recherche."""

    autorisation_parentale_signee = serializers.BooleanField(read_only=True)
    autorisation_travail_obtenue = serializers.BooleanField(read_only=True)
    disponibilite_scolaire = serializers.CharField(read_only=True)


class ProfilDetailSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(read_only=True)
    est_mineur = serializers.BooleanField(read_only=True)
    departement = DepartementSerializer(read_only=True)

    apparences = serializers.SlugRelatedField(slug_field="nom", many=True, read_only=True)
    registres = serializers.SlugRelatedField(slug_field="nom", many=True, read_only=True)
    metiers = serializers.SlugRelatedField(slug_field="nom", many=True, read_only=True)
    competences_particulieres = serializers.SlugRelatedField(
        slug_field="nom", many=True, read_only=True
    )
    costumes = serializers.SlugRelatedField(slug_field="nom", many=True, read_only=True)
    zones_mobilite = serializers.SlugRelatedField(slug_field="nom", many=True, read_only=True)
    types_experience = serializers.SlugRelatedField(slug_field="nom", many=True, read_only=True)
    prestations_acceptees = serializers.SlugRelatedField(slug_field="nom", many=True, read_only=True)
    competences_conduite = serializers.SlugRelatedField(slug_field="nom", many=True, read_only=True)
    permis = serializers.SlugRelatedField(slug_field="code", many=True, read_only=True)

    sports = ProfilSportSerializer(source="profilsport_set", many=True, read_only=True)
    competences_artistiques = ProfilCompetenceArtistiqueSerializer(
        source="profilcompetenceartistique_set", many=True, read_only=True
    )
    instruments = ProfilInstrumentSerializer(
        source="profilinstrument_set", many=True, read_only=True
    )
    langues = ProfilLangueSerializer(source="profillangue_set", many=True, read_only=True)
    vehicules = ProfilVehiculeSerializer(source="profilvehicule_set", many=True, read_only=True)

    photos = PhotoSerializer(many=True, read_only=True)
    mineur = MineurSerializer(read_only=True)

    class Meta:
        model = Profil
        fields = (
            "id",
            "reference",
            "prenom",
            "nom",
            "nom_artiste",
            "sexe",
            "age",
            "est_mineur",
            "age_apparent_min",
            "age_apparent_max",
            "telephone",
            "email",
            "ville",
            "departement",
            "distance_max_km",
            "peut_dormir_sur_place",
            "vehicule_personnel_disponible",
            "besoin_transport",
            "taille_cm",
            "poids_kg",
            "pointure",
            "taille_vetement",
            "taille_pantalon",
            "tour_poitrine_cm",
            "tour_taille_cm",
            "tour_hanches_cm",
            "couleur_yeux",
            "couleur_cheveux",
            "type_cheveux",
            "longueur_cheveux",
            "cheveux_colores",
            "barbe",
            "moustache",
            "calvitie",
            "tatouages_visibles",
            "piercings",
            "lunettes",
            "lentilles",
            "profil_multiculturel",
            "composition",
            "disponibilite",
            "deja_figurant",
            "nombre_tournages",
            "apparences",
            "registres",
            "metiers",
            "competences_particulieres",
            "costumes",
            "zones_mobilite",
            "types_experience",
            "prestations_acceptees",
            "competences_conduite",
            "permis",
            "sports",
            "competences_artistiques",
            "instruments",
            "langues",
            "vehicules",
            "photos",
            "mineur",
            "reseaux_sociaux",
            "autres_caracteristiques",
        )


class MineurEcritureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mineur
        exclude = ("id", "profil")


class ProfilEcritureSerializer(serializers.ModelSerializer):
    """Saisie d'un profil depuis le front (voir decisions/0001).

    Les through models arrivent en listes imbriquées ; DRF ne sait pas les écrire
    seul, d'où le `create`/`update` explicite plus bas.
    """

    # write_only : ces noms désignent des M2M côté modèle (`profil.sports` renvoie
    # des Sport, pas des ProfilSport). En sortie, on relit le détail du profil.
    sports = SportEcritureSerializer(many=True, required=False, write_only=True)
    langues = LangueEcritureSerializer(many=True, required=False, write_only=True)
    instruments = InstrumentEcritureSerializer(many=True, required=False, write_only=True)
    competences_artistiques = CompetenceArtistiqueEcritureSerializer(
        many=True, required=False, write_only=True
    )
    vehicules = VehiculeEcritureSerializer(many=True, required=False, write_only=True)
    mineur = MineurEcritureSerializer(required=False, allow_null=True, write_only=True)

    LIENS = {
        "sports": (ProfilSport, "sport"),
        "langues": (ProfilLangue, "langue"),
        "instruments": (ProfilInstrument, "instrument"),
        "competences_artistiques": (ProfilCompetenceArtistique, "competence"),
        "vehicules": (ProfilVehicule, "type_vehicule"),
    }

    class Meta:
        model = Profil
        exclude = ("cree_le", "date_derniere_maj")

    def validate(self, donnees):
        naissance = donnees.get("date_naissance", getattr(self.instance, "date_naissance", None))
        if naissance:
            aujourdhui = date.today()
            age = (
                aujourdhui.year
                - naissance.year
                - ((aujourdhui.month, aujourdhui.day) < (naissance.month, naissance.day))
            )
            if age < 0:
                raise serializers.ValidationError(
                    {"date_naissance": "La date de naissance est dans le futur."}
                )
            # Un mineur sans dossier = pas de responsable légal ni d'autorisation
            # traçable : c'est le point sensible du projet, on refuse plutôt qu'on devine.
            dossier = donnees.get("mineur") or getattr(self.instance, "mineur", None)
            if age < 18 and not dossier:
                raise serializers.ValidationError(
                    {
                        "mineur": "Profil de moins de 18 ans : le dossier mineur "
                        "(responsable légal, autorisations) est obligatoire."
                    }
                )

        borne_min = donnees.get("age_apparent_min")
        borne_max = donnees.get("age_apparent_max")
        if borne_min and borne_max and borne_min > borne_max:
            raise serializers.ValidationError(
                {"age_apparent_max": "L'âge apparent maximum doit être supérieur au minimum."}
            )
        return donnees

    def _ecrire_liens(self, profil, liens):
        """Remplace les lignes de through : le formulaire envoie l'état complet."""
        for cle, valeurs in liens.items():
            modele, champ_cible = self.LIENS[cle]
            modele.objects.filter(profil=profil).delete()
            modele.objects.bulk_create(
                [modele(profil=profil, **valeur) for valeur in valeurs]
            )

    def _extraire(self, donnees_validees):
        liens = {cle: donnees_validees.pop(cle) for cle in self.LIENS if cle in donnees_validees}
        m2m = {
            champ.name: donnees_validees.pop(champ.name)
            for champ in Profil._meta.many_to_many
            if champ.name in donnees_validees and champ.name not in self.LIENS
        }
        dossier = donnees_validees.pop("mineur", None)
        return liens, m2m, dossier

    def create(self, donnees_validees):
        liens, m2m, dossier = self._extraire(donnees_validees)
        profil = Profil.objects.create(**donnees_validees)
        for nom, valeurs in m2m.items():
            getattr(profil, nom).set(valeurs)
        self._ecrire_liens(profil, liens)
        if dossier:
            Mineur.objects.create(profil=profil, **dossier)
        return profil

    def update(self, profil, donnees_validees):
        liens, m2m, dossier = self._extraire(donnees_validees)
        for nom, valeur in donnees_validees.items():
            setattr(profil, nom, valeur)
        profil.save()
        for nom, valeurs in m2m.items():
            getattr(profil, nom).set(valeurs)
        self._ecrire_liens(profil, liens)
        if dossier is not None:
            Mineur.objects.update_or_create(profil=profil, defaults=dossier)
        return profil


class PhotoEcritureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ("id", "profil", "type", "image", "prise_le")


class SessionSerializer(serializers.Serializer):
    """Réponse de /api/session/ — déclarée pour que le contrat la documente.

    `utilisateur` vaut null quand personne n'est connecté : l'endpoint reste
    accessible en anonyme, car c'est lui qui pose le cookie CSRF dont la page de
    connexion a besoin pour poster.
    """

    utilisateur = serializers.CharField(read_only=True, allow_null=True)
    peut_saisir = serializers.BooleanField(read_only=True)


class ConnexionSerializer(serializers.Serializer):
    identifiant = serializers.CharField(write_only=True)
    mot_de_passe = serializers.CharField(write_only=True, style={"input_type": "password"})
