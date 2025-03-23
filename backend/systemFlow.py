from utils.add_timestamp import add_timestamp_to_dayharry
from services.speech_recognition import listen_for_speech
from utils.notes_utils import fetch_notes
from services.tts_client import call_tts_endpoint
from services.llm_client import call_llm_endpoint, call_llm_identity_endpoint
import time

def check_contact():
    """
    Placeholder function simulating a contact check.
    Returns (True, name) if the person is in contacts, otherwise (False, None).
    """
    answer = listen_for_speech("Is the detected person in contacts? Please say 'yes' or 'no'.")
    if answer.lower().startswith("y"):
        name = listen_for_speech("Please state the contact's name.")
        return True, name
    else:
        return False, None

def main_flow(known_contact, contact_name, stop_event):
    """
    Main doorbell conversation flow.

    :param known_contact: Boolean indicating if the visitor is known
    :param contact_name: The known contact's name if applicable
    :param stop_event: A threading.Event used to signal this flow to stop
    """
    add_timestamp_to_dayharry()
    print("Camera detected a person.")

    # Step 1: Check if the person is in contacts (dummy simulation)
    in_contacts, name = check_contact()
    notes = fetch_notes()
    extra_info = " ".join(note["text"] for note in notes if note["text"])
    print("Extra info for unknown visitors:", extra_info)

    # Step 2: Decide on the TTS message and instructions
    if in_contacts and name:
        tts_text = f"Hi, {name}! How can I help you?"
        instructions = (
            "You are a friendly AI doorbell. Greet known contacts warmly and offer help, "
            "keeping your responses brief and conversational. "
            f"Always respond to {name} with a friendly tone."
        )
    else:
        tts_text = "Hi, how can I help you?"
        instructions = (
            "You are an AI doorbell. Greet unknown visitors formally and ask for their identification. "
            "If the visitor says they are a delivery worker, simply reply, 'Could you put your delivery to the porch?' "
            "Keep responses concise and to the point. "
            + extra_info
        )

    # Step 3: Use TTS to ask the initial question
    tts_audio = call_tts_endpoint(tts_text)
    if tts_audio:
        print("Playing TTS audio...")
        # (Your code to actually play the audio if needed)
    else:
        print("Failed to generate TTS audio.")
        return

    # Step 4: If unknown visitor, ask identity
    if not in_contacts:
        identity_input = listen_for_speech("Please state your identity.")
        identity = call_llm_identity_endpoint(identity_input)
        print(f"Identified as: {identity}")
        instructions += f" Visitor has identified themselves as {identity}. "
        llm_audio = call_llm_endpoint(identity_input, instructions)
        if llm_audio:
            print("Playing LLM-generated audio for identity confirmation...")
            # (Your code to play the audio)
        else:
            print("Failed to generate LLM audio for identity confirmation.")

    # Step 5: Conversation loop until the user says exit or the stop_event is set
    while True:
        # Check if we've been signaled to stop
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
            # (Your code to play the audio)
        else:
            print("Failed to generate LLM audio.")