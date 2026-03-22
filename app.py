from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import pymysql

app = Flask(__name__)
app.secret_key = "secret_archive_key"

# Database Configuration (Using pymysql as per your last night's sync)
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

# --- MASTER VIEWER (Combined Core Logic) ---
@app.route('/view_master')
def view_master():
    sid = request.args.get('id')
    conn = get_db_connection()
    result, albums_list, other_versions, interactions = None, [], [], []
    with conn.cursor() as cursor:
        cursor.execute("SELECT m.id, a.album FROM master_release_entry m JOIN lookup_album a ON m.album_id = a.album_id ORDER BY a.album ASC")
        albums_list = cursor.fetchall()
        
        if sid:
            # Main Master Query
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

            # Other Versions Query
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

            # Interactions Query
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

# --- CONTROL PANEL NAVIGATION ---
@app.route('/control_panel')
def control_panel_home():
    return render_template('control_panel_menu.html')

@app.route('/control_panel/artists', methods=['GET', 'POST'])
def manage_artists():
    conn, res, q = get_db_connection(), [], request.form.get('artist_search', '')
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, artist FROM lookup_artist ORDER BY artist ASC")
        all_art = cursor.fetchall()
        if request.method == 'POST' and q:
            cursor.execute("SELECT id, artist FROM lookup_artist WHERE artist LIKE %s", (f"%{q}%",))
            res = cursor.fetchall()
    conn.close()
    return render_template('manage_artists.html', all_artists=all_art, search_results=res, search_query=q)

@app.route('/control_panel/albums', methods=['GET', 'POST'])
def manage_albums():
    conn, res, q = get_db_connection(), [], request.form.get('album_search', '')
    with conn.cursor() as cursor:
        cursor.execute("SELECT album_id AS id, album FROM lookup_album ORDER BY album ASC")
        all_alb = cursor.fetchall()
        if request.method == 'POST' and q:
            cursor.execute("SELECT album_id AS id, album FROM lookup_album WHERE album LIKE %s", (f"%{q}%",))
            res = cursor.fetchall()
    conn.close()
    return render_template('manage_albums.html', all_albums=all_alb, search_results=res, search_query=q)

@app.route('/control_panel/labels', methods=['GET', 'POST'])
def manage_labels():
    conn, res, q = get_db_connection(), [], request.form.get('label_search', '')
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, label FROM lookup_label ORDER BY label ASC")
        all_lab = cursor.fetchall()
        if request.method == 'POST' and q:
            cursor.execute("SELECT id, label FROM lookup_label WHERE label LIKE %s", (f"%{q}%",))
            res = cursor.fetchall()
    conn.close()
    return render_template('manage_labels.html', all_labels=all_lab, search_results=res, search_query=q)

@app.route('/control_panel/catalogue_numbers')
def manage_catalogue_numbers():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, catalogue_number FROM lookup_catalogue_no ORDER BY catalogue_number ASC")
        c = cursor.fetchall()
    conn.close()
    return render_template('manage_catalogue_numbers.html', cat_nos=c)

@app.route('/control_panel/locations')
def manage_locations():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, storage_location FROM lookup_storage_location ORDER BY storage_location ASC")
        l = cursor.fetchall()
    conn.close()
    return render_template('manage_locations.html', locations=l)

@app.route('/control_panel/media_specs')
def manage_media_specs():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, disc_brand FROM lookup_disc_brand ORDER BY disc_brand ASC")
        b = cursor.fetchall()
        cursor.execute("SELECT id1 AS id, cdr_code FROM lookup_cdr_code ORDER BY cdr_code ASC")
        c = cursor.fetchall()
        cursor.execute("SELECT id, bdr_dvdr_code FROM lookup_bdr_dvdr_code ORDER BY bdr_dvdr_code ASC")
        d = cursor.fetchall()
    conn.close()
    return render_template('manage_media_specs.html', brands=b, cdr_codes=c, dvd_codes=d)

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
    mid = request.args.get('id')
    conn = get_db_connection()
    with conn.cursor() as cursor:
        query = "SELECT a.album FROM lookup_album a JOIN master_release_entry m ON a.album_id = m.album_id WHERE m.id = %s"
        cursor.execute(query, (mid,))
        res = cursor.fetchone()
    conn.close()
    return jsonify({'album': res['album'] if res else 'ID NOT FOUND'})

@app.route('/control_panel/interactions/save', methods=['POST'])
def save_interaction():
    d = request.form
    cat_no = d.get('cat_number')
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM lookup_catalogue_no WHERE catalogue_number = %s", (cat_no,))
        res = cur.fetchone()
        cat_id = res['id'] if res else None
        v = (d.get('master_id'), d.get('interaction_date'), d.get('interaction_type'), cat_id, d.get('format_id'), d.get('bit_id') or None, d.get('sample_id') or None, d.get('comment'))
        cur.execute("INSERT INTO media_interaction_log (master_release_entry_id, interaction_date, interaction_type_id, catalogue_no_id, physical_format_type_id, bit_depth_id, sample_rate_id, individual_comment) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", v)
        conn.commit()
    conn.close()
    flash("Interaction Logged!", "success")
    return redirect(url_for('manage_interactions'))

# --- NEW REPORT ROUTE ---
@app.route('/reports/top_listened')
def report_top_listened():
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
            ORDER BY play_count DESC
            LIMIT 10
        """
        cursor.execute(query)
        data = cursor.fetchall()
    conn.close()
    return render_template('report_top_listened.html', data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
