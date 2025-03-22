from flask import Blueprint, request, jsonify
from services.llm_services import generate_llm_text

llm_identity_bp = Blueprint("llm_identity", __name__)

@llm_identity_bp.route("/llm_identity", methods=["GET"])
def llm_identity():
    # Get the visitor's input, e.g., "I am John Doe" or "I am a delivery man"
    user_input = request.args.get("text", "")
    if not user_input:
        return jsonify({"error": "Missing 'text' query parameter."}), 400

    # Create instructions that prompt the LLM to identify the person
    instructions = (
        "You are a smart AI that specializes in identifying visitors at the door. "
        "When provided with a statement such as 'I am John Doe' or 'I am a delivery man', "
        "analyze the statement and return only the person's identity. "
        "If a name is mentioned, return the name. If a role is given, return the role. "
        "Keep your answer concise."
    )

    # Call the existing LLM service function with these instructions
    identity = generate_llm_text(user_input, instructions=instructions)
    
    return jsonify({"identity": identity})
