from db_config import get_connection

def test_database():
    try:
        # Test connection
        conn = get_connection()
        print("Successfully connected to database!")
        
        # Test table existence
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES LIKE 'prekes'")
        result = cursor.fetchone()
        
        if result:
            print("Table 'prekes' exists!")
            
            # Test if table has data
            cursor.execute("SELECT COUNT(*) FROM prekes")
            count = cursor.fetchone()[0]
            print(f"Table has {count} records")
            
            # Show table structure
            cursor.execute("DESCRIBE prekes")
            print("\nTable structure:")
            for column in cursor.fetchall():
                print(column)
        else:
            print("Table 'prekes' does not exist!")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_database() 