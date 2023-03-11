import os
import imghdr
import zhconv
from flask import Flask, request, jsonify, render_template, Response
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

def run_whisper(cmd):
    proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
    for line in iter(proc.stdout.readline, b''):
        yield f'{zhconv.convert(line.decode("utf-8"), "zh-cn")}'
    for line in iter(proc.stderr.readline, b''):
        yield f'{line.decode("utf-8")}\n'
    proc.stdout.close()
    proc.stderr.close()
    proc.wait()


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    default_language = 'Chinese'  # 默认语言为中文
    default_operation = 'transcribe'  # 默认选项为 transcribe
    default_model = 'medium'  # 默认模型为 medium
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

        # Convert video to audio if file is a video
        file_type = imghdr.what(file_path)
        if file_type in ('mp4', 'avi', 'mov', 'mkv'):
            audio_path = os.path.splitext(file_path)[0] + '.wav'
            cmd = ['ffmpeg', '-i', file_path, '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', audio_path]
            proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
            proc.communicate()
            if proc.returncode != 0:
                return jsonify({'error': 'Failed to convert video to audio.'}), 400
            file_path = audio_path

        # Use whisper to transcribe/translate the file based on the selected option and model
        option = request.form.get('operation', default_operation)  # 获取用户选择的选项，默认为 transcribe
        model = request.form.get('model', default_model)  # 获取用户选择的模型，默认为 medium

        if option == 'transcribe':
            language = request.form.get('language', default_language)  # 获取用户选择的语言，默认为 Chinese
            cmd = ['/home/$USER/Documents/miniconda3/envs/whisper/bin/python',
                   '/home/$USER/Documents/miniconda3/envs/whisper/bin/whisper', file_path, '--model',
                   model, '--language', language, '-f', 'txt']
        elif option == 'translate':
            src_lang = request.form.get('src_lang', default_language)  # 获取用户选择的源语言，默认为 en-US
            trg_lang = request.form.get('trg_lang', 'en')  # 获取用户选择的目标语言，默认为 en
            cmd = ['/home/chase/Documents/miniconda3/envs/whisper/bin/python',
                   '/home/chase/Documents/miniconda3/envs/whisper/bin/whisper', file_path, '--model',
                   model, '--task', 'translate', '--language', trg_lang, '-f', 'txt']
        else:
            return jsonify({'error': 'Invalid option selected.'}), 400
        # Run whisper

        # Run whisper command and return output using SSE
        return Response(run_whisper(cmd), mimetype='text/event-stream')
    else:
        return render_template('upload.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
