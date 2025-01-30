// Funciones para el dashboard
const dashboard = {
    charts: {
        appointmentsChart: null,
        patientsChart: null,
        leadsChart: null
    },

    async initCharts() {
        try {
            const stats = await api.get('/api/v1/stats/dashboard');
            this.updateCharts(stats);
        } catch (error) {
            console.error('Error loading dashboard stats:', error);
        }
    },

    updateCharts(stats) {
        // Aquí puedes integrar una librería de gráficos como Chart.js
        // y crear visualizaciones con los datos
    },

    async refreshStats() {
        try {
            const stats = await api.get('/api/v1/stats/dashboard');
            this.updateStats(stats);
        } catch (error) {
            console.error('Error refreshing stats:', error);
        }
    },

    updateStats(stats) {
        // Actualizar los contadores y estadísticas del dashboard
        Object.entries(stats).forEach(([key, value]) => {
            const element = document.getElementById(`stat-${key}`);
            if (element) {
                element.textContent = value;
            }
        });
    }
};

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('#dashboard')) {
        dashboard.initCharts();
        
        // Actualizar estadísticas cada 5 minutos
        setInterval(() => {
            dashboard.refreshStats();
        }, 300000);
    }
});