from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.utils import timezone


class Sport(models.Model):
    """Model to store different sports"""
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=10, unique=True, help_text="Short code like 'FB' for Football")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Competition(models.Model):
    """Model to store competitions/leagues"""
    
    # Division choices
    DIVISION_CHOICES = [
        ('1', 'Division 1'),
        ('2', 'Division 2'), 
        ('3', 'Division 3'),
        ('none', 'Tournament/Cup'),
    ]
    
    # Competition type choices
    COMPETITION_TYPE_CHOICES = [
        ('championship', 'Championship Phase'),
        ('group_stage', 'Group Stage'),
        ('playoffs', 'Playoffs'),
        ('finals', 'Finals'),
        ('knockout', 'Knockout Phase'),
        ('regular_season', 'Regular Season'),
    ]
    
    name = models.CharField(max_length=100)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='competitions')
    country = models.CharField(max_length=50, blank=True, help_text="Country or region")
    
    # Updated fields based on your requirements
    division = models.CharField(
        max_length=10, 
        choices=DIVISION_CHOICES, 
        default='none',
        help_text="Division level (1, 2, 3) or none for tournaments"
    )
    competition_type = models.CharField(
        max_length=20,
        choices=COMPETITION_TYPE_CHOICES,
        default='regular_season',
        help_text="Type/phase of competition"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sport__name', 'name']
        unique_together = ['name', 'sport', 'division', 'competition_type']

    def __str__(self):
        division_display = f"Div {self.division}" if self.division != 'none' else "Tournament"
        type_display = self.get_competition_type_display()
        return f"{self.sport.name} - {self.name} ({division_display} - {type_display})"

    def get_display_name(self):
        """Get a clean display name for frontend"""
        return f"{self.name} - {self.get_competition_type_display()}"


class Team(models.Model):
    """Model to store teams"""
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=10, blank=True, help_text="Abbreviation like 'FCB'")
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='teams')
    country = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sport__name', 'name']
        unique_together = ['name', 'sport']

    def __str__(self):
        return f"{self.name} ({self.sport.name})"


class Bookmaker(models.Model):
    """Model to store bookmakers"""
    name = models.CharField(max_length=50, unique=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class BetType(models.Model):
    """Model to store different bet types/markets"""
    
    # Updated categories based on your requirements
    CATEGORY_CHOICES = [
        ('match_result', 'Match Result'),
        ('over_goals', 'Over Goals'),
        ('under_goals', 'Under Goals'),
        ('both_to_score', 'Both Teams to Score'),
        ('player', 'Player Markets'),
        ('handicap', 'Handicap'),
        ('total_points', 'Total Points'),
        ('set_games', 'Sets/Games'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(
        max_length=50, 
        choices=CATEGORY_CHOICES, 
        default='other'
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Bet(models.Model):
    """Main model to store individual bets"""
    
    # Bet outcome choices
    OUTCOME_CHOICES = [
        ('win', 'Win'),
        ('loss', 'Loss'),
        ('push', 'Push'),  # Tie/Draw for certain bet types
        ('void', 'Void'),  # Cancelled bet
        ('pending', 'Pending'),
    ]

    # Basic bet information
    date = models.DateTimeField(default=timezone.now, help_text="When the bet was placed")
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='bets')
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='bets')
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_bets')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_bets')
    neutral_ground = models.BooleanField(default=False, help_text="Is this match on neutral ground?")
    
    # Bet details
    bet_type = models.ForeignKey(BetType, on_delete=models.CASCADE, related_name='bets')
    bet_description = models.TextField(blank=True, help_text="Additional details about the bet")
    
    # Probabilities and odds
    estimated_probability = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Your estimated probability (%)"
    )
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE, related_name='bets')
    bookmaker_odds = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        validators=[MinValueValidator(1.01)],
        help_text="Decimal odds from bookmaker"
    )
    
    # Financial data
    stake = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)],
        help_text="Amount staked (€)"
    )
    
    # Results
    outcome = models.CharField(max_length=10, choices=OUTCOME_CHOICES, default='pending')
    profit_loss = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Profit/Loss amount (€)"
    )
    
    # Analytics fields
    confidence_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Confidence level (1-5)"
    )
    
    # Metadata
    notes = models.TextField(blank=True, help_text="Personal notes about this bet")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['sport']),
            models.Index(fields=['outcome']),
            models.Index(fields=['bookmaker']),
        ]

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} - {self.bet_type} ({self.date.strftime('%Y-%m-%d')})"

    @property
    def implied_probability(self):
        """Calculate implied probability from bookmaker odds"""
        if self.bookmaker_odds is not None and self.bookmaker_odds > 0:
            return round((1 / float(self.bookmaker_odds)) * 100, 2)
        return 0
    
    @property
    def bookmaker_edge(self):
        """Calculate bookmaker edge (margin)"""
        if self.estimated_probability is not None:
            return round(self.implied_probability - float(self.estimated_probability), 2)
        return 0
    
    @property
    def expected_value(self):
        """Calculate Expected Value (EV)"""
        if (self.estimated_probability is not None and 
            self.bookmaker_odds is not None and 
            self.stake is not None):
            
            prob = float(self.estimated_probability) / 100
            odds = float(self.bookmaker_odds)
            stake = float(self.stake)
            
            # EV = (Probability of winning * Amount won per bet) - (Probability of losing * Amount lost per bet)
            ev = (prob * (odds - 1) * stake) - ((1 - prob) * stake)
            return round(ev, 2)
        return 0
    
    @property
    def roi(self):
        """Calculate Return on Investment (ROI) %"""
        if self.stake is not None and self.stake > 0 and self.profit_loss is not None:
            return round((float(self.profit_loss) / float(self.stake)) * 100, 2)
        return 0
    
    @property
    def potential_payout(self):
        """Calculate potential payout (stake * odds)"""
        if self.stake is not None and self.bookmaker_odds is not None:
            return round(float(self.stake) * float(self.bookmaker_odds), 2)
        return 0
    
    @property
    def potential_profit(self):
        """Calculate potential profit (payout - stake)"""
        if self.stake is not None:
            return round(self.potential_payout - float(self.stake), 2)
        return 0

    def save(self, *args, **kwargs):
        """Override save to auto-calculate profit/loss for completed bets"""
        if self.outcome == 'win':
            self.profit_loss = self.potential_profit
        elif self.outcome == 'loss':
            self.profit_loss = -float(self.stake)
        elif self.outcome in ['push', 'void']:
            self.profit_loss = 0
        # For pending bets, keep current profit_loss value
        
        super().save(*args, **kwargs)

    # Analytics methods for dashboard
    @classmethod
    def get_total_bets(cls):
        """Get total number of bets"""
        return cls.objects.count()

    @classmethod
    def get_completed_bets(cls):
        """Get completed bets (win/loss/push/void)"""
        return cls.objects.exclude(outcome='pending')

    @classmethod
    def get_win_rate(cls):
        """Calculate overall win rate"""
        completed = cls.get_completed_bets()
        if completed.count() > 0:
            wins = completed.filter(outcome='win').count()
            return round((wins / completed.count()) * 100, 2)
        return 0

    @classmethod
    def get_total_profit_loss(cls):
        """Calculate total profit/loss"""
        return cls.get_completed_bets().aggregate(
            total=models.Sum('profit_loss')
        )['total'] or 0

    @classmethod
    def get_total_staked(cls):
        """Calculate total amount staked"""
        return cls.objects.aggregate(
            total=models.Sum('stake')
        )['total'] or 0

    @classmethod
    def get_average_odds(cls):
        """Calculate average odds"""
        return cls.objects.aggregate(
            avg=models.Avg('bookmaker_odds')
        )['avg'] or 0

    @classmethod
    def get_monthly_stats(cls, year=None, month=None):
        """Get monthly betting statistics"""
        if not year:
            year = timezone.now().year
        if not month:
            month = timezone.now().month
            
        monthly_bets = cls.objects.filter(
            date__year=year,
            date__month=month
        )
        
        return {
            'total_bets': monthly_bets.count(),
            'total_staked': monthly_bets.aggregate(models.Sum('stake'))['stake__sum'] or 0,
            'total_profit_loss': monthly_bets.exclude(outcome='pending').aggregate(
                models.Sum('profit_loss'))['profit_loss__sum'] or 0,
            'win_rate': cls._calculate_win_rate(monthly_bets.exclude(outcome='pending')),
        }

    @staticmethod
    def _calculate_win_rate(queryset):
        """Helper method to calculate win rate for a queryset"""
        total = queryset.count()
        if total > 0:
            wins = queryset.filter(outcome='win').count()
            return round((wins / total) * 100, 2)
        return 0