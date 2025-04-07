document.addEventListener('DOMContentLoaded', function() {
    const table = document.getElementById('uzsakymoDetalesTable');
    let data = [];
    let editingId = null;

    // Fetch data from server
    function fetchData() {
        console.log('Fetching data...');
        fetch('/uzsakymo_detales/data')
            .then(response => {
                console.log('Response status:', response.status);
                return response.json();
            })
            .then(result => {
                console.log('Received data:', result);
                data = result;
                renderTable();
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });
    }

    // Render table with data
    function renderTable() {
        console.log('Rendering table with data:', data);
        let html = '';

        if (data.length === 0) {
            html += '<tr><td colspan="10" class="no-data">Nėra duomenų</td></tr>';
        } else {
            data.forEach(item => {
                console.log('Processing item:', item);
                html += `
                    <tr data-id="${item.id_Uzsakymo_detale}">
                        <td>${item.id_Uzsakymo_detale}</td>
                        <td>${item.Prekes_pavadinimas || ''}</td>
                        <td>${item.Paslaugos_pavadinimas || ''}</td>
                        <td>${item.Dovanu_cekis || ''}</td>
                        <td>${item.Vieneto_kaina ? parseFloat(item.Vieneto_kaina).toFixed(2) : ''}</td>
                        <td>${item.Uzsakymo_data || ''}</td>
                        <td>${item.Kaina ? parseFloat(item.Kaina).toFixed(2) : ''}</td>
                        <td>${item.Busena || ''}</td>
                        <td>${item.fk_Klientasid_Klientas || ''}</td>
                        <td>
                            <button class="btn-edit" onclick="editItem(${item.id_Uzsakymo_detale})">Redaguoti</button>
                            <button class="btn-delete" onclick="deleteItem(${item.id_Uzsakymo_detale})">Ištrinti</button>
                        </td>
                    </tr>
                `;
            });
        }

        table.innerHTML = html;
    }

    // Delete item
    window.deleteItem = function(id) {
        if (confirm('Ar tikrai norite ištrinti šią užsakymo detalę?')) {
            fetch(`/uzsakymo_detales/delete/${id}`, {
                method: 'DELETE'
            })
            .then(response => {
                if (response.ok) {
                    fetchData();
                } else {
                    throw new Error('Delete failed');
                }
            })
            .catch(error => console.error('Error:', error));
        }
    };

    // Edit item
    window.editItem = function(id) {
        const item = data.find(item => item.id_Uzsakymo_detale === id);
        if (!item) return;

        editingId = id;
        const row = table.querySelector(`tr[data-id="${id}"]`);
        
        // Create editable cells
        const cells = row.cells;
        cells[1].innerHTML = `<input type="text" value="${item.Prekes_pavadinimas || ''}" class="edit-input">`;
        cells[2].innerHTML = `<input type="text" value="${item.Paslaugos_pavadinimas || ''}" class="edit-input">`;
        cells[3].innerHTML = `<input type="text" value="${item.Dovanu_cekis || ''}" class="edit-input">`;
        cells[4].innerHTML = `<input type="number" step="0.01" value="${item.Vieneto_kaina || ''}" class="edit-input">`;
        cells[5].innerHTML = `<input type="date" value="${item.Uzsakymo_data || ''}" class="edit-input">`;
        cells[6].innerHTML = `<input type="number" step="0.01" value="${item.Kaina || ''}" class="edit-input">`;
        cells[7].innerHTML = `<input type="text" value="${item.Busena || ''}" class="edit-input">`;
        cells[8].innerHTML = `<input type="number" value="${item.fk_Klientasid_Klientas || ''}" class="edit-input">`;
        
        // Change action buttons
        cells[9].innerHTML = `
            <button class="btn-edit" onclick="saveEdit(${id})">Išsaugoti</button>
            <button class="btn-delete" onclick="cancelEdit(${id})">Atšaukti</button>
        `;
    };

    // Save edit
    window.saveEdit = function(id) {
        const row = table.querySelector(`tr[data-id="${id}"]`);
        const cells = row.cells;
        
        const updatedData = {
            Prekes_pavadinimas: cells[1].querySelector('input').value,
            Paslaugos_pavadinimas: cells[2].querySelector('input').value,
            Dovanu_cekis: cells[3].querySelector('input').value,
            Vieneto_kaina: cells[4].querySelector('input').value,
            Uzsakymo_data: cells[5].querySelector('input').value,
            Kaina: cells[6].querySelector('input').value,
            Busena: cells[7].querySelector('input').value,
            fk_Klientasid_Klientas: cells[8].querySelector('input').value
        };

        console.log('Updating with data:', updatedData);

        fetch(`/uzsakymo_detales/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(updatedData)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Failed to update order detail');
                });
            }
            return response.json();
        })
        .then(data => {
            console.log('Success:', data);
            fetchData();
            editingId = null;
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Klaida atnaujinant užsakymo detalę: ' + error.message);
        });
    };

    // Cancel edit
    window.cancelEdit = function(id) {
        fetchData();
        editingId = null;
    };

    // Initial data fetch
    fetchData();
}); 