from flask import render_template, request, redirect, url_for, flash, jsonify
from database import get_db_connection

def get_album_name_func():
    master_id = request.args.get('id')
    if not master_id: return jsonify({'album': ''})
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT alb.album FROM master_release_entry m JOIN lookup_album alb ON m.album_id = alb.album_id WHERE m.id = %s", (master_id,))
        result = cursor.fetchone()
    conn.close()
    return jsonify({'album': result['album'] if result else 'ID NOT FOUND'})

def control_panel_home_func():
    return render_template('control_panel_menu.html')

# --- ARTISTS ---
def manage_artists_func():
    conn, res, q = get_db_connection(), [], request.form.get('artist_search', '')
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, artist FROM lookup_artist ORDER BY artist ASC")
        all_art = cursor.fetchall()
        if request.method == 'POST' and q:
            cursor.execute("SELECT id, artist FROM lookup_artist WHERE artist LIKE %s", (f"%{q}%",))
            res = cursor.fetchall()
    conn.close()
    return render_template('manage_artists.html', all_artists=all_art, search_results=res, search_query=q)

def save_artist_func():
    artist_id, name_val = request.form.get('artist_id'), request.form.get('artist_name')
    if name_val:
        conn = get_db_connection()
        with conn.cursor() as cur:
            if artist_id and artist_id.strip():
                cur.execute("UPDATE lookup_artist SET artist = %s WHERE id = %s", (name_val, artist_id))
                msg = f"SUCCESSFULLY UPDATED ARTIST: {name_val}"
            else:
                cur.execute("INSERT INTO lookup_artist (artist) VALUES (%s)", (name_val,))
                msg = f"SUCCESSFULLY ADDED ARTIST: {name_val}"
            conn.commit()
            flash(msg.upper(), "success")
        conn.close()
    return redirect(url_for('manage_artists'))

# --- ALBUMS ---
def manage_albums_func():
    conn, res, q = get_db_connection(), [], request.form.get('album_search', '')
    with conn.cursor() as cursor:
        cursor.execute("SELECT album_id AS id, album FROM lookup_album ORDER BY album ASC")
        all_alb = cursor.fetchall()
        if request.method == 'POST' and q:
            cursor.execute("SELECT album_id AS id, album FROM lookup_album WHERE album LIKE %s", (f"%{q}%",))
            res = cursor.fetchall()
    conn.close()
    return render_template('manage_albums.html', all_albums=all_alb, search_results=res, search_query=q)

def save_album_func():
    album_id, name_val = request.form.get('album_id'), request.form.get('album_name')
    if name_val:
        conn = get_db_connection()
        with conn.cursor() as cur:
            if album_id and album_id.strip():
                cur.execute("UPDATE lookup_album SET album = %s WHERE album_id = %s", (name_val, album_id))
                msg = f"SUCCESSFULLY UPDATED ALBUM: {name_val}"
            else:
                cur.execute("INSERT INTO lookup_album (album) VALUES (%s)", (name_val,))
                msg = f"SUCCESSFULLY ADDED ALBUM: {name_val}"
            conn.commit()
            flash(msg.upper(), "success")
        conn.close()
    return redirect(url_for('manage_albums'))

# --- LABELS ---
def manage_labels_func():
    conn, res, q = get_db_connection(), [], request.form.get('label_search', '')
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, label FROM lookup_label ORDER BY label ASC")
        all_lab = cursor.fetchall()
        if request.method == 'POST' and q:
            cursor.execute("SELECT id, label FROM lookup_label WHERE label LIKE %s", (f"%{q}%",))
            res = cursor.fetchall()
    conn.close()
    return render_template('manage_labels.html', all_labels=all_lab, search_results=res, search_query=q)

def save_label_func():
    label_id, name_val = request.form.get('label_id'), request.form.get('label_name')
    if name_val:
        conn = get_db_connection()
        with conn.cursor() as cur:
            if label_id and label_id.strip():
                cur.execute("UPDATE lookup_label SET label = %s WHERE id = %s", (name_val, label_id))
                msg = f"SUCCESSFULLY UPDATED LABEL: {name_val}"
            else:
                cur.execute("INSERT INTO lookup_label (label) VALUES (%s)", (name_val,))
                msg = f"SUCCESSFULLY ADDED LABEL: {name_val}"
            conn.commit()
            flash(msg.upper(), "success")
        conn.close()
    return redirect(url_for('manage_labels'))

# --- LOCATIONS ---
def manage_locations_func():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, storage_location FROM lookup_storage_location ORDER BY storage_location ASC")
        l = cursor.fetchall()
    conn.close()
    return render_template('manage_locations.html', locations=l)

def save_location_func():
    loc_id, loc_name = request.form.get('loc_id'), request.form.get('loc_name')
    if loc_name:
        conn = get_db_connection()
        with conn.cursor() as cur:
            if loc_id and loc_id.strip():
                cur.execute("UPDATE lookup_storage_location SET storage_location = %s WHERE id = %s", (loc_name, loc_id))
                msg = f"SUCCESSFULLY UPDATED LOCATION: {loc_name}"
            else:
                cur.execute("INSERT INTO lookup_storage_location (storage_location) VALUES (%s)", (loc_name,))
                msg = f"SUCCESSFULLY ADDED LOCATION: {loc_name}"
            conn.commit()
            flash(msg.upper(), "success")
        conn.close()
    return redirect(url_for('manage_locations'))

# --- CATALOGUE NUMBERS ---
def manage_catalogue_numbers_func():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, catalogue_number FROM lookup_catalogue_no ORDER BY catalogue_number ASC")
        cat_nos = cursor.fetchall()
    conn.close()
    return render_template('manage_catalogue_numbers.html', cat_nos=cat_nos)

def save_catalogue_number_func():
    cat_id, cat_val = request.form.get('cat_id'), request.form.get('cat_val')
    if cat_val:
        conn = get_db_connection()
        with conn.cursor() as cur:
            if cat_id and cat_id.strip():
                cur.execute("UPDATE lookup_catalogue_no SET catalogue_number = %s WHERE id = %s", (cat_val, cat_id))
                msg = f"SUCCESSFULLY UPDATED CATALOGUE #: {cat_val}"
            else:
                cur.execute("INSERT INTO lookup_catalogue_no (catalogue_number) VALUES (%s)", (cat_val,))
                msg = f"SUCCESSFULLY ADDED CATALOGUE #: {cat_val}"
            conn.commit()
            flash(msg.upper(), "success")
        conn.close()
    return redirect(url_for('manage_catalogue_numbers'))

# --- INTERACTIONS ---
def manage_interactions_func():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id, interaction_type FROM lookup_interaction_type ORDER BY interaction_type ASC"); t = cur.fetchall()
        cur.execute("SELECT id, catalogue_number FROM lookup_catalogue_no ORDER BY catalogue_number ASC"); c = cur.fetchall()
        cur.execute("SELECT id, physical_format_type FROM lookup_physical_format_type ORDER BY physical_format_type ASC"); f = cur.fetchall()
        cur.execute("SELECT id, bit_depth FROM lookup_bit_depth ORDER BY bit_depth ASC"); b = cur.fetchall()
        cur.execute("SELECT id, sample_rate FROM lookup_sample_rate ORDER BY sample_rate ASC"); s = cur.fetchall()
    conn.close()
    return render_template('manage_interactions.html', types=t, cats=c, formats=f, bits=b, rates=s)

def save_interaction_func():
    d = request.form
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM lookup_catalogue_no WHERE catalogue_number = %s", (d.get('cat_number'),))
        res = cur.fetchone()
        cat_id = res['id'] if res else None
        v = (d.get('master_id'), d.get('interaction_date'), d.get('interaction_type'), cat_id, 
             d.get('format_id'), d.get('bit_id') or None, d.get('sample_id') or None, d.get('comment'))
        cur.execute("""INSERT INTO media_interaction_log 
                    (master_release_entry_id, interaction_date, interaction_type_id, catalogue_no_id, 
                    physical_format_type_id, bit_depth_id, sample_rate_id, individual_comment) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""", v)
        conn.commit()
        flash("SUCCESSFULLY LOGGED INTERACTION", "success")
    conn.close()
    return redirect(url_for('manage_interactions'))

# --- MEDIA SPECS ---
def manage_media_specs_func():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, disc_brand FROM lookup_disc_brand ORDER BY disc_brand ASC"); b = cursor.fetchall()
        cursor.execute("SELECT id1 AS id, cdr_code FROM lookup_cdr_code ORDER BY cdr_code ASC"); c = cursor.fetchall()
        cursor.execute("SELECT id, bdr_dvdr_code FROM lookup_bdr_dvdr_code ORDER BY bdr_dvdr_code ASC"); d = cursor.fetchall()
    conn.close()
    return render_template('manage_media_specs.html', brands=b, cdr_codes=c, dvd_codes=d)

def save_media_spec_func():
    spec_type, item_id, item_val = request.form.get('spec_type'), request.form.get('item_id'), request.form.get('item_value')
    if item_val:
        conn = get_db_connection()
        with conn.cursor() as cur:
            mapping = {'brand': ('lookup_disc_brand', 'disc_brand', 'id'), 'cdr': ('lookup_cdr_code', 'cdr_code', 'id1'), 'dvd': ('lookup_bdr_dvdr_code', 'bdr_dvdr_code', 'id')}
            table, col, id_col = mapping.get(spec_type)
            if item_id and item_id.strip():
                cur.execute(f"UPDATE {table} SET {col} = %s WHERE {id_col} = %s", (item_val, item_id))
                msg = f"SUCCESSFULLY UPDATED {spec_type}: {item_val}"
            else:
                cur.execute(f"INSERT INTO {table} ({col}) VALUES (%s)", (item_val,))
                msg = f"SUCCESSFULLY ADDED {spec_type}: {item_val}"
            conn.commit()
            flash(msg.upper(), "success")
        conn.close()
    return redirect(url_for('manage_media_specs'))
