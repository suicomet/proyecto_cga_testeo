from django.contrib.auth.models import Group, User
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .permissions import EstaAutenticadoYConRol
from .usuarios_serializers import ROLES_OFICIALES, UsuarioSistemaSerializer


class UsuarioSistemaViewSet(viewsets.ModelViewSet):
    queryset = User.objects.prefetch_related("groups").all().order_by("id")
    serializer_class = UsuarioSistemaSerializer
    permission_classes = [IsAuthenticated, EstaAutenticadoYConRol]
    roles_permitidos = ["Administrador"]

    def get_queryset(self):
        return (
            User.objects
            .prefetch_related("groups")
            .all()
            .order_by("id")
        )

    def destroy(self, request, *args, **kwargs):
        return Response(
            {
                "detail": (
                    "No se permite eliminar usuarios desde el sistema. "
                    "Puedes desactivarlos cambiando su estado a inactivo."
                )
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    @action(detail=False, methods=["get"])
    def roles(self, request):
        for rol in ROLES_OFICIALES:
            Group.objects.get_or_create(name=rol)

        return Response({
            "roles": ROLES_OFICIALES
        })
    