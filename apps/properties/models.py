import random
import string

from autoslug import AutoSlugField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from apps.common.models import TimeStampedUUIDModel

User = get_user_model()


class PropertyPublishedManager(models.Manager):
    def get_queryset(self):
        return (
            super(PropertyPublishedManager, self)
            .get_queryset()
            .filter(published_status=True)
        )


class Property(TimeStampedUUIDModel):
    class PropertyType(models.TextChoices):
        HOUSE = "House", _("House")
        APARTMENT = "Apartment", _("Apartment")
        OFFICE = "Office", _("Office")
        WAREHOUSE = "Warehouse", _("Warehouse")
        COMMERCIAL = "Commercial", _("Commercial")
        OTHER = "Other", _("Other")

    class AdvertType(models.TextChoices):
        FOR_SALE = "For Sale", _("For Sale")
        FOR_RENT = "For Rent", _("For Rent")
        FOR_AUCTION = "For Auction", _("For Auction")

    user = models.ForeignKey(
        User,
        verbose_name=_("Agent, seller, or Buyer"),
        related_name="agent_or_buyer",
        on_delete=models.DO_NOTHING,
    )
    title = models.CharField(verbose_name=_("Property title"), max_length=250)
    slug = AutoSlugField(populate_from="title", unique=True, always_update=True)
    ref_code = models.CharField(
        verbose_name=_("Property Reference Code"),
        max_length=255,
        unique=True,
        blank=True,
    )
    description = models.TextField(
        verbose_name=_("Description"), default="Default description..."
    )
    country = CountryField(verbose_name=_("Country"), blank_label="Select country")
    city = models.CharField(verbose_name=_("City"), max_length=100)
    postal_code = models.CharField(verbose_name=_("Postal code"), max_length=10)
    street_address = models.CharField(verbose_name=_("Street address"), max_length=150)
    property_number = models.IntegerField(
        verbose_name=_("Property number"), validators=[MinValueValidator(1)]
    )
    price = models.DecimalField(
        verbose_name=_("Price"), max_digits=12, decimal_places=2
    )
    tax = models.DecimalField(
        verbose_name=_("Tax"),
        max_digits=6,
        decimal_places=2,
        default=0.05,
        help_text=_("Tax upon property price"),
    )
    plot_area = models.DecimalField(
        verbose_name=_("Plot area (m^2)"), max_digits=10, decimal_places=2, default=0.0
    )
    number_of_floors = models.IntegerField(
        verbose_name=_("Number of floors"), default=0
    )
    number_of_bedrooms = models.IntegerField(
        verbose_name=_("Number of bedrooms"), default=0
    )
    number_of_bathrooms = models.IntegerField(
        verbose_name=_("Number of bathrooms"), default=0
    )
    property_type = models.CharField(
        verbose_name=_("Property type"),
        max_length=50,
        choices=PropertyType.choices,
        default=PropertyType.OTHER,
    )
    advert_type = models.CharField(
        verbose_name=_("Advert type"),
        max_length=50,
        choices=AdvertType.choices,
        default=AdvertType.FOR_SALE,
    )
    cover_image = models.ImageField(
        verbose_name=_("Cover image"),
        default="/sample_property_cover_image.jpg",
        null=True,
        blank=True,
    )
    image1 = models.ImageField(
        verbose_name=_("Image 1"),
        default="/sample_property_image1.jpg",
        null=True,
        blank=True,
    )
    image2 = models.ImageField(
        verbose_name=_("Image 2"),
        default="/sample_property_image2.jpg",
        null=True,
        blank=True,
    )
    image3 = models.ImageField(
        verbose_name=_("Image 3"),
        default="/sample_property_image3.jpg",
        null=True,
        blank=True,
    )
    image4 = models.ImageField(
        verbose_name=_("Image 4"),
        default="/sample_property_image4.jpg",
        null=True,
        blank=True,
    )
    published_status = models.BooleanField(
        verbose_name=_("Published status"), default=False
    )
    views = models.IntegerField(verbose_name=_("Number of views"), default=0)

    objects = models.Manager()
    published = PropertyPublishedManager()

    class Meta:
        verbose_name = "Property"
        verbose_name_plural = "Properties"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.title = str.title(self.title)
        self.description = str.capitalize(self.description)
        self.ref_code = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=20)
        )
        super(Property, self).save(*args, **kwargs)

    @property
    def final_porperty_Price(self):
        tax_percentage = self.tax
        property_price = self.price
        tax_amount = round(tax_percentage * property_price, 2)
        price_after_tax = float(round(property_price + tax_amount, 2))
        return price_after_tax


class PropertyView(TimeStampedUUIDModel):
    viewer_ip = models.CharField(verbose_name=_("Viewer IP address"), max_length=250)
    property = models.ForeignKey(
        Property, related_name="property_views", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Total views on {self.property.title} is {self.property.views}"

    class Meta:
        verbose_name = "Total views on Property"
        verbose_name_plural = "Total Property Views"
