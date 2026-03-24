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

# --- HELPER: ID RANGE PARSER ---
def parse_id_list(input_str):
    ids = set()
    if not input_str: return []
    parts = str(input_str).replace(' ', '').split(',')
    for part in parts:
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                ids.update(range(min(start, end), max(start, end) + 1))
            except ValueError: continue
        else:
            try:
                if part: ids.add(int(part))
            except ValueError: continue
    return sorted(list(ids))

@app.route('/')
def index():
    return render_template('index.html')

# --- API ENDPOINT: AUTO-POPULATE ALBUM NAME ---
@app.route('/api/get_album_name')
def get_album_name():
    master_id = request.args.get('id')
    if not master_id:
        return jsonify({'album': ''})
    
    conn = get_db_connection()
    with conn.cursor() as cursor:
        query = """
            SELECT alb.album 
            FROM master_release_entry m 
            JOIN lookup_album alb ON m.album_id = alb.album_id 
            WHERE m.id = %s
        """
        cursor.execute(query, (master_id,))
        result = cursor.fetchone()
    conn.close()
    
    return jsonify({'album': result['album'] if result else 'ID NOT FOUND'})

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

# --- REPORTS & LABELS ---
@app.route('/reports_labels')
def reports_labels_home():
    return render_template('reports_labels_menu.html')

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

@app.route('/labels/storage')
def label_storage_selection():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT m.id, alb.album FROM master_release_entry m JOIN lookup_album alb ON m.album_id = alb.album_id ORDER BY alb.album ASC")
        masters = cursor.fetchall()
    conn.close()
    return render_template('label_storage_selection.html', masters=masters)

@app.route('/labels/storage/master/batch', methods=['GET', 'POST'])
def print_master_batch():
    raw_input = request.form.get('id_list') or request.args.get('id')
    if not raw_input: return redirect(url_for('label_storage_selection'))
    id_list = parse_id_list(raw_input)
    conn = get_db_connection()
    with conn.cursor() as cursor:
        ph = ', '.join(['%s'] * len(id_list))
        query = f"SELECT m.id, art.artist, alb.album, cat.catalogue_number, fmt.physical_format_type, yr_orig.release_year AS original_year, m.this_release_year, m.this_release_duration, m.duration_less_bonus, loc.storage_location FROM master_release_entry m LEFT JOIN lookup_artist art ON m.artist_id = art.id LEFT JOIN lookup_album alb ON m.album_id = alb.album_id LEFT JOIN lookup_catalogue_no cat ON m.catalogue_no_id = cat.id LEFT JOIN lookup_physical_format_type fmt ON m.physical_format_type_id = fmt.id LEFT JOIN lookup_original_release_year yr_orig ON m.original_release_year_id = yr_orig.id LEFT JOIN lookup_storage_location loc ON m.storage_location_id = loc.id WHERE m.id IN ({ph}) ORDER BY FIELD(m.id, {ph})"
        cursor.execute(query, id_list + id_list)
        labels = cursor.fetchall()
    conn.close()
    return render_template('label_storage_print.html', labels=labels, mode='MASTER')

# --- CONTROL PANEL ---
@app.route('/control_panel')
def control_panel_home():
    return render_template('control_panel_menu.html')

# Artists
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

@app.route('/control_panel/artists/save', methods=['POST'])
def save_artist():
    artist_id = request.form.get('artist_id')
    name_val = request.form.get('artist_name')
    if name_val:
        conn = get_db_connection()
        with conn.cursor() as cur:
            if artist_id and artist_id.strip():
                cur.execute("UPDATE lookup_artist SET artist = %s WHERE id = %s", (name_val, artist_id))
            else:
                cur.execute("INSERT INTO lookup_artist (artist) VALUES (%s)", (name_val,))
            conn.commit()
        conn.close()
    return redirect(url_for('manage_artists'))

# Albums
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

@app.route('/control_panel/albums/save', methods=['POST'])
def save_album():
    album_id = request.form.get('album_id')
    name_val = request.form.get('album_name')
    if name_val:
        conn = get_db_connection()
        with conn.cursor() as cur:
            if album_id and album_id.strip():
                cur.execute("UPDATE lookup_album SET album = %s WHERE album_id = %s", (name_val, album_id))
            else:
                cur.execute("INSERT INTO lookup_album (album) VALUES (%s)", (name_val,))
            conn.commit()
        conn.close()
    return redirect(url_for('manage_albums'))

# Labels
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

@app.route('/control_panel/labels/save', methods=['POST'])
def save_label():
    label_id = request.form.get('label_id')
    name_val = request.form.get('label_name')
    if name_val:
        conn = get_db_connection()
        with conn.cursor() as cur:
            if label_id and label_id.strip():
                cur.execute("UPDATE lookup_label SET label = %s WHERE id = %s", (name_val, label_id))
            else:
                cur.execute("INSERT INTO lookup_label (label) VALUES (%s)", (name_val,))
            conn.commit()
        conn.close()
    return redirect(url_for('manage_labels'))

# Locations
@app.route('/control_panel/locations', methods=['GET', 'POST'])
def manage_locations():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, storage_location FROM lookup_storage_location ORDER BY storage_location ASC")
        l = cursor.fetchall()
    conn.close()
    return render_template('manage_locations.html', locations=l)

@app.route('/control_panel/locations/save', methods=['POST'])
def save_location():
    loc_id = request.form.get('loc_id')
    loc_name = request.form.get('loc_name')
    if loc_name:
        conn = get_db_connection()
        with conn.cursor() as cur:
            if loc_id and loc_id.strip():
                cur.execute("UPDATE lookup_storage_location SET storage_location = %s WHERE id = %s", (loc_name, loc_id))
            else:
                cur.execute("INSERT INTO lookup_storage_location (storage_location) VALUES (%s)", (loc_name,))
            conn.commit()
        conn.close()
    return redirect(url_for('manage_locations'))

# Media Specs
@app.route('/control_panel/media_specs')
def manage_media_specs():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, disc_brand FROM lookup_disc_brand ORDER BY disc_brand ASC"); b = cursor.fetchall()
        cursor.execute("SELECT id1 AS id, cdr_code FROM lookup_cdr_code ORDER BY cdr_code ASC"); c = cursor.fetchall()
        cursor.execute("SELECT id, bdr_dvdr_code FROM lookup_bdr_dvdr_code ORDER BY bdr_dvdr_code ASC"); d = cursor.fetchall()
    conn.close()
    return render_template('manage_media_specs.html', brands=b, cdr_codes=c, dvd_codes=d)

@app.route('/control_panel/media_specs/save', methods=['POST'])
def save_media_spec():
    spec_type = request.form.get('spec_type')
    item_id = request.form.get('item_id')
    item_val = request.form.get('item_value')
    if item_val:
        conn = get_db_connection()
        with conn.cursor() as cur:
            mapping = {
                'brand': ('lookup_disc_brand', 'disc_brand', 'id'),
                'cdr':   ('lookup_cdr_code', 'cdr_code', 'id1'),
                'dvd':   ('lookup_bdr_dvdr_code', 'bdr_dvdr_code', 'id')
            }
            table, col, id_col = mapping.get(spec_type)
            if item_id and item_id.strip():
                cur.execute(f"UPDATE {table} SET {col} = %s WHERE {id_col} = %s", (item_val, item_id))
            else:
                cur.execute(f"INSERT INTO {table} ({col}) VALUES (%s)", (item_val,))
            conn.commit()
        conn.close()
    return redirect(url_for('manage_media_specs'))

# Interactions
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
        cur.execute("SELECT id FROM lookup_catalogue_no WHERE catalogue_number = %s", (cat_no,))
        res = cur.fetchone()
        cat_id = res['id'] if res else None
        v = (d.get('master_id'), d.get('interaction_date'), d.get('interaction_type'), cat_id, d.get('format_id'), d.get('bit_id') or None, d.get('sample_id') or None, d.get('comment'))
        cur.execute("INSERT INTO media_interaction_log (master_release_entry_id, interaction_date, interaction_type_id, catalogue_no_id, physical_format_type_id, bit_depth_id, sample_rate_id, individual_comment) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", v)
        conn.commit()
    conn.close()
    flash("Interaction Logged!", "success")
    return redirect(url_for('manage_interactions'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
