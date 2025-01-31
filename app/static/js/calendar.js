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

    setupEventListeners() {
        // Botones de navegación del calendario
        document.getElementById('prevMonth').addEventListener('click', () => {
            this.currentDate.setMonth(this.currentDate.getMonth() - 1);
            this.renderCalendar();
        });

        document.getElementById('nextMonth').addEventListener('click', () => {
            this.currentDate.setMonth(this.currentDate.getMonth() + 1);
            this.renderCalendar();
        });

        // Modal de citas
        document.getElementById('appointmentForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const appointmentId = document.getElementById('appointmentId').value;
            
            if (appointmentId) {
                await appointmentForms.edit(appointmentId, Object.fromEntries(formData));
            } else {
                await appointmentForms.create(Object.fromEntries(formData));
            }
            
            await this.loadAppointments();
            this.renderCalendar();
        });
    }

    renderDay(date, appointments) {
        const isToday = date.toDateString() === new Date().toDateString();
        const dateString = date.getDate();
        
        let html = `
            <div class="calendar-day ${isToday ? 'bg-blue-50' : ''}" 
                 data-date="${date.toISOString().split('T')[0]}">
                <div class="day-header ${isToday ? 'text-blue-600 font-bold' : ''}">${dateString}</div>
                <div class="appointments-container">`;
        
        appointments.forEach(appointment => {
            const time = new Date(appointment.date).toLocaleTimeString('es-ES', {
                hour: '2-digit',
                minute: '2-digit'
            });
            
            html += `
                <div class="appointment-item" 
                     data-id="${appointment.id}"
                     onclick="editAppointment(${appointment.id})">
                    <div class="time">${time}</div>
                    <div class="patient">${appointment.patient_name}</div>
                    <div class="type">${appointment.service_type}</div>
                </div>`;
        });

        html += `
                </div>
                <button class="add-appointment" 
                        onclick="newAppointment('${date.toISOString().split('T')[0]}')">
                    +
                </button>
            </div>`;
        
        return html;
    }

    updateMonthDisplay() {
        const monthNames = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                          'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
        document.getElementById('currentMonth').textContent = 
            `${monthNames[this.currentDate.getMonth()]} ${this.currentDate.getFullYear()}`;
    }
}

// Funciones globales para manejar citas
function editAppointment(id) {
    const appointment = calendar.appointments.find(a => a.id === id);
    if (!appointment) return;

    document.getElementById('appointmentId').value = id;
    document.getElementById('patientSelect').value = appointment.patient_id;
    document.getElementById('appointmentDate').value = appointment.date.split('T')[0];
    document.getElementById('appointmentTime').value = appointment.date.split('T')[1].substring(0, 5);
    document.getElementById('appointmentType').value = appointment.service_type.toLowerCase();

    // Mostrar modal
    document.getElementById('appointmentModal').classList.remove('hidden');
}

function newAppointment(date) {
    // Limpiar formulario
    document.getElementById('appointmentForm').reset();
    document.getElementById('appointmentId').value = '';
    document.getElementById('appointmentDate').value = date;

    // Mostrar modal
    document.getElementById('appointmentModal').classList.remove('hidden');
}

// Inicializar calendario cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.calendar = new DentalCalendar();
});