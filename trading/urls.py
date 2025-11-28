# trading/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'trading'

router = DefaultRouter()
router.register(r'camarilla-levels', views.CamarillaLevelViewSet)
router.register(r'whole-number-stocks', views.WholeNumberStockViewSet)
router.register(r'script-logs', views.ScriptRunLogViewSet)

urlpatterns = [
    # Dashboard
    path('', views.dashboard_home, name='dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),

    # HTML Views
    path('camarilla/', views.camarilla_levels_view, name='camarilla_levels'),
    path('camarilla/<int:pk>/', views.camarilla_detail_view, name='camarilla_detail'),
    path('whole-number/', views.whole_number_view, name='whole_number'),
    path('logs/', views.script_logs_view, name='script_logs'),
    path('analytics/', views.analytics_view, name='analytics'),

    # Add this line for symbol management
    path('symbols/', views.symbol_management, name='symbol_management'),

    # API Endpoints
    path('api/run-camarilla/', views.run_camarilla_script, name='run_camarilla'),
    path('api/run-whole-number/', views.run_whole_number_script, name='run_whole_number'),
    path('api/script-status/', views.get_script_status, name='script_status'),

    # DRF API Routes
    path('api/', include(router.urls)),
]