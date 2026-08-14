"""Jeu de données fictif pour faire tourner la recherche en local.

Tous les profils créés portent une référence `DEMO-xxx` : ce sont des personnes
inventées et des images générées, jamais des données réelles. `--reset` les
supprime sans toucher au reste de la base.
"""

import random
from datetime import date, timedelta
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from PIL import Image, ImageDraw, ImageFont

from casting.models import (
    Accent,
    Apparence,
    CompetenceArtistique,
    CompetenceParticuliere,
    Costume,
    Departement,
    Instrument,
    Langue,
    Metier,
    Mineur,
    NiveauArtistique,
    NiveauInstrument,
    NiveauLangue,
    NiveauSport,
    Permis,
    Photo,
    Profil,
    ProfilCompetenceArtistique,
    ProfilInstrument,
    ProfilLangue,
    ProfilSport,
    Registre,
    Sport,
    TypeExperience,
    TypePrestation,
    ZoneMobilite,
)

PRENOMS_F = [
    "Alice", "Nadia", "Lucie", "Fatou", "Camille", "Mei", "Sofia", "Inès", "Clara",
    "Awa", "Léa", "Priya", "Chloé", "Yasmine", "Manon",
]
PRENOMS_H = [
    "Karim", "Thomas", "Ibrahim", "Lucas", "Wei", "Mathieu", "Diego", "Antoine",
    "Rachid", "Julien", "Amir", "Paul", "Kofi", "Nicolas", "Hugo",
]
NOMS = [
    "Durand", "Benali", "Nguyen", "Martin", "Diallo", "Rossi", "Lefèvre", "Silva",
    "Traoré", "Moreau", "Chen", "Garcia", "Dubois", "Haddad", "Petit", "Fontaine",
    "Okonkwo", "Marchand", "Ferrari", "Bernard",
]

# Fonds sourds et légèrement colorés : chaque fiche se distingue sur la planche
# sans virer au bariolé, et le sujet reste plus clair que son fond.
FONDS = [
    (58, 63, 78), (72, 66, 60), (54, 70, 68), (68, 58, 72),
    (46, 58, 76), (74, 62, 58), (52, 66, 58), (64, 60, 78),
]
SUJET = (196, 198, 206)
ENCRE_CLAIRE = (245, 245, 247)
ANNOTATION = (150, 154, 166)

# Cadrage propre à chaque type de plan : une planche-contact montre le même
# visage sous plusieurs valeurs, pas la même vignette répétée.
CADRAGES = {
    "portrait": {"echelle": 1.00, "decalage": 0.00, "profil": False},
    # Plan large : sujet plus petit, mais recentré — sinon la vignette est vide en haut.
    "pied": {"echelle": 0.62, "decalage": -0.04, "profil": False},
    "profil": {"echelle": 0.95, "decalage": 0.02, "profil": True},
    "avec_barbe": {"echelle": 1.05, "decalage": -0.02, "profil": False},
    "sans_barbe": {"echelle": 1.05, "decalage": -0.02, "profil": False},
}


def _police(taille, gras=True):
    """Une TrueType réelle : la police bitmap par défaut de Pillow ne s'agrandit pas."""
    for chemin in (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if gras else None,
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        if not chemin:
            continue
        try:
            return ImageFont.truetype(chemin, taille)
        except OSError:
            continue
    return ImageFont.load_default()


def _placeholder(reference, initiales, type_photo, libelle, indice, taille=(480, 600)):
    """Vignette de démonstration : silhouette stylisée, jamais un visage.

    Volontairement non photographique — il s'agit d'une base de casting, on ne
    fabrique pas de personnes crédibles. Mais l'image doit être *lisible* : c'est
    ce qui manquait à la version précédente, dont le texte était invisible.
    """
    largeur, hauteur = taille
    fond = FONDS[indice % len(FONDS)]
    image = Image.new("RGB", taille, fond)
    dessin = ImageDraw.Draw(image)

    cadrage = CADRAGES.get(type_photo, CADRAGES["portrait"])
    echelle = cadrage["echelle"]
    centre_x = largeur / 2 + (largeur * 0.06 if cadrage["profil"] else 0)
    centre_y = hauteur * (0.52 + cadrage["decalage"])

    # Halo doux derrière le sujet : donne du volume sans dégradé tape-à-l'œil.
    halo = int(min(largeur, hauteur) * 0.42 * echelle)
    dessin.ellipse(
        [centre_x - halo, centre_y - halo, centre_x + halo, centre_y + halo],
        fill=tuple(min(255, c + 14) for c in fond),
    )

    # Silhouette : tête + buste, en clair sur fond sourd.
    rayon_tete = int(hauteur * 0.13 * echelle)
    haut_tete = centre_y - rayon_tete * 2.1
    dessin.ellipse(
        [centre_x - rayon_tete, haut_tete, centre_x + rayon_tete, haut_tete + rayon_tete * 2],
        fill=SUJET,
    )
    demi_buste = rayon_tete * 2.05
    dessin.ellipse(
        [
            centre_x - demi_buste,
            haut_tete + rayon_tete * 2.35,
            centre_x + demi_buste,
            haut_tete + rayon_tete * 2.35 + demi_buste * 2.4,
        ],
        fill=SUJET,
    )

    # Initiales lisibles, posées sur le buste.
    police_initiales = _police(int(rayon_tete * 1.15))
    dessin.text(
        (centre_x, haut_tete + rayon_tete * 3.5),
        initiales,
        font=police_initiales,
        fill=fond,
        anchor="mm",
    )

    # Annotations de planche : référence en haut, type de plan en bas sur un bandeau
    # opaque — sans lui, la silhouette recouvre le libellé sur les plans larges.
    police_meta = _police(19, gras=False)
    dessin.text((22, 20), reference, font=police_meta, fill=ENCRE_CLAIRE)
    dessin.rectangle([0, hauteur - 48, largeur, hauteur], fill=fond)
    dessin.text(
        (largeur / 2, hauteur - 26), libelle.upper(), font=police_meta,
        fill=ANNOTATION, anchor="mm",
    )
    dessin.rectangle([10, 10, largeur - 11, hauteur - 11], outline=ANNOTATION, width=1)

    tampon = BytesIO()
    image.save(tampon, format="JPEG", quality=88)
    return ContentFile(tampon.getvalue())


class Command(BaseCommand):
    help = "Crée des profils fictifs (référence DEMO-xxx) pour tester la recherche."

    def add_arguments(self, parser):
        parser.add_argument("--nombre", type=int, default=30)
        parser.add_argument("--reset", action="store_true", help="Supprime les profils DEMO-*")

    @transaction.atomic
    def handle(self, *args, **options):
        anciens = Profil.objects.filter(reference__startswith="DEMO-")
        if options["reset"]:
            nombre_supprimes = anciens.count()
            anciens.delete()
            self.stdout.write(self.style.WARNING(f"{nombre_supprimes} profil(s) DEMO supprimé(s)."))
            return

        if anciens.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"{anciens.count()} profil(s) DEMO existent déjà — relancer avec --reset "
                    "pour repartir de zéro."
                )
            )
            return

        alea = random.Random(42)  # jeu reproductible
        referentiels = {
            "departements": list(Departement.objects.all()),
            "sports": list(Sport.objects.all()),
            "langues": list(Langue.objects.all()),
            "accents": list(Accent.objects.all()),
            "instruments": list(Instrument.objects.all()),
            "artistiques": list(CompetenceArtistique.objects.all()),
            "apparences": list(Apparence.objects.all()),
            "registres": list(Registre.objects.all()),
            "metiers": list(Metier.objects.all()),
            "particulieres": list(CompetenceParticuliere.objects.all()),
            "costumes": list(Costume.objects.all()),
            "zones": list(ZoneMobilite.objects.all()),
            "experiences": list(TypeExperience.objects.all()),
            "prestations": list(TypePrestation.objects.all()),
            "permis": list(Permis.objects.all()),
        }
        if not referentiels["sports"]:
            self.stdout.write(self.style.ERROR("Référentiel vide : lancer charger_referentiel."))
            return

        francais = Langue.objects.filter(nom="Français").first()
        aujourdhui = date.today()
        crees = 0

        for index in range(1, options["nombre"] + 1):
            reference = f"DEMO-{index:03d}"
            femme = alea.random() < 0.5
            prenom = alea.choice(PRENOMS_F if femme else PRENOMS_H)
            nom = alea.choice(NOMS)
            # Un profil mineur pour exercer le modèle dédié.
            est_mineur = index == options["nombre"]
            age = alea.randint(14, 17) if est_mineur else alea.randint(18, 68)

            profil = Profil.objects.create(
                reference=reference,
                nom=nom,
                prenom=prenom,
                sexe=Profil.Sexe.FEMME if femme else Profil.Sexe.HOMME,
                date_naissance=aujourdhui - timedelta(days=age * 365 + alea.randint(0, 364)),
                age_apparent_min=max(1, age - alea.randint(2, 5)),
                age_apparent_max=age + alea.randint(2, 5),
                telephone=f"06{alea.randint(10000000, 99999999)}",
                email=f"{prenom.lower()}.{nom.lower()}@exemple-demo.test",
                ville=alea.choice(["Paris", "Montreuil", "Lyon", "Marseille", "Lille", "Nantes"]),
                departement=alea.choice(referentiels["departements"]),
                distance_max_km=alea.choice([20, 50, 100, 300]),
                taille_cm=alea.randint(155, 195),
                poids_kg=alea.randint(48, 95),
                pointure=alea.randint(36, 46),
                taille_vetement=alea.choice(Profil.TailleVetement.values),
                tour_poitrine_cm=alea.randint(80, 110),
                tour_taille_cm=alea.randint(62, 100),
                tour_hanches_cm=alea.randint(85, 115),
                couleur_yeux=alea.choice(Profil.CouleurYeux.values),
                couleur_cheveux=alea.choice(Profil.CouleurCheveux.values),
                type_cheveux=alea.choice(Profil.TypeCheveux.values),
                longueur_cheveux=alea.choice(Profil.LongueurCheveux.values),
                barbe=not femme and alea.random() < 0.45,
                moustache=not femme and alea.random() < 0.15,
                lunettes=alea.random() < 0.3,
                tatouages_visibles=alea.random() < 0.25,
                piercings=alea.random() < 0.2,
                composition=alea.choice(Profil.Composition.values),
                disponibilite=alea.choice(Profil.Disponibilite.values),
                deja_figurant=alea.random() < 0.6,
                nombre_tournages=alea.randint(0, 25),
                peut_dormir_sur_place=alea.random() < 0.5,
                vehicule_personnel_disponible=alea.random() < 0.6,
                consentement_obtenu_le=aujourdhui - timedelta(days=alea.randint(1, 400)),
                source_consentement="Jeu de démonstration",
            )

            profil.apparences.set(alea.sample(referentiels["apparences"], alea.randint(1, 2)))
            profil.registres.set(alea.sample(referentiels["registres"], alea.randint(1, 4)))
            profil.metiers.set(alea.sample(referentiels["metiers"], alea.randint(0, 2)))
            profil.competences_particulieres.set(
                alea.sample(referentiels["particulieres"], alea.randint(1, 4))
            )
            profil.costumes.set(alea.sample(referentiels["costumes"], alea.randint(0, 3)))
            profil.zones_mobilite.set(alea.sample(referentiels["zones"], alea.randint(1, 3)))
            profil.types_experience.set(alea.sample(referentiels["experiences"], alea.randint(0, 3)))
            profil.prestations_acceptees.set(
                alea.sample(referentiels["prestations"], alea.randint(1, 3))
            )
            profil.permis.set(alea.sample(referentiels["permis"], alea.randint(0, 2)))

            for sport in alea.sample(referentiels["sports"], alea.randint(1, 3)):
                ProfilSport.objects.get_or_create(
                    profil=profil, sport=sport,
                    defaults={"niveau": alea.choice(NiveauSport.values)},
                )

            if francais:
                ProfilLangue.objects.get_or_create(
                    profil=profil, langue=francais,
                    defaults={
                        "niveau": NiveauLangue.LANGUE_MATERNELLE,
                        "accent": alea.choice(referentiels["accents"]) if alea.random() < 0.4 else None,
                    },
                )
            for langue in alea.sample(referentiels["langues"], alea.randint(1, 2)):
                ProfilLangue.objects.get_or_create(
                    profil=profil, langue=langue,
                    defaults={
                        "niveau": alea.choice(NiveauLangue.values),
                        "accent": alea.choice(referentiels["accents"]) if alea.random() < 0.3 else None,
                    },
                )
            for instrument in alea.sample(referentiels["instruments"], alea.randint(0, 2)):
                ProfilInstrument.objects.get_or_create(
                    profil=profil, instrument=instrument,
                    defaults={"niveau": alea.choice(NiveauInstrument.values)},
                )
            for competence in alea.sample(referentiels["artistiques"], alea.randint(1, 3)):
                ProfilCompetenceArtistique.objects.get_or_create(
                    profil=profil, competence=competence,
                    defaults={"niveau": alea.choice(NiveauArtistique.values)},
                )

            if est_mineur:
                Mineur.objects.create(
                    profil=profil,
                    responsable_legal_nom=nom,
                    responsable_legal_prenom=alea.choice(PRENOMS_F),
                    responsable_legal_lien=Mineur.LienResponsable.MERE,
                    responsable_legal_telephone="0600000000",
                    autorisation_parentale_signee=True,
                    autorisation_parentale_le=aujourdhui - timedelta(days=30),
                    autorisation_travail_obtenue=True,
                    autorisation_travail_reference="DDETS-DEMO-001",
                    disponibilite_scolaire=Mineur.DisponibiliteScolaire.VACANCES_UNIQUEMENT,
                )

            initiales = f"{prenom[0]}{nom[0]}"
            plans = [Photo.Type.PORTRAIT, Photo.Type.PIED, Photo.Type.PROFIL]
            if profil.barbe:
                plans.append(Photo.Type.AVEC_BARBE)
            for type_photo in plans:
                photo = Photo(profil=profil, type=type_photo, prise_le=aujourdhui)
                photo.image.save(
                    f"{reference}-{type_photo}.jpg",
                    _placeholder(
                        reference, initiales, type_photo, photo.get_type_display(), index
                    ),
                    save=True,
                )
            crees += 1

        self.stdout.write(
            self.style.SUCCESS(f"{crees} profils de démonstration créés (références DEMO-*).")
        )
