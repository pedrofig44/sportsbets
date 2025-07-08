from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count, Avg
from .models import Sport, Competition, Team, Bookmaker, BetType, Bet


@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'total_bets', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code']
    ordering = ['name']

    def total_bets(self, obj):
        return obj.bets.count()
    total_bets.short_description = 'Total Bets'


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'sport', 'country', 'division_display', 
        'competition_type_display', 'is_active', 'total_bets'
    ]
    list_filter = [
        'sport', 'division', 'competition_type', 
        'is_active', 'country'
    ]
    search_fields = ['name', 'country']
    ordering = ['sport__name', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'sport', 'country')
        }),
        ('Competition Details', {
            'fields': ('division', 'competition_type', 'is_active')
        }),
    )

    def division_display(self, obj):
        if obj.division == 'none':
            return format_html('<span style="color: #007cba; font-weight: bold;">Tournament</span>')
        else:
            return format_html('<span style="color: #28a745;">Division {}</span>', obj.division)
    division_display.short_description = 'Division'
    division_display.admin_order_field = 'division'

    def competition_type_display(self, obj):
        colors = {
            'championship': '#dc3545',
            'group_stage': '#ffc107', 
            'playoffs': '#fd7e14',
            'finals': '#28a745',
            'knockout': '#6f42c1',
            'regular_season': '#007cba'
        }
        color = colors.get(obj.competition_type, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_competition_type_display()
        )
    competition_type_display.short_description = 'Type'
    competition_type_display.admin_order_field = 'competition_type'

    def total_bets(self, obj):
        return obj.bets.count()
    total_bets.short_description = 'Total Bets'


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_name', 'sport', 'country', 'is_active', 'total_bets']
    list_filter = ['sport', 'country', 'is_active']
    search_fields = ['name', 'short_name', 'country']
    ordering = ['sport__name', 'name']

    def total_bets(self, obj):
        return obj.home_bets.count() + obj.away_bets.count()
    total_bets.short_description = 'Total Bets'


@admin.register(Bookmaker)
class BookmakerAdmin(admin.ModelAdmin):
    list_display = ['name', 'website', 'is_active', 'total_bets', 'avg_odds']
    list_filter = ['is_active']
    search_fields = ['name', 'website']
    ordering = ['name']

    def total_bets(self, obj):
        return obj.bets.count()
    total_bets.short_description = 'Total Bets'

    def avg_odds(self, obj):
        avg = obj.bets.aggregate(Avg('bookmaker_odds'))['bookmaker_odds__avg']
        return f"{avg:.2f}" if avg else "0.00"
    avg_odds.short_description = 'Avg Odds'


@admin.register(BetType)
class BetTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_display', 'is_active', 'total_bets']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['category', 'name']

    def category_display(self, obj):
        # Color coding for different bet categories
        colors = {
            'match_result': '#007cba',
            'over_goals': '#28a745',
            'under_goals': '#ffc107',
            'both_to_score': '#fd7e14',
            'player': '#dc3545',
            'handicap': '#6f42c1',
            'total_points': '#20c997',
            'set_games': '#6610f2',
            'other': '#6c757d'
        }
        color = colors.get(obj.category, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_category_display()
        )
    category_display.short_description = 'Category'
    category_display.admin_order_field = 'category'

    def total_bets(self, obj):
        return obj.bets.count()
    total_bets.short_description = 'Total Bets'


@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = [
        'bet_summary', 'sport', 'competition_info', 'stake_display', 
        'odds_display', 'outcome_display', 'profit_loss_display', 
        'roi_display', 'date'
    ]
    list_filter = [
        'outcome', 'sport', 'competition', 'bookmaker', 
        'confidence_level', 'date', 'bet_type__category',
        'competition__division', 'competition__competition_type'
    ]
    search_fields = [
        'home_team__name', 'away_team__name', 'bet_type__name', 
        'bet_description', 'notes'
    ]
    ordering = ['-date', '-created_at']
    
    fieldsets = (
        ('Match Information', {
            'fields': (
                'date', 'sport', 'competition', 
                ('home_team', 'away_team'), 'neutral_ground'
            )
        }),
        ('Bet Details', {
            'fields': (
                'bet_type', 'bet_description', 
                'estimated_probability', 'confidence_level'
            )
        }),
        ('Financial Information', {
            'fields': (
                'bookmaker', 'bookmaker_odds', 'stake'
            )
        }),
        ('Results', {
            'fields': ('outcome', 'profit_loss')
        }),
        ('Analytics (Read-only)', {
            'fields': ('implied_probability_display', 'expected_value_display', 'bookmaker_edge_display'),
            'classes': ('collapse',),
            'description': 'These values are automatically calculated'
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = [
        'created_at', 'updated_at', 
        'implied_probability_display', 'expected_value_display', 'bookmaker_edge_display'
    ]
    
    # Custom display methods
    def bet_summary(self, obj):
        return f"{obj.home_team.name} vs {obj.away_team.name} - {obj.bet_type.name}"
    bet_summary.short_description = 'Bet'
    bet_summary.admin_order_field = 'home_team__name'

    def competition_info(self, obj):
        """Display competition with division and type info"""
        comp = obj.competition
        division = f"Div {comp.division}" if comp.division != 'none' else "Tournament"
        type_short = {
            'championship': 'Championship',
            'group_stage': 'Groups',
            'playoffs': 'Playoffs', 
            'finals': 'Finals',
            'knockout': 'Knockout',
            'regular_season': 'Regular'
        }.get(comp.competition_type, comp.competition_type)
        
        return f"{comp.name} ({division} - {type_short})"
    competition_info.short_description = 'Competition'
    competition_info.admin_order_field = 'competition__name'

    def stake_display(self, obj):
        return f"€{obj.stake}"
    stake_display.short_description = 'Stake'
    stake_display.admin_order_field = 'stake'

    def odds_display(self, obj):
        return f"{obj.bookmaker_odds} ({obj.implied_probability}%)"
    odds_display.short_description = 'Odds (Implied %)'
    odds_display.admin_order_field = 'bookmaker_odds'

    def outcome_display(self, obj):
        colors = {
            'win': '#28a745',
            'loss': '#dc3545', 
            'push': '#ffc107',
            'void': '#6c757d',
            'pending': '#17a2b8'
        }
        color = colors.get(obj.outcome, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_outcome_display()
        )
    outcome_display.short_description = 'Outcome'
    outcome_display.admin_order_field = 'outcome'

    def profit_loss_display(self, obj):
        color = '#28a745' if obj.profit_loss > 0 else '#dc3545' if obj.profit_loss < 0 else '#6c757d'
        return format_html(
            '<span style="color: {}; font-weight: bold;">€{}</span>',
            color,
            obj.profit_loss
        )
    profit_loss_display.short_description = 'P/L'
    profit_loss_display.admin_order_field = 'profit_loss'

    def roi_display(self, obj):
        roi = obj.roi
        color = '#28a745' if roi > 0 else '#dc3545' if roi < 0 else '#6c757d'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color,
            roi
        )
    roi_display.short_description = 'ROI'

    # Read-only calculated fields for admin
    def implied_probability_display(self, obj):
        return f"{obj.implied_probability}%"
    implied_probability_display.short_description = 'Implied Probability'

    def expected_value_display(self, obj):
        ev = obj.expected_value
        color = 'green' if ev > 0 else 'red' if ev < 0 else 'black'
        return format_html('<span style="color: {};">€{}</span>', color, ev)
    expected_value_display.short_description = 'Expected Value'

    def bookmaker_edge_display(self, obj):
        edge = obj.bookmaker_edge
        return f"{edge}%"
    bookmaker_edge_display.short_description = 'Bookmaker Edge'

    # Custom actions
    actions = ['mark_as_won', 'mark_as_lost', 'mark_as_void']

    def mark_as_won(self, request, queryset):
        updated = 0
        for bet in queryset:
            if bet.outcome == 'pending':
                bet.outcome = 'win'
                bet.save()
                updated += 1
        self.message_user(request, f'{updated} bets marked as won.')
    mark_as_won.short_description = "Mark selected bets as won"

    def mark_as_lost(self, request, queryset):
        updated = 0
        for bet in queryset:
            if bet.outcome == 'pending':
                bet.outcome = 'loss'
                bet.save()
                updated += 1
        self.message_user(request, f'{updated} bets marked as lost.')
    mark_as_lost.short_description = "Mark selected bets as lost"

    def mark_as_void(self, request, queryset):
        updated = 0
        for bet in queryset:
            if bet.outcome == 'pending':
                bet.outcome = 'void'
                bet.save()
                updated += 1
        self.message_user(request, f'{updated} bets marked as void.')
    mark_as_void.short_description = "Mark selected bets as void"

    # Add statistics to the changelist
    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        metrics = {
            'total_bets': qs.count(),
            'total_staked': qs.aggregate(Sum('stake'))['stake__sum'] or 0,
            'total_profit_loss': qs.exclude(outcome='pending').aggregate(
                Sum('profit_loss'))['profit_loss__sum'] or 0,
            'avg_odds': qs.aggregate(Avg('bookmaker_odds'))['bookmaker_odds__avg'] or 0,
            'win_rate': 0,
        }

        # Calculate win rate
        completed_bets = qs.exclude(outcome='pending')
        if completed_bets.count() > 0:
            wins = completed_bets.filter(outcome='win').count()
            metrics['win_rate'] = round((wins / completed_bets.count()) * 100, 2)

        response.context_data['summary'] = metrics
        return response
    
    def get_readonly_fields(self, request, obj=None):
        """Show calculated fields only when editing existing objects"""
        base_readonly = ['created_at', 'updated_at']
        
        # Only show calculated fields for existing objects (not when adding new)
        if obj:  # obj exists when editing, None when adding
            base_readonly.extend([
                'implied_probability_display', 
                'expected_value_display', 
                'bookmaker_edge_display'
            ])
        
        return base_readonly
    
    def get_fieldsets(self, request, obj=None):
        """Hide analytics fieldset when adding new bet"""
        base_fieldsets = [
            ('Match Information', {
                'fields': (
                    'date', 'sport', 'competition', 
                    ('home_team', 'away_team'), 'neutral_ground'
                )
            }),
            ('Bet Details', {
                'fields': (
                    'bet_type', 'bet_description', 
                    'estimated_probability', 'confidence_level'
                )
            }),
            ('Financial Information', {
                'fields': (
                    'bookmaker', 'bookmaker_odds', 'stake'
                )
            }),
            ('Results', {
                'fields': ('outcome', 'profit_loss')
            }),
            ('Notes', {
                'fields': ('notes',),
                'classes': ('collapse',)
            })
        ]
        
        # Only show analytics for existing objects
        if obj:
            analytics_fieldset = ('Analytics (Read-only)', {
                'fields': ('implied_probability_display', 'expected_value_display', 'bookmaker_edge_display'),
                'classes': ('collapse',),
                'description': 'These values are automatically calculated'
            })
            # Insert analytics before Notes
            base_fieldsets.insert(-1, analytics_fieldset)
        
        return base_fieldsets


# Admin site customization
admin.site.site_header = "SportBets Admin"
admin.site.site_title = "SportBets Admin Portal"
admin.site.index_title = "Welcome to SportBets Administration"