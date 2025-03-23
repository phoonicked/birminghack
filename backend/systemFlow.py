from utils.add_timestamp import add_timestamp_to_dayharry
from services.speech_recognition import listen_for_speech
from utils.notes_utils import fetch_notes, get_contact_name_from_db
from services.tts_client import call_tts_endpoint
from services.llm_client import call_llm_endpoint, call_llm_identity_endpoint
import time

def main_flow(known_contact, contact_name, stop_event):
    """
    Main doorbell conversation flow.
    
    :param known_contact: Boolean indicating if the visitor is recognized.
    :param contact_name: The name of the recognized visitor (if known).
    :param stop_event: A threading.Event used to signal this flow to stop
    """
    add_timestamp_to_dayharry()
    print("Camera detected a person.")

    notes = fetch_notes()
    extra_info = " ".join(note["text"] for note in notes if note["text"])
    print("Extra info for unknown visitors:", extra_info)

    # Step 1: Decide on the TTS message and instructions
    if known_contact:
        tts_text = f"Hi, {contact_name}! How can I help you?"
        instructions = (
            "You are a friendly AI doorbell. Greet known contacts warmly and offer help, "
            "keeping your responses brief and conversational. "
            f"Always respond to {contact_name} with a friendly tone."
        )
    else:
        tts_text = "Hi, who am I speaking to?"
        instructions = (
            "You are an AI doorbell. Greet unknown visitors formally and ask for their identification. "
            "If the visitor says they are a delivery worker, simply reply, 'Could you put your delivery to the porch?' "
            "Keep responses concise and to the point. "
            + extra_info
        )
    
    # Step 2: Use TTS to initiate conversation
    tts_audio = call_tts_endpoint(tts_text)
    if tts_audio:
        print("Playing TTS audio...")
    else:
        print("Failed to generate TTS audio.")
        return
    
    # Step 3: If unknown visitor, ask for their name
    if not known_contact:
        name = listen_for_speech("Please state your name.")
    
    # Step 4: Ask for identity
    identity_input = listen_for_speech("Please state your identity.")
    identity = call_llm_identity_endpoint(identity_input)
    print(f"Identified as: {identity}")
    instructions += f" Visitor has identified themselves as {identity}. "
    llm_audio = call_llm_endpoint(identity_input, instructions)
    if llm_audio:
        print("Playing LLM-generated audio for identity confirmation...")
    else:
        print("Failed to generate LLM audio for identity confirmation.")

    # Step 5: Conversation loop until the user says exit or the stop_event is set
    while True:
        if stop_event.is_set():
            print("Stop event set. Exiting conversation loop.")
            break

        user_input = listen_for_speech("What did the person say? Say 'exit' or 'quit' to stop.")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting conversation loop.")
            break

        instructions += f" Visitor said: '{user_input}'. "
        print("Updated instructions for LLM:")
        print(instructions)

        llm_audio = call_llm_endpoint(user_input, instructions)
        if llm_audio:
            print("Playing LLM-generated audio...")
        else:
            print("Failed to generate LLM audio.")
    return instructions