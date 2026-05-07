from flask import Flask, render_template, flash, request, redirect, url_for
from routes.view_master import view_master_func
from routes.control_panel import (
    control_panel_home_func, manage_artists_func, save_artist_func,
    manage_albums_func, save_album_func, manage_labels_func,
    save_label_func, manage_locations_func, save_location_func,
    manage_catalogue_numbers_func, save_catalogue_number_func,
    manage_interactions_func, save_interaction_func,
    manage_media_specs_func, save_media_spec_func, get_album_name_func
)
from routes.reports_labels import (
    reports_home_func, label_inlay_selection_func,
    label_storage_selection_func, generate_storage_label_func,
    generate_inlay_func, report_top_100_func,
    report_unplayed_func, report_by_artist_func,
    storage_master_batch_func, storage_version_batch_func,
    report_latest_additions_func, report_todo_list_func  # All reports now included
)
from routes.data_entry import (
    data_entry_home_func, manage_master_func, manage_version_func,
    save_master_func, get_master_details_func,
    save_version_func, get_version_details_func
)

app = Flask(__name__)
app.secret_key = "secret_archive_key"

# --- MAIN INDEX ---
@app.route('/')
def index(): return render_template('index.html')

# --- VIEW MASTER ---
@app.route('/view_master')
def view_master(): return view_master_func()

# --- CONTROL PANEL ---
@app.route('/control_panel')
def control_panel_home(): return control_panel_home_func()

@app.route('/api/get_album_name')
def get_album_name(): return get_album_name_func()

@app.route('/control_panel/artists', methods=['GET', 'POST'])
def manage_artists(): return manage_artists_func()

@app.route('/control_panel/artists/save', methods=['POST'])
def save_artist(): return save_artist_func()

@app.route('/control_panel/albums', methods=['GET', 'POST'])
def manage_albums(): return manage_albums_func()

@app.route('/control_panel/albums/save', methods=['POST'])
def save_album(): return save_album_func()

@app.route('/control_panel/labels', methods=['GET', 'POST'])
def manage_labels(): return manage_labels_func()

@app.route('/control_panel/labels/save', methods=['POST'])
def save_label(): return save_label_func()

@app.route('/control_panel/locations', methods=['GET', 'POST'])
def manage_locations(): return manage_locations_func()

@app.route('/control_panel/locations/save', methods=['POST'])
def save_location(): return save_location_func()

@app.route('/control_panel/catalogue_numbers', methods=['GET', 'POST'])
def manage_catalogue_numbers(): return manage_catalogue_numbers_func()

@app.route('/control_panel/catalogue_numbers/save', methods=['POST'])
def save_catalogue_number(): return save_catalogue_number_func()

@app.route('/control_panel/interactions', methods=['GET', 'POST'])
def manage_interactions(): return manage_interactions_func()

@app.route('/control_panel/interactions/save', methods=['POST'])
def save_interaction(): return save_interaction_func()

@app.route('/control_panel/media_specs')
def manage_media_specs(): return manage_media_specs_func()

@app.route('/control_panel/media_specs/save', methods=['POST'])
def save_media_spec(): return save_media_spec_func()

# --- REPORTS & LABELS ---
@app.route('/reports_labels')
def reports_home(): return reports_home_func()

@app.route('/labels/inlay')
def label_inlay_selection(): return label_inlay_selection_func()

@app.route('/labels/storage')
def label_storage_selection(): return label_storage_selection_func()

@app.route('/labels/storage/generate/<int:master_id>')
def generate_storage_label(master_id): return generate_storage_label_func(master_id)

@app.route('/labels/inlay/generate/<int:master_id>')
def generate_inlay(master_id): return generate_inlay_func(master_id)

@app.route('/labels/storage/master/batch', methods=['GET', 'POST'])
def storage_master_batch(): return storage_master_batch_func()

@app.route('/labels/storage/version/batch', methods=['GET', 'POST'])
def storage_version_batch(): return storage_version_batch_func()

@app.route('/reports/top_100')
def report_top_100(): return report_top_100_func()

@app.route('/reports/unplayed')
def report_unplayed(): return report_unplayed_func()

@app.route('/reports/by_artist', methods=['GET', 'POST'])
def report_by_artist(): return report_by_artist_func()

@app.route('/reports/latest')
def report_latest_additions(): return report_latest_additions_func()

@app.route('/reports/todo')
def report_todo_list(): return report_todo_list_func()

# --- DATA ENTRY ---
@app.route('/data_entry')
def data_entry_home(): return data_entry_home_func()

@app.route('/data_entry/master', methods=['GET', 'POST'])
def manage_master(): return manage_master_func()

@app.route('/data_entry/version', methods=['GET', 'POST'])
def manage_version(): return manage_version_func()

@app.route('/data_entry/master/save', methods=['POST'])
def save_master(): return save_master_func()

@app.route('/data_entry/version/save', methods=['POST'])
def save_version(): return save_version_func()

@app.route('/api/get_master_details')
def get_master_details(): return get_master_details_func()

@app.route('/api/get_version_details')
def get_version_details(): return get_version_details_func()

# --- START THE APP ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
