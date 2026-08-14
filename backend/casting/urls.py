from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("profils", views.ProfilViewSet, basename="profil")
router.register("photos", views.PhotoViewSet)

# Référentiels : alimentent le rail de filtres côté front.
router.register("apparences", views.ApparenceViewSet)
router.register("registres", views.RegistreViewSet)
router.register("sports", views.SportViewSet)
router.register("langues", views.LangueViewSet)
router.register("accents", views.AccentViewSet)
router.register("instruments", views.InstrumentViewSet)
router.register("competences-artistiques", views.CompetenceArtistiqueViewSet)
router.register("competences-particulieres", views.CompetenceParticuliereViewSet)
router.register("competences-conduite", views.CompetenceConduiteViewSet)
router.register("metiers", views.MetierViewSet)
router.register("costumes", views.CostumeViewSet)
router.register("zones-mobilite", views.ZoneMobiliteViewSet)
router.register("types-experience", views.TypeExperienceViewSet)
router.register("prestations", views.TypePrestationViewSet)
router.register("types-vehicule", views.TypeVehiculeViewSet)
router.register("permis", views.PermisViewSet)
router.register("departements", views.DepartementViewSet)

urlpatterns = [
    path("session/", views.SessionView.as_view(), name="session"),
    path("connexion/", views.ConnexionView.as_view(), name="connexion"),
    path("deconnexion/", views.DeconnexionView.as_view(), name="deconnexion"),
    *router.urls,
]
