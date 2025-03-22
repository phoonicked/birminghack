from flask import Blueprint, request, send_file
from services.tts_services import generate_tts_wav

tts_bp = Blueprint("tts", __name__)

@tts_bp.route("/tts", methods=["GET"])
def tts_endpoint():
    # Grab query param
    text = request.args.get("text", "Hello, world!")
    speed = float(request.args.get("speed", 1.05))
    lang_code = request.args.get("lang_code", "en")
    voice_id = request.args.get("voice_id")  # optional param
    
    # Generate TTS
    filename = generate_tts_wav(text, speed, lang_code, voice_id)

    # Return the WAV file
    return send_file(filename, mimetype="audio/wav")
