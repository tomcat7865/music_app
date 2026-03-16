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
    
    try:
        with conn.cursor() as cursor:
            dropdown_query = "SELECT m.id AS master_id, a.album AS album_name FROM master_release_entry m JOIN lookup_album a ON m.album_id = a.album_id ORDER BY a.album ASC"
            cursor.execute(dropdown_query)
            albums = cursor.fetchall()

            if search_id:
                query = """
                    SELECT m.*, art.artist, alb.album, lab.label, cat.catalogue_number, 
                           loc.storage_location, yr.release_year, m.this_release_year,
                           pft.physical_format_type, m.this_release_duration, 
                           m.duration_less_bonus, m.side_change_point, m.average_dynamic_range
                    FROM master_release_entry m
                    INNER JOIN lookup_artist art ON m.artist_id = art.id
                    INNER JOIN lookup_album alb ON m.album_id = alb.album_id
                    INNER JOIN lookup_label lab ON m.label_id = lab.id
                    INNER JOIN lookup_catalogue_no cat ON m.catalogue_no_id = cat.id
                    INNER JOIN lookup_storage_location loc ON m.storage_location_id = loc.id
                    INNER JOIN lookup_original_release_year yr ON m.original_release_year_id = yr.id
                    INNER JOIN lookup_physical_format_type pft ON m.physical_format_type_id = pft.id
                    WHERE m.id = %s
                """
                cursor.execute(query, (search_id,))
                result = cursor.fetchone()

                if result:
                    # Final Version Query with Storage Location Join
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
    finally:
        conn.close()

    return render_template('view_master.html', albums=albums, result=result, other_versions=other_versions)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
