function openNewLeadModal() {
    document.getElementById('newLeadModal').style.display = 'block';
}

function closeNewLeadModal() {
    document.getElementById('newLeadModal').style.display = 'none';
}

async function updateLeadStatus(leadId, newStatus) {
    try {
        const response = await fetch(`/api/v1/leads/${leadId}/status`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status: newStatus })
        });
        
        if (response.ok) {
            // Recargar la página para ver los cambios
            location.reload();
        } else {
            alert('Error al actualizar el estado del lead');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al actualizar el estado del lead');
    }
}

async function viewLead(leadId) {
    // Implementar vista de detalles del lead
    alert('Funcionalidad en desarrollo');
}