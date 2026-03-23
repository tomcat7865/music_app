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
    return render_template('index.html')

# --- MASTER VIEWER ---
@app.route('/view_master')
def view_master():
    sid = request.args.get('id')
    conn = get_db_connection()
    result, albums_list, other_versions, interactions = None, [], [], []
    with conn.cursor() as cursor:
        cursor.execute("SELECT m.id, a.album FROM master_release_entry m JOIN lookup_album a ON m.album_id = a.album_id ORDER BY a.album ASC")
        albums_list = cursor.fetchall()
        
        if sid:
            query = """
                SELECT m.id, art.artist, alb.album, lab.label, cat.catalogue_number, 
                       fmt.physical_format_type, yr.release_year AS original_year, m.this_release_year,
                       m.this_release_duration, m.duration_less_bonus, m.side_change_point, 
                       m.average_dynamic_range, loc.storage_location,
                       m.notes_1, m.notes_2, m.notes_3,
                       yn.yes_no AS retail_disc, 
                       b1.disc_brand AS cdr_brand, 
                       cc.cdr_code, 
                       b2.disc_brand AS dvdr_brand, 
                       dc.bdr_dvdr_code, 
                       m.disc_creation_date, 
                       dwd.disc_writing_device
                FROM master_release_entry m 
                LEFT JOIN lookup_artist art ON m.artist_id = art.id 
                LEFT JOIN lookup_album alb ON m.album_id = alb.album_id 
                LEFT JOIN lookup_label lab ON m.label_id = lab.id
                LEFT JOIN lookup_catalogue_no cat ON m.catalogue_no_id = cat.id
                LEFT JOIN lookup_physical_format_type fmt ON m.physical_format_type_id = fmt.id
                LEFT JOIN lookup_original_release_year yr ON m.original_release_year_id = yr.id
                LEFT JOIN lookup_storage_location loc ON m.storage_location_id = loc.id
                LEFT JOIN lookup_yes_no yn ON m.retail_disc_id = yn.id
                LEFT JOIN lookup_disc_brand b1 ON m.cdr_brand_id = b1.id
                LEFT JOIN lookup_cdr_code cc ON m.cdr_code_id = cc.id1
                LEFT JOIN lookup_disc_brand b2 ON m.dvdr_brand_id = b2.id
                LEFT JOIN lookup_bdr_dvdr_code dc ON m.dvdr_code_id = dc.id
                LEFT JOIN lookup_disc_writing_device dwd ON m.disc_writing_device_id = dwd.id
                WHERE m.id = %s
            """
            cursor.execute(query, (sid,))
            result = cursor.fetchone()

            ov_query = """
                SELECT ov.id, b.bit_depth, s.sample_rate, df.digital_format_type, 
                       y.release_year, l.label, c.catalogue_number, 
                       pft.physical_format_type, ov.duration, ov.average_dynamic_range, 
                       yn.yes_no AS booklet, ov.individual_comment, loc.storage_location
                FROM other_version_entry ov
                LEFT JOIN lookup_bit_depth b ON ov.bit_depth_id = b.id
                LEFT JOIN lookup_sample_rate s ON ov.sample_rate_id = s.id
                LEFT JOIN lookup_digital_format_type df ON ov.digital_format_type_id = df.id
                LEFT JOIN lookup_original_release_year y ON ov.this_release_year_id = y.id
                LEFT JOIN lookup_label l ON ov.label_id = l.id
                LEFT JOIN lookup_catalogue_no c ON ov.catalogue_no_id = c.id
                LEFT JOIN lookup_physical_format_type pft ON ov.physical_format_type_id = pft.id
                LEFT JOIN lookup_yes_no yn ON ov.booklet_available_id = yn.id
                LEFT JOIN lookup_storage_location loc ON ov.storage_location_id = loc.id
                WHERE ov.master_release_entry_id = %s
            """
            cursor.execute(ov_query, (sid,))
            other_versions = cursor.fetchall()

            int_query = """
                SELECT log.id, log.interaction_date, it.interaction_type, 
                       cat.catalogue_number, pft.physical_format_type, 
                       bd.bit_depth, sr.sample_rate, log.individual_comment
                FROM media_interaction_log log
                LEFT JOIN lookup_interaction_type it ON log.interaction_type_id = it.id
                LEFT JOIN lookup_catalogue_no cat ON log.catalogue_no_id = cat.id
                LEFT JOIN lookup_physical_format_type pft ON log.physical_format_type_id = pft.id
                LEFT JOIN lookup_bit_depth bd ON log.bit_depth_id = bd.id
                LEFT JOIN lookup_sample_rate sr ON log.sample_rate_id = sr.id
                WHERE log.master_release_entry_id = %s
                ORDER BY log.interaction_date DESC
            """
            cursor.execute(int_query, (sid,))
            interactions = cursor.fetchall()

    conn.close()
    return render_template('view_master.html', result=result, albums_list=albums_list, 
                           other_versions=other_versions, interactions=interactions)

# --- NAVIGATION ---
@app.route('/control_panel')
def control_panel_home():
    return render_template('control_panel_menu.html')

@app.route('/reports_labels')
def reports_labels_home():
    return render_template('reports_labels_menu.html')

# --- INLAY LABEL ROUTES ---
@app.route('/labels/inlay')
def label_inlay_selection():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT m.id, alb.album FROM master_release_entry m JOIN lookup_album alb ON m.album_id = alb.album_id ORDER BY alb.album ASC")
        masters = cursor.fetchall()
    conn.close()
    return render_template('label_inlay_selection.html', masters=masters)

@app.route('/labels/inlay/generate/<int:mid>')
def label_inlay_generate(mid):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT m.*, art.artist, alb.album, cat.catalogue_number, fmt.physical_format_type, lab.label, yr_orig.release_year AS original_year, br_cdr.disc_brand AS cdr_brand, cc.cdr_code, br_dvd.disc_brand AS dvdr_brand, yn_retail.yes_no AS retail_disc FROM master_release_entry m LEFT JOIN lookup_artist art ON m.artist_id = art.id LEFT JOIN lookup_album alb ON m.album_id = alb.album_id LEFT JOIN lookup_catalogue_no cat ON m.catalogue_no_id = cat.id LEFT JOIN lookup_physical_format_type fmt ON m.physical_format_type_id = fmt.id LEFT JOIN lookup_label lab ON m.label_id = lab.id LEFT JOIN lookup_original_release_year yr_orig ON m.original_release_year_id = yr_orig.id LEFT JOIN lookup_disc_brand br_cdr ON m.cdr_brand_id = br_cdr.id LEFT JOIN lookup_cdr_code cc ON m.cdr_code_id = cc.id1 LEFT JOIN lookup_disc_brand br_dvd ON m.dvdr_brand_id = br_dvd.id LEFT JOIN lookup_yes_no yn_retail ON m.retail_disc_id = yn_retail.id WHERE m.id = %s", (mid,))
        master = cursor.fetchone()
        cursor.execute("SELECT ov.*, bd.bit_depth, sr.sample_rate, df.digital_format_type, lab.label, cat.catalogue_number, yr.release_year AS this_release_year, fmt.physical_format_type, yn_book.yes_no AS booklet_available FROM other_version_entry ov LEFT JOIN lookup_bit_depth bd ON ov.bit_depth_id = bd.id LEFT JOIN lookup_sample_rate sr ON ov.sample_rate_id = sr.id LEFT JOIN lookup_digital_format_type df ON ov.digital_format_type_id = df.id LEFT JOIN lookup_label lab ON ov.label_id = lab.id LEFT JOIN lookup_catalogue_no cat ON ov.catalogue_no_id = cat.id LEFT JOIN lookup_original_release_year yr ON ov.this_release_year_id = yr.id LEFT JOIN lookup_physical_format_type fmt ON ov.physical_format_type_id = fmt.id LEFT JOIN lookup_yes_no yn_book ON ov.booklet_available_id = yn_book.id WHERE ov.master_release_entry_id = %s", (mid,))
        versions = cursor.fetchall()
    conn.close()
    return render_template('label_inlay_print.html', m=master, versions=versions)

# --- CONTROL PANEL ROUTES (MATCHED TO TREE) ---
@app.route('/control_panel/artists', methods=['GET', 'POST'])
def manage_artists():
    conn = get_db_connection()
    if request.method == 'POST':
        with conn.cursor() as cur:
            cur.execute("INSERT INTO lookup_artist (artist) VALUES (%s)", (request.form.get('artist'),))
            conn.commit()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM lookup_artist ORDER BY artist ASC")
        data = cur.fetchall()
    conn.close()
    return render_template('manage_artists.html', data=data)

@app.route('/control_panel/albums', methods=['GET', 'POST'])
def manage_albums():
    conn = get_db_connection()
    if request.method == 'POST':
        with conn.cursor() as cur:
            cur.execute("INSERT INTO lookup_album (album) VALUES (%s)", (request.form.get('album'),))
            conn.commit()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM lookup_album ORDER BY album ASC")
        data = cur.fetchall()
    conn.close()
    return render_template('manage_albums.html', data=data)

@app.route('/control_panel/labels', methods=['GET', 'POST'])
def manage_labels():
    conn = get_db_connection()
    if request.method == 'POST':
        with conn.cursor() as cur:
            cur.execute("INSERT INTO lookup_label (label) VALUES (%s)", (request.form.get('label'),))
            conn.commit()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM lookup_label ORDER BY label ASC")
        data = cur.fetchall()
    conn.close()
    return render_template('manage_labels.html', data=data)

@app.route('/control_panel/catalogue_numbers', methods=['GET', 'POST'])
def manage_catalogue_numbers():
    conn = get_db_connection()
    if request.method == 'POST':
        with conn.cursor() as cur:
            cur.execute("INSERT INTO lookup_catalogue_no (catalogue_number) VALUES (%s)", (request.form.get('cat_no'),))
            conn.commit()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM lookup_catalogue_no ORDER BY catalogue_number ASC")
        data = cur.fetchall()
    conn.close()
    return render_template('manage_catalogue_numbers.html', data=data)

@app.route('/control_panel/locations', methods=['GET', 'POST'])
def manage_locations():
    conn = get_db_connection()
    if request.method == 'POST':
        with conn.cursor() as cur:
            cur.execute("INSERT INTO lookup_storage_location (storage_location) VALUES (%s)", (request.form.get('location'),))
            conn.commit()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM lookup_storage_location ORDER BY storage_location ASC")
        data = cur.fetchall()
    conn.close()
    return render_template('manage_locations.html', data=data)

@app.route('/control_panel/media_specs')
def manage_media_specs():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM lookup_bit_depth"); bits = cur.fetchall()
        cur.execute("SELECT * FROM lookup_sample_rate"); rates = cur.fetchall()
        cur.execute("SELECT * FROM lookup_digital_format_type"); digi = cur.fetchall()
        cur.execute("SELECT * FROM lookup_physical_format_type"); phys = cur.fetchall()
    conn.close()
    return render_template('manage_media_specs.html', bits=bits, rates=rates, digital=digi, physical=phys)

# --- REPORTS (MATCHED TO TREE) ---
@app.route('/reports/top_100')
def report_top_100():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        query = """
            SELECT art.artist, alb.album, COUNT(log.id) as play_count
            FROM media_interaction_log log
            JOIN master_release_entry m ON log.master_release_entry_id = m.id
            JOIN lookup_artist art ON m.artist_id = art.id
            JOIN lookup_album alb ON m.album_id = alb.album_id
            WHERE log.interaction_type_id = 1
            GROUP BY art.artist, alb.album
            ORDER BY play_count DESC LIMIT 100
        """
        cursor.execute(query)
        data = cursor.fetchall()
    conn.close()
    return render_template('report_top_listened.html', data=data, title="TOP 100 PLAYED ALBUMS")

@app.route('/reports/unplayed')
def report_unplayed():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        query = "SELECT art.artist, alb.album FROM master_release_entry m JOIN lookup_artist art ON m.artist_id = art.id JOIN lookup_album alb ON m.album_id = alb.album_id LEFT JOIN media_interaction_log log ON m.id = log.master_release_entry_id AND log.interaction_type_id = 1 WHERE log.id IS NULL ORDER BY art.artist, alb.album"
        cursor.execute(query)
        data = cursor.fetchall()
    conn.close()
    return render_template('report_unplayed.html', data=data)

@app.route('/reports/by_artist', methods=['GET', 'POST'])
def report_by_artist():
    conn = get_db_connection()
    selected_artist_id = request.form.get('artist_id')
    data, artists = [], []
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, artist FROM lookup_artist ORDER BY artist ASC")
        artists = cursor.fetchall()
        if selected_artist_id:
            cursor.execute("SELECT art.artist, alb.album, cat.catalogue_number, fmt.physical_format_type FROM master_release_entry m JOIN lookup_artist art ON m.artist_id = art.id JOIN lookup_album alb ON m.album_id = alb.album_id LEFT JOIN lookup_catalogue_no cat ON m.catalogue_no_id = cat.id LEFT JOIN lookup_physical_format_type fmt ON m.physical_format_type_id = fmt.id WHERE art.id = %s ORDER BY alb.album ASC", (selected_artist_id,))
            data = cursor.fetchall()
    conn.close()
    return render_template('report_by_artist.html', data=data, artists=artists, selected_id=selected_artist_id)

# --- INTERACTIONS ---
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

@app.route('/api/get_album_name')
def get_album_name():
    mid = request.args.get('id'); conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT a.album FROM lookup_album a JOIN master_release_entry m ON a.album_id = m.album_id WHERE m.id = %s", (mid,))
        res = cursor.fetchone()
    conn.close()
    return jsonify({'album': res['album'] if res else 'ID NOT FOUND'})

@app.route('/control_panel/interactions/save', methods=['POST'])
def save_interaction():
    d = request.form; conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM lookup_catalogue_no WHERE catalogue_number = %s", (d.get('cat_number'),))
        res = cur.fetchone(); cat_id = res['id'] if res else None
        v = (d.get('master_id'), d.get('interaction_date'), d.get('interaction_type'), cat_id, d.get('format_id'), d.get('bit_id') or None, d.get('sample_id') or None, d.get('comment'))
        cur.execute("INSERT INTO media_interaction_log (master_release_entry_id, interaction_date, interaction_type_id, catalogue_no_id, physical_format_type_id, bit_depth_id, sample_rate_id, individual_comment) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", v)
        conn.commit()
    conn.close(); flash("Interaction Logged!", "success"); return redirect(url_for('manage_interactions'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
