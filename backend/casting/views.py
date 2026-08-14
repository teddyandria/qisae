"""API de recherche et de saisie.

La consultation est ouverte à tout compte connecté ; l'écriture est réservée au staff
(voir docs/decisions/0001-saisie-par-formulaires-front.md).
"""

from django.contrib.auth import authenticate, login, logout
from django.db.models import Prefetch
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .filters import ProfilFilter
from .permissions import LectureAuthentifieeEcritureStaff
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
    Permis,
    Photo,
    Profil,
    Registre,
    Sport,
    TypeExperience,
    TypePrestation,
    TypeVehicule,
    ZoneMobilite,
)
from .serializers import (
    AccentSerializer,
    ApparenceSerializer,
    ConnexionSerializer,
    PhotoEcritureSerializer,
    ProfilEcritureSerializer,
    SessionSerializer,
    CompetenceArtistiqueSerializer,
    CompetenceConduiteSerializer,
    CompetenceParticuliereSerializer,
    CostumeSerializer,
    DepartementSerializer,
    InstrumentSerializer,
    LangueSerializer,
    MetierSerializer,
    PermisSerializer,
    ProfilDetailSerializer,
    ProfilListeSerializer,
    RegistreSerializer,
    SportSerializer,
    TypeExperienceSerializer,
    TypePrestationSerializer,
    TypeVehiculeSerializer,
    ZoneMobiliteSerializer,
)


@method_decorator(ensure_csrf_cookie, name="list")
class ProfilViewSet(viewsets.ModelViewSet):
    """Recherche à facettes, consultation et saisie d'un profil.

    `ensure_csrf_cookie` sur la liste : le front récupère le cookie CSRF en
    affichant la planche, avant tout envoi de formulaire.
    """

    permission_classes = [LectureAuthentifieeEcritureStaff]
    filterset_class = ProfilFilter
    ordering_fields = ("nom", "taille_cm", "date_naissance", "reference")
    ordering = ("nom", "prenom")

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ProfilEcritureSerializer
        if self.action == "retrieve":
            return ProfilDetailSerializer
        return ProfilListeSerializer

    def get_queryset(self):
        queryset = Profil.objects.select_related("departement", "departement__region")
        # Les comp cards affichent portrait + plans alternatifs : sans prefetch,
        # une planche de 24 profils déclencherait 24 requêtes de plus.
        queryset = queryset.prefetch_related(
            Prefetch("photos", queryset=Photo.objects.order_by("type")),
            "apparences",
        )
        if self.action == "retrieve":
            queryset = queryset.prefetch_related(
                "registres",
                "metiers",
                "competences_particulieres",
                "costumes",
                "zones_mobilite",
                "types_experience",
                "prestations_acceptees",
                "competences_conduite",
                "permis",
                "profilsport_set__sport",
                "profilcompetenceartistique_set__competence",
                "profilinstrument_set__instrument",
                "profillangue_set__langue",
                "profillangue_set__accent",
                "profilvehicule_set__type_vehicule",
            ).select_related("mineur")
        return queryset


class PhotoViewSet(viewsets.ModelViewSet):
    """Upload et suppression des photos d'un profil (multipart)."""

    queryset = Photo.objects.select_related("profil")
    serializer_class = PhotoEcritureSerializer
    permission_classes = [LectureAuthentifieeEcritureStaff]
    pagination_class = None
    filterset_fields = ("profil", "type")


def _etat_session(utilisateur):
    connecte = utilisateur and utilisateur.is_authenticated
    return {
        "utilisateur": utilisateur.get_username() if connecte else None,
        "peut_saisir": bool(connecte and utilisateur.is_staff),
    }


class SessionView(APIView):
    """Qui est connecté, et pose le cookie CSRF.

    Ouverte en anonyme à dessein : la page de connexion a besoin du cookie CSRF
    pour poster, et elle ne peut pas l'obtenir d'un endpoint qui la rejette.
    Ne divulgue rien d'autre que « personne n'est connecté ».
    """

    permission_classes = [AllowAny]
    serializer_class = SessionSerializer

    @extend_schema(responses=SessionSerializer)
    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return Response(_etat_session(request.user))


@method_decorator(csrf_protect, name="post")
class ConnexionView(APIView):
    """Ouvre une session à partir d'un identifiant et d'un mot de passe.

    `csrf_protect` est explicite : DRF exempte ses vues du CSRF et ne le vérifie
    qu'au moment d'authentifier une session existante. Sans ce décorateur, un site
    tiers pourrait connecter la victime sur un compte qu'il contrôle (login CSRF).
    """

    permission_classes = [AllowAny]
    serializer_class = ConnexionSerializer

    @extend_schema(request=ConnexionSerializer, responses=SessionSerializer)
    def post(self, request):
        formulaire = ConnexionSerializer(data=request.data)
        formulaire.is_valid(raise_exception=True)

        utilisateur = authenticate(
            request,
            username=formulaire.validated_data["identifiant"],
            password=formulaire.validated_data["mot_de_passe"],
        )
        if utilisateur is None:
            # Message volontairement identique que le compte existe ou non :
            # distinguer les deux cas permettrait d'énumérer les identifiants.
            return Response(
                {"detail": "Identifiant ou mot de passe incorrect."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # login() régénère la clé de session (protection contre la fixation).
        login(request, utilisateur)
        return Response(_etat_session(utilisateur))


@method_decorator(csrf_protect, name="post")
class DeconnexionView(APIView):
    """Ferme la session courante."""

    permission_classes = [AllowAny]
    serializer_class = SessionSerializer

    @extend_schema(request=None, responses=SessionSerializer)
    def post(self, request):
        logout(request)
        return Response(_etat_session(None))


class ReferenceViewSet(viewsets.ReadOnlyModelViewSet):
    """Listes qui alimentent le rail de filtres."""

    pagination_class = None


def _viewset_reference(modele, serializer):
    return type(
        f"{modele.__name__}ViewSet",
        (ReferenceViewSet,),
        {"queryset": modele.objects.all(), "serializer_class": serializer},
    )


ApparenceViewSet = _viewset_reference(Apparence, ApparenceSerializer)
RegistreViewSet = _viewset_reference(Registre, RegistreSerializer)
MetierViewSet = _viewset_reference(Metier, MetierSerializer)
CompetenceParticuliereViewSet = _viewset_reference(
    CompetenceParticuliere, CompetenceParticuliereSerializer
)
CompetenceConduiteViewSet = _viewset_reference(CompetenceConduite, CompetenceConduiteSerializer)
CompetenceArtistiqueViewSet = _viewset_reference(CompetenceArtistique, CompetenceArtistiqueSerializer)
CostumeViewSet = _viewset_reference(Costume, CostumeSerializer)
ZoneMobiliteViewSet = _viewset_reference(ZoneMobilite, ZoneMobiliteSerializer)
TypeExperienceViewSet = _viewset_reference(TypeExperience, TypeExperienceSerializer)
TypePrestationViewSet = _viewset_reference(TypePrestation, TypePrestationSerializer)
TypeVehiculeViewSet = _viewset_reference(TypeVehicule, TypeVehiculeSerializer)
InstrumentViewSet = _viewset_reference(Instrument, InstrumentSerializer)
LangueViewSet = _viewset_reference(Langue, LangueSerializer)
AccentViewSet = _viewset_reference(Accent, AccentSerializer)
SportViewSet = _viewset_reference(Sport, SportSerializer)
PermisViewSet = _viewset_reference(Permis, PermisSerializer)


class DepartementViewSet(ReferenceViewSet):
    queryset = Departement.objects.select_related("region")
    serializer_class = DepartementSerializer
