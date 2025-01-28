document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('loginForm');
    const errorDiv = document.getElementById('error-message');

    function showError(message) {
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        }
    }

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
                    headers: {
                        'Accept': 'text/html'
                    },
                    redirect: 'follow'
                });

                if (response.redirected) {
                    // Si hay redirección, seguirla
                    window.location.href = response.url;
                } else {
                    // Si hay error, mostrar el mensaje
                    const html = await response.text();
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    const error = doc.querySelector('.error-message');
                    if (error) {
                        showError(error.textContent);
                    } else {
                        showError('Error en el inicio de sesión');
                    }
                }
            } catch (error) {
                console.error('Error:', error);
                showError('Error de conexión');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Iniciar Sesión';
            }
        });
    }
});