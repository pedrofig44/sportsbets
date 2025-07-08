from django.urls import path
from . import views

app_name = 'bets'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    
    # URLs para dados dos gráficos (agora a apontar para views.py)
    path('chart-data/profit-evolution/', views.profit_evolution_data, name='profit_evolution_data'),
    path('chart-data/roi-by-sport/', views.roi_by_sport_data, name='roi_by_sport_data'),
    path('chart-data/monthly-summary/', views.monthly_summary_data, name='monthly_summary_data'),
]
# No seu urls.py principal (projeto)
# from django.urls import path, include

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', include('bets.urls')),  # ou path('dashboard/', include('bets.urls')),
# ]