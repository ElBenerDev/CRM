    document.addEventListener('DOMContentLoaded', function() {
        const calendarEl = document.getElementById('calendar');
        const calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'timeGridWeek',
            locale: 'es',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,timeGridDay'
            },
            buttonText: {
                today: 'Hoy',
                month: 'Mes',
                week: 'Semana',
                day: 'Día'
            },
            slotMinTime: '08:00:00',
            slotMaxTime: '20:00:00',
            allDaySlot: false,
            slotDuration: '00:30:00',
            slotLabelInterval: '01:00',
            businessHours: {
                daysOfWeek: [1, 2, 3, 4, 5, 6], // Lunes a Sábado
                startTime: '08:00',
                endTime: '20:00',
            },
            eventTimeFormat: {
                hour: '2-digit',
                minute: '2-digit',
                hour12: true
            },
            // Cambiamos la configuración de eventos para usar un eventSource
            eventSources: [{
                url: '/api/v1/appointments/',
                method: 'GET',
                extraParams: function(start, end) {
                    return {
                        start: start.startStr,
                        end: end.endStr
                    };
                },
                failure: function() {
                    alert('Error al cargar los eventos');
                }
            }],
            eventClick: function(info) {
                openAppointmentModal(info.event);
            },
            dateClick: function(info) {
                openAppointmentModal(null, info.date);
            },
            eventContent: function(arg) {
                return {
                    html: `
                        <div class="fc-event-main-frame">
                            <div class="fc-event-time">${arg.timeText}</div>
                            <div class="fc-event-title-container">
                                <div class="fc-event-title">${arg.event.title}</div>
                                <div class="fc-event-desc">${arg.event.extendedProps.serviceType || ''}</div>
                            </div>
                        </div>
                    `
                };
            }
        });
        
        calendar.render();

        // Manejador del formulario de citas
        document.getElementById('appointmentForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const appointmentData = {
                patient_id: formData.get('patient_id'),
                date: formData.get('date'),
                time: formData.get('time'),
                service_type: formData.get('service_type')
            };

            const appointmentId = document.getElementById('appointmentId').value;
            const method = appointmentId ? 'PUT' : 'POST';
            const url = appointmentId 
                ? `/api/v1/appointments/${appointmentId}/`
                : '/api/v1/appointments/';

            try {
                const response = await fetch(url, {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(appointmentData)
                });

                if (response.ok) {
                    calendar.refetchEvents();
                    closeAppointmentModal();
                } else {
                    const error = await response.json();
                    alert(error.detail || 'Error al guardar la cita');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error al guardar la cita');
            }
        });
    });

    function openAppointmentModal(event = null, date = null) {
        const modal = document.getElementById('appointmentModal');
        const form = document.getElementById('appointmentForm');
        const idInput = document.getElementById('appointmentId');
        
        // Limpiar el formulario
        form.reset();
        idInput.value = '';

        if (event) {
            // Editar cita existente
            const startDate = new Date(event.start);
            idInput.value = event.id;
            form.elements['patient_id'].value = event.extendedProps.patientId;
            form.elements['date'].value = startDate.toISOString().split('T')[0];
            form.elements['time'].value = startDate.toTimeString().slice(0, 5);
            form.elements['service_type'].value = event.extendedProps.serviceType;
        } else if (date) {
            // Nueva cita en fecha seleccionada
            form.elements['date'].value = date.toISOString().split('T')[0];
            form.elements['time'].value = date.toTimeString().slice(0, 5);
        }

        modal.style.display = 'block';
    }

    function closeAppointmentModal() {
        document.getElementById('appointmentModal').style.display = 'none';
    }