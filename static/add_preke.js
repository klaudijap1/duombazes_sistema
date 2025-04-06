document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('prekeForm');

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = {
            pavadinimas: document.getElementById('pavadinimas').value,
            aprasymas: document.getElementById('aprasymas').value,
            kaina: document.getElementById('kaina').value,
            busena: document.getElementById('busena').value
        };

        fetch('/prekes/insert', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            window.location.href = '/prekes';
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Įvyko klaida pridedant prekę. Bandykite dar kartą.');
        });
    });
}); 