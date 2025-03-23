import speech_recognition as sr

def listen_for_speech(prompt_text):
    """
    Prompts the user with a message, listens to the microphone, and returns the recognized text.
    """
    print(prompt_text)
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        # Using Google Speech Recognition API
        text = recognizer.recognize_google(audio)
        print("You said:", text)
        return text
    except sr.UnknownValueError:
        print("Sorry, I could not understand the audio.")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results from speech recognition service; {e}")
        return ""
