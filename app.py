from flask import Flask, render_template, request
import pymysql

app = Flask(__name__)

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
            query = """
                SELECT m.id AS master_id, a.album AS album_name 
                FROM master_release_entry m
                JOIN lookup_album a ON m.album_id = a.album_id
                ORDER BY a.album ASC
            """
            cursor.execute(query)
            albums = cursor.fetchall()
    finally:
        conn.close()
    return render_template('index.html', albums=albums)

@app.route('/view_master')
def view_master():
    search_id = request.args.get('id')
    conn = get_db_connection()
    albums = []
    result = None
    other_versions = []
    interactions = []
    
    try:
        with conn.cursor() as cursor:
            dropdown_query = "SELECT m.id AS master_id, a.album AS album_name FROM master_release_entry m JOIN lookup_album a ON m.album_id = a.album_id ORDER BY a.album ASC"
            cursor.execute(dropdown_query)
            albums = cursor.fetchall()

            if search_id:
                # 1. Main Master Record Query
                query = """
                    SELECT m.*, art.artist, alb.album, lab.label, cat.catalogue_number, 
                           loc.storage_location, yr.release_year, m.this_release_year,
                           pft.physical_format_type, m.this_release_duration, 
                           m.duration_less_bonus, m.side_change_point, m.average_dynamic_range,
                           m.notes_1, m.notes_2, m.notes_3, m.disc_creation_date,
                           ryn.yes_no AS retail_disc_status,
                           ldb.disc_brand,
                           ldb2.disc_brand AS dvdr_brand,
                           lcc.cdr_code,
                           lbc.bdr_dvdr_code,
                           lwd.disc_writing_device
                    FROM master_release_entry m
                    INNER JOIN lookup_artist art ON m.artist_id = art.id
                    INNER JOIN lookup_album alb ON m.album_id = alb.album_id
                    INNER JOIN lookup_label lab ON m.label_id = lab.id
                    INNER JOIN lookup_catalogue_no cat ON m.catalogue_no_id = cat.id
                    INNER JOIN lookup_storage_location loc ON m.storage_location_id = loc.id
                    INNER JOIN lookup_original_release_year yr ON m.original_release_year_id = yr.id
                    INNER JOIN lookup_physical_format_type pft ON m.physical_format_type_id = pft.id
                    LEFT JOIN lookup_yes_no ryn ON m.retail_disc_id = ryn.id
                    LEFT JOIN lookup_disc_brand ldb ON m.cdr_brand_id = ldb.id
                    LEFT JOIN lookup_disc_brand ldb2 ON m.dvdr_brand_id = ldb2.id
                    LEFT JOIN lookup_cdr_code lcc ON m.cdr_code_id = lcc.id1
                    LEFT JOIN lookup_bdr_dvdr_code lbc ON m.dvdr_code_id = lbc.id
                    LEFT JOIN lookup_disc_writing_device lwd ON m.disc_writing_device_id = lwd.id
                    WHERE m.id = %s
                """
                cursor.execute(query, (search_id,))
                result = cursor.fetchone()

                if result:
                    # 2. Other Versions Query
                    version_query = """
                        SELECT v.id, v.duration, v.average_dynamic_range, v.individual_comment,
                               bd.bit_depth, sr.sample_rate, df.digital_format_type, 
                               vlab.label, vcat.catalogue_number, vyr.release_year AS version_year, 
                               vpft.physical_format_type AS version_format, vbook.yes_no AS booklet_status,
                               vloc.storage_location AS version_location
                        FROM other_version_entry v
                        LEFT JOIN lookup_bit_depth bd ON v.bit_depth_id = bd.id
                        LEFT JOIN lookup_sample_rate sr ON v.sample_rate_id = sr.id
                        LEFT JOIN lookup_digital_format_type df ON v.digital_format_type_id = df.id
                        LEFT JOIN lookup_label vlab ON v.label_id = vlab.id
                        LEFT JOIN lookup_catalogue_no vcat ON v.catalogue_no_id = vcat.id
                        LEFT JOIN lookup_original_release_year vyr ON v.this_release_year_id = vyr.id
                        LEFT JOIN lookup_physical_format_type vpft ON v.physical_format_type_id = vpft.id
                        LEFT JOIN lookup_yes_no vbook ON v.booklet_available_id = vbook.id
                        LEFT JOIN lookup_storage_location vloc ON v.storage_location_id = vloc.id
                        WHERE v.master_release_entry_id = %s
                    """
                    cursor.execute(version_query, (search_id,))
                    other_versions = cursor.fetchall()

                    # 3. Interactions Log Query
                    interaction_query = """
                        SELECT mil.id, mil.interaction_date, li.interaction_type, 
                               lcat.catalogue_number, lpft.physical_format_type, 
                               lbd.bit_depth, lsr.sample_rate, mil.individual_comment
                        FROM media_interaction_log mil
                        LEFT JOIN lookup_interaction_type li ON mil.interaction_type_id = li.id
                        LEFT JOIN lookup_catalogue_no lcat ON mil.catalogue_no_id = lcat.id
                        LEFT JOIN lookup_physical_format_type lpft ON mil.physical_format_type_id = lpft.id
                        LEFT JOIN lookup_bit_depth lbd ON mil.bit_depth_id = lbd.id
                        LEFT JOIN lookup_sample_rate lsr ON mil.sample_rate_id = lsr.id
                        WHERE mil.master_release_entry_id = %s
                        ORDER BY mil.interaction_date DESC
                    """
                    cursor.execute(interaction_query, (search_id,))
                    interactions = cursor.fetchall()

    finally:
        conn.close()

    return render_template('view_master.html', albums=albums, result=result, 
                           other_versions=other_versions, interactions=interactions)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
