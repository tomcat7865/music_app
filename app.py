from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
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
    with conn.cursor() as cursor:
        cursor.execute("SELECT m.id AS master_id, a.album AS album_name FROM master_release_entry m JOIN lookup_album a ON m.album_id = a.album_id ORDER BY a.album ASC")
        data = cursor.fetchall()
    conn.close()
    return render_template('index.html', albums=data)

@app.route('/view_master')
def view_master():
    sid = request.args.get('id')
    conn, result = get_db_connection(), None
    with conn.cursor() as cursor:
        if sid:
            query = """
                SELECT m.*, art.artist, alb.album, lab.label, cat.catalogue_number 
                FROM master_release_entry m 
                LEFT JOIN lookup_artist art ON m.artist_id = art.id 
                LEFT JOIN lookup_album alb ON m.album_id = alb.album_id 
                LEFT JOIN lookup_label lab ON m.label_id = lab.id 
                LEFT JOIN lookup_catalogue_no cat ON m.catalogue_no_id = cat.id 
                WHERE m.id = %s
            """
            cursor.execute(query, (sid,))
            result = cursor.fetchone()
    conn.close()
    return render_template('view_master.html', result=result)

@app.route('/control_panel')
def control_panel_home():
    return render_template('control_panel_menu.html')

@app.route('/api/verify_master/<int:master_id>')
def verify_master(master_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT art.artist, alb.album FROM master_release_entry m JOIN lookup_artist art ON m.artist_id = art.id JOIN lookup_album alb ON m.album_id = alb.album_id WHERE m.id = %s", (master_id,))
        res = cursor.fetchone()
    conn.close()
    return jsonify({"success": True, "display": f"{res['artist']} - {res['album']}"}) if res else jsonify({"success": False})

@app.route('/control_panel/interactions')
def manage_interactions():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id, interaction_type FROM lookup_interaction_type ORDER BY interaction_type ASC"); t = cur.fetchall()
        cur.execute("SELECT id, catalogue_number FROM lookup_catalogue_no ORDER BY catalogue_number ASC"); c = cur.fetchall()
        cur.execute("SELECT id, physical_format_type FROM lookup_physical_format_type ORDER BY physical_format_type ASC"); f = cur.fetchall()
        cur.execute("SELECT id, bit_depth FROM lookup_bit_depth ORDER BY bit_depth ASC"); b = cur.fetchall()
        cur.execute("SELECT id, sample_rate FROM lookup_sample_rate ORDER BY sample_rate ASC"); s = cur.fetchall()
    conn.close()
    return render_template('manage_interactions.html', types=t, cats=c, formats=f, bits=b, rates=s)

@app.route('/control_panel/interactions/save', methods=['POST'])
def save_interaction():
    d = request.form
    cat_no = d.get('cat_number')
    conn = get_db_connection()
    with conn.cursor() as cur:
        # Resolve the string Catalogue Number to its ID
        cur.execute("SELECT id FROM lookup_catalogue_no WHERE catalogue_number = %s", (cat_no,))
        cat_result = cur.fetchone()
        cat_id = cat_result['id'] if cat_result else None
        
        if not cat_id:
            flash("Invalid Catalogue Number", "error")
            return redirect(url_for('manage_interactions'))

        bit_id = d.get('bit_id') if d.get('bit_id') != "" else None
        sample_id = d.get('sample_id') if d.get('sample_id') != "" else None
        
        vals = (d.get('master_id'), d.get('interaction_date'), d.get('interaction_type'), 
                cat_id, d.get('format_id'), bit_id, sample_id, d.get('comment'))
        
        cur.execute("INSERT INTO media_interaction_log (master_release_entry_id, interaction_date, interaction_type_id, catalogue_no_id, physical_format_type_id, bit_depth_id, sample_rate_id, individual_comment) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", vals)
        conn.commit()
    conn.close()
    flash("Interaction Logged!", "success")
    return redirect(url_for('manage_interactions'))

@app.route('/control_panel/artists', methods=['GET', 'POST'])
def manage_artists():
    conn, res, q = get_db_connection(), [], request.form.get('artist_search', '')
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, artist FROM lookup_artist ORDER BY artist ASC"); all_art = cursor.fetchall()
        if request.method == 'POST' and q:
            cursor.execute("SELECT id, artist FROM lookup_artist WHERE artist LIKE %s", (f"%{q}%",)); res = cursor.fetchall()
    conn.close()
    return render_template('manage_artists.html', all_artists=all_art, search_results=res, search_query=q)

@app.route('/control_panel/albums', methods=['GET', 'POST'])
def manage_albums():
    conn, res, q = get_db_connection(), [], request.form.get('album_search', '')
    with conn.cursor() as cursor:
        cursor.execute("SELECT album_id AS id, album FROM lookup_album ORDER BY album ASC"); all_alb = cursor.fetchall()
        if request.method == 'POST' and q:
            cursor.execute("SELECT album_id AS id, album FROM lookup_album WHERE album LIKE %s", (f"%{q}%",)); res = cursor.fetchall()
    conn.close()
    return render_template('manage_albums.html', all_albums=all_alb, search_results=res, search_query=q)

@app.route('/control_panel/labels', methods=['GET', 'POST'])
def manage_labels():
    conn, res, q = get_db_connection(), [], request.form.get('label_search', '')
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, label FROM lookup_label ORDER BY label ASC"); all_lab = cursor.fetchall()
        if request.method == 'POST' and q:
            cursor.execute("SELECT id, label FROM lookup_label WHERE label LIKE %s", (f"%{q}%",)); res = cursor.fetchall()
    conn.close()
    return render_template('manage_labels.html', all_labels=all_lab, search_results=res, search_query=q)

@app.route('/control_panel/catalogue_numbers', methods=['GET', 'POST'])
def manage_catalogue_numbers():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, catalogue_number FROM lookup_catalogue_no ORDER BY catalogue_number ASC"); c = cursor.fetchall()
    conn.close()
    return render_template('manage_catalogue_numbers.html', cat_nos=c)

@app.route('/control_panel/locations')
def manage_locations():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, storage_location FROM lookup_storage_location ORDER BY storage_location ASC"); l = cursor.fetchall()
    conn.close()
    return render_template('manage_locations.html', locations=l)

@app.route('/control_panel/media_specs')
def manage_media_specs():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, disc_brand FROM lookup_disc_brand ORDER BY disc_brand ASC"); b = cursor.fetchall()
        cursor.execute("SELECT id1 AS id, cdr_code FROM lookup_cdr_code ORDER BY cdr_code ASC"); c = cursor.fetchall()
        cursor.execute("SELECT id, bdr_dvdr_code FROM lookup_bdr_dvdr_code ORDER BY bdr_dvdr_code ASC"); d = cursor.fetchall()
    conn.close()
    return render_template('manage_media_specs.html', brands=b, cdr_codes=c, dvd_codes=d)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
