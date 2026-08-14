# Modèle de données — les 5 patterns

Référence pour modéliser n'importe quelle facette du projet. Toute la structure
Django, l'admin et la recherche découlent de ce fichier.

## Règle directrice

> **Recherchable ⇒ relationnel.** Toute facette sur laquelle on veut filtrer est
> une colonne, une FK, un M2M ou un through model — jamais du JSONB, jamais de l'EAV.
> Le JSONB est réservé au texte libre non filtrable.

On filtrera sur *presque tout*. Donc en cas de doute : relationnel.

## Les 5 patterns

| # | Type de champ | Exemples | Construction Django |
|---|---------------|----------|---------------------|
| 1 | Scalaire simple | nom, âge, taille, ville, tél, tour de taille | colonne sur `Profil` |
| 2 | Choix unique dans une liste | sexe, couleur des yeux, type de cheveux, niveau de français | `choices` (liste figée) ou **FK** (liste éditable) |
| 3 | Multi-valué sans attribut | permis possédés, véhicules possédés, métiers, apparences | `ManyToManyField` |
| 4 | Multi-valué **avec** attribut | sport **+ niveau**, instrument **+ niveau**, langue **+ niveau** | **through model** |
| 5 | Fichiers rattachés | photos (portrait, pied, avec/sans barbe…) | modèle séparé (one-to-many) |

Choix `choices` vs FK (pattern 2) : si la liste peut évoluer sans redéploiement
(l'admin veut ajouter une valeur), utilise une **FK vers une table de référence**.
Si elle est stable et courte (sexe, niveau), `choices` suffit.

## Squelette de référence (`backend/.../models.py`)

Un représentant par pattern. À répliquer, pas à recopier tel quel.

```python
from django.db import models


# --- Tables de référence : listes éditables sans redéploiement (patterns 3 & 4) ---
class Sport(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.nom

class Instrument(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.nom

class Langue(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.nom

class Permis(models.Model):
    code = models.CharField(max_length=10, unique=True)   # B, A, A1, A2, C, D...
    def __str__(self): return self.code

class Metier(models.Model):
    nom = models.CharField(max_length=120, unique=True)
    def __str__(self): return self.nom


# --- Choix réutilisables ---
class Niveau(models.TextChoices):          # compétences artistiques, instruments, langues
    DEBUTANT = "1", "Débutant"
    INTERMEDIAIRE = "2", "Intermédiaire"
    CONFIRME = "3", "Confirmé"
    PRO = "4", "Professionnel"

class NiveauSport(models.TextChoices):     # les sports ont une échelle à 5 crans
    DEBUTANT = "1", "Débutant"
    AMATEUR = "2", "Amateur"
    CONFIRME = "3", "Confirmé"
    COMPETITION = "4", "Compétition"
    PRO = "5", "Professionnel"


# --- Modèle central ---
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

    # Pattern 1 — scalaires
    nom = models.CharField(max_length=150)
    prenom = models.CharField(max_length=150)
    nom_artiste = models.CharField(max_length=150, blank=True)
    date_naissance = models.DateField(null=True, blank=True)
    ville = models.CharField(max_length=120, blank=True)
    departement = models.CharField(max_length=100, blank=True)
    telephone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    taille_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    tour_taille_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    distance_max_km = models.PositiveSmallIntegerField(null=True, blank=True)

    # Pattern 2 — choix unique
    sexe = models.CharField(max_length=1, choices=Sexe.choices, blank=True)
    couleur_yeux = models.CharField(max_length=20, choices=CouleurYeux.choices, blank=True)

    # champs booléens (cas particulier du choix unique) : barbe, lunettes, tatouages...
    lunettes = models.BooleanField(default=False)
    tatouages_visibles = models.BooleanField(default=False)

    # Pattern 3 — multi-valué sans attribut
    permis = models.ManyToManyField(Permis, blank=True)
    metiers = models.ManyToManyField(Metier, blank=True)

    # Pattern 4 — multi-valué AVEC attribut → via through models
    sports = models.ManyToManyField(Sport, through="ProfilSport", blank=True)
    instruments = models.ManyToManyField(Instrument, through="ProfilInstrument", blank=True)
    langues = models.ManyToManyField(Langue, through="ProfilLangue", blank=True)

    # JSONB — UNIQUEMENT le libre non filtrable (ex. note casting, remarque)
    notes = models.JSONField(default=dict, blank=True)

    def __str__(self): return f"{self.prenom} {self.nom}"


# --- Pattern 4 — les through models ---
# Base abstraite pour ne pas dupliquer profil + niveau (DRY).
class LienNiveauAbstrait(models.Model):
    profil = models.ForeignKey(Profil, on_delete=models.CASCADE)
    class Meta:
        abstract = True

class ProfilSport(LienNiveauAbstrait):
    sport = models.ForeignKey(Sport, on_delete=models.PROTECT)
    niveau = models.CharField(max_length=1, choices=NiveauSport.choices)
    class Meta:
        unique_together = ("profil", "sport")

class ProfilInstrument(LienNiveauAbstrait):
    instrument = models.ForeignKey(Instrument, on_delete=models.PROTECT)
    niveau = models.CharField(max_length=1, choices=Niveau.choices)
    class Meta:
        unique_together = ("profil", "instrument")

class ProfilLangue(LienNiveauAbstrait):
    langue = models.ForeignKey(Langue, on_delete=models.PROTECT)
    niveau = models.CharField(max_length=1, choices=Niveau.choices)
    # accent : à trancher — si un profil peut avoir un accent par langue, il vit ici ;
    # si c'est un accent global (ex. maghrébin en français), une FK sur Profil suffit.
    class Meta:
        unique_together = ("profil", "langue")


# --- Pattern 5 — photos ---
class Photo(models.Model):
    class Type(models.TextChoices):
        PORTRAIT = "portrait", "Portrait"
        PIED = "pied", "En pied"
        PROFIL = "profil", "Profil"
        SANS_BARBE = "sans_barbe", "Sans barbe"
        AVEC_BARBE = "avec_barbe", "Avec barbe"

    profil = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name="photos")
    type = models.CharField(max_length=20, choices=Type.choices)
    image = models.ImageField(upload_to="profils/%Y/%m/")
    prise_le = models.DateField(null=True, blank=True)
```

## Classification de tes catégories

Table de correspondance pour classer les ~300 champs sans réfléchir à chaque fois :

| Catégorie du cahier des charges | Pattern | Note |
|---------------------------------|---------|------|
| Infos générales (identité, contact, localisation) | 1 | scalaires |
| Sexe, couleur yeux/cheveux, type cheveux, niveau français | 2 | `choices` |
| Mensurations (taille, poids, tours…) | 1 | scalaires numériques |
| Barbe, lunettes, tatouages, piercings, chauve | 2 | `BooleanField` |
| Apparence / représentation (européenne, méditerranéenne…) | 3 | M2M référence |
| Registres visuels (élégant, business, militaire…) | 3 | M2M référence |
| **Sports + niveau** | **4** | through `ProfilSport` |
| **Compétences artistiques + niveau** | **4** | through |
| **Instruments + niveau** | **4** | through |
| **Langues + niveau (+ accent ?)** | **4** | through |
| Permis, véhicules possédés | 3 | M2M référence |
| Compétences de conduite / cascade | 3 (ou 2 booléens) | selon granularité |
| Métiers / savoir-faire | 3 | M2M référence |
| Compétences particulières (sait nager, coudre…) | 3 | M2M référence |
| Costumes / vêtements disponibles | 3 | M2M référence |
| Expérience de tournage (figuration, silhouette, pub…) | 3 | M2M référence |
| Mobilité (peut dormir sur place, transport…) | 2 | booléens |
| Composition de groupe (seul, couple, fratrie…) | 2 | `choices` |
| Mineurs (responsable légal, autorisations) | — | modèle dédié + RGPD (voir `project.md`) |
| Photos | 5 | modèle `Photo` |
| « Autre caractéristique pertinente » | JSONB | libre, non filtrable |

## Conséquences admin

Les through models (pattern 4) s'affichent en **`TabularInline`** dans l'admin →
saisir « ce profil pratique le tennis niveau confirmé » se fait directement sur la
fiche du profil, sans page séparée. C'est ce qui rend le back-office utilisable
quasi gratuitement. Détail dans `conventions-backend.md`.

## Conséquences recherche

- M2M et through → filtres par **jointure** (`profils.filter(sports__sport__nom="Tennis", profilsport__niveau__gte="3")`).
- Prévoir un **index GIN** sur les champs de recherche intensive quand le volume monte.
- Postgres suffit tant que la recherche reste rapide ; on n'ajoute Meilisearch/Typesense
  que si la latence des facettes devient un problème réel (pas avant).

## Décider où va un nouveau champ

1. Une seule valeur, pas de liste ? → **pattern 1** (colonne).
2. Une valeur choisie dans une liste ? → **pattern 2** (`choices` ou FK si éditable).
3. Plusieurs valeurs, sans info attachée ? → **pattern 3** (M2M).
4. Plusieurs valeurs **avec** une info (niveau, accent…) ? → **pattern 4** (through).
5. Un fichier ? → **pattern 5** (modèle séparé).
6. Du texte libre qu'on ne filtrera jamais ? → **JSONB**. Sinon, remonte à 1-4.