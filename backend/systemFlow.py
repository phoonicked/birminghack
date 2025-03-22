from utils.notes_utils import fetch_notes
from services.tts_client import call_tts_endpoint
from services.llm_client import call_llm_endpoint, call_llm_identity_endpoint
from services.audio_player import play_audio

def check_contact():
    """
    Placeholder function simulating a contact check.
    Returns (True, name) if the person is in contacts, otherwise (False, None).
    """
    answer = input("Is the detected person in contacts? (Y/N): ").strip().lower()
    if answer == 'y':
        name = input("Enter the contact's name: ").strip()
        return True, name
    else:
        return False, None

def main_flow():
    # Simulate the event: a camera detects a person.
    print("Camera detected a person.")

    # Step 1: Check if the person is in contacts.
    in_contacts, name = check_contact()
    notes = fetch_notes()
    extra_info = " ".join(note["text"] for note in notes if note["text"])
    print("Extra info for unknown visitors:", extra_info)

    # Step 2: Decide on the TTS message and initial instructions.
    if in_contacts and name:
        tts_text = f"Hi, {name}! How can I help you?"
        instructions = (
            "You are a smart AI doorbell and door lock system. "
            "When a known contact speaks at the door, greet them warmly and helpfully. "
            "Respond in a friendly and polite tone, and ask them how you can assist them. "
            f"Always respond to {name} with a friendly tone."
        )
    else:
        tts_text = "Hi, how can I help you?"
        instructions = (
            "You are a smart AI doorbell and door lock system. "
            "When an unknown person speaks at the door, greet them formally and cautiously. "
            "Ask them to identify themselves, and maintain a secure tone while verifying their identity."
            f"{extra_info}"
        )

    # Step 3: Use TTS to ask the initial question.
    tts_audio = call_tts_endpoint(tts_text)
    if tts_audio:
        print("Playing TTS audio...")
    else:
        print("Failed to generate TTS audio.")
        return

    # Step 4: If unknown visitor, listen for their identity and update instructions.
    if not in_contacts:
        identity_input = input("Simulated microphone input for identity - Please state your identity: ").strip()
        identity = call_llm_identity_endpoint(identity_input)
        print(f"Identified as: {identity}")
        # Update instructions to include the identified identity.
        instructions += f" Visitor has identified themselves as {identity}. "
        # Optionally, play a follow-up audio using the identity information.
        llm_audio = call_llm_endpoint(identity_input, instructions)
        if llm_audio:
            print("Playing LLM-generated audio for identity confirmation...")
        else:
            print("Failed to generate LLM audio for identity confirmation.")

    # Step 5: Enter a conversation loop until the user stops.
    # Here we accumulate conversation context into the instructions.
    while True:
        user_input = input("Simulated microphone input - What did the person say? (type 'exit' or 'quit' to stop): ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting conversation loop.")
            break

        # Append the new user input to the conversation context.
        instructions += f" Visitor said: '{user_input}'. "
        print("Updated instructions for LLM:")
        print(instructions)

        # Call the LLM endpoint using the updated, accumulated instructions.
        llm_audio = call_llm_endpoint(user_input, instructions)
        if llm_audio:
            print("Playing LLM-generated audio...")
        else:
            print("Failed to generate LLM audio.")

if __name__ == "__main__":
    main_flow()
