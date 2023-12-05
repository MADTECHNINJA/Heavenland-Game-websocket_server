from django.urls import path
from . import views

urlpatterns = [
    path('', views.ApiBaseView.as_view()),
    path('version',views.ApiVersionView().as_view()),
    path('builder', views.BuildingsView.as_view()),
    path('builder/<int:building_id>', views.BuildingView.as_view()),
    path('builder/<int:building_id>/blocks', views.BuildingBlocksView.as_view()),
    path('builder/<int:building_id>/blocks/<int:floor>', views.BuildingBlockView.as_view()),
    path('character', views.CharacterEditorView.as_view()),
    path('character/<int:id>', views.CharacterView.as_view()),
    path('character/list', views.CharacterListView.as_view()),
    path('game/login', views.GameLoginView.as_view()),
    path('game/assets', views.GameAssetsView.as_view()),
    path('game/globalSettings', views.GameGlobalSettingsView.as_view()),
    path('user/inventory', views.InventoryView.as_view()),
    path('user/parcels/<int:parcel_id>', views.ParcelsView.as_view()),
]
