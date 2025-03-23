import json
from flask import Blueprint, request, jsonify
from services.llm_services import generate_llm_text

llm_get_name_desc_bp = Blueprint("llm_get_name_desc", __name__)

@llm_get_name_desc_bp.route("/llm_get_name_desc", methods=["GET"])
def llm_get_name_desc():
    # Get the visitor's input, e.g., "I am John Doe" or "I am a delivery man"
    user_input = request.args.get("text", "")
    if not user_input:
        return jsonify({"error": "Missing 'text' query parameter."}), 400

    # Create instructions that prompt the LLM to extract name and description.
    instructions = (
        "You are a smart AI doorbell system. When a visitor speaks, analyze the statement and extract two pieces of information: "
        "the visitor's name (if mentioned) and a brief description of what they intend to do at the door. "
        "Return your answer as valid JSON with two keys: 'name' and 'description'. "
        "Could you make the description more descriptive on what the visitor intends to do? "
        "Do not include any markdown formatting or extra text."
    )

    # Call the LLM service function with these instructions.
    llm_response = generate_llm_text(user_input, instructions=instructions)

    # Clean up the response if it's wrapped in markdown code fences.
    cleaned_response = llm_response.strip()
    if cleaned_response.startswith("```"):
        lines = cleaned_response.splitlines()
        if len(lines) >= 3 and lines[0].startswith("```"):
            # Remove the first and last lines (the fences)
            cleaned_response = "\n".join(lines[1:-1]).strip()

    try:
        result = json.loads(cleaned_response)
    except json.JSONDecodeError as e:
        return jsonify({
            "error": "JSON decoding error",
            "raw_response": cleaned_response,
            "exception": str(e)
        }), 500

    return jsonify(result)
