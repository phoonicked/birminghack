from playsound import playsound

def play_audio(filename):
    """
    Plays the specified audio file.
    """
    if filename:
        playsound(filename)
    else:
        print("No audio to play.")
