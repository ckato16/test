from flask import Flask, render_template, request, send_file
from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH
import tempfile, os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file uploaded', 400

    file = request.files['file']
    if file.filename == '':
        return 'No file selected', 400

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, file.filename)
        file.save(input_path)

        predict_and_save(
            [input_path],
            tmpdir,
            True,   # save_midi
            False,  # sonify_midi
            False,  # save_model_outputs
            False,  # save_notes
            ICASSP_2022_MODEL_PATH
        )

        midi_files = [f for f in os.listdir(tmpdir) if f.endswith('.mid')]
        if not midi_files:
            return 'MIDI conversion failed', 500

        output_path = os.path.join(tmpdir, midi_files[0])
        return send_file(output_path, as_attachment=True, download_name='output.mid')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
