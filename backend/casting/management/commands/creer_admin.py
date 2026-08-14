"""Crée le compte administrateur initial à partir de variables d'environnement.

Le Shell de Render étant payant, `createsuperuser` (interactif) est inutilisable
en production : cette commande fait la même chose sans saisie, pendant le build.

Idempotente : relancée à chaque déploiement, elle ne recrée ni n'écrase un compte
existant — sauf demande explicite via ADMIN_FORCER_MOT_DE_PASSE.
"""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crée le superutilisateur initial depuis ADMIN_IDENTIFIANT / ADMIN_MOT_DE_PASSE."

    def handle(self, *args, **options):
        identifiant = os.environ.get("ADMIN_IDENTIFIANT")
        mot_de_passe = os.environ.get("ADMIN_MOT_DE_PASSE")
        courriel = os.environ.get("ADMIN_EMAIL", "")

        if not identifiant or not mot_de_passe:
            self.stdout.write(
                "Compte admin ignoré : ADMIN_IDENTIFIANT et ADMIN_MOT_DE_PASSE non définis."
            )
            return

        if len(mot_de_passe) < 12:
            # L'application est publique et sans limitation de tentatives : un mot
            # de passe court y serait forcé en quelques minutes.
            self.stderr.write(
                self.style.ERROR(
                    "ADMIN_MOT_DE_PASSE fait moins de 12 caractères : compte non créé."
                )
            )
            return

        Utilisateur = get_user_model()
        utilisateur, cree = Utilisateur.objects.get_or_create(
            username=identifiant,
            defaults={"email": courriel, "is_staff": True, "is_superuser": True},
        )

        if cree:
            utilisateur.set_password(mot_de_passe)
            utilisateur.save()
            self.stdout.write(self.style.SUCCESS(f"Compte administrateur « {identifiant} » créé."))
            return

        if os.environ.get("ADMIN_FORCER_MOT_DE_PASSE") == "1":
            utilisateur.set_password(mot_de_passe)
            utilisateur.is_staff = True
            utilisateur.is_superuser = True
            utilisateur.save()
            self.stdout.write(
                self.style.WARNING(f"Mot de passe de « {identifiant} » réinitialisé.")
            )
        else:
            self.stdout.write(f"Compte « {identifiant} » déjà présent, inchangé.")
