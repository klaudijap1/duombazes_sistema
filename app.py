from flask import Flask, render_template, request, redirect, url_for, flash
from db_config import get_connection

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for flashing messages

@app.route('/')
def main_menu():
    return render_template('main_menu.html')

@app.route('/uzsakymo_detales')
def uzsakymo_detales():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
    SELECT 
        ud.id_Uzsakymo,
        ud.Paslaugos_pavadinimas,
        ud.Dovanu_cekis,
        ud.Vieneto_kaina,
        ud.Uzsakymo_data,
        ud.Kaina,
        ud.Busena,
        ud.fk_Klientai_id_Klientas,
        CONCAT(k.Vardas, ' ', k.Pavarde) as Kliento_vardas,
        GROUP_CONCAT(CONCAT(p.Pavadinimas, ' (', up.Kiekis, ')') SEPARATOR ', ') as Prekiu_pavadinimai
    FROM uzsakymo_detales ud
    LEFT JOIN klientai k ON ud.fk_Klientai_id_Klientas = k.id_Klientas
    LEFT JOIN uzsakytos_prekes up ON ud.id_Uzsakymo = up.fk_Uzsakymo_detales_id_Uzsakymo
    LEFT JOIN prekes p ON up.fk_Prekes_id_Preke = p.id_Preke
    GROUP BY ud.id_Uzsakymo
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    # Get all clients for the dropdown
    cursor.execute("SELECT id_Klientas, CONCAT(Vardas, ' ', Pavarde) as Kliento_vardas FROM klientai")
    clients = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('uzsakymo_detales.html', orders=results, clients=clients)

@app.route('/create_order', methods=['GET', 'POST'])
def create_order():
    if request.method == 'POST':
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # Get form data
            service_name = request.form['service_name']
            gift_certificate = request.form['gift_certificate']
            unit_price = float(request.form['unit_price'])
            order_date = request.form['order_date']
            price = float(request.form['price'])
            status = request.form['status']
            client_id = request.form['client_id']
            
            # Insert new order
            cursor.execute("""
                INSERT INTO uzsakymo_detales 
                (Paslaugos_pavadinimas, Dovanu_cekis, Vieneto_kaina, Uzsakymo_data, Kaina, Busena, fk_Klientai_id_Klientas)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (service_name, gift_certificate, unit_price, order_date, price, status, client_id))
            
            # Get the ID of the newly created order
            order_id = cursor.lastrowid
            
            # Handle products
            product_ids = request.form.getlist('product_id[]')
            product_quantities = request.form.getlist('product_quantity[]')
            
            for product_id, quantity in zip(product_ids, product_quantities):
                if product_id and quantity:
                    cursor.execute("""
                        INSERT INTO uzsakytos_prekes 
                        (Kiekis, fk_Prekes_id_Preke, fk_Uzsakymo_detales_id_Uzsakymo)
                        VALUES (%s, %s, %s)
                    """, (int(quantity), product_id, order_id))
            
            conn.commit()
            flash('Užsakymas sėkmingai sukurtas!', 'success')
            return redirect(url_for('uzsakymo_detales'))
            
        except Exception as e:
            conn.rollback()
            flash(f'Klaida kuriant užsakymą: {str(e)}', 'error')
            return redirect(url_for('create_order'))
        finally:
            cursor.close()
            conn.close()
    
    # GET request - show the form
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Get clients for the dropdown
        cursor.execute("SELECT id_Klientas, CONCAT(Vardas, ' ', Pavarde) as Kliento_vardas FROM klientai")
        clients = cursor.fetchall()
        
        # Get products for the dropdown
        cursor.execute("SELECT id_Preke, Pavadinimas FROM prekes")
        products = cursor.fetchall()
        
        return render_template('create_order.html', clients=clients, products=products)
    finally:
        cursor.close()
        conn.close()

@app.route('/edit_order/<int:id>', methods=['GET', 'POST'])
def edit_order(id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        try:
            # Start transaction
            conn.start_transaction()
            
            # Update order details
            update_query = """
            UPDATE uzsakymo_detales 
            SET Paslaugos_pavadinimas = %s,
                Dovanu_cekis = %s,
                Vieneto_kaina = %s,
                Uzsakymo_data = %s,
                Kaina = %s,
                Busena = %s,
                fk_Klientai_id_Klientas = %s
            WHERE id_Uzsakymo = %s
            """
            
            cursor.execute(update_query, (
                request.form.get('service_name'),
                request.form.get('gift_certificate'),
                request.form.get('unit_price'),
                request.form.get('order_date'),
                request.form.get('price'),
                request.form.get('status'),
                request.form.get('client_id'),
                id
            ))
            
            # Delete existing product relationships
            cursor.execute("DELETE FROM uzsakytos_prekes WHERE fk_Uzsakymo_detales_id_Uzsakymo = %s", (id,))
            
            # Add new product relationships
            product_ids = request.form.getlist('product_id[]')
            product_quantities = request.form.getlist('product_quantity[]')
            
            for product_id, quantity in zip(product_ids, product_quantities):
                if product_id and quantity:  # Only add if both product and quantity are provided
                    cursor.execute("""
                        INSERT INTO uzsakytos_prekes 
                        (Kiekis, fk_Prekes_id_Preke, fk_Uzsakymo_detales_id_Uzsakymo)
                        VALUES (%s, %s, %s)
                    """, (int(quantity), product_id, id))
            
            conn.commit()
            flash('Užsakymas sėkmingai atnaujintas!', 'success')
            return redirect(url_for('uzsakymo_detales'))
            
        except Exception as e:
            conn.rollback()
            flash(f'Klaida atnaujinant užsakymą: {str(e)}', 'error')
            return redirect(url_for('edit_order', id=id))
    
    # GET request - fetch order details
    cursor.execute("""
        SELECT * FROM uzsakymo_detales 
        WHERE id_Uzsakymo = %s
    """, (id,))
    order = cursor.fetchone()
    
    # Get all clients for the dropdown
    cursor.execute("SELECT id_Klientas, CONCAT(Vardas, ' ', Pavarde) as Kliento_vardas FROM klientai")
    clients = cursor.fetchall()
    
    # Get all products for the dropdown
    cursor.execute("SELECT id_Preke, Pavadinimas FROM prekes")
    products = cursor.fetchall()
    
    # Get current product relationships
    cursor.execute("""
        SELECT up.*, p.Pavadinimas 
        FROM uzsakytos_prekes up
        JOIN prekes p ON up.fk_Prekes_id_Preke = p.id_Preke
        WHERE up.fk_Uzsakymo_detales_id_Uzsakymo = %s
    """, (id,))
    current_products = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('edit_order.html', 
                         order=order, 
                         clients=clients, 
                         products=products,
                         current_products=current_products)

@app.route('/delete_order/<int:id>', methods=['POST'])
def delete_order(id):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Start transaction
        conn.start_transaction()
        
        # Delete related services first
        cursor.execute("DELETE FROM uzsakytos_paslaugos WHERE fk_Uzsakymo_detales_id_Uzsakymo = %s", (id,))
        
        # Delete related products
        cursor.execute("DELETE FROM uzsakytos_prekes WHERE fk_Uzsakymo_detales_id_Uzsakymo = %s", (id,))
        
        # Delete related gift certificates
        cursor.execute("DELETE FROM uzsakyti_cekiai WHERE fk_Uzsakymo_detales_id_Uzsakymo = %s", (id,))
        
        # Delete the order
        cursor.execute("DELETE FROM uzsakymo_detales WHERE id_Uzsakymo = %s", (id,))
        
        conn.commit()
        flash('Užsakymas sėkmingai ištrintas!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Klaida ištrinant užsakymą: {str(e)}', 'error')
    
    cursor.close()
    conn.close()
    return redirect(url_for('uzsakymo_detales'))

@app.route('/ataskaita_filtrai')
def ataskaita_filtrai():
    return render_template('ataskaita_filtrai.html')

@app.route('/ataskaita', methods=['GET', 'POST'])
def ataskaita():
    # Get filter parameters
    date_from = request.args.get('date_from', '') if request.method == 'GET' else request.form.get('date_from', '')
    date_to = request.args.get('date_to', '') if request.method == 'GET' else request.form.get('date_to', '')
    price_from = request.args.get('price_from', '') if request.method == 'GET' else request.form.get('price_from', '')
    price_to = request.args.get('price_to', '') if request.method == 'GET' else request.form.get('price_to', '')
    client_search = request.args.get('client_search', '') if request.method == 'GET' else request.form.get('client_search', '')
    duration_from = request.args.get('duration_from', '') if request.method == 'GET' else request.form.get('duration_from', '')
    duration_to = request.args.get('duration_to', '') if request.method == 'GET' else request.form.get('duration_to', '')
    row_limit = request.args.get('row_limit', '') if request.method == 'GET' else request.form.get('row_limit', '')
    sort_order = request.args.get('sort_order', '') if request.method == 'GET' else request.form.get('sort_order', '')
      # Store filters for the template
    filters = {
        'date_from': date_from,
        'date_to': date_to,
        'price_from': price_from,
        'price_to': price_to,
        'client_search': client_search,
        'duration_from': duration_from,
        'duration_to': duration_to,
        'row_limit': row_limit,
        'sort_order': sort_order
    }
    conditions = []
    parameters = []

    if date_from:
        conditions.append("uzsakymo_detales.Uzsakymo_data >= %s")
        parameters.append(date_from)
    if date_to:
        conditions.append("uzsakymo_detales.Uzsakymo_data <= %s")
        parameters.append(date_to)
    if price_from:
        conditions.append("uzsakymo_detales.Kaina >= %s")
        parameters.append(price_from)
    if price_to:
        conditions.append("uzsakymo_detales.Kaina <= %s")
        parameters.append(price_to)
    if client_search:
        conditions.append("CONCAT(klientai.Vardas, ' ', klientai.Pavarde) LIKE %s")
        parameters.append(f"%{client_search}%")
    if duration_from:
        conditions.append("paslaugos.Trukme >= %s")
        parameters.append(duration_from)
    if duration_to:
        conditions.append("paslaugos.Trukme <= %s")
        parameters.append(duration_to)
    if row_limit:
        limit_condition = f"LIMIT {int(row_limit)}"
    else:
        limit_condition = ""
    
    if sort_order:
        order_clause = f"ORDER BY sort_group ASC, CAST(Kaina AS Decimal) {sort_order}"
    else:
        order_clause = "ORDER BY sort_group ASC"

    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)
    else:
        where_clause = ""

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = f"""
WITH suformatuota AS (
    SELECT 
        uzsakymo_detales.id_Uzsakymo, 
        uzsakymo_detales.Uzsakymo_data, 
        CAST(uzsakymo_detales.Kaina AS CHAR) AS Kaina, 
        CONCAT(klientai.Vardas, ' ', klientai.Pavarde) AS Klientas, 
        klientai.Gyvenamoji_vieta, 
        CAST(uzsakytos_paslaugos.Kiekis AS CHAR) AS Kiekis, 
        paslaugos.Pavadinimas AS Paslaugos_pavadinimas, 
        CAST(paslaugos.Trukme AS CHAR) AS Trukme
    FROM uzsakymo_detales 
    INNER JOIN klientai 
        ON uzsakymo_detales.fk_Klientai_id_Klientas = klientai.id_Klientas 
    LEFT JOIN uzsakytos_paslaugos 
        ON uzsakytos_paslaugos.fk_Uzsakymo_detales_id_Uzsakymo = uzsakymo_detales.id_Uzsakymo 
    LEFT JOIN paslaugos 
        ON paslaugos.id_Paslauga = uzsakytos_paslaugos.fk_Paslauga_id_Paslauga
    {where_clause}
),

suformatuota_limited AS (
    SELECT *, 1 AS sort_group
    FROM suformatuota
    {order_clause}
    {limit_condition}
)

-- Main output and summary rows
SELECT * FROM suformatuota_limited

UNION ALL
SELECT '', '', '', '', '', '', '', '', 2

UNION ALL
SELECT '', '', 'Kaina', '', '', 'Kiekis', '', 'Trukme', 3

UNION ALL
SELECT 'Viso:', '', 
    CAST(SUM(CAST(Kaina AS DECIMAL)) AS CHAR), '', '', 
    CAST(SUM(CAST(Kiekis AS DECIMAL)) AS CHAR), '', 
    CAST(SUM(CAST(Trukme AS DECIMAL)) AS CHAR), 4
FROM suformatuota_limited

UNION ALL
SELECT 'Vidurkiai:', '', 
    CAST(AVG(CAST(Kaina AS DECIMAL)) AS CHAR), '', '', 
    CAST(AVG(CAST(Kiekis AS DECIMAL)) AS CHAR), '', 
    CAST(AVG(CAST(Trukme AS DECIMAL)) AS CHAR), 5
FROM suformatuota_limited

UNION ALL
SELECT 'Maksimalus:', '', 
    CAST(MAX(CAST(Kaina AS DECIMAL)) AS CHAR), '', '', 
    CAST(MAX(CAST(Kiekis AS DECIMAL)) AS CHAR), '', 
    CAST(MAX(CAST(Trukme AS DECIMAL)) AS CHAR), 6
FROM suformatuota_limited

UNION ALL
SELECT 'Minimalus:', '', 
    CAST(MIN(CAST(Kaina AS DECIMAL)) AS CHAR), '', '', 
    CAST(MIN(CAST(Kiekis AS DECIMAL)) AS CHAR), '', 
    CAST(MIN(CAST(Trukme AS DECIMAL)) AS CHAR), 7
FROM suformatuota_limited

{order_clause};

"""



    cursor.execute(query, parameters)
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('ataskaita.html', report_data=results, filters=filters)

if __name__ == '__main__':
    app.run(debug=True)
