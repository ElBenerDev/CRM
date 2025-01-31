// static/js/calendar.js
class DentalCalendar {
    constructor() {
        this.currentDate = new Date();
        this.appointments = [];
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.loadAppointments();
        this.renderCalendar();
    }

    async loadAppointments() {
        try {
            const response = await fetch('/api/appointments');
            this.appointments = await response.json();
        } catch (error) {
            console.error('Error loading appointments:', error);
        }
    }

    renderCalendar() {
        const calendar = document.getElementById('calendar');
        const firstDay = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth(), 1);
        const lastDay = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() + 1, 0);
        
        // Renderizar días y citas
        let html = '<div class="calendar-days">';
        for (let date = new Date(firstDay); date <= lastDay; date.setDate(date.getDate() + 1)) {
            const dayAppointments = this.appointments.filter(app => 
                new Date(app.date).toDateString() === date.toDateString()
            );
            
            html += this.renderDay(date, dayAppointments);
        }
        html += '</div>';
        calendar.innerHTML = html;
    }

    // ... más métodos para manejar eventos y actualizar el calendario
}