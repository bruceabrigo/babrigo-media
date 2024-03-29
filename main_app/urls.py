from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('reviews', views.show_reviews, name='reviews'),
    path('reviews/<int:review_id>/', views.view_review, name='edit_review'),
    path('reviews/create/', views.PostReview.as_view(), name='create_review'),
    path('reviews/<int:pk>/update/', views.UpdateReview.as_view(), name='update_review'),
    path('reviews/<int:pk>/delete/', views.DeleteReview.as_view(), name='delete_review'),
    # ----------------------------- collections view paths -----------------------------
    path('collections', views.collections, name='collections'),
    path('collections/create/', views.CreateCollection.as_view(), name='create_collection'),
    path('collections/<int:pk>/delete/', views.DeleteCollection.as_view(), name='delete_collection'),
    path('collections/<int:collection_id>/', views.view_collection, name='view_collection'),
    path('collections/mine/<int:user_id>/', views.my_collections, name='my_collections'),
    path('collections/<int:collection_id>/upload', views.upload_photo, name='upload_photo'),
    # ----------------------------- contact form -----------------------------
    path('contact', views.contact, name='contact'),
    # ----------------------------- auth -----------------------------
    path('accounts/signup', views.signup, name='signup')
]
