from rest_framework.viewsets import ModelViewSet

from .serializers import (
    CreateUserSerializer, CustomUser, LoginSerializer, UpdatePasswordSerializer,
    CustomUserSerializer, UserActivities, UserActivitiesSerializer, TokenWPP, TokenWPPSerializer, WPPGroup, WPPGroupSerializer
    )
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime
from backend.utils import CustomPagination, get_access_token, get_query
from backend.custom_methods import IsAuthenticatedCustom
from user_control.utils import getwpptoken
from django.db import transaction


def add_user_activity(user, action):
    UserActivities.objects.create(
        user_id=user.id,
        email=user.email,
        fullname=user.fullname,
        action=action
    )

@swagger_auto_schema(tags=['Admin'])
class CreateUserView(ModelViewSet):
    http_method_names = ["post"]
    queryset = CustomUser.objects.all()
    serializer_class = CreateUserSerializer
    serializer_class1 = TokenWPPSerializer
    permission_classes = (IsAuthenticatedCustom, )

    def create(self, request):
        with transaction.atomic():
            valid_request = self.serializer_class(data=request.data)
            valid_request.is_valid(raise_exception=True)
            
            # Gerar token
            session_wpp_value = valid_request.validated_data.get('email')
            token_value = getwpptoken(session_wpp_value)

            # Criar TokenWPP, se um token foi recebido
            token_wpp = None
            if token_value:
                token_wpp = TokenWPP.objects.create(token_wpp=token_value)

            # Criar usuário e associar token
            user_data = valid_request.validated_data
            CustomUser.objects.create(**user_data, token=token_wpp)

            # Adicionar atividade do usuário
            add_user_activity(request.user, "Adicionado novo usuário")

            return Response(
                {"success": "User created successfully"},
                status=status.HTTP_201_CREATED
            )

@swagger_auto_schema(tags=['User'])
class LoginView(ModelViewSet):
    http_method_names = ["post"]
    queryset = CustomUser.objects.all()
    serializer_class = LoginSerializer

    def create(self, request):
        valid_request = self.serializer_class(data=request.data)
        valid_request.is_valid(raise_exception=True)

        new_user = valid_request.validated_data["is_new_user"]

        if new_user:
            user = CustomUser.objects.filter(
                email=valid_request.validated_data["email"]
            )

            if user:
                user = user[0]
                if not user.password:
                    return Response({"user_id": user.id})
                else:
                    raise Exception("User has password already")
            else:
                raise Exception("User with email not found")

        user = authenticate(
            username=valid_request.validated_data["email"],
            password=valid_request.validated_data.get("password", None)
        )

        if not user:
            return Response(
                {"error": "Invalid email or password"},
                status=status.HTTP_400_BAD_REQUEST
            )

        access = get_access_token({"user_id": user.id}, 1)

        user.last_login = datetime.now()
        user.save()

        add_user_activity(user, "Logado em")

        return Response({"access": access})

@swagger_auto_schema(tags=['User'])
class UpdatePasswordView(ModelViewSet):
    serializer_class = UpdatePasswordSerializer
    http_method_names = ["post"]
    queryset = CustomUser.objects.all()

    def create(self, request):
        valid_request = self.serializer_class(data=request.data)
        valid_request.is_valid(raise_exception=True)

        user = CustomUser.objects.filter(
            id=valid_request.validated_data["user_id"])

        if not user:
            raise Exception("User with id not found")

        user = user[0]

        user.set_password(valid_request.validated_data["password"])
        user.save()

        add_user_activity(user, "Atualizou a senha")

        return Response({"success": "User password updated"})

@swagger_auto_schema(tags=['User'])
class MeView(ModelViewSet):
    serializer_class = CustomUserSerializer
    http_method_names = ["get"]
    queryset = CustomUser.objects.all()
    permission_classes = (IsAuthenticatedCustom, )

    def list(self, request):
        data = self.serializer_class(request.user).data
        return Response(data)

@swagger_auto_schema(tags=['User'])
class UserActivitiesView(ModelViewSet):
    serializer_class = UserActivitiesSerializer
    http_method_names = ["get"]
    queryset = UserActivities.objects.all()
    permission_classes = (IsAuthenticatedCustom, )
    pagination_class = CustomPagination
    
    def get_queryset(self):
        if self.request.method.lower() != "get":
            return self.queryset

        data = self.request.query_params.dict()
        data.pop("page", None)
        keyword = data.pop("keyword", None)

        results = self.queryset.filter(**data)

        if keyword:
            search_fields = (
                "fullname", "email", "action"
            )
            query = get_query(keyword, search_fields)
            results = results.filter(query)
        
        return results

@swagger_auto_schema(tags=['User'])
class UsersView(ModelViewSet):
    serializer_class = CustomUserSerializer
    http_method_names = ["get"]
    queryset = CustomUser.objects.all()
    permission_classes = (IsAuthenticatedCustom, )
    pagination_class = CustomPagination
    
    def get_queryset(self):
        if self.request.method.lower() != "get":
            return self.queryset

        data = self.request.query_params.dict()
        data.pop("page", None)
        keyword = data.pop("keyword", None)

        results = self.queryset.filter(**data, is_superuser=False)

        if keyword:
            search_fields = (
                "fullname", "email", "role"
            )
            query = get_query(keyword, search_fields)
            results = results.filter(query)
        
        return results

@swagger_auto_schema(tags=['Group'])
class WPPGroupView(ModelViewSet):
    serializer_class = WPPGroupSerializer
    queryset = WPPGroup.objects.all()
    permission_classes = (IsAuthenticatedCustom, )
    pagination_class = CustomPagination

    def create(self, request, *args, **kwargs):
        request.data.update({"created_by_id": request.user.id})
        add_user_activity(request.user, "Criou um grupo")
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_name = instance.origin
        new_name = request.data.get("origin", old_name)
        action = f"Atualizado Grupo de '{old_name}' para '{new_name}'"
        add_user_activity(request.user, action)
        return super().update(request, *args, **kwargs)