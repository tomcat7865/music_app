from flask import Flask, render_template, request, g
import mysql.connector

app = Flask(__name__)

# Database Configuration - Ensure your password is correct here
db_config = {
    'host': 'localhost',
    'user': 'music_user',
    'password': '5YRACU$E', 
    'database': 'physical_music'
}

def get_db_connection():
    if 'db' not in g:
        g.db = mysql.connector.connect(**db_config)
    return g.db

@app.teardown_appcontext
def close_db_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch total count for status bar
    cursor.execute("SELECT COUNT(*) as total FROM master_release_entry")
    total_count = cursor.fetchone()['total']
    
    # Corrected Dropdown Query: Uses Master ID (150) so the link works
    cursor.execute("""
        SELECT m.id, alb.album as album_name 
        FROM master_release_entry m 
        JOIN lookup_album alb ON m.album = alb.album_id 
        ORDER BY alb.album ASC
    """)
    albums = cursor.fetchall()
    
    return render_template('index.html', total_count=total_count, albums=albums)

@app.route('/view_master')
def view_master():
    album_id = request.args.get('id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Always fetch the album list for the dropdown on this page
    cursor.execute("""
        SELECT m.id, alb.album as album_name 
        FROM master_release_entry m 
        JOIN lookup_album alb ON m.album = alb.album_id 
        ORDER BY alb.album ASC
    """)
    all_albums = cursor.fetchall()

    result = None
    other_versions = []

    if album_id:
        # Fetch Master Details using the "Safe" catalogue_no column
        query = """
            SELECT m.id, art.artist, alb.album, lab.label, 
                   m.catalogue_no, 
                   f.physical_format_type AS format, 
                   s.storage_location AS location,
                   m.original_release_year, m.this_release_year, 
                   m.this_release_duration, m.average_album_dynamic_range
            FROM master_release_entry m
            LEFT JOIN lookup_artist art ON m.artist = art.id
            LEFT JOIN lookup_album alb ON m.album = alb.album_id
            LEFT JOIN lookup_label lab ON m.label = lab.id
            LEFT JOIN lookup_physical_format_type f ON m.physical_format_type = f.id
            LEFT JOIN lookup_storage_location s ON m.storage_location = s.id
            WHERE m.id = %s
        """
        cursor.execute(query, (album_id,))
        result = cursor.fetchone()

        # Fetch Digital Rips (sub-form data)
        if result:
            version_query = """
                SELECT v.version_id, d.digital_format_type, sr.sample_rate, bd.bit_depth
                FROM other_version_entry v
                LEFT JOIN lookup_digital_format_type d ON v.digital_format_type = d.id
                LEFT JOIN lookup_sample_rate sr ON v.sample_rate = sr.id
                LEFT JOIN lookup_bit_depth bd ON v.bit_depth = bd.id
                WHERE v.id = %s
            """
            cursor.execute(version_query, (album_id,))
            other_versions = cursor.fetchall()

    return render_template('view_master.html', 
                           albums=all_albums, 
                           result=result, 
                           other_versions=other_versions)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
