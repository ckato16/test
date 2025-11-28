from flask import Flask, request, jsonify
import librosa
import torch
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from difflib import SequenceMatcher

app = Flask(__name__, static_folder='static', static_url_path='')

# Load wav2vec2 model
try:
    processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
    model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")
    print("✓ Wav2Vec2 loaded")
except Exception as e:
    print(f"✗ Model load failed: {e}")
    processor = None
    model = None

# ARPABET to IPA mapping
ARPABET_TO_IPA = {
    "AA": "ɑ", "AE": "æ", "AH": "ə", "AO": "ɔ", "AW": "aʊ",
    "AY": "aɪ", "EH": "ɛ", "ER": "ɚ", "EY": "eɪ", "IH": "ɪ",
    "IY": "i", "OW": "oʊ", "OY": "ɔɪ", "UH": "ʊ", "UW": "u",
    "B": "b", "CH": "tʃ", "D": "d", "DH": "ð", "F": "f",
    "G": "ɡ", "HH": "h", "JH": "dʒ", "K": "k", "L": "l",
    "M": "m", "N": "n", "NG": "ŋ", "P": "p", "R": "ɹ",
    "S": "s", "SH": "ʃ", "T": "t", "TH": "θ", "V": "v",
    "W": "w", "Y": "j", "Z": "z", "ZH": "ʒ"
}

# Phoneme mappings
WORDS = {
    "tomato": {
        "GA": {"arpabet": "T AH M EY T OW", "ipa": "təˈmeɪtoʊ"},
        "RP": {"arpabet": "T AH M AA T AH", "ipa": "təˈmɑːtəʊ"}
    },
    "dance": {
        "GA": {"arpabet": "D AE N S", "ipa": "dæns"},
        "RP": {"arpabet": "D AA N S", "ipa": "dɑːns"}
    },
    "bath": {
        "GA": {"arpabet": "B AE TH", "ipa": "bæθ"},
        "RP": {"arpabet": "B AA TH", "ipa": "bɑːθ"}
    },
    "grass": {
        "GA": {"arpabet": "G R AE S", "ipa": "ɡræs"},
        "RP": {"arpabet": "G R AA S", "ipa": "ɡrɑːs"}
    },
    "lot": {
        "GA": {"arpabet": "L AA T", "ipa": "lɑt"},
        "RP": {"arpabet": "L AO T", "ipa": "lɒt"}
    },
    "cloth": {
        "GA": {"arpabet": "K L AO TH", "ipa": "klɔθ"},
        "RP": {"arpabet": "K L AO TH", "ipa": "klɒθ"}
    },
    "phone": {
        "GA": {"arpabet": "F OW N", "ipa": "foʊn"},
        "RP": {"arpabet": "F AH N", "ipa": "fəʊn"}
    },
    "schedule": {
        "GA": {"arpabet": "S K EH JH UL", "ipa": "ˈskɛdʒuːl"},
        "RP": {"arpabet": "SH EH JH UL", "ipa": "ˈʃɛdʒuːl"}
    },
    "lever": {
        "GA": {"arpabet": "L EH V ER", "ipa": "ˈlɛvɚ"},
        "RP": {"arpabet": "L IY V ER", "ipa": "ˈliːvə"}
    },
    "route": {
        "GA": {"arpabet": "R UW T", "ipa": "rut"},
        "RP": {"arpabet": "R AW T", "ipa": "raʊt"}
    },
}

def arpabet_to_ipa(arpabet_str):
    """Convert ARPABET phonemes to IPA"""
    if not arpabet_str or arpabet_str == "N/A":
        return "N/A"
    
    phonemes = arpabet_str.split()
    ipa_phonemes = []
    
    for phoneme in phonemes:
        clean_phoneme = ''.join(c for c in phoneme if not c.isdigit())
        ipa_phonemes.append(ARPABET_TO_IPA.get(clean_phoneme, clean_phoneme))
    
    return ''.join(ipa_phonemes)

def calculate_score(detected, expected):
    """Calculate similarity score 0-100 using SequenceMatcher"""
    if expected == "N/A":
        return 0
    
    matcher = SequenceMatcher(None, detected.upper(), expected.upper())
    ratio = matcher.ratio()
    return int(ratio * 100)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/models')
def get_models():
    available = [{"id": "wav2vec2", "name": "Wav2Vec2 Base"}]
    return jsonify(available)

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file"}), 400
    
    if not model or not processor:
        return jsonify({"error": "Model not loaded"}), 500
    
    audio_file = request.files['audio']
    accent = request.form.get('accent', 'GA')
    word = request.form.get('word', '')
    
    audio_path = '/tmp/audio.wav'
    audio_file.save(audio_path)
    
    try:
        speech, sr = librosa.load(audio_path, sr=16000)
    except Exception as e:
        return jsonify({"error": f"Audio load failed: {e}"}), 400
    
    try:
        inputs = processor(speech, sampling_rate=sr, return_tensors="pt")
        with torch.no_grad():
            logits = model(**inputs).logits
        
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = processor.batch_decode(predicted_ids)[0]
    except Exception as e:
        return jsonify({"error": f"Inference failed: {e}"}), 500
    
    phoneme_data = WORDS.get(word, {}).get(accent, {})
    expected_arpabet = phoneme_data.get("arpabet", "N/A")
    expected_ipa = phoneme_data.get("ipa", "N/A")
    detected_ipa = arpabet_to_ipa(transcription)
    
    score = calculate_score(transcription, expected_arpabet)
    
    return jsonify({
        "transcription": transcription,
        "detected_ipa": detected_ipa,
        "expected_arpabet": expected_arpabet,
        "expected_ipa": expected_ipa,
        "score": score,
        "match": score == 100
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
