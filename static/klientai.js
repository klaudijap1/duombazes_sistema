document.addEventListener('DOMContentLoaded', function() {
    const table = document.getElementById('klientaiTable');
    let data = [];
    let editingId = null;

    // Fetch data from server
    function fetchData() {
        console.log('Fetching data...');
        fetch('/klientai/data')
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
            html += '<tr><td colspan="9" class="no-data">Nėra duomenų</td></tr>';
        } else {
            data.forEach(item => {
                console.log('Processing item:', item);
                html += `
                    <tr data-id="${item.id_Klientas}">
                        <td>${item.id_Klientas}</td>
                        <td>${item.Vardas || ''}</td>
                        <td>${item.Pavarde || ''}</td>
                        <td>${item.Gimimo_diena || ''}</td>
                        <td>${item.Telefono_numeris || ''}</td>
                        <td>${item.Gyvenamoji_vieta || ''}</td>
                        <td>${item.Pasto_kodas || ''}</td>
                        <td>${item.Elektroninio_pasto_adresas || ''}</td>
                        <td>
                            <button class="btn-edit" onclick="editItem(${item.id_Klientas})">Redaguoti</button>
                            <button class="btn-delete" onclick="deleteItem(${item.id_Klientas})">Ištrinti</button>
                        </td>
                    </tr>
                `;
            });
        }

        table.innerHTML = html;
    }

    // Delete item
    window.deleteItem = function(id) {
        if (confirm('Ar tikrai norite ištrinti šį klientą?')) {
            fetch(`/klientai/delete/${id}`, {
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
        const item = data.find(item => item.id_Klientas === id);
        if (!item) return;

        editingId = id;
        const row = table.querySelector(`tr[data-id="${id}"]`);
        
        // Create editable cells
        const cells = row.cells;
        cells[1].innerHTML = `<input type="text" value="${item.Vardas || ''}" class="edit-input">`;
        cells[2].innerHTML = `<input type="text" value="${item.Pavarde || ''}" class="edit-input">`;
        cells[3].innerHTML = `<input type="date" value="${item.Gimimo_diena || ''}" class="edit-input">`;
        cells[4].innerHTML = `<input type="text" value="${item.Telefono_numeris || ''}" class="edit-input">`;
        cells[5].innerHTML = `<input type="text" value="${item.Gyvenamoji_vieta || ''}" class="edit-input">`;
        cells[6].innerHTML = `<input type="text" value="${item.Pasto_kodas || ''}" class="edit-input">`;
        cells[7].innerHTML = `<input type="email" value="${item.Elektroninio_pasto_adresas || ''}" class="edit-input">`;
        
        // Change action buttons
        cells[8].innerHTML = `
            <button class="btn-edit" onclick="saveEdit(${id})">Išsaugoti</button>
            <button class="btn-delete" onclick="cancelEdit(${id})">Atšaukti</button>
        `;
    };

    // Save edit
    window.saveEdit = function(id) {
        const row = table.querySelector(`tr[data-id="${id}"]`);
        const cells = row.cells;
        
        const updatedData = {
            Vardas: cells[1].querySelector('input').value,
            Pavarde: cells[2].querySelector('input').value,
            Gimimo_diena: cells[3].querySelector('input').value,
            Telefono_numeris: cells[4].querySelector('input').value,
            Gyvenamoji_vieta: cells[5].querySelector('input').value,
            Pasto_kodas: cells[6].querySelector('input').value,
            Elektroninio_pasto_adresas: cells[7].querySelector('input').value
        };

        fetch(`/klientai/update/${id}`, {
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