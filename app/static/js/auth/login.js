document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('loginForm');
    const errorElement = document.getElementById('error-message');

    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            const submitBtn = form.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.innerHTML = 'Iniciando sesión...';

            try {
                const formData = new FormData(this);
                console.log('Enviando datos:', Object.fromEntries(formData));
                
                const response = await fetch('/auth/login', {
                    method: 'POST',
                    body: formData,
                    redirect: 'follow',
                    credentials: 'same-origin' // Importante para las cookies de sesión
                });

                console.log('Status:', response.status);
                console.log('Headers:', Object.fromEntries(response.headers));

                if (response.redirected) {
                    console.log('Redirigiendo a:', response.url);
                    window.location.href = response.url;
                } else {
                    const html = await response.text();
                    console.log('Respuesta HTML:', html);
                    
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    const error = doc.querySelector('#error-message')?.textContent 
                        || 'Error en el inicio de sesión';
                    
                    if (errorElement) {
                        errorElement.textContent = error;
                        errorElement.style.display = 'block';
                    }
                }
            } catch (error) {
                console.error('Error completo:', error);
                if (errorElement) {
                    errorElement.textContent = 'Error de conexión';
                    errorElement.style.display = 'block';
                }
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Iniciar Sesión';
            }
        });
    }
});