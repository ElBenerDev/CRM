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
                const response = await fetch('/auth/token', {
                    method: 'POST',
                    body: formData,
                    redirect: 'follow'
                });

                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    const html = await response.text();
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
                console.error('Error:', error);
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