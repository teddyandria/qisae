"""Modèle de données casting.

Chaque champ suit un des 5 patterns de docs/data-model.md. Les sections reprennent
la numérotation de docs/cahier-des-charges.md pour garder la traçabilité entre
un critère demandé et sa colonne.
"""

from datetime import date

from django.db import models


# =============================================================================
# Échelles de niveau
# Les valeurs sont ordonnées lexicographiquement : `niveau__gte="3"` fonctionne.
# Le cahier des charges impose trois échelles distinctes (§5, §7, §8).
# =============================================================================


class NiveauSport(models.TextChoices):
    DEBUTANT = "1", "Débutant"
    AMATEUR = "2", "Amateur"
    CONFIRME = "3", "Confirmé"
    COMPETITION = "4", "Compétition"
    PRO = "5", "Professionnel"


class NiveauArtistique(models.TextChoices):
    DEBUTANT = "1", "Débutant"
    AMATEUR = "2", "Amateur"
    CONFIRME = "3", "Confirmé"
    PRO = "4", "Professionnel"


class NiveauInstrument(models.TextChoices):
    DEBUTANT = "1", "Débutant"
    INTERMEDIAIRE = "2", "Intermédiaire"
    AVANCE = "3", "Avancé"
    PRO = "4", "Professionnel"


class NiveauLangue(models.TextChoices):
    """CECRL. « LM » trie après « C2 », l'ordre reste croissant."""

    A1 = "A1", "A1 — Découverte"
    A2 = "A2", "A2 — Intermédiaire"
    B1 = "B1", "B1 — Seuil"
    B2 = "B2", "B2 — Avancé"
    C1 = "C1", "C1 — Autonome"
    C2 = "C2", "C2 — Maîtrise"
    LANGUE_MATERNELLE = "LM", "Langue maternelle"


# =============================================================================
# Tables de référence — listes éditables sans redéploiement (patterns 3 & 4)
# =============================================================================


class TableReference(models.Model):
    nom = models.CharField(max_length=120, unique=True)

    class Meta:
        abstract = True
        ordering = ["nom"]

    def __str__(self):
        return self.nom


class Region(TableReference):
    class Meta(TableReference.Meta):
        verbose_name = "région"
        verbose_name_plural = "régions"


class Departement(TableReference):
    code = models.CharField(max_length=3, unique=True)  # 01…95, 2A, 2B, 971…
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name="departements")

    class Meta(TableReference.Meta):
        ordering = ["code"]
        verbose_name = "département"
        verbose_name_plural = "départements"

    def __str__(self):
        return f"{self.code} — {self.nom}"


class Registre(TableReference):
    """§3 — élégant, business, militaire, policier…"""

    class Meta(TableReference.Meta):
        verbose_name = "registre"


class Apparence(TableReference):
    """§4 — européenne, méditerranéenne, métissée…

    Donnée relative à l'origine : catégorie particulière au sens de l'article 9
    du RGPD. Collecte soumise à consentement explicite (voir docs/projects.md §5).
    """

    class Meta(TableReference.Meta):
        verbose_name = "apparence"


class Sport(TableReference):
    class Categorie(models.TextChoices):
        COLLECTIF = "collectif", "Sport collectif"
        INDIVIDUEL = "individuel", "Sport individuel"

    categorie = models.CharField(max_length=12, choices=Categorie.choices, blank=True)

    class Meta(TableReference.Meta):
        verbose_name = "sport"


class Permis(models.Model):
    code = models.CharField(max_length=10, unique=True)  # B, A, A1, A2, C, D…
    libelle = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["code"]
        verbose_name = "permis"
        verbose_name_plural = "permis"

    def __str__(self):
        return self.code


class TypeVehicule(TableReference):
    """§6 — voiture, moto, van, véhicule de collection…"""

    class Meta(TableReference.Meta):
        verbose_name = "type de véhicule"
        verbose_name_plural = "types de véhicule"


class CompetenceConduite(TableReference):
    """§6 — conduite sportive, sur circuit, cascade auto/moto…"""

    class Meta(TableReference.Meta):
        verbose_name = "compétence de conduite"
        verbose_name_plural = "compétences de conduite"


class CompetenceArtistique(TableReference):
    """§7 — théâtre, improvisation, cascade, motion capture…"""

    class Meta(TableReference.Meta):
        verbose_name = "compétence artistique"
        verbose_name_plural = "compétences artistiques"


class Instrument(TableReference):
    class Meta(TableReference.Meta):
        verbose_name = "instrument"


class Langue(TableReference):
    class Meta(TableReference.Meta):
        verbose_name = "langue"


class Accent(TableReference):
    """§9 — parisien, marseillais, québécois, maghrébin…"""

    class Meta(TableReference.Meta):
        verbose_name = "accent"


class Metier(TableReference):
    """§10 — métier ou savoir-faire réel du profil."""

    class Meta(TableReference.Meta):
        verbose_name = "métier"


class CompetenceParticuliere(TableReference):
    """§11 — savoir-faire sans niveau associé (coudre, bricoler, échecs…).

    Ce qui se mesure par un niveau vit dans son through dédié (sport, instrument,
    compétence artistique) et ne doit pas être dupliqué ici.
    """

    class Meta(TableReference.Meta):
        verbose_name = "compétence particulière"
        verbose_name_plural = "compétences particulières"


class Costume(TableReference):
    """§13 — costume, uniforme, tenue militaire, vintage…"""

    class Meta(TableReference.Meta):
        verbose_name = "costume"


class ZoneMobilite(TableReference):
    """§14 — Paris intra-muros, Île-de-France, province, national, international."""

    class Meta(TableReference.Meta):
        verbose_name = "zone de mobilité"
        verbose_name_plural = "zones de mobilité"


class TypeExperience(TableReference):
    """§15 — figuration, silhouette parlante, publicité, long métrage…"""

    class Meta(TableReference.Meta):
        verbose_name = "type d'expérience"
        verbose_name_plural = "types d'expérience"


class TypePrestation(TableReference):
    """§15 — prestations acceptées : scène avec interaction, scène de foule…"""

    class Meta(TableReference.Meta):
        verbose_name = "type de prestation"
        verbose_name_plural = "types de prestation"


# =============================================================================
# Modèle central
# =============================================================================


class Profil(models.Model):
    class Sexe(models.TextChoices):
        HOMME = "H", "Homme"
        FEMME = "F", "Femme"
        AUTRE = "A", "Autre"

    class CouleurYeux(models.TextChoices):
        MARRON = "marron", "Marron"
        BLEU = "bleu", "Bleu"
        VERT = "vert", "Vert"
        NOISETTE = "noisette", "Noisette"
        GRIS = "gris", "Gris"
        NOIR = "noir", "Noir"

    class CouleurCheveux(models.TextChoices):
        BLOND = "blond", "Blond"
        CHATAIN = "chatain", "Châtain"
        BRUN = "brun", "Brun"
        NOIR = "noir", "Noir"
        ROUX = "roux", "Roux"
        GRIS = "gris", "Gris"
        BLANC = "blanc", "Blanc"
        COLORE = "colore", "Coloré (fantaisie)"

    class TypeCheveux(models.TextChoices):
        RAIDES = "raides", "Raides"
        ONDULES = "ondules", "Ondulés"
        BOUCLES = "boucles", "Bouclés"
        CREPUS = "crepus", "Crépus"

    class LongueurCheveux(models.TextChoices):
        COURTS = "courts", "Courts"
        MI_LONGS = "mi_longs", "Mi-longs"
        LONGS = "longs", "Longs"

    class Calvitie(models.TextChoices):
        NON = "non", "Non"
        DEGARNI = "degarni", "Dégarni"
        CHAUVE = "chauve", "Chauve"

    class TailleVetement(models.TextChoices):
        XS = "XS", "XS"
        S = "S", "S"
        M = "M", "M"
        L = "L", "L"
        XL = "XL", "XL"
        XXL = "XXL", "XXL"
        XXXL = "XXXL", "XXXL"

    class Disponibilite(models.TextChoices):
        # Valeurs provisoires : le cahier des charges ne les énumère pas.
        IMMEDIATE = "immediate", "Immédiate"
        SOUS_48H = "sous_48h", "Sous 48 h"
        WEEK_ENDS = "week_ends", "Week-ends uniquement"
        VACANCES = "vacances", "Vacances scolaires"
        SUR_DEMANDE = "sur_demande", "Sur demande"

    class Composition(models.TextChoices):
        SEUL = "seul", "Seul"
        COUPLE = "couple", "Couple"
        FRATRIE = "fratrie", "Fratrie"
        FAMILLE = "famille", "Famille"
        AMIS = "amis", "Groupe d'amis"
        DUO = "duo", "Duo"
        TRIO = "trio", "Trio"
        GROUPE_SPORTIF = "groupe_sportif", "Groupe sportif"
        GROUPE_PRO = "groupe_pro", "Groupe professionnel"

    # --- §1 Informations générales -------------------------------------------
    # null=True (et non blank seul) pour que plusieurs profils sans référence
    # cohabitent malgré la contrainte unique.
    reference = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nom = models.CharField(max_length=150)
    prenom = models.CharField(max_length=150)
    nom_artiste = models.CharField(max_length=150, blank=True)
    sexe = models.CharField(max_length=1, choices=Sexe.choices, blank=True)
    date_naissance = models.DateField(null=True, blank=True)
    age_apparent_min = models.PositiveSmallIntegerField(null=True, blank=True)
    age_apparent_max = models.PositiveSmallIntegerField(null=True, blank=True)
    telephone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    disponibilite = models.CharField(max_length=15, choices=Disponibilite.choices, blank=True)
    deja_figurant = models.BooleanField(default=False)
    nombre_tournages = models.PositiveSmallIntegerField(null=True, blank=True)

    # --- §2 Physique ---------------------------------------------------------
    taille_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    poids_kg = models.PositiveSmallIntegerField(null=True, blank=True)
    pointure = models.PositiveSmallIntegerField(null=True, blank=True)
    taille_vetement = models.CharField(max_length=4, choices=TailleVetement.choices, blank=True)
    taille_pantalon = models.PositiveSmallIntegerField(null=True, blank=True)
    tour_poitrine_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    tour_taille_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    tour_hanches_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    couleur_yeux = models.CharField(max_length=20, choices=CouleurYeux.choices, blank=True)
    couleur_cheveux = models.CharField(max_length=20, choices=CouleurCheveux.choices, blank=True)
    type_cheveux = models.CharField(max_length=20, choices=TypeCheveux.choices, blank=True)
    longueur_cheveux = models.CharField(max_length=20, choices=LongueurCheveux.choices, blank=True)
    cheveux_colores = models.BooleanField(default=False)
    barbe = models.BooleanField(default=False)
    moustache = models.BooleanField(default=False)
    calvitie = models.CharField(max_length=10, choices=Calvitie.choices, blank=True)
    tatouages_visibles = models.BooleanField(default=False)
    piercings = models.BooleanField(default=False)
    lunettes = models.BooleanField(default=False)
    lentilles = models.BooleanField(default=False)

    # --- §4 Apparence / représentation ---------------------------------------
    profil_multiculturel = models.BooleanField(default=False)

    # --- §12 Composition du groupe -------------------------------------------
    composition = models.CharField(max_length=15, choices=Composition.choices, blank=True)

    # --- §14 Géographie / mobilité -------------------------------------------
    ville = models.CharField(max_length=120, blank=True)
    departement = models.ForeignKey(
        Departement, on_delete=models.PROTECT, null=True, blank=True, related_name="profils"
    )
    distance_max_km = models.PositiveSmallIntegerField(null=True, blank=True)
    peut_dormir_sur_place = models.BooleanField(default=False)
    vehicule_personnel_disponible = models.BooleanField(default=False)
    besoin_transport = models.BooleanField(default=False)

    # --- Pattern 3 — multi-valué sans attribut -------------------------------
    registres = models.ManyToManyField(Registre, blank=True, related_name="profils")
    apparences = models.ManyToManyField(Apparence, blank=True, related_name="profils")
    permis = models.ManyToManyField(Permis, blank=True, related_name="profils")
    competences_conduite = models.ManyToManyField(
        CompetenceConduite, blank=True, related_name="profils"
    )
    metiers = models.ManyToManyField(Metier, blank=True, related_name="profils")
    competences_particulieres = models.ManyToManyField(
        CompetenceParticuliere, blank=True, related_name="profils"
    )
    costumes = models.ManyToManyField(Costume, blank=True, related_name="profils")
    zones_mobilite = models.ManyToManyField(ZoneMobilite, blank=True, related_name="profils")
    types_experience = models.ManyToManyField(TypeExperience, blank=True, related_name="profils")
    prestations_acceptees = models.ManyToManyField(
        TypePrestation, blank=True, related_name="profils"
    )

    # --- Pattern 4 — multi-valué AVEC attribut, via through models -----------
    sports = models.ManyToManyField(Sport, through="ProfilSport", blank=True, related_name="profils")
    competences_artistiques = models.ManyToManyField(
        CompetenceArtistique, through="ProfilCompetenceArtistique", blank=True, related_name="profils"
    )
    instruments = models.ManyToManyField(
        Instrument, through="ProfilInstrument", blank=True, related_name="profils"
    )
    langues = models.ManyToManyField(
        Langue, through="ProfilLangue", blank=True, related_name="profils"
    )
    vehicules = models.ManyToManyField(
        TypeVehicule, through="ProfilVehicule", blank=True, related_name="profils"
    )

    # --- RGPD : traçabilité du consentement et de la conservation ------------
    consentement_obtenu_le = models.DateField(null=True, blank=True)
    source_consentement = models.CharField(max_length=200, blank=True)
    actif = models.BooleanField(default=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    date_derniere_maj = models.DateTimeField(auto_now=True)

    # --- JSONB : libre, jamais filtré ----------------------------------------
    reseaux_sociaux = models.JSONField(default=dict, blank=True)
    autres_caracteristiques = models.JSONField(default=dict, blank=True)
    notes = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["nom", "prenom"]
        verbose_name = "profil"

    def __str__(self):
        return f"{self.prenom} {self.nom}"

    @property
    def age(self):
        if not self.date_naissance:
            return None
        aujourdhui = date.today()
        return (
            aujourdhui.year
            - self.date_naissance.year
            - ((aujourdhui.month, aujourdhui.day) < (self.date_naissance.month, self.date_naissance.day))
        )

    @property
    def est_mineur(self):
        age = self.age
        return age is not None and age < 18


# =============================================================================
# Pattern 4 — through models
# Pas de related_name sur `profil` : le query name par défaut (`profilsport__…`)
# est celui utilisé par les filtres de docs/conventions-backend.md.
# =============================================================================


class LienProfilAbstrait(models.Model):
    profil = models.ForeignKey(Profil, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class ProfilSport(LienProfilAbstrait):
    sport = models.ForeignKey(Sport, on_delete=models.PROTECT)
    niveau = models.CharField(max_length=1, choices=NiveauSport.choices)

    class Meta:
        unique_together = ("profil", "sport")
        verbose_name = "sport pratiqué"
        verbose_name_plural = "sports pratiqués"

    def __str__(self):
        return f"{self.sport} — {self.get_niveau_display()}"


class ProfilCompetenceArtistique(LienProfilAbstrait):
    competence = models.ForeignKey(CompetenceArtistique, on_delete=models.PROTECT)
    niveau = models.CharField(max_length=1, choices=NiveauArtistique.choices)

    class Meta:
        unique_together = ("profil", "competence")
        verbose_name = "compétence artistique"
        verbose_name_plural = "compétences artistiques"

    def __str__(self):
        return f"{self.competence} — {self.get_niveau_display()}"


class ProfilInstrument(LienProfilAbstrait):
    instrument = models.ForeignKey(Instrument, on_delete=models.PROTECT)
    niveau = models.CharField(max_length=1, choices=NiveauInstrument.choices)

    class Meta:
        unique_together = ("profil", "instrument")
        verbose_name = "instrument pratiqué"
        verbose_name_plural = "instruments pratiqués"

    def __str__(self):
        return f"{self.instrument} — {self.get_niveau_display()}"


class ProfilLangue(LienProfilAbstrait):
    langue = models.ForeignKey(Langue, on_delete=models.PROTECT)
    niveau = models.CharField(max_length=2, choices=NiveauLangue.choices)
    accent = models.ForeignKey(
        Accent, on_delete=models.PROTECT, null=True, blank=True
    )

    class Meta:
        unique_together = ("profil", "langue")
        verbose_name = "langue parlée"
        verbose_name_plural = "langues parlées"

    def __str__(self):
        return f"{self.langue} — {self.get_niveau_display()}"


class ProfilVehicule(LienProfilAbstrait):
    type_vehicule = models.ForeignKey(TypeVehicule, on_delete=models.PROTECT)
    marque = models.CharField(max_length=80, blank=True)
    modele = models.CharField(max_length=80, blank=True)
    annee = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("profil", "type_vehicule", "marque", "modele")
        verbose_name = "véhicule possédé"
        verbose_name_plural = "véhicules possédés"

    def __str__(self):
        return " ".join(filter(None, [str(self.type_vehicule), self.marque, self.modele]))


# =============================================================================
# Pattern 5 — photos
# =============================================================================


class Photo(models.Model):
    class Type(models.TextChoices):
        PORTRAIT = "portrait", "Portrait"
        PIED = "pied", "En pied"
        PROFIL = "profil", "Profil"
        RECENTE = "recente", "Photo récente"
        SANS_LUNETTES = "sans_lunettes", "Sans lunettes"
        AVEC_LUNETTES = "avec_lunettes", "Avec lunettes"
        CHEVEUX_ACTUELS = "cheveux_actuels", "Cheveux actuels"
        AVEC_BARBE = "avec_barbe", "Avec barbe"
        SANS_BARBE = "sans_barbe", "Sans barbe"

    profil = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name="photos")
    type = models.CharField(max_length=20, choices=Type.choices)
    image = models.ImageField(upload_to="profils/%Y/%m/")
    prise_le = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["type"]
        verbose_name = "photo"

    def __str__(self):
        return f"{self.get_type_display()} — {self.profil}"


# =============================================================================
# §12 — mineurs
# Ne porte que le spécifique : taille, expérience et mobilité restent sur Profil.
# =============================================================================


class Mineur(models.Model):
    class LienResponsable(models.TextChoices):
        MERE = "mere", "Mère"
        PERE = "pere", "Père"
        TUTEUR = "tuteur", "Tuteur légal"

    class DisponibiliteScolaire(models.TextChoices):
        VACANCES_UNIQUEMENT = "vacances", "Vacances scolaires uniquement"
        MERCREDI = "mercredi", "Mercredi et week-ends"
        HORS_TEMPS_SCOLAIRE = "hors_scolaire", "Hors temps scolaire"
        SANS_CONTRAINTE = "sans_contrainte", "Sans contrainte particulière"

    profil = models.OneToOneField(Profil, on_delete=models.CASCADE, related_name="mineur")

    responsable_legal_nom = models.CharField(max_length=150)
    responsable_legal_prenom = models.CharField(max_length=150)
    responsable_legal_lien = models.CharField(max_length=10, choices=LienResponsable.choices)
    responsable_legal_telephone = models.CharField(max_length=30, blank=True)
    responsable_legal_email = models.EmailField(blank=True)

    autorisation_parentale_signee = models.BooleanField(default=False)
    autorisation_parentale_le = models.DateField(null=True, blank=True)

    # Autorisation préalable de la commission des enfants du spectacle (DDETS).
    autorisation_travail_obtenue = models.BooleanField(default=False)
    autorisation_travail_reference = models.CharField(max_length=100, blank=True)
    autorisation_travail_expire_le = models.DateField(null=True, blank=True)

    disponibilite_scolaire = models.CharField(
        max_length=20, choices=DisponibiliteScolaire.choices, blank=True
    )
    remarques = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "mineur"

    def __str__(self):
        return f"Mineur — {self.profil}"
