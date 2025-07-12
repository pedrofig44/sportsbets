# bets/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Bet, Sport, Competition, Team, Bookmaker, BetType
from decimal import Decimal


class BetForm(forms.ModelForm):
    class Meta:
        model = Bet
        fields = [
            'date', 'sport', 'competition', 'home_team', 'away_team', 
            'neutral_ground', 'bet_type', 'bet_description', 
            'estimated_probability', 'bookmaker', 'bookmaker_odds', 
            'stake', 'confidence_level', 'notes'
        ]
        
        widgets = {
            'date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                }
            ),
            'sport': forms.Select(attrs={'class': 'form-select'}),
            'competition': forms.Select(attrs={'class': 'form-select'}),
            'home_team': forms.Select(attrs={'class': 'form-select'}),
            'away_team': forms.Select(attrs={'class': 'form-select'}),
            'neutral_ground': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'bet_type': forms.Select(attrs={'class': 'form-select'}),
            'bet_description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Detalhes adicionais sobre a aposta...'
                }
            ),
            'estimated_probability': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '0',
                    'max': '100',
                    'step': '0.01',
                    'placeholder': '0.00'
                }
            ),
            'bookmaker': forms.Select(attrs={'class': 'form-select'}),
            'bookmaker_odds': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '1.01',
                    'step': '0.01',
                    'placeholder': '1.00'
                }
            ),
            'stake': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '0.01',
                    'step': '0.01',
                    'placeholder': '0.00'
                }
            ),
            'confidence_level': forms.Select(
                choices=[(i, f'{i} ⭐' * i) for i in range(1, 6)],
                attrs={'class': 'form-select'}
            ),
            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Notas pessoais sobre esta aposta...'
                }
            ),
        }
        
        labels = {
            'date': 'Data e Hora',
            'sport': 'Desporto',
            'competition': 'Competição',
            'home_team': 'Equipa Casa',
            'away_team': 'Equipa Visitante',
            'neutral_ground': 'Campo Neutro',
            'bet_type': 'Tipo de Aposta',
            'bet_description': 'Descrição da Aposta',
            'estimated_probability': 'Probabilidade Estimada (%)',
            'bookmaker': 'Casa de Apostas',
            'bookmaker_odds': 'Odds',
            'stake': 'Valor Apostado (€)',
            'confidence_level': 'Nível de Confiança',
            'notes': 'Notas',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter active items only
        self.fields['sport'].queryset = Sport.objects.filter(is_active=True)
        self.fields['competition'].queryset = Competition.objects.filter(is_active=True)
        self.fields['home_team'].queryset = Team.objects.filter(is_active=True)
        self.fields['away_team'].queryset = Team.objects.filter(is_active=True)
        self.fields['bookmaker'].queryset = Bookmaker.objects.filter(is_active=True)
        self.fields['bet_type'].queryset = BetType.objects.filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        home_team = cleaned_data.get('home_team')
        away_team = cleaned_data.get('away_team')
        sport = cleaned_data.get('sport')
        competition = cleaned_data.get('competition')
        estimated_probability = cleaned_data.get('estimated_probability')
        bookmaker_odds = cleaned_data.get('bookmaker_odds')
        
        # Validate teams are different
        if home_team and away_team and home_team == away_team:
            raise ValidationError("A equipa da casa e visitante devem ser diferentes.")
        
        # Validate teams belong to the same sport
        if home_team and away_team:
            if home_team.sport != away_team.sport:
                raise ValidationError("Ambas as equipas devem pertencer ao mesmo desporto.")
        
        # Validate competition belongs to the sport
        if sport and competition and competition.sport != sport:
            raise ValidationError("A competição deve pertencer ao desporto selecionado.")
        
        # Validate teams belong to the sport
        if sport and home_team and home_team.sport != sport:
            raise ValidationError("A equipa da casa deve pertencer ao desporto selecionado.")
            
        if sport and away_team and away_team.sport != sport:
            raise ValidationError("A equipa visitante deve pertencer ao desporto selecionado.")
        
        return cleaned_data