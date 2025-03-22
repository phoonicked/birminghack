# routes/llm_routes.py
from flask import Blueprint, request, send_file, jsonify
from services.llm_services import generate_llm_text
from services.tts_services import generate_tts_wav

llm_bp = Blueprint("llm", __name__)

@llm_bp.route("/llm_voice", methods=["GET"])
def llm_voice():
    prompt = request.args.get("prompt", "How do I check if a Python object is an instance of a class?")
    instructions = request.args.get("instructions", "Talk like a Ring Doorbell (AI sounnding).")
    
    try:
        # Generate text using the LLM
        llm_text = generate_llm_text(prompt, instructions=instructions)
    except Exception as e:
        return jsonify({"error": f"LLM generation error: {str(e)}"}), 500

    print("LLM generated text:", llm_text)
    
    try:
        # Use the TTS service to generate a WAV file from the LLM output
        filename = generate_tts_wav(llm_text)
    except Exception as e:
        return jsonify({"error": f"TTS generation error: {str(e)}"}), 500

    return send_file(filename, mimetype="audio/wav")
