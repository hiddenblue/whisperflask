import os
import zhconv
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from subprocess import Popen, PIPE

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = './uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index_html():
    return render_template('upload.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        # if user does not select file, browser also submit an empty part without filename
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        # Save the file to disk
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        # Use whisper to transcribe the file
        cmd = ['/home/chase/Documents/miniconda3/envs/whisper/bin/python',
               '/home/chase/Documents/miniconda3/envs/whisper/bin/whisper', file_path, '--model',
               'medium', '--language', 'Chinese', '-f', 'txt']
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = proc.communicate()
        stdout_zh_cn = zhconv.convert(stdout.decode("utf-8"), 'zh-cn')
        if stderr:
            return jsonify({'error': stderr.decode('utf-8')}), 400
        else:
            transcription = stdout_zh_cn
            # Remove the uploaded file from disk
            os.remove(file_path)
            return jsonify({'transcription': transcription})
    else:
        return render_template('upload.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

