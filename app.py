from flask import Flask, render_template, request, jsonify, redirect, url_for
from db_config import get_connection
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Range", "X-Content-Range"]
    }
})

# Handle preflight requests for all routes
@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    return '', 204

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/prekes')
def prekes():
    return render_template('prekes.html')

@app.route('/prekes/data')
def get_prekes():
    try:
        print("Attempting to fetch prekes data...")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM prekes")
        rows = cursor.fetchall()
        print(f"Fetched {len(rows)} rows from database")
        
        # Convert the rows to a list of dictionaries with proper value handling
        result = []
        for row in rows:
            item = {
                'id_Preke': row[0],
                'Pavadinimas': row[1],
                'Aprasymas': row[2],
                'Kaina': str(row[3]),  # Convert Decimal to string
                'Busena': row[4]
            }
            result.append(item)
        
        print("Processed data:", result)
        cursor.close()
        conn.close()
        return jsonify(result)
    except Exception as e:
        print(f"Error in get_prekes: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/prekes/add')
def add_preke_form():
    return render_template('add_preke.html')

@app.route('/prekes/insert', methods=['POST'])
def insert_preke():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No JSON data received'}), 400
            
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO prekes (
                Pavadinimas, Aprasymas, Kaina, Busena
            ) VALUES (%s, %s, %s, %s)
        """, (
            data['pavadinimas'], data['aprasymas'], data['kaina'], data['busena']
        ))
        
        conn.commit()
        
        last_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        return jsonify({'message': f'Prekė sėkmingai pridėta! (ID: {last_id})'})
        
    except Exception as e:
        print(f"Error in insert: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Server error: {str(e)}'}), 500

@app.route('/prekes/delete/<id>', methods=['DELETE'])
def delete_preke(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM prekes WHERE id_Preke = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Deleted successfully'})

@app.route('/prekes/update/<id>', methods=['PUT', 'OPTIONS'])
def update_preke(id):
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        print(f"Update request received for ID: {id}")
        print(f"Request data: {request.data}")
        print(f"Request content type: {request.content_type}")
        
        data = request.get_json()
        print(f"Parsed JSON data: {data}")
        
        if not data:
            print("No data received")
            return jsonify({'message': 'No JSON data received'}), 400
        
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM prekes WHERE id_Preke = %s", (id,))
            current_data = cursor.fetchone()
            
            if not current_data:
                print(f"Preke with ID {id} not found")
                return jsonify({'message': 'Preke not found'}), 404
                
            valid_fields = [
                'Pavadinimas', 'Aprasymas', 'Kaina', 'Busena'
            ]
            
            update_fields = []
            update_values = []
            
            for field, value in data.items():
                if field in valid_fields:
                    if field == 'Kaina':
                        # Handle float value for Kaina
                        try:
                            float_value = float(value)
                            update_fields.append(f"`{field}` = %s")
                            update_values.append(float_value)
                        except (ValueError, TypeError):
                            continue
                    elif value and (isinstance(value, str) and value.strip()):
                        # Handle string values
                        update_fields.append(f"`{field}` = %s")
                        update_values.append(value)
            
            if not update_fields:
                print("No fields to update")
                return jsonify({'message': 'No fields to update'}), 400
                
            update_values.append(id)
            
            query = f"UPDATE prekes SET {', '.join(update_fields)} WHERE id_Preke = %s"
            print(f"Executing query: {query}")
            print(f"With values: {update_values}")
            
            cursor.execute(query, update_values)
            affected_rows = cursor.rowcount
            print(f"Affected rows: {affected_rows}")
            
            conn.commit()
            
            if affected_rows > 0:
                return jsonify({'message': 'Updated successfully'}), 200
            else:
                return jsonify({'message': 'No changes made'}), 200
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                
    except Exception as e:
        print(f"Error in update: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Server error: {str(e)}'}), 500

# Užsakytos prekės routes
@app.route('/uzsakytos_prekes')
def uzsakytos_prekes():
    return render_template('uzsakytos_prekes.html')

@app.route('/uzsakytos_prekes/data')
def get_uzsakytos_prekes():
    try:
        print("Attempting to fetch uzsakytos_prekes data...")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM uzsakytos_prekes")
        rows = cursor.fetchall()
        print(f"Fetched {len(rows)} rows from database")
        
        # Convert the rows to a list of dictionaries with proper value handling
        result = []
        for row in rows:
            item = {
                'id_Uzsakyta_preke': row[0],
                'Tipas': row[1],
                'Kiekis': row[2],
                'fk_Prekes_id_Preke': row[3],
                'fk_Uzsakymo_detales_id_Uzsakymo': row[4]
            }
            result.append(item)
        
        print("Processed data:", result)
        cursor.close()
        conn.close()
        return jsonify(result)
    except Exception as e:
        print(f"Error in get_uzsakytos_prekes: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/uzsakytos_prekes/delete/<int:id>', methods=['DELETE', 'OPTIONS'])
def delete_uzsakyta_preke(id):
    if request.method == 'OPTIONS':
        return '', 204
    try:
        print(f"Attempting to delete uzsakyta_preke {id}...")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM uzsakytos_prekes WHERE id_Uzsakyta_preke = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Užsakyta prekė sėkmingai ištrinta'})
    except Exception as e:
        print(f"Error in delete_uzsakyta_preke: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/uzsakytos_prekes/edit/<int:id>', methods=['GET'])
def edit_uzsakyta_preke(id):
    try:
        print(f"Attempting to fetch uzsakyta_preke {id} for editing...")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM uzsakytos_prekes WHERE id_Uzsakyta_preke = %s", (id,))
        row = cursor.fetchone()
        
        if row:
            uzsakyta_preke = {
                'id_Uzsakyta_preke': row[0],
                'Tipas': row[1],
                'Kiekis': row[2],
                'fk_Prekes_id_Preke': row[3],
                'fk_Uzsakymo_detales_id_Uzsakymo': row[4]
            }
            cursor.close()
            conn.close()
            return render_template('uzsakytos_prekes_edit.html', uzsakyta_preke=uzsakyta_preke)
        else:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Užsakyta prekė nerasta'}), 404
    except Exception as e:
        print(f"Error in edit_uzsakyta_preke: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/uzsakytos_prekes/update/<int:id>', methods=['PUT', 'OPTIONS'])
def update_uzsakyta_preke(id):
    if request.method == 'OPTIONS':
        return '', 204
    try:
        print(f"Attempting to update uzsakyta_preke {id}...")
        data = request.get_json()
        print("Received data:", data)
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE uzsakytos_prekes 
            SET Tipas = %s,
                Kiekis = %s,
                fk_Prekes_id_Preke = %s,
                fk_Uzsakymo_detales_id_Uzsakymo = %s
            WHERE id_Uzsakyta_preke = %s
        """, (
            data['Tipas'],
            data['Kiekis'],
            data['fk_Prekes_id_Preke'],
            data['fk_Uzsakymo_detales_id_Uzsakymo'],
            id
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Užsakyta prekė sėkmingai atnaujinta'})
    except Exception as e:
        print(f"Error in update_uzsakyta_preke: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/uzsakytos_prekes/nauja')
def add_uzsakyta_preke_form():
    return render_template('add_uzsakyta_preke.html')

@app.route('/uzsakytos_prekes/insert', methods=['POST'])
def insert_uzsakyta_preke():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No JSON data received'}), 400
            
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO uzsakytos_prekes (
                Tipas, Kiekis, fk_Prekes_id_Preke, fk_Uzsakymo_detales_id_Uzsakymo
            ) VALUES (%s, %s, %s, %s)
        """, (
            data['tipas'], data['kiekis'], data['fk_prekes_id'], data['fk_uzsakymo_id']
        ))
        
        conn.commit()
        last_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        return jsonify({'message': f'Užsakyta prekė sėkmingai pridėta! (ID: {last_id})'})
        
    except Exception as e:
        print(f"Error in insert: {str(e)}")
        return jsonify({'message': f'Server error: {str(e)}'}), 500

@app.route('/uzsakymo_detales')
def uzsakymo_detales():
    return render_template('uzsakymo_detales.html')

@app.route('/uzsakymo_detales/data')
def get_uzsakymo_detales():
    try:
        print("Attempting to fetch uzsakymo_detales...")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ud.*, k.Vardas, k.Pavarde 
            FROM uzsakymo_detales ud
            LEFT JOIN klientai k ON ud.fk_Klientai_id_Klientas = k.id_Klientas
        """)
        rows = cursor.fetchall()
        print(f"Fetched {len(rows)} rows from database")
        
        # Convert the rows to a list of dictionaries
        result = []
        for row in rows:
            item = {
                'id_Uzsakymo': row[0],
                'Prekes_pavadinimas': row[1],
                'Paslaugos_pavadinimas': row[2],
                'Dovanu_cekis': row[3],
                'Vieneto_kaina': row[4],
                'Uzsakymo_data': row[5],
                'Kaina': row[6],
                'Busena': row[7],
                'fk_Klientai_id_Klientas': row[8],
                'Klientas': {
                    'Vardas': row[9],
                    'Pavarde': row[10]
                }
            }
            result.append(item)
        
        print("Processed data:", result)
        cursor.close()
        conn.close()
        return jsonify(result)
    except Exception as e:
        print(f"Error in get_uzsakymo_detales: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/uzsakymo_detales/delete/<int:id>', methods=['DELETE'])
def delete_uzsakymo_detale(id):
    try:
        print(f"Attempting to delete uzsakymo_detale {id}...")
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if the order exists
        cursor.execute("""
            SELECT * FROM uzsakymo_detales 
            WHERE id_Uzsakymo = %s
        """, (id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'error': 'Užsakymo detalė nerasta'}), 404
        
        # Delete related ordered items first
        cursor.execute("""
            DELETE FROM uzsakytos_prekes 
            WHERE fk_Uzsakymo_detales_id_Uzsakymo = %s
        """, (id,))
        
        # Delete the order
        cursor.execute("""
            DELETE FROM uzsakymo_detales 
            WHERE id_Uzsakymo = %s
        """, (id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Užsakymo detalė sėkmingai ištrinta'})
    except Exception as e:
        print(f"Error in delete_uzsakymo_detale: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/uzsakymo_detales/<int:id>', methods=['PUT', 'OPTIONS'])
def update_uzsakymo_detale(id):
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        print(f"Attempting to update uzsakymo_detale {id}...")
        data = request.get_json()
        print("Received data:", data)
        
        # Validate required fields
        required_fields = ['Prekes_pavadinimas', 'Paslaugos_pavadinimas', 'Dovanu_cekis', 
                         'Vieneto_kaina', 'Uzsakymo_data', 'Kaina', 'Busena', 'fk_Klientai_id_Klientas']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if the order exists
        cursor.execute("""
            SELECT * FROM uzsakymo_detales 
            WHERE id_Uzsakymo = %s
        """, (id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'error': 'Užsakymo detalė nerasta'}), 404
        
        # Update the order
        cursor.execute("""
            UPDATE uzsakymo_detales 
            SET Prekes_pavadinimas = %s,
                Paslaugos_pavadinimas = %s,
                Dovanu_cekis = %s,
                Vieneto_kaina = %s,
                Uzsakymo_data = %s,
                Kaina = %s,
                Busena = %s,
                fk_Klientai_id_Klientas = %s
            WHERE id_Uzsakymo = %s
        """, (data['Prekes_pavadinimas'], data['Paslaugos_pavadinimas'], 
              data['Dovanu_cekis'], data['Vieneto_kaina'], data['Uzsakymo_data'],
              data['Kaina'], data['Busena'], data['fk_Klientai_id_Klientas'], id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Užsakymo detalė sėkmingai atnaujinta'})
    except Exception as e:
        print(f"Error in update_uzsakymo_detale: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/uzsakymo_detales/check')
def check_uzsakymo_detales():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SHOW TABLES LIKE 'uzsakymo_detales'")
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            return jsonify({'error': 'Table uzsakymo_detales does not exist'}), 404
            
        # Get table structure
        cursor.execute("DESCRIBE uzsakymo_detales")
        structure = cursor.fetchall()
        
        # Get row count
        cursor.execute("SELECT COUNT(*) FROM uzsakymo_detales")
        row_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'table_exists': True,
            'row_count': row_count,
            'structure': structure
        })
    except Exception as e:
        print(f"Error checking table: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/klientai')
def klientai():
    return render_template('klientai.html')

@app.route('/klientai/data')
def get_klientai():
    try:
        print("Attempting to fetch klientai data...")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM klientai")
        rows = cursor.fetchall()
        print(f"Fetched {len(rows)} rows from database")
        
        # Convert rows to list of dictionaries
        data = []
        for row in rows:
            data.append({
                'id_Klientas': row[0],
                'Vardas': row[1],
                'Pavarde': row[2],
                'Gimimo_diena': row[3].strftime('%Y-%m-%d') if row[3] is not None else None,
                'Telefono_numeris': row[4],
                'Gyvenamoji_vieta': row[5],
                'Pasto_kodas': row[6],
                'Elektroninio_pasto_adresas': row[7]
            })
        
        print("Processed data:", data)
        cursor.close()
        conn.close()
        return jsonify(data)
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/klientai/delete/<int:id>', methods=['DELETE'])
def delete_klientas(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM klientai WHERE id_Klientas = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Klientas sėkmingai ištrintas'})
    except Exception as e:
        print(f"Error deleting data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/klientai/update/<int:id>', methods=['PUT', 'OPTIONS'])
def update_klientas(id):
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        data = request.get_json()
            
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE klientai 
            SET Vardas = %s,
                Pavarde = %s,
                Gimimo_diena = %s,
                Telefono_numeris = %s,
                Gyvenamoji_vieta = %s,
                Pasto_kodas = %s,
                Elektroninio_pasto_adresas = %s
            WHERE id_Klientas = %s
        """, (
            data.get('Vardas'),
            data.get('Pavarde'),
            data.get('Gimimo_diena'),
            data.get('Telefono_numeris'),
            data.get('Gyvenamoji_vieta'),
            data.get('Pasto_kodas'),
            data.get('Elektroninio_pasto_adresas'),
            id
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Klientas sėkmingai atnaujintas'})
    except Exception as e:
        print(f"Error updating data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/klientai/nauja')
def add_klientas_form():
    return render_template('add_klientas.html')

@app.route('/klientai/insert', methods=['POST'])
def insert_klientas():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No JSON data received'}), 400
            
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO klientai (
                Vardas, Pavarde, El_pastas, Telefonas, Adresas
            ) VALUES (%s, %s, %s, %s, %s)
        """, (
            data['vardas'], data['pavarde'], data['el_pastas'],
            data['telefonas'], data['adresas']
        ))
        
        conn.commit()
        last_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        return jsonify({'message': f'Klientas sėkmingai pridėtas! (ID: {last_id})'})
        
    except Exception as e:
        print(f"Error in insert: {str(e)}")
        return jsonify({'message': f'Server error: {str(e)}'}), 500

@app.route('/uzsakymo_detales/nauja')
def add_uzsakymo_detale_form():
    return render_template('add_uzsakymo_detale.html')

@app.route('/uzsakymo_detales/insert', methods=['POST'])
def insert_uzsakymo_detale():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No JSON data received'}), 400
            
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO uzsakymo_detales (
                Kiekis, fk_Prekes_id_Preke, fk_Uzsakymo_id_Uzsakymo
            ) VALUES (%s, %s, %s)
        """, (
            data['kiekis'], data['fk_prekes_id'], data['fk_uzsakymo_id']
        ))
        
        conn.commit()
        last_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        return jsonify({'message': f'Užsakymo detalė sėkmingai pridėta! (ID: {last_id})'})
        
    except Exception as e:
        print(f"Error in insert: {str(e)}")
        return jsonify({'message': f'Server error: {str(e)}'}), 500

@app.route('/uzsakytos_prekes/by_uzsakymas/<int:id>')
def get_uzsakytos_prekes_by_uzsakymas(id):
    try:
        print(f"Attempting to fetch uzsakytos_prekes for uzsakymas {id}...")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM uzsakytos_prekes 
            WHERE fk_Uzsakymo_detales_id_Uzsakymo = %s
        """, (id,))
        rows = cursor.fetchall()
        print(f"Fetched {len(rows)} rows from database")
        
        # Convert the rows to a list of dictionaries
        result = []
        for row in rows:
            item = {
                'id_Uzsakyta_preke': row[0],
                'Tipas': row[1],
                'Kiekis': row[2],
                'fk_Prekes_id_Preke': row[3],
                'fk_Uzsakymo_detales_id_Uzsakymo': row[4]
            }
            result.append(item)
        
        print("Processed data:", result)
        cursor.close()
        conn.close()
        return jsonify(result)
    except Exception as e:
        print(f"Error in get_uzsakytos_prekes_by_uzsakymas: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/uzsakytos_prekes/view/<int:id>')
def view_uzsakyta_preke(id):
    try:
        print(f"Attempting to fetch uzsakyta_preke {id}...")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM uzsakytos_prekes 
            WHERE id_Uzsakyta_preke = %s
        """, (id,))
        row = cursor.fetchone()
        print(f"Fetched row: {row}")
        
        if row:
            uzsakyta_preke = {
                'id_Uzsakyta_preke': row[0],
                'Tipas': row[1],
                'Kiekis': row[2],
                'fk_Prekes_id_Preke': row[3],
                'fk_Uzsakymo_detales_id_Uzsakymo': row[4]
            }
            
            cursor.close()
            conn.close()
            return jsonify(uzsakyta_preke)
        else:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Užsakyta prekė nerasta'}), 404
    except Exception as e:
        print(f"Error in view_uzsakyta_preke: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/uzsakymo_detales/view/<int:order_id>', methods=['GET', 'OPTIONS'])
def view_order_details(order_id):
    if request.method == 'OPTIONS':
        return '', 204
    try:
        print(f"Attempting to fetch order details for order {order_id}...")
        conn = get_connection()
        cursor = conn.cursor()
        
        # First, let's check the table structure
        cursor.execute("DESCRIBE uzsakymo_detales")
        columns = cursor.fetchall()
        print("Table structure:", columns)
        
        # Then try to fetch the order
        cursor.execute("SELECT * FROM uzsakymo_detales WHERE id_Uzsakymo = %s", (order_id,))
        order = cursor.fetchone()
        
        if order:
            order_data = {
                'id_Uzsakymo': order[0],
                'Prekes_pavadinimas': order[1],
                'Paslaugos_pavadinimas': order[2],
                'Dovanu_cekis': order[3],
                'Vieneto_kaina': str(order[4]),
                'Uzsakymo_data': order[5].strftime('%Y-%m-%d') if order[5] else None,
                'Kaina': str(order[6]),
                'Busena': order[7],
                'fk_Klientai_id_Klientas': order[8]
            }
            print("Order details:", order_data)
            return jsonify(order_data)
        else:
            return jsonify({'error': 'Užsakymas nerastas'}), 404
    except Exception as e:
        print(f"Error in view_order_details: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/uzsakymo_detales/by_klientas/<int:id>')
def get_uzsakymo_detales_by_klientas(id):
    try:
        print(f"Attempting to fetch uzsakymo_detales for klientas {id}...")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM uzsakymo_detales 
            WHERE fk_Klientai_id_Klientas = %s
        """, (id,))
        rows = cursor.fetchall()
        print(f"Fetched {len(rows)} rows from database")
        
        # Convert the rows to a list of dictionaries
        result = []
        for row in rows:
            item = {
                'id_Uzsakymo': row[0],
                'Prekes_pavadinimas': row[1],
                'Paslaugos_pavadinimas': row[2],
                'Dovanu_cekis': row[3],
                'Vieneto_kaina': row[4],
                'Uzsakymo_data': row[5],
                'Kaina': row[6],
                'Busena': row[7],
                'fk_Klientai_id_Klientas': row[8]
            }
            result.append(item)
        
        print("Processed data:", result)
        cursor.close()
        conn.close()
        return jsonify(result)
    except Exception as e:
        print(f"Error in get_uzsakymo_detales_by_klientas: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/uzsakymo_detales/edit/<int:id>')
def edit_uzsakymo_detale(id):
    try:
        print(f"Attempting to fetch uzsakymo_detale {id}...")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM uzsakymo_detales 
            WHERE id_Uzsakymo = %s
        """, (id,))
        row = cursor.fetchone()
        print(f"Fetched row: {row}")
        
        if row:
            uzsakymo_detale = {
                'id_Uzsakymo': row[0],
                'Prekes_pavadinimas': row[1],
                'Paslaugos_pavadinimas': row[2],
                'Dovanu_cekis': row[3],
                'Vieneto_kaina': row[4],
                'Uzsakymo_data': row[5],
                'Kaina': row[6],
                'Busena': row[7],
                'fk_Klientai_id_Klientas': row[8]
            }
            
            cursor.close()
            conn.close()
            return render_template('uzsakymo_detales_edit.html', uzsakymo_detale=uzsakymo_detale)
        else:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Užsakymo detalė nerasta'}), 404
    except Exception as e:
        print(f"Error in edit_uzsakymo_detale: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/uzsakymo_detales', methods=['POST'])
def create_uzsakymo_detale():
    try:
        print("Attempting to create uzsakymo_detale...")
        data = request.get_json()
        print("Received data:", data)
        
        # Validate required fields
        required_fields = ['Prekes_pavadinimas', 'Paslaugos_pavadinimas', 'Dovanu_cekis', 
                         'Vieneto_kaina', 'Uzsakymo_data', 'Kaina', 'Busena', 'fk_Klientai_id_Klientas']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Insert the order
        cursor.execute("""
            INSERT INTO uzsakymo_detales (
                Prekes_pavadinimas, Paslaugos_pavadinimas, Dovanu_cekis,
                Vieneto_kaina, Uzsakymo_data, Kaina, Busena, fk_Klientai_id_Klientas
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_Uzsakymo
        """, (data['Prekes_pavadinimas'], data['Paslaugos_pavadinimas'], 
              data['Dovanu_cekis'], data['Vieneto_kaina'], data['Uzsakymo_data'],
              data['Kaina'], data['Busena'], data['fk_Klientai_id_Klientas']))
        
        new_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'message': 'Užsakymo detalė sėkmingai sukurta',
            'id': new_id
        })
    except Exception as e:
        print(f"Error in create_uzsakymo_detale: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/uzsakymo_detales/data/<int:order_id>', methods=['GET', 'OPTIONS'])
def get_order_details(order_id):
    if request.method == 'OPTIONS':
        return '', 204
    try:
        print(f"Attempting to fetch order details for order {order_id}...")
        conn = get_connection()
        cursor = conn.cursor()
        
        # First, let's check the table structure
        cursor.execute("DESCRIBE uzsakymo_detales")
        columns = cursor.fetchall()
        print("Table structure:", columns)
        
        # Then try to fetch the order
        cursor.execute("SELECT * FROM uzsakymo_detales WHERE id_Uzsakymo = %s", (order_id,))
        order = cursor.fetchone()
        
        if order:
            order_data = {
                'id_Uzsakymo': order[0],
                'Prekes_pavadinimas': order[1],
                'Paslaugos_pavadinimas': order[2],
                'Dovanu_cekis': order[3],
                'Vieneto_kaina': str(order[4]),
                'Uzsakymo_data': order[5].strftime('%Y-%m-%d') if order[5] else None,
                'Kaina': str(order[6]),
                'Busena': order[7],
                'fk_Klientai_id_Klientas': order[8]
            }
            print("Order details:", order_data)
            return jsonify(order_data)
        else:
            return jsonify({'error': 'Užsakymas nerastas'}), 404
    except Exception as e:
        print(f"Error in get_order_details: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
