from django.urls import path, include
from newsapp import views

app_name = "newsapp"

urlpatterns = [
    path('', views.mainpage, name='mainpage'),
    path('auth_login/', views.auth_login, name='auth_login'),
    path('create_account/', views.create_account, name='create_account'),
    path('auth_logout/', views.auth_logout, name='auth_logout'),
    path('get_distinct_categories/', views.get_distinct_categories, name='get_distinct_categories'),
    path('browse_category/<slug:category_value>/', views.browse_category, name='browse_category'),
    path('profile/', views.profile, name='profile'),
    path('update_categories/', views.update_categories, name='update_categories'),
    path('get_favourite_categories/', views.get_favourite_categories, name='get_favourite_categories'),
    path('like_article/', views.like_article, name='like_article'),
    path('article_page/<int:article_id>/', views.article_page, name='article_page'),
    path('create_comment/', views.create_comment, name='create_comment'),
    path('delete_comment/', views.delete_comment, name='delete_comment'),
    path('edit_comment/', views.edit_comment, name='edit_comment'),
]