// Función para manejar modales
function toggleModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal.classList.contains('hidden')) {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden'; // Prevenir scroll en el fondo
    } else {
        modal.classList.add('hidden');
        document.body.style.overflow = 'auto'; // Restaurar scroll
    }
}

// Cerrar modal al hacer click fuera de él
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('fixed')) {
        toggleModal(e.target.id);
    }
});

// Función para mostrar notificaciones toast
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `fixed bottom-4 right-4 px-6 py-3 rounded-lg text-white ${
        type === 'success' ? 'bg-green-500' : 'bg-red-500'
    } transition-opacity duration-300`;
    toast.textContent = message;
    document.body.appendChild(toast);

    // Desvanecer y remover después de 3 segundos
    setTimeout(() => {
        toast.classList.add('opacity-0');
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}

// Función para enviar formularios vía AJAX
async function submitForm(formId, endpoint, method = 'POST') {
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await fetch(endpoint, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            showToast('Datos guardados exitosamente');
            window.location.reload();
        } else {
            const error = await response.json();
            showToast(error.detail || 'Error al guardar los datos', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Error al enviar los datos', 'error');
    }
}

// Función para formatear fechas
function formatDate(dateString) {
    const options = { 
        year: 'numeric', 
        month: '2-digit', 
        day: '2-digit',
        hour: '2-digit', 
        minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString('es-ES', options);
}

// Función para manejar la paginación
function handlePagination(page) {
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set('page', page);
    window.location.search = urlParams.toString();
}

// Función para manejar el ordenamiento
function handleSort(column) {
    const urlParams = new URLSearchParams(window.location.search);
    const currentOrder = urlParams.get('order_by') || '';
    const isDesc = currentOrder === column;
    
    urlParams.set('order_by', isDesc ? `-${column}` : column);
    window.location.search = urlParams.toString();
}

// Función para manejar la búsqueda
function handleSearch(formId) {
    const form = document.getElementById(formId);
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(form);
        const urlParams = new URLSearchParams(formData);
        window.location.search = urlParams.toString();
    });
}

// Función para confirmar eliminación
function confirmDelete(message = '¿Está seguro de eliminar este registro?') {
    return confirm(message);
}

// Función para eliminar registros
async function deleteRecord(endpoint) {
    if (!confirmDelete()) return;

    try {
        const response = await fetch(endpoint, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (response.ok) {
            showToast('Registro eliminado exitosamente');
            window.location.reload();
        } else {
            const error = await response.json();
            showToast(error.detail || 'Error al eliminar el registro', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Error al eliminar el registro', 'error');
    }
}

// Función para actualizar el estado de una cita
async function updateAppointmentStatus(appointmentId, status) {
    try {
        const response = await fetch(`/api/appointments/${appointmentId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status })
        });

        if (response.ok) {
            showToast(`Cita ${status === 'cancelled' ? 'cancelada' : 'actualizada'} exitosamente`);
            window.location.reload();
        } else {
            const error = await response.json();
            showToast(error.detail || 'Error al actualizar la cita', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Error al actualizar la cita', 'error');
    }
}

// Función para cargar datos en un formulario de edición
function loadFormData(formId, data) {
    const form = document.getElementById(formId);
    for (const [key, value] of Object.entries(data)) {
        const input = form.elements[key];
        if (input) {
            if (input.type === 'datetime-local') {
                // Formatear fecha para input datetime-local
                input.value = new Date(value).toISOString().slice(0, 16);
            } else {
                input.value = value;
            }
        }
    }
}

// Inicializar tooltips
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar cualquier tooltip o popover que uses
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(tooltip => {
        tooltip.addEventListener('mouseenter', function(e) {
            const tip = document.createElement('div');
            tip.className = 'absolute bg-black text-white p-2 rounded text-sm';
            tip.textContent = this.dataset.tooltip;
            tip.style.top = (e.pageY + 10) + 'px';
            tip.style.left = (e.pageX + 10) + 'px';
            document.body.appendChild(tip);
            
            this.addEventListener('mouseleave', function() {
                tip.remove();
            }, { once: true });
        });
    });
});

// Función para manejar cambios en los filtros
function handleFilterChange() {
    const urlParams = new URLSearchParams(window.location.search);
    const filters = document.querySelectorAll('[data-filter]');
    
    filters.forEach(filter => {
        filter.addEventListener('change', function() {
            urlParams.set(this.name, this.value);
            window.location.search = urlParams.toString();
        });
    });
}

// Exportar funciones que necesiten ser accedidas desde los templates
window.toggleModal = toggleModal;
window.submitForm = submitForm;
window.handlePagination = handlePagination;
window.handleSort = handleSort;
window.deleteRecord = deleteRecord;
window.updateAppointmentStatus = updateAppointmentStatus;
window.loadFormData = loadFormData;
window.handleFilterChange = handleFilterChange;