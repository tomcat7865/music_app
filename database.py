import pymysql

# Database configuration - Centralized for all modules
db_config = {
    'host': 'localhost',
    'user': 'music_user',
    'password': '2481',
    'database': 'physical_music',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection():
    """
    Creates and returns a new connection to the MariaDB/MySQL database.
    Used by view_master, control_panel, and reports_labels.
    """
    try:
        return pymysql.connect(**db_config)
    except pymysql.MySQLError as e:
        print(f"Error connecting to MariaDB: {e}")
        return None
