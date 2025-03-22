import requests

def call_tts_endpoint(text, filename="temp_tts.wav"):
    """
    Calls your TTS endpoint with the provided text.
    Returns the filename where the WAV file is saved.
    """
    url = "http://localhost:5000/tts"
    params = {"text": text}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        return filename
    else:
        print("Error calling TTS endpoint:", response.text)
        return None
