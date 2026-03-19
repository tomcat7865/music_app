from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql

app = Flask(__name__)
app.secret_key = "secret_archive_key"

db_config = {
    'host': 'localhost',
    'user': 'music_user',
    'password': '2481',
    'database': 'physical_music',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection():
    return pymysql.connect(**db_config)

@app.route('/')
def index():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            query = "SELECT m.id AS master_id, a.album AS album_name FROM master_release_entry m JOIN lookup_album a ON m.album_id = a.album_id ORDER BY a.album ASC"
            cursor.execute(query)
            albums = cursor.fetchall()
    finally:
        conn.close()
    return render_template('index.html', albums=albums)

@app.route('/control_panel')
def control_panel_home():
    return render_template('control_panel_menu.html')

# --- ARTIST / ALBUM / LABEL MANAGERS ---
@app.route('/control_panel/artists', methods=['GET', 'POST'])
def manage_artists():
    conn = get_db_connection()
    search_results = []
    search_query = request.form.get('artist_search', '')
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, artist FROM lookup_artist ORDER BY artist ASC")
            all_artists = cursor.fetchall()
            if request.method == 'POST' and search_query:
                cursor.execute("SELECT id, artist FROM lookup_artist WHERE artist LIKE %s ORDER BY artist ASC", (f"%{search_query}%",))
                search_results = cursor.fetchall()
    finally:
        conn.close()
    return render_template('manage_artists.html', all_artists=all_artists, search_results=search_results, search_query=search_query)

@app.route('/control_panel/artists/save', methods=['POST'])
def save_artist():
    artist_id = request.form.get('artist_id')
    artist_name = request.form.get('artist_name')
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if artist_id:
                cursor.execute("UPDATE lookup_artist SET artist = %s WHERE id = %s", (artist_name, artist_id))
            else:
                cursor.execute("INSERT INTO lookup_artist (artist) VALUES (%s)", (artist_name,))
            conn.commit()
            flash("Artist Saved Successfully", "success")
    finally:
        conn.close()
    return redirect(url_for('manage_artists'))

@app.route('/control_panel/albums', methods=['GET', 'POST'])
def manage_albums():
    conn = get_db_connection()
    search_results = []
    search_query = request.form.get('album_search', '')
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT album_id AS id, album FROM lookup_album ORDER BY album ASC")
            all_albums = cursor.fetchall()
            if request.method == 'POST' and search_query:
                cursor.execute("SELECT album_id AS id, album FROM lookup_album WHERE album LIKE %s ORDER BY album ASC", (f"%{search_query}%",))
                search_results = cursor.fetchall()
    finally:
        conn.close()
    return render_template('manage_albums.html', all_albums=all_albums, search_results=search_results, search_query=search_query)

@app.route('/control_panel/albums/save', methods=['POST'])
def save_album():
    album_id = request.form.get('album_id')
    album_name = request.form.get('album_name')
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if album_id:
                cursor.execute("UPDATE lookup_album SET album = %s WHERE album_id = %s", (album_name, album_id))
            else:
                cursor.execute("INSERT INTO lookup_album (album) VALUES (%s)", (album_name,))
            conn.commit()
            flash("Album Saved Successfully", "success")
    finally:
        conn.close()
    return redirect(url_for('manage_albums'))

@app.route('/control_panel/labels', methods=['GET', 'POST'])
def manage_labels():
    conn = get_db_connection()
    search_results = []
    search_query = request.form.get('label_search', '')
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, label FROM lookup_label ORDER BY label ASC")
            all_labels = cursor.fetchall()
            if request.method == 'POST' and search_query:
                cursor.execute("SELECT id, label FROM lookup_label WHERE label LIKE %s ORDER BY label ASC", (f"%{search_query}%",))
                search_results = cursor.fetchall()
    finally:
        conn.close()
    return render_template('manage_labels.html', all_labels=all_labels, search_results=search_results, search_query=search_query)

@app.route('/control_panel/labels/save', methods=['POST'])
def save_label():
    label_id = request.form.get('label_id')
    label_name = request.form.get('label_name')
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if label_id:
                cursor.execute("UPDATE lookup_label SET label = %s WHERE id = %s", (label_name, label_id))
            else:
                cursor.execute("INSERT INTO lookup_label (label) VALUES (%s)", (label_name,))
            conn.commit()
            flash("Label Saved Successfully", "success")
    finally:
        conn.close()
    return redirect(url_for('manage_labels'))

# --- CATALOGUE NUMBERS MANAGER ---
@app.route('/control_panel/catalogue_numbers', methods=['GET'])
def manage_catalogue_numbers():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, catalogue_number FROM lookup_catalogue_no ORDER BY catalogue_number ASC")
            cat_nos = cursor.fetchall()
    finally:
        conn.close()
    return render_template('manage_catalogue_numbers.html', cat_nos=cat_nos)

@app.route('/control_panel/catalogue_numbers/save', methods=['POST'])
def save_catalogue_number():
    cat_id = request.form.get('cat_id')
    cat_val = request.form.get('cat_val')
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if cat_id:
                cursor.execute("UPDATE lookup_catalogue_no SET catalogue_number = %s WHERE id = %s", (cat_val, cat_id))
            else:
                cursor.execute("INSERT INTO lookup_catalogue_no (catalogue_number) VALUES (%s)", (cat_val,))
            conn.commit()
            flash("Catalogue Number Saved Successfully", "success")
    finally:
        conn.close()
    return redirect(url_for('manage_catalogue_numbers'))

# --- MEDIA SPECS (BRANDS / CDR / DVDR) ---
@app.route('/control_panel/media_specs')
def manage_media_specs():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, disc_brand FROM lookup_disc_brand ORDER BY disc_brand ASC")
            brands = cursor.fetchall()
            cursor.execute("SELECT id1 AS id, cdr_code FROM lookup_cdr_code ORDER BY cdr_code ASC")
            cdr_codes = cursor.fetchall()
            cursor.execute("SELECT id, bdr_dvdr_code FROM lookup_bdr_dvdr_code ORDER BY bdr_dvdr_code ASC")
            dvd_codes = cursor.fetchall()
    finally:
        conn.close()
    return render_template('manage_media_specs.html', brands=brands, cdr_codes=cdr_codes, dvd_codes=dvd_codes)

@app.route('/control_panel/media_specs/save', methods=['POST'])
def save_media_spec():
    spec_type = request.form.get('spec_type')
    item_id = request.form.get('item_id')
    item_value = request.form.get('item_value')
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if spec_type == 'brand':
                if item_id:
                    cursor.execute("UPDATE lookup_disc_brand SET disc_brand = %s WHERE id = %s", (item_value, item_id))
                else:
                    cursor.execute("INSERT INTO lookup_disc_brand (disc_brand) VALUES (%s)", (item_value,))
            elif spec_type == 'cdr':
                if item_id:
                    cursor.execute("UPDATE lookup_cdr_code SET cdr_code = %s WHERE id1 = %s", (item_value, item_id))
                else:
                    cursor.execute("INSERT INTO lookup_cdr_code (cdr_code) VALUES (%s)", (item_value,))
            elif spec_type == 'dvd':
                if item_id:
                    cursor.execute("UPDATE lookup_bdr_dvdr_code SET bdr_dvdr_code = %s WHERE id = %s", (item_value, item_id))
                else:
                    cursor.execute("INSERT INTO lookup_bdr_dvdr_code (bdr_dvdr_code) VALUES (%s)", (item_value,))
            conn.commit()
            flash(f"Successfully saved to {spec_type.upper()} table.", "success")
    finally:
        conn.close()
    return redirect(url_for('manage_media_specs'))

# --- LOCATIONS MANAGER ---
@app.route('/control_panel/locations', methods=['GET'])
def manage_locations():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, storage_location FROM lookup_storage_location ORDER BY storage_location ASC")
            locations = cursor.fetchall()
    finally:
        conn.close()
    return render_template('manage_locations.html', locations=locations)

@app.route('/control_panel/locations/save', methods=['POST'])
def save_location():
    loc_id = request.form.get('loc_id')
    loc_name = request.form.get('loc_name')
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if loc_id:
                cursor.execute("UPDATE lookup_storage_location SET storage_location = %s WHERE id = %s", (loc_name, loc_id))
            else:
                cursor.execute("INSERT INTO lookup_storage_location (storage_location) VALUES (%s)", (loc_name,))
            conn.commit()
            flash("Location Saved Successfully", "success")
    finally:
        conn.close()
    return redirect(url_for('manage_locations'))

@app.route('/view_master')
def view_master():
    search_id = request.args.get('id')
    conn = get_db_connection()
    albums = []
    result = None
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT m.id AS master_id, a.album AS album_name FROM master_release_entry m JOIN lookup_album a ON m.album_id = a.album_id ORDER BY a.album ASC")
            albums = cursor.fetchall()
            if search_id:
                query = "SELECT m.*, art.artist, alb.album, lab.label, cat.catalogue_number FROM master_release_entry m JOIN lookup_artist art ON m.artist_id = art.id JOIN lookup_album alb ON m.album_id = alb.album_id JOIN lookup_label lab ON m.label_id = lab.id JOIN lookup_catalogue_no cat ON m.catalogue_no_id = cat.id WHERE m.id = %s"
                cursor.execute(query, (search_id,))
                result = cursor.fetchone()
    finally:
        conn.close()
    return render_template('view_master.html', albums=albums, result=result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
