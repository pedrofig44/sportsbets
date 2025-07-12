/**
 * Inicialização dos gráficos do dashboard
 * static/js/dashboard.js
 */

class DashboardCharts {
    constructor() {
        this.charts = {};
        this.urls = {
            profitEvolution: '/bets/chart-data/profit-evolution/',
            roiBySport: '/bets/chart-data/roi-by-sport/',
            monthlySummary: '/bets/chart-data/monthly-summary/'
        };
    }

    /**
     * Inicializa todos os gráficos do dashboard
     */
    async init() {
        try {
            await this.waitForApexCharts();
            await this.initProfitEvolutionChart();
            // Adicione outros gráficos aqui conforme necessário
            // await this.initROIBySportChart();
            // await this.initMonthlySummaryChart();
            
            console.log('Dashboard charts initialized successfully');
        } catch (error) {
            console.error('Error initializing dashboard charts:', error);
        }
    }

    /**
     * Aguarda o ApexCharts estar disponível
     */
    waitForApexCharts() {
        return new Promise((resolve, reject) => {
            let attempts = 0;
            const maxAttempts = 50; // 5 segundos máximo
            
            const checkApexCharts = () => {
                if (typeof ApexCharts !== 'undefined') {
                    resolve();
                } else if (attempts < maxAttempts) {
                    attempts++;
                    setTimeout(checkApexCharts, 100);
                } else {
                    reject(new Error('ApexCharts not loaded'));
                }
            };
            
            checkApexCharts();
        });
    }

    /**
     * Inicializa o gráfico de evolução dos lucros
     */
    async initProfitEvolutionChart() {
        const container = document.getElementById('profit-evolution-chart');
        if (container && window.ProfitEvolutionChart) {
            try {
                this.charts.profitEvolution = new window.ProfitEvolutionChart(
                    'profit-evolution-chart',
                    this.urls.profitEvolution
                );
                await this.charts.profitEvolution.init();
            } catch (error) {
                console.error('Error initializing profit evolution chart:', error);
            }
        }
    }

    /**
     * Atualiza todos os gráficos
     */
    async updateAllCharts() {
        const updatePromises = Object.values(this.charts)
            .filter(chart => chart && typeof chart.update === 'function')
            .map(chart => chart.update().catch(error => 
                console.error('Error updating chart:', error)
            ));
        
        await Promise.allSettled(updatePromises);
    }

    /**
     * Destroi todos os gráficos (útil para limpeza)
     */
    destroyAllCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        this.charts = {};
    }

    /**
     * Redimensiona todos os gráficos (útil para mudanças de layout)
     */
    resizeAllCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.chart && typeof chart.chart.resize === 'function') {
                chart.chart.resize();
            }
        });
    }
}

// Inicialização quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    window.dashboardCharts = new DashboardCharts();
    window.dashboardCharts.init();
});

// Redimensionar gráficos quando a janela mudar de tamanho
window.addEventListener('resize', function() {
    if (window.dashboardCharts) {
        window.dashboardCharts.resizeAllCharts();
    }
});

// Auto-refresh dos gráficos a cada 5 minutos (opcional)
setInterval(() => {
    if (window.dashboardCharts) {
        window.dashboardCharts.updateAllCharts();
    }
}, 5 * 60 * 1000);