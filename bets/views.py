from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Sum, Avg, Count, Q
from .models import Bet, Sport, BetType, Bookmaker, Competition, Team
from django.utils import timezone 
from datetime import datetime, timedelta
from decimal import Decimal
from .forms import BetForm

# Adicione estas importações no topo do views.py
from django.http import JsonResponse
import calendar

def add_bet_view(request):
    """View for adding a new bet"""
    if request.method == 'POST':
        form = BetForm(request.POST)
        if form.is_valid():
            bet = form.save()
            messages.success(request, f'Aposta adicionada com sucesso! EV: €{bet.expected_value}')
            return redirect('bets:dashboard')
        else:
            messages.error(request, 'Erro ao adicionar aposta. Verifique os dados inseridos.')
    else:
        form = BetForm()
    
    context = {
        'form': form,
        'page_title': 'Adicionar Nova Aposta'
    }
    return render(request, 'bets/add_bet.html', context)

def calculate_ev(request):
    """HTMX view to calculate and display Expected Value in real-time"""
    try:
        estimated_prob = request.GET.get('estimated_probability')
        odds = request.GET.get('bookmaker_odds')
        stake = request.GET.get('stake')
        
        ev = 0
        implied_prob = 0
        potential_profit = 0
        roi_percentage = 0
        
        if estimated_prob and odds and stake:
            prob = float(estimated_prob) / 100
            odds_val = float(odds)
            stake_val = float(stake)
            
            # Calculate Expected Value
            ev = (prob * (odds_val - 1) * stake_val) - ((1 - prob) * stake_val)
            
            # Calculate implied probability
            implied_prob = (1 / odds_val) * 100
            
            # Calculate potential profit
            potential_profit = (odds_val - 1) * stake_val
            
            # Calculate ROI percentage
            roi_percentage = (potential_profit / stake_val) * 100 if stake_val > 0 else 0
        
        context = {
            'ev': round(ev, 2),
            'implied_prob': round(implied_prob, 2),
            'estimated_prob': float(estimated_prob) if estimated_prob else 0,
            'potential_profit': round(potential_profit, 2),
            'roi_percentage': round(roi_percentage, 2),
            'ev_positive': ev > 0,
            'prob_advantage': float(estimated_prob) > implied_prob if estimated_prob else False
        }
        
        return render(request, 'bets/partials/ev_display.html', context)
    
    except (ValueError, TypeError):
        return render(request, 'bets/partials/ev_display.html', {
            'ev': 0,
            'implied_prob': 0,
            'estimated_prob': 0,
            'potential_profit': 0,
            'roi_percentage': 0,
            'ev_positive': False,
            'prob_advantage': False
        })

def profit_evolution_data(request):
    """
    Fornece dados JSON para o gráfico de evolução dos lucros (últimos 30 dias)
    """
    print("=== DEBUG: profit_evolution_data called (30 days) ===")
    
    try:
        # Período - últimos 30 dias
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        print(f"DEBUG: Date range: {start_date} to {end_date}")
        
        # Buscar apostas completadas no período
        completed_bets = Bet.objects.filter(
            date__date__gte=start_date,
            date__date__lte=end_date
        ).exclude(outcome='pending').order_by('date')
        
        print(f"DEBUG: Found {completed_bets.count()} completed bets")
        
        # Dicionário para agrupar por dia
        daily_data = {}
        
        # Inicializar todos os dias do período com lucro 0
        current_date = start_date
        while current_date <= end_date:
            day_key = current_date.strftime('%Y-%m-%d')
            daily_data[day_key] = {
                'daily_profit': Decimal('0'),
                'label': current_date.strftime('%d/%m'),  # Formato mais compacto
                'full_date': current_date
            }
            current_date += timedelta(days=1)
        
        print(f"DEBUG: Created {len(daily_data)} day slots")
        
        # Processar apostas - agrupar por dia
        for bet in completed_bets:
            day_key = bet.date.strftime('%Y-%m-%d')
            if day_key in daily_data:
                daily_data[day_key]['daily_profit'] += bet.profit_loss or Decimal('0')
                print(f"DEBUG: Added bet {bet.id} profit {bet.profit_loss} to {day_key}")
        
        # Preparar dados para o gráfico
        labels = []
        daily_profits = []
        cumulative_data = []
        cumulative_profit = Decimal('0')
        
        # Processar dados ordenados por data
        for day_key in sorted(daily_data.keys()):
            day_info = daily_data[day_key]
            daily_profit = float(day_info['daily_profit'])
            cumulative_profit += day_info['daily_profit']
            
            labels.append(day_info['label'])
            daily_profits.append(daily_profit)
            cumulative_data.append(float(cumulative_profit))
        
        # Calcular estatísticas adicionais
        total_bets = completed_bets.count()
        days_with_bets = len([day for day in daily_data.values() if day['daily_profit'] != 0])
        best_day = max(daily_profits) if daily_profits else 0
        worst_day = min(daily_profits) if daily_profits else 0
        
        print(f"DEBUG: Final data - {len(labels)} days, best day: {best_day}, worst day: {worst_day}")
        
        # Resposta JSON
        response_data = {
            'labels': labels,
            'daily_profit': daily_profits,
            'cumulative_profit': cumulative_data,
            'period': {
                'start': start_date.strftime('%d/%m/%Y'),
                'end': end_date.strftime('%d/%m/%Y'),
                'days': len(labels)
            },
            'stats': {
                'total_bets': total_bets,
                'days_with_bets': days_with_bets,
                'best_day': best_day,
                'worst_day': worst_day,
                'average_daily': float(cumulative_profit / len(labels)) if len(labels) > 0 else 0
            },
            'final_cumulative': float(cumulative_profit),
            'debug': f'Successfully processed {total_bets} bets across {len(labels)} days'
        }
        
        print("DEBUG: Returning JSON response")
        return JsonResponse(response_data)
        
    except Exception as e:
        print(f"DEBUG: Exception occurred: {str(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        return JsonResponse({
            'error': 'Erro ao processar dados',
            'message': str(e),
            'debug': 'Exception in profit_evolution_data'
        }, status=500)


def roi_by_sport_data(request):
    """
    Dados para gráfico de ROI por desporto
    """
    print("=== DEBUG: roi_by_sport_data called ===")
    
    try:
        sports_data = []
        all_sports = Sport.objects.all()
        print(f"DEBUG: Found {all_sports.count()} sports")
        
        for sport in all_sports:
            sport_bets = Bet.objects.filter(sport=sport).exclude(outcome='pending')
            print(f"DEBUG: Sport {sport.name} has {sport_bets.count()} completed bets")
            
            if sport_bets.exists():
                total_staked = sport_bets.aggregate(Sum('stake'))['stake__sum'] or Decimal('0')
                total_profit = sport_bets.aggregate(Sum('profit_loss'))['profit_loss__sum'] or Decimal('0')
                
                if total_staked > 0:
                    roi = (float(total_profit) / float(total_staked)) * 100
                    
                    sports_data.append({
                        'sport': sport.name,
                        'roi': round(roi, 2),
                        'total_bets': sport_bets.count(),
                        'profit': float(total_profit)
                    })
                    
                    print(f"DEBUG: {sport.name} - ROI: {roi:.2f}%, Profit: {total_profit}")
        
        # Ordenar por ROI
        sports_data.sort(key=lambda x: x['roi'], reverse=True)
        print(f"DEBUG: Returning {len(sports_data)} sports with data")
        
        return JsonResponse({
            'sports': sports_data[:10],  # Top 10 desportos
            'labels': [sport['sport'] for sport in sports_data[:10]],
            'roi_values': [sport['roi'] for sport in sports_data[:10]],
            'debug': f'Processed {len(sports_data)} sports'
        })
        
    except Exception as e:
        print(f"DEBUG: Exception in roi_by_sport_data: {str(e)}")
        return JsonResponse({
            'error': 'Erro ao processar dados de ROI',
            'message': str(e),
            'debug': 'Exception in roi_by_sport_data'
        }, status=500)


def monthly_summary_data(request):
    """
    Dados para gráfico de resumo mensal
    """
    print("=== DEBUG: monthly_summary_data called ===")
    
    try:
        # Últimos 6 meses
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=180)
        
        print(f"DEBUG: Monthly summary range: {start_date} to {end_date}")
        
        monthly_stats = []
        current_date = start_date.replace(day=1)
        
        while current_date <= end_date:
            month_bets = Bet.objects.filter(
                date__year=current_date.year,
                date__month=current_date.month
            ).exclude(outcome='pending')
            
            print(f"DEBUG: {current_date.strftime('%Y-%m')} has {month_bets.count()} bets")
            
            if month_bets.exists():
                total_staked = month_bets.aggregate(Sum('stake'))['stake__sum'] or Decimal('0')
                total_profit = month_bets.aggregate(Sum('profit_loss'))['profit_loss__sum'] or Decimal('0')
                wins = month_bets.filter(outcome='win').count()
                total_completed = month_bets.count()
                win_rate = (wins / total_completed * 100) if total_completed > 0 else 0
                
                monthly_stats.append({
                    'month': f"{calendar.month_name[current_date.month][:3]} {current_date.year}",
                    'profit': float(total_profit),
                    'staked': float(total_staked),
                    'win_rate': round(win_rate, 2),
                    'bets_count': total_completed
                })
            
            # Próximo mês
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        print(f"DEBUG: Generated {len(monthly_stats)} monthly stats")
        
        return JsonResponse({
            'monthly_data': monthly_stats,
            'labels': [item['month'] for item in monthly_stats],
            'profits': [item['profit'] for item in monthly_stats],
            'staked': [item['staked'] for item in monthly_stats],
            'win_rates': [item['win_rate'] for item in monthly_stats],
            'debug': f'Generated {len(monthly_stats)} months of data'
        })
        
    except Exception as e:
        print(f"DEBUG: Exception in monthly_summary_data: {str(e)}")
        return JsonResponse({
            'error': 'Erro ao processar dados mensais',
            'message': str(e),
            'debug': 'Exception in monthly_summary_data'
        }, status=500)


def dashboard_view(request):
    """View para o dashboard principal de análise de apostas"""
    
    # Estatísticas gerais
    all_bets = Bet.objects.all()
    completed_bets = all_bets.exclude(outcome='pending')
    
    # Métricas principais
    total_bets = all_bets.count()
    total_staked = all_bets.aggregate(Sum('stake'))['stake__sum'] or Decimal('0')
    total_profit_loss = completed_bets.aggregate(Sum('profit_loss'))['profit_loss__sum'] or Decimal('0')
    
    # Taxa de vitórias
    if completed_bets.count() > 0:
        wins = completed_bets.filter(outcome='win').count()
        win_rate = round((wins / completed_bets.count()) * 100, 2)
    else:
        win_rate = 0
    
    # ROI geral
    if total_staked > 0:
        roi = round((float(total_profit_loss) / float(total_staked)) * 100, 2)
    else:
        roi = 0
    
    # Apostas pendentes
    pending_bets = all_bets.filter(outcome='pending').count()
    pending_stake = all_bets.filter(outcome='pending').aggregate(Sum('stake'))['stake__sum'] or Decimal('0')
    
    # Odds média
    avg_odds = all_bets.aggregate(Avg('bookmaker_odds'))['bookmaker_odds__avg'] or 0
    if avg_odds:
        avg_odds = round(float(avg_odds), 2)
    
    # Valor esperado médio (apenas de apostas com dados completos)
    bets_with_data = all_bets.filter(
        estimated_probability__isnull=False,
        bookmaker_odds__isnull=False,
        stake__isnull=False
    )
    
    total_ev = 0
    ev_count = 0
    for bet in bets_with_data:
        if bet.expected_value is not None:
            total_ev += bet.expected_value
            ev_count += 1
    
    avg_expected_value = round(total_ev / ev_count, 2) if ev_count > 0 else 0
    
    # Estatísticas dos últimos 30 dias
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_bets = all_bets.filter(date__gte=thirty_days_ago)
    recent_completed = recent_bets.exclude(outcome='pending')
    
    recent_profit_loss = recent_completed.aggregate(Sum('profit_loss'))['profit_loss__sum'] or Decimal('0')
    recent_staked = recent_bets.aggregate(Sum('stake'))['stake__sum'] or Decimal('0')
    
    # Tendência (comparação com 30 dias anteriores)
    sixty_days_ago = timezone.now() - timedelta(days=60)
    previous_period = all_bets.filter(
        date__gte=sixty_days_ago, 
        date__lt=thirty_days_ago
    ).exclude(outcome='pending')
    
    previous_profit_loss = previous_period.aggregate(Sum('profit_loss'))['profit_loss__sum'] or Decimal('0')
    
    # Calcular tendência de lucro
    if previous_profit_loss != 0:
        profit_trend = round(((float(recent_profit_loss) - float(previous_profit_loss)) / float(abs(previous_profit_loss))) * 100, 2)
    elif recent_profit_loss > 0:
        profit_trend = 100  # 100% de melhoria se antes era 0 e agora é positivo
    else:
        profit_trend = 0
    
    # Estatísticas por desporto
    sports_stats = []
    for sport in Sport.objects.all():
        sport_bets = completed_bets.filter(sport=sport)
        if sport_bets.exists():
            sport_profit = sport_bets.aggregate(Sum('profit_loss'))['profit_loss__sum'] or Decimal('0')
            sport_wins = sport_bets.filter(outcome='win').count()
            sport_total = sport_bets.count()
            sport_win_rate = round((sport_wins / sport_total) * 100, 2) if sport_total > 0 else 0
            
            sports_stats.append({
                'sport': sport,
                'total_bets': sport_total,
                'profit_loss': sport_profit,
                'win_rate': sport_win_rate
            })
    
    # Últimas apostas (últimas 10)
    latest_bets = all_bets.order_by('-date', '-created_at')[:10]
    
    # Top bookmakers por volume
    bookmaker_stats = []
    for bookmaker in Bookmaker.objects.all():
        bm_bets = completed_bets.filter(bookmaker=bookmaker)
        if bm_bets.exists():
            bm_profit = bm_bets.aggregate(Sum('profit_loss'))['profit_loss__sum'] or Decimal('0')
            bm_total = bm_bets.count()
            bm_staked = all_bets.filter(bookmaker=bookmaker).aggregate(Sum('stake'))['stake__sum'] or Decimal('0')
            
            bookmaker_stats.append({
                'bookmaker': bookmaker,
                'total_bets': bm_total,
                'total_staked': bm_staked,
                'profit_loss': bm_profit
            })
    
    # Ordenar por volume apostado
    bookmaker_stats.sort(key=lambda x: x['total_staked'], reverse=True)
    
    context = {
        # Métricas principais
        'total_bets': total_bets,
        'total_staked': total_staked,
        'total_profit_loss': total_profit_loss,
        'win_rate': win_rate,
        'roi': roi,
        'pending_bets': pending_bets,
        'pending_stake': pending_stake,
        'avg_odds': avg_odds,
        'avg_expected_value': avg_expected_value,
        
        # Estatísticas recentes
        'recent_profit_loss': recent_profit_loss,
        'recent_staked': recent_staked,
        'profit_trend': profit_trend,
        
        # Listas
        'sports_stats': sports_stats[:5],  # Top 5 desportos
        'latest_bets': latest_bets,
        'bookmaker_stats': bookmaker_stats[:5],  # Top 5 bookmakers
        
        # Status de tendência
        'profit_trend_positive': profit_trend > 0,
        'roi_positive': roi > 0,
        'ev_positive': avg_expected_value > 0,
    }
    
    return render(request, 'bets/dashboard.html', context)


