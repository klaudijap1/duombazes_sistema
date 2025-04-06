document.addEventListener('DOMContentLoaded', function() {
    const table = document.getElementById('prekesTable');
    let data = [];
    let editingId = null;

    // Fetch data from server
    function fetchData() {
        console.log('Fetching data...');
        fetch('/prekes/data')
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
            html += '<tr><td colspan="6" class="no-data">Nėra duomenų</td></tr>';
        } else {
            data.forEach(item => {
                console.log('Processing item:', item);
                html += `
                    <tr data-id="${item.id_Preke}">
                        <td>${item.id_Preke}</td>
                        <td>${item.Pavadinimas || ''}</td>
                        <td>${item.Aprasymas || ''}</td>
                        <td>${parseFloat(item.Kaina).toFixed(2)} €</td>
                        <td>${item.Busena || ''}</td>
                        <td>
                            <button class="btn-edit" onclick="editItem(${item.id_Preke})">Redaguoti</button>
                            <button class="btn-delete" onclick="deleteItem(${item.id_Preke})">Ištrinti</button>
                        </td>
                    </tr>
                `;
            });
        }

        table.innerHTML = html;
    }

    // Delete item
    window.deleteItem = function(id) {
        if (confirm('Ar tikrai norite ištrinti šią prekę?')) {
            fetch(`/prekes/delete/${id}`, {
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
        const item = data.find(item => item.id_Preke === id);
        if (!item) return;

        editingId = id;
        const row = table.querySelector(`tr[data-id="${id}"]`);
        
        // Create editable cells
        const cells = row.cells;
        cells[1].innerHTML = `<input type="text" value="${item.Pavadinimas || ''}" class="edit-input">`;
        cells[2].innerHTML = `<input type="text" value="${item.Aprasymas || ''}" class="edit-input">`;
        cells[3].innerHTML = `<input type="number" step="0.01" value="${item.Kaina || ''}" class="edit-input">`;
        cells[4].innerHTML = `<input type="text" value="${item.Busena || ''}" class="edit-input">`;
        
        // Change action buttons
        cells[5].innerHTML = `
            <button class="btn-edit" onclick="saveEdit(${id})">Išsaugoti</button>
            <button class="btn-delete" onclick="cancelEdit(${id})">Atšaukti</button>
        `;
    };

    // Save edit
    window.saveEdit = function(id) {
        const row = table.querySelector(`tr[data-id="${id}"]`);
        const cells = row.cells;
        
        const updatedData = {
            Pavadinimas: cells[1].querySelector('input').value,
            Aprasymas: cells[2].querySelector('input').value,
            Kaina: cells[3].querySelector('input').value,
            Busena: cells[4].querySelector('input').value
        };

        fetch(`/prekes/update/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(updatedData)
        })
        .then(response => {
            if (response.ok) {
                fetchData();
                editingId = null;
            } else {
                throw new Error('Update failed');
            }
        })
        .catch(error => console.error('Error:', error));
    };

    // Cancel edit
    window.cancelEdit = function(id) {
        fetchData();
        editingId = null;
    };

    // Initial data fetch
    fetchData();
}); 