// Funciones para la gestión de leads
const leadForms = {
    create: async (formData) => {
        try {
            showLoader();
            const response = await api.post('/api/v1/leads/', formData);
            showToast('Lead creado exitosamente');
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
            const response = await api.put(`/api/v1/leads/${id}`, formData);
            showToast('Lead actualizado exitosamente');
            location.reload();
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            hideLoader();
        }
    },

    delete: async (id) => {
        if (!confirm('¿Estás seguro de eliminar este lead?')) return;
        
        try {
            showLoader();
            await api.delete(`/api/v1/leads/${id}`);
            showToast('Lead eliminado exitosamente');
            location.reload();
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            hideLoader();
        }
    },
    
    updateStatus: async (id, status) => {
        try {
            showLoader();
            await api.put(`/api/v1/leads/${id}/status`, { status });
            showToast('Estado del lead actualizado');
            location.reload();
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            hideLoader();
        }
    },
    
    convertToPatient: async (id) => {
        try {
            showLoader();
            await api.post(`/api/v1/leads/${id}/convert`, {});
            showToast('Lead convertido a paciente exitosamente');
            location.href = '/patients';
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            hideLoader();
        }
    }
};

// Utilidades para el seguimiento de leads
const leadTracking = {
    updateKanbanBoard() {
        // Actualizar el tablero Kanban de leads
        const columns = document.querySelectorAll('.kanban-column');
        if (!columns.length) return;

        columns.forEach(column => {
            new Sortable(column, {
                group: 'leads',
                animation: 150,
                onEnd: function(evt) {
                    const leadId = evt.item.dataset.leadId;
                    const newStatus = evt.to.dataset.status;
                    if (leadId && newStatus) {
                        leadForms.updateStatus(leadId, newStatus);
                    }
                }
            });
        });
    }
};

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    const addLeadForm = document.getElementById('addLeadForm');
    if (addLeadForm) {
        addLeadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(addLeadForm);
            await leadForms.create(Object.fromEntries(formData));
        });
    }

    // Inicializar Kanban board si existe
    const kanbanBoard = document.querySelector('.kanban-board');
    if (kanbanBoard) {
        leadTracking.updateKanbanBoard();
    }

    // Event listeners para botones de conversión
    document.querySelectorAll('[data-convert-lead]').forEach(button => {
        button.addEventListener('click', (e) => {
            const leadId = e.currentTarget.dataset.convertLead;
            leadForms.convertToPatient(leadId);
        });
    });
});