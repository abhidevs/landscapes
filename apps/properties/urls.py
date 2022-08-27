from django.urls import path

from apps.properties.views import (
    ListAgentsPropertiesAPIView,
    ListAllPropertiesAPIView,
    PropertyDetailAPIView,
    PropertySearchAPIView,
    create_property_api_view,
    delete_property_api_view,
    update_property_api_view,
)

urlpatterns = [
    path("all/", ListAllPropertiesAPIView.as_view(), name="all-properties"),
    path("agents/", ListAgentsPropertiesAPIView.as_view(), name="agent-properties"),
    path("create/", create_property_api_view, name="create-property"),
    path(
        "<slug:slug>/details/", PropertyDetailAPIView.as_view(), name="property-details"
    ),
    path("<slug:slug>/update/", update_property_api_view, name="update-property"),
    path("<slug:slug>/delete/", delete_property_api_view, name="delete-property"),
    path("search/", PropertySearchAPIView.as_view(), name="search-properties"),
]
