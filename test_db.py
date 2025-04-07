from db_config import get_connection

def test_connection():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Testuojame klientų lentelę
        cursor.execute("SELECT * FROM klientai")
        clients = cursor.fetchall()
        print(f"Klientų skaičius: {len(clients)}")
        
        # Testuojame prekių lentelę
        cursor.execute("SELECT * FROM prekes")
        products = cursor.fetchall()
        print(f"Prekių skaičius: {len(products)}")
        
        # Testuojame užsakymų detalių lentelę
        cursor.execute("SELECT * FROM uzsakymo_detales")
        orders = cursor.fetchall()
        print(f"Užsakymų skaičius: {len(orders)}")
        
        cursor.close()
        conn.close()
        print("Prisijungimas prie duomenų bazės sėkmingas!")
        
    except Exception as e:
        print(f"Klaida prisijungiant prie duomenų bazės: {str(e)}")

if __name__ == "__main__":
    test_connection() 