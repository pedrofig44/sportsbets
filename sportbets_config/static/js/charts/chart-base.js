/**
 * Configurações base para todos os gráficos Apex Charts
 * static/js/charts/chart-base.js
 */

class ChartBase {
    constructor() {
        this.defaultOptions = {
            chart: {
                fontFamily: 'Inter, sans-serif',
                toolbar: {
                    show: false
                },
                background: 'transparent',
                animations: {
                    enabled: true,
                    easing: 'easeinout',
                    speed: 800,
                }
            },
            colors: ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'],
            grid: {
                borderColor: '#E5E7EB',
                strokeDashArray: 3,
            },
            tooltip: {
                theme: 'light',
                style: {
                    fontSize: '12px',
                    fontFamily: 'Inter, sans-serif',
                }
            },
            responsive: [{
                breakpoint: 768,
                options: {
                    chart: {
                        height: 250
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }]
        };
    }

    /**
     * Formata valores monetários para exibição
     * @param {number} value 
     * @returns {string}
     */
    formatCurrency(value) {
        return new Intl.NumberFormat('pt-PT', {
            style: 'currency',
            currency: 'EUR',
            minimumFractionDigits: 2
        }).format(value);
    }

    /**
     * Formata percentagens
     * @param {number} value 
     * @returns {string}
     */
    formatPercentage(value) {
        return `${value.toFixed(2)}%`;
    }

    /**
     * Combina configurações base com configurações específicas
     * @param {object} specificOptions 
     * @returns {object}
     */
    mergeOptions(specificOptions) {
        return this.deepMerge(this.defaultOptions, specificOptions);
    }

    /**
     * Deep merge de objectos
     * @param {object} target 
     * @param {object} source 
     * @returns {object}
     */
    deepMerge(target, source) {
        const result = { ...target };
        
        for (const key in source) {
            if (source.hasOwnProperty(key)) {
                if (typeof source[key] === 'object' && source[key] !== null && !Array.isArray(source[key])) {
                    result[key] = this.deepMerge(result[key] || {}, source[key]);
                } else {
                    result[key] = source[key];
                }
            }
        }
        
        return result;
    }

    /**
     * Mostra loading no container do gráfico
     * @param {string} containerId 
     */
    showLoading(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="d-flex justify-content-center align-items-center" style="height: 100%;">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">A carregar...</span>
                    </div>
                </div>
            `;
        }
    }

    /**
     * Mostra erro no container do gráfico
     * @param {string} containerId 
     * @param {string} message 
     */
    showError(containerId, message = 'Erro ao carregar dados') {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="d-flex justify-content-center align-items-center" style="height: 100%;">
                    <div class="text-muted">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        ${message}
                    </div>
                </div>
            `;
        }
    }
}

// Instância global para uso em outros scripts
window.ChartBase = new ChartBase();