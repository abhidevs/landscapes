import logging

import django_filters
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import PropertyNotFound
from .models import Property, PropertyView
from .pagination import PropertyPagination
from .serializers import (
    PropertyCreateSerializer,
    PropertySerializer,
    PropertyViewSerializer,
)

logger = logging.getLogger(__name__)


class PropertyFilter(django_filters.FilterSet):
    advert_type = django_filters.CharFilter(
        field_name="advert_type", lookup_expr="iexact"
    )
    property_type = django_filters.CharFilter(
        field_name="property_type", lookup_expr="iexact"
    )
    price = django_filters.NumberFilter()
    price__gt = django_filters.NumberFilter(field="price", lookup_expr="gt")
    price__lt = django_filters.NumberFilter(field="price", lookup_expr="lt")

    class Meta:
        model = Property
        fields = ["advert_type", "property_type", "price"]


class ListAllPropertiesAPIView(generics.ListAPIView):
    serializer_class = PropertySerializer
    queryset = Property.objects.all().order_by("-created_at")
    pagination_class = PropertyPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_class = PropertyFilter
    search_fields = ["country", "city"]
    ordering_fields = ["created_at"]


class ListAgentsPropertiesAPIView(generics.ListAPIView):
    serializer_class = PropertySerializer
    pagination_class = PropertyPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = PropertyFilter
    search_fields = ["country", "city"]
    ordering_fields = ["created_at"]

    def get_queryset(self):
        user = self.request.user
        queryset = Property.objects.filter(user=user).order_by("-created_at")
        return queryset


class PropertyViewsAPIView(generics.ListAPIView):
    serializer_class = PropertyViewSerializer
    queryset = PropertyView.objects.all()


class PropertyDetailAPIView(APIView):
    def get(self, request, slug):
        property = Property.objects.get(slug=slug)

        # Get IP address of the user
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            viewer_ip = x_forwarded_for.split(",")[0]
        else:
            viewer_ip = request.META.get("REMOTE_ADDR")

        # If the view for the property and user does not exists
        # then create one
        if not PropertyView.objects.filter(
            property=property, viewer_ip=viewer_ip
        ).exists():
            PropertyView.objects.create(property=property, viewer_ip=viewer_ip)
            property.views += 1
            property.save()

        context = {"request": request}
        serializer = PropertySerializer(property, context)

        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["PUT"])
@permission_classes([permissions.IsAuthenticated])
def update_property_api_view(request, slug):
    try:
        property = Property.objects.get(slug=slug)
    except Property.DoesNotExist:
        raise PropertyNotFound

    user = request.user
    if property.user != user:
        return Response(
            {"error": "You cannot modify a property that does not belongs to you"},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method == "PUT":
        data = request.data
        serializer = PropertySerializer(property, data, many=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def create_property_api_view(request):
    user = request.user
    data = request.data
    data["user"] = request.user.pkid
    serializer = PropertyCreateSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        logger.info(
            f"Property {serializer.data.get('title')} has been created by {user.username}"
        )
        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def delete_property_api_view(request, slug):
    try:
        property = Property.objects.get(slug=slug)
    except Property.DoesNotExist:
        raise PropertyNotFound

    user = request.user
    if property.user != user:
        return Response(
            {"error": "You cannot delete a property that does not belongs to you"},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method == "DELETE":
        delete_operation = property.delete()
        data = {}

        if delete_operation:
            data["success"] = "Property deleted successfully"
        else:
            data["failure"] = "Failed to delete property"

        return Response(data=data)


@api_view(["POST"])
def upload_property_image(request):
    data = request.data

    property_id = data["property_id"]
    property = Property.objects.get(id=property_id)
    property.cover_image = request.FILES.get("cover_image")
    property.image1 = request.FILES.get("image1")
    property.image2 = request.FILES.get("image2")
    property.image3 = request.FILES.get("image3")
    property.image4 = request.FILES.get("image4")
    property.save()
    return Response("Images updated successfully for this property")


class PropertySearchAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PropertyCreateSerializer

    def post(self, request):
        queryset = Property.objects.filter(published_status=True)
        data = self.request.data

        advert_type = data.get("advert_type", None)
        if advert_type:
            queryset = queryset.filter(advert_type__iexact=advert_type)

        property_type = data.get("property_type", None)
        if property_type:
            queryset = queryset.filter(property_type__iexact=property_type)

        price = data.get("price", None)

        if price == "below₹1L":
            price = 100000
        elif price == "below₹10L":
            price = 1000000
        elif price == "below₹50L":
            price = 5000000
        elif price == "below₹1Cr":
            price = 10000000
        elif price == "below₹10Cr":
            price = 100000000
        elif price == "below₹100Cr":
            price = 1000000000
        elif price == "any" or price is None:
            price = -1

        if price != -1:
            queryset = queryset.filter(price__lte=price)

        number_of_bedrooms = data.get("number_of_bedrooms", None)

        if number_of_bedrooms == "0":
            number_of_bedrooms = 0
        elif number_of_bedrooms == "1-2":
            number_of_bedrooms_gte = 1
            number_of_bedrooms_lte = 2
        elif number_of_bedrooms == "3-5":
            number_of_bedrooms_gte = 3
            number_of_bedrooms_lte = 5
        elif number_of_bedrooms == "6-10":
            number_of_bedrooms_gte = 6
            number_of_bedrooms_lte = 10
        elif number_of_bedrooms == "10-20":
            number_of_bedrooms_gte = 10
            number_of_bedrooms_lte = 20
        elif number_of_bedrooms == "20+":
            number_of_bedrooms_gte = 20
        elif number_of_bedrooms == "any" or number_of_bedrooms is None:
            number_of_bedrooms = -1

        if number_of_bedrooms == 0:
            queryset = queryset.filter(number_of_bedrooms=number_of_bedrooms)
        elif number_of_bedrooms == 20:
            queryset = queryset.filter(number_of_bedrooms__gte=number_of_bedrooms_gte)
        elif number_of_bedrooms != -1:
            queryset = queryset.filter(
                number_of_bedrooms__gte=number_of_bedrooms_gte,
                number_of_bedrooms__lte=number_of_bedrooms_lte,
            )

        number_of_bathrooms = data.get("number_of_bathrooms", None)

        if number_of_bathrooms == "0":
            number_of_bathrooms = 0
        elif number_of_bathrooms == "1-2":
            number_of_bathrooms_gte = 1
            number_of_bathrooms_lte = 2
        elif number_of_bathrooms == "3-5":
            number_of_bathrooms_gte = 3
            number_of_bathrooms_lte = 5
        elif number_of_bathrooms == "6-10":
            number_of_bathrooms_gte = 6
            number_of_bathrooms_lte = 10
        elif number_of_bathrooms == "10+":
            number_of_bathrooms_gte = 10
        elif number_of_bathrooms == "any" or number_of_bathrooms is None:
            number_of_bathrooms = -1

        if number_of_bathrooms == 0:
            queryset = queryset.filter(number_of_bathrooms=number_of_bathrooms)
        elif number_of_bathrooms == 10:
            queryset = queryset.filter(number_of_bathrooms__gte=number_of_bathrooms_gte)
        elif number_of_bathrooms != -1:
            queryset = queryset.filter(
                number_of_bathrooms__gte=number_of_bathrooms_gte,
                number_of_bathrooms__lte=number_of_bathrooms_lte,
            )

        query = data.get("query", None)
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(street_address__icontains=query)
            )

        serializer = PropertySerializer(queryset, many=True)
        return Response(serializer.data)
