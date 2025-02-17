// static/js/api.js
const api = {
    // Método base para el manejo de errores
    async handleResponse(response) {
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Error en la petición');
        }
        return response.json();
    },

    // Método base para las opciones de fetch
    getRequestOptions(method, data = null) {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'same-origin' // Para manejar cookies de sesión
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        return options;
    },

    async get(url) {
        try {
            const response = await fetch(url, this.getRequestOptions('GET'));
            return await this.handleResponse(response);
        } catch (error) {
            console.error('GET Error:', error);
            throw new Error(`Error en GET ${url}: ${error.message}`);
        }
    },
    
    async post(url, data) {
        try {
            const response = await fetch(url, this.getRequestOptions('POST', data));
            return await this.handleResponse(response);
        } catch (error) {
            console.error('POST Error:', error);
            throw new Error(`Error en POST ${url}: ${error.message}`);
        }
    },
    
    async put(url, data) {
        try {
            const response = await fetch(url, this.getRequestOptions('PUT', data));
            return await this.handleResponse(response);
        } catch (error) {
            console.error('PUT Error:', error);
            throw new Error(`Error en PUT ${url}: ${error.message}`);
        }
    },
    
    async delete(url) {
        try {
            const response = await fetch(url, this.getRequestOptions('DELETE'));
            return await this.handleResponse(response);
        } catch (error) {
            console.error('DELETE Error:', error);
            throw new Error(`Error en DELETE ${url}: ${error.message}`);
        }
    },

    // Métodos específicos para las rutas de tu aplicación
    appointments: {
        async getAll() {
            return api.get('/api/v1/appointments/');
        },
        async create(appointmentData) {
            return api.post('/api/v1/appointments/', appointmentData);
        },
        async update(id, appointmentData) {
            return api.put(`/api/v1/appointments/${id}/`, appointmentData);
        },
        async delete(id) {
            return api.delete(`/api/v1/appointments/${id}/`);
        },
        async getCalendarEvents() {
            return api.get('/api/v1/appointments/calendar');
        }
    },

    leads: {
        async getAll() {
            return api.get('/api/v1/leads/');
        },
        async create(leadData) {
            return api.post('/api/v1/leads/', leadData);
        },
        async updateStatus(id, status) {
            return api.put(`/api/v1/leads/${id}/update-status`, { status });
        }
    }
};

// Ejemplo de uso en tus páginas:
/*
// En appointments.js
async function createAppointment(formData) {
    try {
        showLoader();
        const result = await api.appointments.create(formData);
        showToast('Cita creada exitosamente');
        return result;
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        hideLoader();
    }
}

// En leads.js
async function updateLeadStatus(id, status) {
    try {
        showLoader();
        await api.leads.updateStatus(id, status);
        showToast('Estado actualizado exitosamente');
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        hideLoader();
    }
}
*/