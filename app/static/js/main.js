// Constantes para configuración
const CONFIG = {
    DATE_FORMAT: {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    },
    NOTIFICATION_DURATION: 3000,
    API_BASE_URL: '', // Agregar tu URL base si es necesario
    USER: {
        name: 'ElBenerDev',
        role: 'Admin',
        lastLogin: '2025-01-25 01:21:20'
    }
};

// Clase para manejar notificaciones
class NotificationManager {
    static container = null;

    static initialize() {
        this.container = document.getElementById('toast-container');
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.className = 'fixed top-4 right-4 z-50 flex flex-col gap-2';
            document.body.appendChild(this.container);
        }
    }

    static show(message, type = 'success') {
        if (!this.container) this.initialize();

        const notification = document.createElement('div');
        notification.className = `px-6 py-4 rounded-lg text-white toast flex items-center ${
            type === 'success' ? 'bg-green-500' : 'bg-red-500'
        }`;

        // Agregar ícono
        const icon = document.createElement('i');
        icon.className = `fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} mr-2`;
        notification.appendChild(icon);

        // Agregar mensaje
        const text = document.createElement('span');
        text.textContent = message;
        notification.appendChild(text);

        this.container.appendChild(notification);

        // Animación de entrada
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(0)';
        }, 10);

        // Animación de salida
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }, CONFIG.NOTIFICATION_DURATION);
    }
}

// Clase para manejar modales
class ModalManager {
    static toggle(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        if (modal.classList.contains('hidden')) {
            this.openModal(modal);
        } else {
            this.closeModal(modal);
        }
    }

    static openModal(modal) {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        modal.setAttribute('aria-hidden', 'false');

        // Enfocar el primer input si existe
        const firstInput = modal.querySelector('input, select, textarea');
        if (firstInput) firstInput.focus();
    }

    static closeModal(modal) {
        modal.classList.add('hidden');
        document.body.style.overflow = 'auto';
        modal.setAttribute('aria-hidden', 'true');

        // Limpiar formularios si existen
        const form = modal.querySelector('form');
        if (form) form.reset();
    }

    static closeAll() {
        document.querySelectorAll('.modal:not(.hidden)').forEach(modal => {
            this.closeModal(modal);
        });
    }
}

// Clase para manejar fechas
class DateFormatter {
    static format(dateString, options = CONFIG.DATE_FORMAT) {
        try {
            const date = new Date(dateString);
            if (isNaN(date.getTime())) throw new Error('Fecha inválida');
            return date.toLocaleDateString('es-ES', options);
        } catch (error) {
            console.error('Error al formatear fecha:', error);
            return dateString;
        }
    }

    static getTimeAgo(dateString) {
        try {
            const date = new Date(dateString);
            const now = new Date();
            const seconds = Math.floor((now - date) / 1000);

            const intervals = {
                año: 31536000,
                mes: 2592000,
                semana: 604800,
                día: 86400,
                hora: 3600,
                minuto: 60
            };

            for (const [unit, secondsInUnit] of Object.entries(intervals)) {
                const interval = Math.floor(seconds / secondsInUnit);
                if (interval >= 1) {
                    return `hace ${interval} ${unit}${interval !== 1 ? 's' : ''}`;
                }
            }
            return 'hace un momento';
        } catch (error) {
            console.error('Error al calcular tiempo:', error);
            return dateString;
        }
    }

    static formatAppointmentDate(dateString) {
        try {
            const date = new Date(dateString);
            const today = new Date();
            const tomorrow = new Date(today);
            tomorrow.setDate(today.getDate() + 1);

            if (date.toDateString() === today.toDateString()) {
                return 'Hoy a las ' + date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
            } else if (date.toDateString() === tomorrow.toDateString()) {
                return 'Mañana a las ' + date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
            } else {
                return this.format(dateString);
            }
        } catch (error) {
            console.error('Error al formatear fecha de cita:', error);
            return dateString;
        }
    }
}

// Clase para manejar peticiones API
class ApiService {
    static async request(url, options = {}) {
        const loader = document.getElementById('loader');
        if (loader) loader.classList.remove('hidden');

        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.detail || `Error HTTP: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            NotificationManager.show(
                error.message || 'Ha ocurrido un error. Por favor, inténtalo de nuevo.',
                'error'
            );
            throw error;
        } finally {
            if (loader) loader.classList.add('hidden');
        }
    }

    static async get(url) {
        return this.request(url);
    }

    static async post(url, data) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    static async put(url, data) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    static async delete(url) {
        return this.request(url, {
            method: 'DELETE'
        });
    }

    // Métodos específicos para el CRM
    static async createPatient(patientData) {
        return this.post('/api/patients/', patientData);
    }

    static async createAppointment(appointmentData) {
        return this.post('/api/appointments/', appointmentData);
    }

    static async cancelAppointment(appointmentId) {
        return this.put(`/api/appointments/${appointmentId}/cancel`);
    }

    static async createLead(leadData) {
        return this.post('/api/leads/', leadData);
    }
}

// Utilidades adicionales
const Utils = {
    validateForm(form) {
        let isValid = true;
        const errors = [];

        form.querySelectorAll('[required]').forEach(input => {
            if (!input.value.trim()) {
                isValid = false;
                errors.push(`El campo ${input.name || input.id} es requerido`);
                input.classList.add('border-red-500');
            } else {
                input.classList.remove('border-red-500');
            }
        });

        if (!isValid) {
            NotificationManager.show(errors.join('. '), 'error');
        }

        return isValid;
    },

    formatPhoneNumber(phone) {
        const cleaned = ('' + phone).replace(/\D/g, '');
        const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
        if (match) {
            return '(' + match[1] + ') ' + match[2] + '-' + match[3];
        }
        return phone;
    }
};

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    NotificationManager.initialize();

    // Cerrar modales con Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') ModalManager.closeAll();
    });

    // Cerrar modales al hacer clic fuera
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            ModalManager.closeModal(e.target);
        }
    });

    // Formatear teléfonos automáticamente
    document.querySelectorAll('input[type="tel"]').forEach(input => {
        input.addEventListener('input', (e) => {
            e.target.value = Utils.formatPhoneNumber(e.target.value);
        });
    });

    // Exponer funciones globalmente
    window.showNotification = NotificationManager.show.bind(NotificationManager);
    window.toggleModal = ModalManager.toggle.bind(ModalManager);
    window.formatDate = DateFormatter.format;
    window.formatAppointmentDate = DateFormatter.formatAppointmentDate;
    window.getTimeAgo = DateFormatter.getTimeAgo;
    window.api = ApiService;
    window.utils = Utils;
});


document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('expired') === 'true') {
        alert('Tu sesión ha expirado. Por favor inicia sesión nuevamente.');
    }
});

// Exportar clases y utilidades
export {
    NotificationManager,
    ModalManager,
    DateFormatter,
    ApiService,
    Utils
};