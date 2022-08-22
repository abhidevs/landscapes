from django_countries.serializer_fields import CountryField
from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers

from .models import Property, PropertyView


class PropertySerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    country = CountryField(name_only=True)

    class Meta:
        model = Property
        fields = [
            "id",
            "user",
            "title",
            "slug",
            "ref_code",
            "description",
            "country",
            "city",
            "postal_code",
            "street_address",
            "property_number",
            "price",
            "tax",
            "final_property_price",
            "plot_area",
            "total_floors",
            "number_of_floors",
            "number_of_bedrooms",
            "number_of_bathrooms",
            "property_type",
            "advert_type",
            "cover_image",
            "image1",
            "image2",
            "image3",
            "image4",
            "published_status",
            "views",
        ]

    def get_user(seld, obj):
        return obj.user.username


class PropertyCreateSerializer(serializers.ModelField):
    country = CountryField(name_only=True)

    class Meta:
        model = Property
        exclude = [
            "pkid",
            "updated_at",
        ]


class PropertyViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyView
        exclude = [
            "pkid",
            "updated_at",
        ]
