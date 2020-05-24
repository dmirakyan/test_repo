from django.urls import path
from rango import views


app_name = 'rango'

urlpatterns = [
    path('',views.index, name='index'),
    path('about',views.AboutView.as_view(), name='about'),
    path('category/<slug:category_name_slug>/',views.show_category,name='show_category'),
    path('add_category/',views.add_category, name='add_category'),
    path('category/<slug:category_name_slug>/add_page/',views.add_page,name='add_page'),
    # path('register/',views.register,name='register'),
    # path('login/',views.user_login, name='login'),
    # path('logout/', views.user_logout, name='logout'),
    path('restricted/', views.restricted, name='restricted'),
    path('search/',views.search, name='search'),
    path('goto/', views.goto_url, name='goto'),
    path('initialize_profile/', views.initialize_profile, name='initialize_profile'),
    path('prof/<username>/', views.ProfileView.as_view(), name='prof'),
    path('like_category/', views.LikeCategoryView.as_view(),name='like_category'),
    path('suggest/', views.CategorySuggestionView.as_view(), name='suggest'),
    path('search_add_page/', views.AddPageFromSearch.as_view(), name='search_add_page'),
]