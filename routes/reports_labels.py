from flask import render_template, request
from database import get_db_connection

def parse_id_list(id_string):
    """Helper to turn '1-3, 5' into [1, 2, 3, 5]"""
    result = []
    if not id_string: return result
    for part in id_string.replace(' ', '').split(','):
        if '-' in part:
            try:
                start, end = part.split('-')
                result.extend(range(int(start), int(end) + 1))
            except ValueError: continue
        elif part.isdigit():
            result.append(int(part))
    return result

def reports_home_func():
    return render_template('reports_labels_menu.html')

def label_inlay_selection_func():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT m.id, art.artist, alb.album 
            FROM master_release_entry m 
            JOIN lookup_artist art ON m.artist_id = art.id 
            JOIN lookup_album alb ON m.album_id = alb.album_id 
            ORDER BY alb.album ASC
        """)
        masters = cursor.fetchall()
    conn.close()
    return render_template('label_inlay_selection.html', masters=masters)

def label_storage_selection_func():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT m.id, art.artist, alb.album 
            FROM master_release_entry m 
            JOIN lookup_artist art ON m.artist_id = art.id 
            JOIN lookup_album alb ON m.album_id = alb.album_id 
            ORDER BY alb.album ASC
        """)
        masters = cursor.fetchall()
    conn.close()
    return render_template('label_storage_selection.html', masters=masters)

def generate_storage_label_func(master_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        query = """
            SELECT m.id, art.artist, alb.album, cat.catalogue_number, loc.storage_location,
                   fmt.physical_format_type, yr_orig.release_year AS original_year, 
                   m.this_release_year, m.this_release_duration, m.duration_less_bonus
            FROM master_release_entry m
            JOIN lookup_artist art ON m.artist_id = art.id
            JOIN lookup_album alb ON m.album_id = alb.album_id
            LEFT JOIN lookup_catalogue_no cat ON m.catalogue_no_id = cat.id
            LEFT JOIN lookup_storage_location loc ON m.storage_location_id = loc.id
            LEFT JOIN lookup_physical_format_type fmt ON m.physical_format_type_id = fmt.id
            LEFT JOIN lookup_original_release_year yr_orig ON m.original_release_year_id = yr_orig.id
            WHERE m.id = %s
        """
        cursor.execute(query, (master_id,))
        data = cursor.fetchone()
    conn.close()
    return render_template('label_storage_print.html', labels=[data] if data else [], mode='MASTER')

def generate_inlay_func(master_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        master_query = """
            SELECT 
                m.id, art.artist, alb.album, cat.catalogue_number,
                fmt.physical_format_type, lab.label, m.average_dynamic_range,
                yn_retail.yes_no AS retail_disc, yr_orig.release_year AS original_year,
                m.this_release_duration, br_cdr.disc_brand AS cdr_brand, cc.cdr_code,
                m.this_release_year, m.duration_less_bonus, br_dvd.disc_brand AS dvdr_brand,
                m.disc_creation_date, m.side_change_point, m.notes_1, m.notes_2, m.notes_3
            FROM master_release_entry m
            LEFT JOIN lookup_artist art ON m.artist_id = art.id
            LEFT JOIN lookup_album alb ON m.album_id = alb.album_id
            LEFT JOIN lookup_catalogue_no cat ON m.catalogue_no_id = cat.id
            LEFT JOIN lookup_physical_format_type fmt ON m.physical_format_type_id = fmt.id
            LEFT JOIN lookup_label lab ON m.label_id = lab.id
            LEFT JOIN lookup_yes_no yn_retail ON m.retail_disc_id = yn_retail.id
            LEFT JOIN lookup_original_release_year yr_orig ON m.original_release_year_id = yr_orig.id
            LEFT JOIN lookup_disc_brand br_cdr ON m.cdr_brand_id = br_cdr.id
            LEFT JOIN lookup_cdr_code cc ON m.cdr_code_id = cc.id1
            LEFT JOIN lookup_disc_brand br_dvd ON m.dvdr_brand_id = br_dvd.id
            WHERE m.id = %s
        """
        cursor.execute(master_query, (master_id,))
        master_data = cursor.fetchone()

        other_query = """
            SELECT 
                ov.id, bd.bit_depth, sr.sample_rate, df.digital_format_type,
                l.label, c.catalogue_number, yr.release_year AS this_release_year, 
                pf.physical_format_type, ov.duration, ov.average_dynamic_range, 
                yn.yes_no AS booklet_available, ov.individual_comment
            FROM other_version_entry ov
            LEFT JOIN lookup_bit_depth bd ON ov.bit_depth_id = bd.id
            LEFT JOIN lookup_sample_rate sr ON ov.sample_rate_id = sr.id
            LEFT JOIN lookup_digital_format_type df ON ov.digital_format_type_id = df.id
            LEFT JOIN lookup_label l ON ov.label_id = l.id
            LEFT JOIN lookup_catalogue_no c ON ov.catalogue_no_id = c.id
            LEFT JOIN lookup_original_release_year yr ON ov.this_release_year_id = yr.id
            LEFT JOIN lookup_physical_format_type pf ON ov.physical_format_type_id = pf.id
            LEFT JOIN lookup_yes_no yn ON ov.booklet_available_id = yn.id
            WHERE ov.master_release_entry_id = %s
        """
        cursor.execute(other_query, (master_id,))
        other_versions = cursor.fetchall()

    conn.close()
    return render_template('label_inlay_print.html', m=master_data, versions=other_versions)

def storage_master_batch_func():
    conn = get_db_connection()
    if request.method == 'POST':
        ids = parse_id_list(request.form.get('id_list', ''))
    else:
        single_id = request.args.get('id')
        ids = [single_id] if single_id else []

    if not ids: return "No Master IDs provided", 400

    with conn.cursor() as cursor:
        query = """
            SELECT m.id, art.artist, alb.album, cat.catalogue_number, loc.storage_location,
                   fmt.physical_format_type, yr_orig.release_year AS original_year, 
                   m.this_release_year, m.this_release_duration, m.duration_less_bonus
            FROM master_release_entry m
            JOIN lookup_artist art ON m.artist_id = art.id
            JOIN lookup_album alb ON m.album_id = alb.album_id
            LEFT JOIN lookup_catalogue_no cat ON m.catalogue_no_id = cat.id
            LEFT JOIN lookup_storage_location loc ON m.storage_location_id = loc.id
            LEFT JOIN lookup_physical_format_type fmt ON m.physical_format_type_id = fmt.id
            LEFT JOIN lookup_original_release_year yr_orig ON m.original_release_year_id = yr_orig.id
            WHERE m.id IN %s ORDER BY alb.album ASC
        """
        cursor.execute(query, (tuple(ids),))
        batch_data = cursor.fetchall()
    conn.close()
    return render_template('label_storage_print.html', labels=batch_data, mode='MASTER')

def storage_version_batch_func():
    conn = get_db_connection()
    # Logic to parse the text box (e.g., 101-105, 110)
    ids = parse_id_list(request.form.get('id_list', ''))
    if not ids: 
        return "NO VERSION IDS PROVIDED", 400

    with conn.cursor() as cursor:
        # This query follows your "OTHER VERSION REQUIRED FIELDS" map exactly
        query = """
            SELECT 
                ov.id, 
                art.artist, 
                alb.album, 
                cat.catalogue_number, 
                loc.storage_location,
                pf.physical_format_type, 
                yr_orig.release_year AS original_year,
                yr_this.release_year AS this_release_year, 
                ov.duration
            FROM other_version_entry ov
            JOIN master_release_entry m ON ov.master_release_entry_id = m.id
            JOIN lookup_artist art ON m.artist_id = art.id
            JOIN lookup_album alb ON m.album_id = alb.album_id
            LEFT JOIN lookup_catalogue_no cat ON ov.catalogue_no_id = cat.id
            LEFT JOIN lookup_storage_location loc ON ov.storage_location_id = loc.id
            LEFT JOIN lookup_physical_format_type pf ON ov.physical_format_type_id = pf.id
            LEFT JOIN lookup_original_release_year yr_orig ON m.original_release_year_id = yr_orig.id
            LEFT JOIN lookup_original_release_year yr_this ON ov.this_release_year_id = yr_this.id
            WHERE ov.id IN %s 
            ORDER BY alb.album ASC
        """
        cursor.execute(query, (tuple(ids),))
        batch_data = cursor.fetchall()
    conn.close()
    
    # Template expects 'labels' and 'mode'
    return render_template('label_storage_print.html', labels=batch_data, mode='VERSION')

def report_top_100_func():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # Aggregating play counts from the interaction log
        query = """
            SELECT art.artist, alb.album, COUNT(l.id) as play_count
            FROM media_interaction_log l
            JOIN master_release_entry m ON l.master_release_entry_id = m.id
            JOIN lookup_artist art ON m.artist_id = art.id
            JOIN lookup_album alb ON m.album_id = alb.album_id
            GROUP BY m.id 
            ORDER BY play_count DESC 
            LIMIT 100
        """
        cursor.execute(query)
        res = cursor.fetchall()
    conn.close()
    # Matches HTML: 'data' for the loop and 'title' for the header
    return render_template('report_top_listened.html', 
                           data=res, 
                           title="TOP 100 MOST PLAYED ALBUMS")

def report_unplayed_func():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # Finding Master IDs that do NOT exist in the media_interaction_log
        query = """
            SELECT art.artist, alb.album 
            FROM master_release_entry m
            JOIN lookup_artist art ON m.artist_id = art.id
            JOIN lookup_album alb ON m.album_id = alb.album_id
            LEFT JOIN media_interaction_log l ON m.id = l.master_release_entry_id
            WHERE l.id IS NULL
            ORDER BY art.artist ASC, alb.album ASC
        """
        cursor.execute(query)
        res = cursor.fetchall()
    conn.close()
    # Assuming unplayed template uses similar 'data' variable
    return render_template('report_unplayed.html', 
                           data=res, 
                           title="THE UNPLAYED GEMS")

def report_by_artist_func():
    conn = get_db_connection()
    selected_artist_id = request.form.get('artist_id')
    data, artists = [], []
    with conn.cursor() as cursor:
        # 1. Get the list of artists for the dropdown
        cursor.execute("SELECT id, artist FROM lookup_artist ORDER BY artist ASC")
        artists = cursor.fetchall()
        
        # 2. If an artist is selected, get their full release data
        if selected_artist_id:
            cursor.execute("""
                SELECT art.artist, alb.album, cat.catalogue_number, fmt.physical_format_type 
                FROM master_release_entry m 
                JOIN lookup_artist art ON m.artist_id = art.id 
                JOIN lookup_album alb ON m.album_id = alb.album_id 
                LEFT JOIN lookup_catalogue_no cat ON m.catalogue_no_id = cat.id 
                LEFT JOIN lookup_physical_format_type fmt ON m.physical_format_type_id = fmt.id 
                WHERE art.id = %s 
                ORDER BY alb.album ASC
            """, (selected_artist_id,))
            data = cursor.fetchall()
            
    conn.close()
    # Passing 'data' to match your template loop and 'selected_id' for the dropdown state
    return render_template('report_by_artist.html', 
                           data=data, 
                           artists=artists, 
                           selected_id=selected_artist_id,
                           title="ALBUMS BY ARTIST")
