from flask import Flask, render_template, request, jsonify, redirect, url_for
from db_config import get_connection
from flask_cors import CORS

app = Flask(__name__)
# Configure CORS to allow all methods and headers
CORS(app, resources={r"/*": {"origins": "*"}})

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
                if field in valid_fields and value and value.strip():
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

if __name__ == '__main__':
    app.run(debug=True)
