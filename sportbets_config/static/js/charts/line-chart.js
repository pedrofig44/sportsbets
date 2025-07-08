/**
 * Gráfico de linha para evolução dos lucros
 * static/js/charts/line-chart.js
 */

class ProfitEvolutionChart {
    constructor(containerId, dataUrl) {
        this.containerId = containerId;
        this.dataUrl = dataUrl;
        this.chart = null;
        this.chartBase = window.ChartBase;
    }

    /**
     * Inicializa o gráfico
     */
    async init() {
        try {
            this.chartBase.showLoading(this.containerId);
            const data = await this.fetchData();
            this.renderChart(data);
        } catch (error) {
            console.error('Erro ao inicializar gráfico de evolução:', error);
            this.chartBase.showError(this.containerId, 'Erro ao carregar evolução dos lucros');
        }
    }

    /**
     * Busca dados do servidor
     * @returns {Promise<object>}
     */
    async fetchData() {
        const response = await fetch(this.dataUrl);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    }

    /**
     * Renderiza o gráfico
     * @param {object} data 
     */
    renderChart(data) {
        const options = this.chartBase.mergeOptions({
            chart: {
                type: 'area',
                height: 300,
                zoom: {
                    enabled: false
                }
            },
            series: [{
                name: 'Lucro Acumulado',
                data: data.cumulative_profit || []
            }, {
                name: 'Lucro Mensal',
                data: data.monthly_profit || []
            }],
            xaxis: {
                categories: data.labels || [],
                title: {
                    text: 'Período'
                },
                labels: {
                    style: {
                        fontSize: '12px'
                    }
                }
            },
            yaxis: {
                title: {
                    text: 'Lucro (€)'
                },
                labels: {
                    formatter: (value) => this.chartBase.formatCurrency(value)
                }
            },
            tooltip: {
                y: {
                    formatter: (value) => this.chartBase.formatCurrency(value)
                }
            },
            fill: {
                type: 'gradient',
                gradient: {
                    shadeIntensity: 1,
                    inverseColors: false,
                    opacityFrom: 0.5,
                    opacityTo: 0,
                    stops: [0, 90, 100]
                }
            },
            stroke: {
                curve: 'smooth',
                width: 2
            },
            markers: {
                size: 4,
                colors: ['#fff'],
                strokeColors: ['#3B82F6', '#10B981'],
                strokeWidth: 2,
                hover: {
                    size: 6
                }
            },
            legend: {
                position: 'top',
                horizontalAlign: 'right'
            }
        });

        // Destruir gráfico anterior se existir
        if (this.chart) {
            this.chart.destroy();
        }

        // Criar novo gráfico
        this.chart = new ApexCharts(
            document.querySelector(`#${this.containerId}`), 
            options
        );
        
        this.chart.render();
    }

    /**
     * Atualiza dados do gráfico
     */
    async update() {
        try {
            const data = await this.fetchData();
            if (this.chart) {
                this.chart.updateSeries([{
                    name: 'Lucro Acumulado',
                    data: data.cumulative_profit || []
                }, {
                    name: 'Lucro Mensal',
                    data: data.monthly_profit || []
                }]);
                this.chart.updateOptions({
                    xaxis: {
                        categories: data.labels || []
                    }
                });
            }
        } catch (error) {
            console.error('Erro ao atualizar gráfico:', error);
        }
    }

    /**
     * Destroi o gráfico
     */
    destroy() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }
}

// Exportar para uso global
window.ProfitEvolutionChart = ProfitEvolutionChart;