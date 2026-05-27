import streamlit.components.v1 as components
import html


def speech_work(speech):
    """
    Create a Streamlit HTML button that reads aloud the given text using browser speech synthesis.

    Args:
        speech (str): The text to be spoken aloud.
    """
    # Replace newlines and tabs for smoother speech output
    processed_text = speech.replace("\n", ". ").replace("\t", "    ")
    # Escape HTML special characters to prevent injection issues
    safe_answer = html.escape(processed_text, quote=True)

    # Embed custom HTML button in Streamlit that triggers speech synthesis on click
    components.html(f"""
        <button onclick="var msg = new SpeechSynthesisUtterance('{safe_answer}');
                        window.speechSynthesis.cancel();  // Cancel any ongoing speech
                        msg.rate = 1.1;    // Set speech rate
                        msg.pitch = 1.5;   // Set speech pitch
                        msg.volume = 1.0;  // Set volume
                        window.speechSynthesis.speak(msg);">  
                        🔊 Read Me
        </button>
        """, height=100)
