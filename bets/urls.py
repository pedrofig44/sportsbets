# bets/urls.py
from django.urls import path
from . import views

app_name = 'bets'

urlpatterns = [
    # Main dashboard
    path('', views.dashboard_view, name='dashboard'),
    
    # Bet management
    path('add/', views.add_bet_view, name='add_bet'),
    
    # Chart data endpoints (existing)
    path('chart-data/profit-evolution/', views.profit_evolution_data, name='profit_evolution_data'),
    path('chart-data/roi-by-sport/', views.roi_by_sport_data, name='roi_by_sport_data'),
    path('chart-data/monthly-summary/', views.monthly_summary_data, name='monthly_summary_data'),
    
    # Admin endpoints for forms
    path('create-competition/', views.create_competition, name='create_competition'),
    path('create-team/', views.create_team, name='create_team'),
    path('api/sports/', views.get_sports_data, name='get_sports_data'),
]