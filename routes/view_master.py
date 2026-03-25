from flask import render_template, request
from database import get_db_connection

def view_master_func():
    sid = request.args.get('id')
    conn = get_db_connection()
    result, albums_list, other_versions, interactions = None, [], [], []
    
    with conn.cursor() as cursor:
        # 1. Sidebar List
        cursor.execute("SELECT m.id, a.album FROM master_release_entry m JOIN lookup_album a ON m.album_id = a.album_id ORDER BY a.album ASC")
        albums_list = cursor.fetchall()
        
        if sid:
            # 2. Main Master Record [cite: 1, 4, 5]
            # Includes Technical Specs and Notes structures
            query = """
                SELECT m.*, art.artist, alb.album, lab.label, cat.catalogue_number, 
                       fmt.physical_format_type, yr.release_year AS original_year,
                       yn_retail.yes_no AS retail_disc, brd_cdr.disc_brand AS cdr_brand,
                       c_code.cdr_code, brd_dvd.disc_brand AS dvdr_brand,
                       d_code.bdr_dvdr_code, dwd.disc_writing_device,
                       loc.storage_location
                FROM master_release_entry m 
                LEFT JOIN lookup_artist art ON m.artist_id = art.id 
                LEFT JOIN lookup_album alb ON m.album_id = alb.album_id 
                LEFT JOIN lookup_label lab ON m.label_id = lab.id
                LEFT JOIN lookup_catalogue_no cat ON m.catalogue_no_id = cat.id
                LEFT JOIN lookup_physical_format_type fmt ON m.physical_format_type_id = fmt.id
                LEFT JOIN lookup_original_release_year yr ON m.original_release_year_id = yr.id
                LEFT JOIN lookup_yes_no yn_retail ON m.retail_disc_id = yn_retail.id
                LEFT JOIN lookup_disc_brand brd_cdr ON m.cdr_brand_id = brd_cdr.id
                LEFT JOIN lookup_cdr_code c_code ON m.cdr_code_id = c_code.id1
                LEFT JOIN lookup_disc_brand brd_dvd ON m.dvdr_brand_id = brd_dvd.id
                LEFT JOIN lookup_bdr_dvdr_code d_code ON m.dvdr_code_id = d_code.id
                LEFT JOIN lookup_disc_writing_device dwd ON m.disc_writing_device_id = dwd.id
                LEFT JOIN lookup_storage_location loc ON m.storage_location_id = loc.id
                WHERE m.id = %s
            """
            cursor.execute(query, (sid,))
            result = cursor.fetchone()

            # 3. Other Versions 
            # Follows the tabular format from your structure file
            ov_query = """
                SELECT ov.id, b.bit_depth, s.sample_rate, df.digital_format_type, 
                       l.label, c.catalogue_number, y.release_year,
                       pft.physical_format_type, ov.duration, ov.average_dynamic_range, 
                       yn.yes_no AS booklet, ov.individual_comment, loc.storage_location
                FROM other_version_entry ov
                LEFT JOIN lookup_bit_depth b ON ov.bit_depth_id = b.id
                LEFT JOIN lookup_sample_rate s ON ov.sample_rate_id = s.id
                LEFT JOIN lookup_digital_format_type df ON ov.digital_format_type_id = df.id
                LEFT JOIN lookup_label l ON ov.label_id = l.id
                LEFT JOIN lookup_catalogue_no c ON ov.catalogue_no_id = c.id
                LEFT JOIN lookup_original_release_year y ON ov.this_release_year_id = y.id
                LEFT JOIN lookup_physical_format_type pft ON ov.physical_format_type_id = pft.id
                LEFT JOIN lookup_yes_no yn ON ov.booklet_available_id = yn.id
                LEFT JOIN lookup_storage_location loc ON ov.storage_location_id = loc.id
                WHERE ov.master_release_entry_id = %s
            """
            cursor.execute(ov_query, (sid,))
            other_versions = cursor.fetchall()

            # 4. Interactions Log 
            int_query = """
                SELECT log.id, log.interaction_date, typ.interaction_type, 
                       cat.catalogue_number, fmt.physical_format_type, 
                       bit.bit_depth, smp.sample_rate, log.individual_comment
                FROM media_interaction_log log
                LEFT JOIN lookup_interaction_type typ ON log.interaction_type_id = typ.id
                LEFT JOIN lookup_catalogue_no cat ON log.catalogue_no_id = cat.id
                LEFT JOIN lookup_physical_format_type fmt ON log.physical_format_type_id = fmt.id
                LEFT JOIN lookup_bit_depth bit ON log.bit_depth_id = bit.id
                LEFT JOIN lookup_sample_rate smp ON log.sample_rate_id = smp.id
                WHERE log.master_release_entry_id = %s 
                ORDER BY log.interaction_date DESC
            """
            cursor.execute(int_query, (sid,))
            interactions = cursor.fetchall()

    conn.close()
    return render_template('view_master.html', 
                           result=result, 
                           albums_list=albums_list, 
                           other_versions=other_versions,
                           interactions=interactions)
