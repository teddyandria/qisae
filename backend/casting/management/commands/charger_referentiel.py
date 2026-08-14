"""Remplit les tables de référence avec les listes du cahier des charges.

Idempotent : relançable sans créer de doublon. Ce sont des listes éditables ensuite
dans l'admin — la commande amorce, elle ne fait pas autorité.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from casting.models import (
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
    Permis,
    Region,
    Registre,
    Sport,
    TypeExperience,
    TypePrestation,
    TypeVehicule,
    ZoneMobilite,
)

DEPARTEMENTS = {
    "Auvergne-Rhône-Alpes": [
        ("01", "Ain"), ("03", "Allier"), ("07", "Ardèche"), ("15", "Cantal"),
        ("26", "Drôme"), ("38", "Isère"), ("42", "Loire"), ("43", "Haute-Loire"),
        ("63", "Puy-de-Dôme"), ("69", "Rhône"), ("73", "Savoie"), ("74", "Haute-Savoie"),
    ],
    "Bourgogne-Franche-Comté": [
        ("21", "Côte-d'Or"), ("25", "Doubs"), ("39", "Jura"), ("58", "Nièvre"),
        ("70", "Haute-Saône"), ("71", "Saône-et-Loire"), ("89", "Yonne"),
        ("90", "Territoire de Belfort"),
    ],
    "Bretagne": [
        ("22", "Côtes-d'Armor"), ("29", "Finistère"), ("35", "Ille-et-Vilaine"),
        ("56", "Morbihan"),
    ],
    "Centre-Val de Loire": [
        ("18", "Cher"), ("28", "Eure-et-Loir"), ("36", "Indre"), ("37", "Indre-et-Loire"),
        ("41", "Loir-et-Cher"), ("45", "Loiret"),
    ],
    "Corse": [("2A", "Corse-du-Sud"), ("2B", "Haute-Corse")],
    "Grand Est": [
        ("08", "Ardennes"), ("10", "Aube"), ("51", "Marne"), ("52", "Haute-Marne"),
        ("54", "Meurthe-et-Moselle"), ("55", "Meuse"), ("57", "Moselle"),
        ("67", "Bas-Rhin"), ("68", "Haut-Rhin"), ("88", "Vosges"),
    ],
    "Hauts-de-France": [
        ("02", "Aisne"), ("59", "Nord"), ("60", "Oise"), ("62", "Pas-de-Calais"),
        ("80", "Somme"),
    ],
    "Île-de-France": [
        ("75", "Paris"), ("77", "Seine-et-Marne"), ("78", "Yvelines"), ("91", "Essonne"),
        ("92", "Hauts-de-Seine"), ("93", "Seine-Saint-Denis"), ("94", "Val-de-Marne"),
        ("95", "Val-d'Oise"),
    ],
    "Normandie": [
        ("14", "Calvados"), ("27", "Eure"), ("50", "Manche"), ("61", "Orne"),
        ("76", "Seine-Maritime"),
    ],
    "Nouvelle-Aquitaine": [
        ("16", "Charente"), ("17", "Charente-Maritime"), ("19", "Corrèze"), ("23", "Creuse"),
        ("24", "Dordogne"), ("33", "Gironde"), ("40", "Landes"), ("47", "Lot-et-Garonne"),
        ("64", "Pyrénées-Atlantiques"), ("79", "Deux-Sèvres"), ("86", "Vienne"),
        ("87", "Haute-Vienne"),
    ],
    "Occitanie": [
        ("09", "Ariège"), ("11", "Aude"), ("12", "Aveyron"), ("30", "Gard"),
        ("31", "Haute-Garonne"), ("32", "Gers"), ("34", "Hérault"), ("46", "Lot"),
        ("48", "Lozère"), ("65", "Hautes-Pyrénées"), ("66", "Pyrénées-Orientales"),
        ("81", "Tarn"), ("82", "Tarn-et-Garonne"),
    ],
    "Pays de la Loire": [
        ("44", "Loire-Atlantique"), ("49", "Maine-et-Loire"), ("53", "Mayenne"),
        ("72", "Sarthe"), ("85", "Vendée"),
    ],
    "Provence-Alpes-Côte d'Azur": [
        ("04", "Alpes-de-Haute-Provence"), ("05", "Hautes-Alpes"), ("06", "Alpes-Maritimes"),
        ("13", "Bouches-du-Rhône"), ("83", "Var"), ("84", "Vaucluse"),
    ],
    "Guadeloupe": [("971", "Guadeloupe")],
    "Martinique": [("972", "Martinique")],
    "Guyane": [("973", "Guyane")],
    "La Réunion": [("974", "La Réunion")],
    "Mayotte": [("976", "Mayotte")],
}

SPORTS_COLLECTIFS = [
    "Football", "Rugby", "Basket", "Handball", "Volley", "Baseball", "Hockey",
    "Cricket", "Football américain",
]
SPORTS_INDIVIDUELS = [
    "Tennis", "Badminton", "Golf", "Athlétisme", "Natation", "Plongeon", "Cyclisme",
    "Escalade", "Ski", "Snowboard", "Surf", "Skateboard", "Roller", "Boxe", "MMA",
    "Judo", "Karaté", "Taekwondo", "Jiu-jitsu", "Lutte", "Escrime", "Tir à l'arc",
    "Équitation", "Danse", "Gymnastique",
]

LISTES = {
    Registre: [
        "Élégant", "Business", "Casual", "Sportif", "Streetwear", "Vintage",
        "Années 70", "Années 80", "Années 90", "Militaire", "Étudiant", "Cadre",
        "Ouvrier", "Médecin", "Avocat", "Policier", "Serveur",
    ],
    Apparence: [
        "Européenne", "Nord-africaine / moyen-orientale", "Subsaharienne",
        "Est-asiatique", "Sud-asiatique", "Latino-américaine", "Méditerranéenne",
        "Métissée",
    ],
    TypeVehicule: [
        "Voiture", "Moto", "Scooter", "Van", "Camping-car", "Vélo", "Véhicule ancien",
        "Véhicule de collection", "Véhicule électrique",
    ],
    CompetenceConduite: [
        "Conduite voiture", "Conduite moto", "Conduite scooter", "Poids lourd",
        "Véhicule ancien", "Conduite sportive", "Conduite sur circuit",
        "Cascade automobile", "Cascade moto",
    ],
    CompetenceArtistique: [
        "Théâtre", "Cinéma", "Figuration", "Silhouette", "Improvisation", "Comédie",
        "Drame", "Danse", "Chant", "Musique", "Stand-up", "Clown", "Marionnettiste",
        "Cirque", "Magie", "Acrobatie", "Cascade", "Doublure", "Motion capture",
        "Présentation / animation",
    ],
    Instrument: [
        "Piano", "Guitare", "Basse", "Batterie", "Violon", "Violoncelle", "Trompette",
        "Saxophone", "Flûte", "Clarinette", "Percussions", "Accordéon", "DJ", "Chant",
    ],
    Langue: [
        "Français", "Anglais", "Espagnol", "Portugais", "Arabe", "Italien", "Allemand",
        "Chinois", "Japonais", "Coréen", "Russe", "Turc", "Hindi",
    ],
    Accent: [
        "Français standard", "Parisien", "Marseillais", "Lyonnais", "Québécois", "Belge",
        "Suisse", "Britannique", "Américain", "Espagnol", "Portugais", "Italien",
        "Maghrébin", "Antillais", "Africain francophone",
    ],
    Metier: [
        "Médecin", "Infirmier", "Pharmacien", "Dentiste", "Avocat", "Policier",
        "Pompier", "Militaire", "Enseignant", "Journaliste", "Architecte", "Ingénieur",
        "Informaticien", "Comptable", "Commercial", "Cuisinier", "Boulanger",
        "Pâtissier", "Serveur", "Barman", "Coiffeur", "Esthéticienne", "Mécanicien",
        "Électricien", "Plombier", "Maçon", "Agriculteur", "Chauffeur", "Pilote", "Marin",
    ],
    CompetenceParticuliere: [
        "Monter à cheval", "Nager", "Plonger", "Skier", "Surf", "Roller", "Skateboard",
        "Cuisiner", "Coudre", "Bricoler", "Jardiner", "Jouer aux échecs", "Danser",
        "Faire du vélo", "Utiliser une machine professionnelle",
        "Manier une arme (cadre légal et professionnel du tournage)",
    ],
    Costume: [
        "Costume", "Smoking", "Robe de soirée", "Uniforme", "Tenue militaire",
        "Tenue sportive", "Tenue professionnelle", "Vêtements vintage", "Années 60",
        "Années 70", "Années 80", "Années 90", "Streetwear", "Luxe", "Casual",
        "Travailleur manuel", "Étudiant",
    ],
    ZoneMobilite: [
        "Paris intra-muros", "Île-de-France", "Province", "National", "International",
    ],
    TypeExperience: [
        "Première expérience", "Figuration", "Silhouette", "Silhouette parlante",
        "Petit rôle", "Rôle principal", "Publicité", "Clip", "Court métrage",
        "Long métrage", "Série", "Téléfilm", "Émission TV", "Photo", "Mode",
    ],
    TypePrestation: [
        "Figuration simple", "Silhouette", "Scène avec interaction", "Scène de foule",
    ],
}

PERMIS = [
    ("B", "Voiture"), ("A", "Moto"), ("A1", "Moto légère"), ("A2", "Moto intermédiaire"),
    ("C", "Poids lourd"), ("D", "Transport en commun"),
]


class Command(BaseCommand):
    help = "Charge les tables de référence à partir du cahier des charges (idempotent)."

    @transaction.atomic
    def handle(self, *args, **options):
        total = 0

        for region_nom, departements in DEPARTEMENTS.items():
            region, _ = Region.objects.get_or_create(nom=region_nom)
            for code, nom in departements:
                _, cree = Departement.objects.get_or_create(
                    code=code, defaults={"nom": nom, "region": region}
                )
                total += cree

        for nom in SPORTS_COLLECTIFS:
            _, cree = Sport.objects.get_or_create(
                nom=nom, defaults={"categorie": Sport.Categorie.COLLECTIF}
            )
            total += cree
        for nom in SPORTS_INDIVIDUELS:
            _, cree = Sport.objects.get_or_create(
                nom=nom, defaults={"categorie": Sport.Categorie.INDIVIDUEL}
            )
            total += cree

        for modele, valeurs in LISTES.items():
            for nom in valeurs:
                _, cree = modele.objects.get_or_create(nom=nom)
                total += cree

        for code, libelle in PERMIS:
            _, cree = Permis.objects.get_or_create(code=code, defaults={"libelle": libelle})
            total += cree

        self.stdout.write(
            self.style.SUCCESS(f"Référentiel chargé — {total} entrée(s) créée(s).")
        )
