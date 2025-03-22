import uuid
import wave
from pyneuphonic.player import AudioPlayer
from pyneuphonic import TTSConfig
from neuphonic_client import neuphonic_client

def generate_tts_wav(text, speed=1.05, lang_code="en", voice_id=None):
    """
    Generate a WAV file from text using Neuphonic SSE.
    Returns the filename where the WAV was saved.
    """
    sse_client = neuphonic_client.tts.SSEClient()
    
    tts_config = TTSConfig(
        speed=speed,
        lang_code=lang_code,
        voice_id=voice_id
    )

    with AudioPlayer() as player:
        response = sse_client.send(text, tts_config=tts_config)
        player.play(response)

        player.save_audio(f'tts_output_{uuid.uuid4().hex}output.wav')
    
    return response
