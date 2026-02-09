from django.urls import path
from . import views
from . import auth_views
from . import dashboard_views

urlpatterns = [
    # Authentication URLs
    path('signup/', auth_views.signup_view, name='signup'),
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    
    # Dashboard URLs
    path('dashboard/', dashboard_views.dashboard_view, name='dashboard'),
    path('search/<int:search_id>/', dashboard_views.search_detail_view, name='search_detail'),
    path('search/<int:search_id>/delete/', dashboard_views.delete_search_view, name='delete_search'),
    
    # Search URLs
    path('', views.search_patents, name='search_patents'),
]

