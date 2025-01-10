from flask import Flask, request, jsonify, send_file, render_template
import os
import threading
from VoiceCommandRecorder import VoiceCommandRecorder, COMMANDS, LANGUAGES, AUDIO_FOLDER, CSV_FILE

app = Flask(__name__)

# Create audio folder if it doesn't exist
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# Initialize the VoiceCommandRecorder
recorder = VoiceCommandRecorder()

@app.route('/')
def index():
    return render_template('index.html', commands=COMMANDS, languages=LANGUAGES)

@app.route('/record', methods=['POST'])
def record():
    data = request.json
    command = data.get('command')
    language = data.get('language')
    speaker = data.get('speaker')

    if not command or not language or not speaker:
        return jsonify({'error': 'Missing parameters'}), 400

    def record_audio():
        recorder.start_recording(command, language, speaker)

    threading.Thread(target=record_audio, daemon=True).start()
    return jsonify({'message': 'Recording started'})


@app.route('/stop', methods=['POST'])
def stop():
    # Stop recording and save the file
    recorder.stop_recording()
    return jsonify({'message': 'Recording stopped and saved'})

@app.route('/recordings', methods=['GET'])
def get_recordings():
    recordings = []
    with open(CSV_FILE, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            recordings.append({
                'command': row[0],
                'speaker': row[1],
                'language': row[2],
                'filename': row[3]
            })
    return jsonify(recordings)

@app.route('/recordings/<filename>', methods=['GET'])
def play_recording(filename):
    filepath = os.path.join(AUDIO_FOLDER, filename)
    
    # Validate file existence and extension
    if not os.path.exists(filepath) or not filename.endswith('.wav'):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(filepath, as_attachment=True)

# Directory where voice commands are stored
voice_commands_dir = './voice_commands/'

# Example route to delete the recording
@app.route("/delete/<filename>", methods=["DELETE"])
def delete_recording(filename):
    file_path = os.path.join(voice_commands_dir, filename)  # Adjust path
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({"message": "Recording deleted successfully."})
    return jsonify({"message": "File not found."}), 404

# Example route to run the voice command
@app.route("/run-voice/<filename>", methods=["POST"])
def run_voice(filename):
    file_path = os.path.join(voice_commands_dir, filename)  # Adjust path
    if os.path.exists(file_path):
        # Logic to process the voice file or run a command
        # For example, if you have a TTS engine or other process
        return jsonify({"message": f"Running voice command for {filename}"})
    return jsonify({"message": "File not found."}), 404

if __name__ == '__main__':
    app.run(debug=True)