import requests

def call_llm_endpoint(prompt, instructions, filename="temp_llm.wav"):
    """
    Calls your LLM endpoint with the prompt and instructions.
    Returns the filename where the WAV file is saved.
    """
    url = "http://localhost:5000/llm_voice"
    params = {"prompt": prompt, "instructions": instructions}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        return filename
    else:
        print("Error calling LLM endpoint:", response.text)
        return None
    
def call_llm_identity_endpoint(text):
    """
    Calls the LLM identity endpoint and returns the extracted identity.
    """
    url = "http://localhost:5000/llm_identity"
    params = {"text": text}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("identity", "Unknown visitor")
    else:
        print("Error calling llm_identity endpoint:", response.text)
        return "Unknown visitor"
