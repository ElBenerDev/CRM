// Funciones para la gestión de citas
const appointmentForms = {
    create: async (formData) => {
        try {
            showLoader();
            const response = await api.post('/api/v1/appointments/', formData);
            showToast('Cita programada exitosamente');
            location.reload();
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            hideLoader();
        }
    },

    edit: async (id, formData) => {
        try {
            showLoader();
            const response = await api.put(`/api/v1/appointments/${id}`, formData);
            showToast('Cita actualizada exitosamente');
            location.reload();
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            hideLoader();
        }
    },

    delete: async (id) => {
        if (!confirm('¿Estás seguro de cancelar esta cita?')) return;
        
        try {
            showLoader();
            await api.delete(`/api/v1/appointments/${id}`);
            showToast('Cita cancelada exitosamente');
            location.reload();
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            hideLoader();
        }
    },
    
    complete: async (id) => {
        try {
            showLoader();
            await api.put(`/api/v1/appointments/${id}/complete`, {});
            showToast('Cita marcada como completada');
            location.reload();
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            hideLoader();
        }
    }
};

// Utilidades para el calendario
const calendar = {
    init() {
        // Aquí puedes integrar una librería de calendario como FullCalendar
        // o implementar tu propia lógica de calendario
    },
    
    refreshEvents() {
        // Actualizar eventos del calendario
    }
};

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    const addAppointmentForm = document.getElementById('addAppointmentForm');
    if (addAppointmentForm) {
        addAppointmentForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(addAppointmentForm);
            await appointmentForms.create(Object.fromEntries(formData));
        });
    }

    // Inicializar calendario si existe el contenedor
    const calendarContainer = document.getElementById('calendar');
    if (calendarContainer) {
        calendar.init();
    }
});