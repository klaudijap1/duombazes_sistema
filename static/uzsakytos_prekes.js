document.addEventListener('DOMContentLoaded', function() {
    const table = document.getElementById('uzsakytosPrekesTable');
    let data = [];
    let editingId = null;

    // Fetch data from server
    function fetchData() {
        console.log('Fetching data...');
        fetch('/uzsakytos_prekes/data')
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
                    <tr data-id="${item.id_Uzsakyta_preke}">
                        <td>${item.id_Uzsakyta_preke}</td>
                        <td>${item.Tipas || ''}</td>
                        <td>${item.Kiekis || ''}</td>
                        <td>${item.fk_Prekes_id_Preke || ''}</td>
                        <td>${item.fk_Uzsakymo_detales_id_Uzsakymo || ''}</td>
                        <td>
                            <button class="btn-edit" onclick="editItem(${item.id_Uzsakyta_preke})">Redaguoti</button>
                            <button class="btn-delete" onclick="deleteItem(${item.id_Uzsakyta_preke})">Ištrinti</button>
                        </td>
                    </tr>
                `;
            });
        }

        table.innerHTML = html;
    }

    // Delete item
    window.deleteItem = function(id) {
        if (confirm('Ar tikrai norite ištrinti šią užsakytą prekę?')) {
            fetch(`/uzsakytos_prekes/delete/${id}`, {
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
        const item = data.find(item => item.id_Uzsakyta_preke === id);
        if (!item) return;

        editingId = id;
        const row = table.querySelector(`tr[data-id="${id}"]`);
        
        // Create editable cells
        const cells = row.cells;
        cells[1].innerHTML = `<input type="text" value="${item.Tipas || ''}" class="edit-input">`;
        cells[2].innerHTML = `<input type="number" value="${item.Kiekis || ''}" class="edit-input">`;
        cells[3].innerHTML = `<input type="number" value="${item.fk_Prekes_id_Preke || ''}" class="edit-input">`;
        cells[4].innerHTML = `<input type="number" value="${item.fk_Uzsakymo_detales_id_Uzsakymo || ''}" class="edit-input">`;
        
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
            Tipas: cells[1].querySelector('input').value,
            Kiekis: cells[2].querySelector('input').value,
            fk_Prekes_id_Preke: cells[3].querySelector('input').value,
            fk_Uzsakymo_detales_id_Uzsakymo: cells[4].querySelector('input').value
        };

        fetch(`/uzsakytos_prekes/update/${id}`, {
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