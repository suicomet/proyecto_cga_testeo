from django.contrib.auth.models import Group, User
from django.db.models import Q
from rest_framework import serializers


ROLES_OFICIALES = [
    "Administrador",
    "Encargado de turno",
]


class UsuarioSistemaSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    rol_asignado = serializers.SerializerMethodField()

    rol = serializers.ChoiceField(
        choices=[(rol, rol) for rol in ROLES_OFICIALES],
        write_only=True,
        required=False
    )

    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=False,
        min_length=6
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_superuser",
            "roles",
            "rol_asignado",
            "rol",
            "password",
        ]
        read_only_fields = [
            "id",
            "is_superuser",
            "roles",
            "rol_asignado",
        ]

    def get_roles(self, obj):
        return list(obj.groups.values_list("name", flat=True))

    def get_rol_asignado(self, obj):
        if obj.is_superuser:
            return "Administrador"

        rol = obj.groups.filter(name__in=ROLES_OFICIALES).first()

        if rol:
            return rol.name

        return "Sin rol"

    def validate_username(self, value):
        username = str(value).strip()

        if not username:
            raise serializers.ValidationError("El nombre de usuario es obligatorio.")

        queryset = User.objects.filter(username__iexact=username)

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError("Ya existe un usuario con ese nombre de usuario.")

        return username

    def validate_email(self, value):
        email = str(value or "").strip().lower()

        if not email:
            return email

        queryset = User.objects.filter(email__iexact=email)

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError("Ya existe un usuario con ese correo.")

        return email

    def validate(self, attrs):
        if self.instance is None:
            password = attrs.get("password")
            rol = attrs.get("rol")

            if not password:
                raise serializers.ValidationError({
                    "password": "La contraseña es obligatoria al crear un usuario."
                })

            if not rol:
                raise serializers.ValidationError({
                    "rol": "Debes asignar un rol al usuario."
                })

            return attrs

        is_active_nuevo = attrs.get("is_active", self.instance.is_active)
        rol_nuevo = attrs.get("rol", None)

        if self._puede_dejar_sin_admin_principal(is_active_nuevo, rol_nuevo):
            raise serializers.ValidationError(
                "No puedes desactivar o quitar el rol Administrador al último administrador activo del sistema."
            )

        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        rol = validated_data.pop("rol")

        usuario = User(
            username=validated_data.get("username"),
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            email=validated_data.get("email", ""),
            is_active=validated_data.get("is_active", True),
        )

        usuario.set_password(password)
        usuario.save()

        self._asignar_rol(usuario, rol)

        return usuario

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        rol = validated_data.pop("rol", None)

        for campo, valor in validated_data.items():
            setattr(instance, campo, valor)

        if password:
            instance.set_password(password)

        instance.save()

        if rol:
            self._asignar_rol(instance, rol)

        return instance

    def _asignar_rol(self, usuario, rol):
        grupos_oficiales = Group.objects.filter(name__in=ROLES_OFICIALES)
        usuario.groups.remove(*grupos_oficiales)

        grupo, _ = Group.objects.get_or_create(name=rol)
        usuario.groups.add(grupo)

    def _usuario_es_admin(self, usuario):
        return usuario.is_superuser or usuario.groups.filter(name="Administrador").exists()

    def _existe_otro_admin_activo(self):
        return User.objects.filter(is_active=True).exclude(pk=self.instance.pk).filter(
            Q(is_superuser=True) | Q(groups__name="Administrador")
        ).distinct().exists()

    def _puede_dejar_sin_admin_principal(self, is_active_nuevo, rol_nuevo):
        if not self.instance:
            return False

        if not self._usuario_es_admin(self.instance):
            return False

        pierde_estado_activo = is_active_nuevo is False

        pierde_rol_admin = (
            rol_nuevo is not None
            and rol_nuevo != "Administrador"
            and not self.instance.is_superuser
        )

        if not pierde_estado_activo and not pierde_rol_admin:
            return False

        return not self._existe_otro_admin_activo()