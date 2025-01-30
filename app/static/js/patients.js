// Funciones para la gestión de pacientes
const patientForms = {
    create: async (formData) => {
        try {
            showLoader();
            const response = await api.post('/api/v1/patients/', formData);
            showToast('Paciente creado exitosamente');
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
            const response = await api.put(`/api/v1/patients/${id}`, formData);
            showToast('Paciente actualizado exitosamente');
            location.reload();
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            hideLoader();
        }
    },

    delete: async (id) => {
        if (!confirm('¿Estás seguro de eliminar este paciente?')) return;
        
        try {
            showLoader();
            await api.delete(`/api/v1/patients/${id}`);
            showToast('Paciente eliminado exitosamente');
            location.reload();
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            hideLoader();
        }
    }
};

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    const addPatientForm = document.getElementById('addPatientForm');
    if (addPatientForm) {
        addPatientForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(addPatientForm);
            await patientForms.create(Object.fromEntries(formData));
        });
    }
});