from rest_framework import permissions


class LectureAuthentifieeEcritureStaff(permissions.BasePermission):
    """Consultation pour tout compte connecté, saisie réservée au staff.

    Voir docs/decisions/0001-saisie-par-formulaires-front.md : la saisie via le front
    est un élargissement de périmètre, et le client a demandé qu'elle lui soit réservée.
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user.is_staff)
