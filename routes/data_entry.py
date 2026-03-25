from flask import render_template, request, redirect, url_for, flash, jsonify
from database import get_db_connection
from datetime import date, timedelta

# 1. API FOR THE 'LOAD' BUTTON (Sandboxed here)
def get_master_details_func():
    m_id = request.args.get('id')
    if not m_id:
        return jsonify({"error": "No ID provided"}), 400

    conn = get_db_connection()
    with conn.cursor() as cursor:
        # Fetching everything from the master table
        cursor.execute("SELECT * FROM master_release_entry WHERE id = %s", (m_id,))
        result = cursor.fetchone()

        if result:
            # FIX: Convert all 'non-serializable' objects to strings
            for key, value in result.items():
                # Convert Dates (YYYY-MM-DD)
                if isinstance(value, date):
                    result[key] = value.strftime('%Y-%m-%d')
                # FIX: Convert Timedelta/Duration (00:00:00)
                elif isinstance(value, timedelta):
                    # This turns the time object into a clean string like "01:15:00"
                    total_seconds = int(value.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    result[key] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

            # Fetch names for the header display verify
            cursor.execute("""
                SELECT 
                    (SELECT artist FROM lookup_artist WHERE id = %s) as artist,
                    (SELECT album FROM lookup_album WHERE album_id = %s) as album
            """, (result['artist_id'], result['album_id']))
            names = cursor.fetchone()
            if names:
                result.update(names)

    conn.close()
    if result:
        return jsonify(result)
    return jsonify({"error": "Not found"}), 404

# 2. MAIN MENU
def data_entry_home_func():
    return render_template('data_entry_menu.html')

# 3. LOAD THE FORM (GET)
def manage_master_func():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, artist FROM lookup_artist ORDER BY artist")
        artists = cursor.fetchall()
        cursor.execute("SELECT album_id, album FROM lookup_album ORDER BY album")
        albums = cursor.fetchall()
        cursor.execute("SELECT id, label FROM lookup_label ORDER BY label")
        labels = cursor.fetchall()
        cursor.execute("SELECT id, catalogue_number FROM lookup_catalogue_no ORDER BY catalogue_number")
        cats = cursor.fetchall()
        cursor.execute("SELECT id, physical_format_type FROM lookup_physical_format_type ORDER BY physical_format_type")
        formats = cursor.fetchall()
        cursor.execute("SELECT id, release_year FROM lookup_original_release_year ORDER BY release_year DESC")
        years = cursor.fetchall()
        cursor.execute("SELECT id, yes_no FROM lookup_yes_no")
        yn = cursor.fetchall()
        cursor.execute("SELECT id, disc_brand FROM lookup_disc_brand ORDER BY disc_brand")
        brands = cursor.fetchall()
        cursor.execute("SELECT id1, cdr_code FROM lookup_cdr_code ORDER BY cdr_code")
        cdr_codes = cursor.fetchall()
        cursor.execute("SELECT id, bdr_dvdr_code FROM lookup_bdr_dvdr_code ORDER BY bdr_dvdr_code")
        dvd_codes = cursor.fetchall()
        cursor.execute("SELECT id, disc_writing_device FROM lookup_disc_writing_device ORDER BY disc_writing_device")
        devices = cursor.fetchall()

    conn.close()
    return render_template('manage_master.html',
                           artists=artists, albums=albums, labels=labels, cats=cats,
                           formats=formats, years=years, yn=yn, brands=brands,
                           cdr_codes=cdr_codes, dvd_codes=dvd_codes, devices=devices)

# 4. SAVE LOGIC (POST)
def save_master_func():
    conn = get_db_connection()
    m_id = request.form.get('id')

    data = (
        request.form.get('artist_id'),
        request.form.get('album_id'),
        request.form.get('label_id'),
        request.form.get('catalogue_no_id') or None,
        request.form.get('physical_format_type_id'),
        request.form.get('original_release_year_id') or None,
        request.form.get('this_release_year'),
        request.form.get('this_release_duration'),
        request.form.get('average_dynamic_range') or None,
        request.form.get('notes_1'),
        request.form.get('notes_2'),
        request.form.get('notes_3'),
        request.form.get('retail_disc_id'),
        request.form.get('cdr_brand_id') or None,
        request.form.get('cdr_code_id') or None,
        request.form.get('dvdr_brand_id') or None,
        request.form.get('dvdr_code_id') or None,
        request.form.get('disc_creation_date') or None,
        request.form.get('disc_writing_device_id') or None
    )

    try:
        with conn.cursor() as cursor:
            if m_id and m_id.isdigit():
                sql = """
                    UPDATE master_release_entry
                    SET artist_id=%s, album_id=%s, label_id=%s, catalogue_no_id=%s,
                        physical_format_type_id=%s, original_release_year_id=%s,
                        this_release_year=%s, this_release_duration=%s,
                        average_dynamic_range=%s, notes_1=%s, notes_2=%s, notes_3=%s,
                        retail_disc_id=%s, cdr_brand_id=%s, cdr_code_id=%s,
                        dvdr_brand_id=%s, dvdr_code_id=%s, disc_creation_date=%s,
                        disc_writing_device_id=%s
                    WHERE id=%s
                """
                cursor.execute(sql, data + (m_id,))
                flash(f"RECORD {m_id} UPDATED", "success")
            else:
                sql = """
                    INSERT INTO master_release_entry
                    (artist_id, album_id, label_id, catalogue_no_id, physical_format_type_id,
                     original_release_year_id, this_release_year, this_release_duration,
                     average_dynamic_range, notes_1, notes_2, notes_3, retail_disc_id,
                     cdr_brand_id, cdr_code_id, dvdr_brand_id, dvdr_code_id,
                     disc_creation_date, disc_writing_device_id)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """
                cursor.execute(sql, data)
                flash("NEW MASTER CREATED", "success")
        conn.commit()
    except Exception as e:
        conn.rollback()
        flash(f"ERROR: {str(e)}", "danger")
    finally:
        conn.close()
    return redirect(url_for('manage_master'))

def manage_version_func():
    return render_template('manage_version.html')
