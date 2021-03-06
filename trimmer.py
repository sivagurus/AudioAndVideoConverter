from flask import Blueprint, request, send_from_directory
from werkzeug.utils import secure_filename
import os, subprocess
from loggers import log_this, log

trimmer = Blueprint('trimmer', __name__)


@trimmer.route("/trimmer", methods=["POST"])
def trim_file():

    if request.form["request_type"] == "upload_complete":

        chosen_file = request.files["chosen_file"]
        # Make the filename safe
        filename_secure = secure_filename(chosen_file.filename)
        # Save the uploaded file to the uploads folder.
        chosen_file.save(os.path.join("uploads", filename_secure))
        return ''

    if request.form["request_type"] == "trim":

        filename = request.form["filename"]
        log_this(f'wants to trim: {filename}')
        uploaded_file_path = os.path.join("uploads", secure_filename(filename))
        start_time = request.form["start_time"]
        log.info(f'START TIME: {start_time}')
        end_time = request.form["end_time"]
        log.info(f'END TIME: {end_time}')
        ext = "." + filename.split(".")[-1]
        just_name = filename.split(".")[0]
        output_name = just_name + " [trimmed]" + ext
        output_file_path = os.path.join('trims', output_name)

        subprocess.run(['ffmpeg', '-y', '-i', uploaded_file_path, '-ss', start_time, '-to', end_time,
                       '-map', '0', '-c', 'copy', output_file_path], shell=False)

        return output_file_path


@trimmer.route("/trims/<filename>", methods=["GET"])
def download_file(filename):
    log.info(f'https://free-av-tools.com/trims/{filename}')
    extension = os.path.splitext(filename)[-1]
    if extension == ".m4a":
        return send_from_directory('trims', filename, mimetype="audio/mp4", as_attachment=True)
    else:
        return send_from_directory('trims', filename, as_attachment=True)