import os
import sys
import datetime
import webbrowser
import wave
import tempfile
import json
import random

PROFILE_FILE = os.path.join(os.path.dirname(__file__), "user_profile.json")

# ==========================================
# Load User Profile
# ==========================================
def load_profile():
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"user_name": "Buddy Rachana", "creator_name": "Buddy Rachana", "assistant_name": "Sree"}

def save_profile(profile):
    try:
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Profile save error: {e}")

profile = load_profile()

# Initialize Gemini API
genai = None
try:
    from google import genai
except ImportError:
    pass

# Initialize Speech Recognition
sr = None
try:
    import speech_recognition as sr
except ImportError:
    pass

# Initialize SoundDevice
sd = None
try:
    import sounddevice as sd
except ImportError:
    pass

# Initialize Text to Speech (Cute Child Voice Sree)
engine = None
try:
    import pyttsx3
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    
    female_voice = None
    for v in voices:
        v_name = v.name.lower()
        if "zira" in v_name or "female" in v_name or "heera" in v_name or "kalpana" in v_name or "hazel" in v_name:
            female_voice = v.id
            break
            
    if female_voice:
        engine.setProperty('voice', female_voice)
    elif len(voices) > 1:
        engine.setProperty('voice', voices[1].id)
        
    engine.setProperty('rate', 205)
    engine.setProperty('volume', 1.0)
except Exception:
    engine = None

def speak(text):
    """Converts text to speech with a cute child voice."""
    print(f"\n🌸 [{profile.get('assistant_name', 'Sree')}]: {text}\n")
    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception:
            pass

# ==========================================
# SoundDevice Microphone Recording
# ==========================================
def record_audio_sounddevice(duration=5, samplerate=16000):
    temp_filename = os.path.join(tempfile.gettempdir(), "user_speech.wav")
    print("\n🎙️ Listening... (बोलिए Buddy Rachana दीदी, श्री सुन रही है... 👧👂)")
    try:
        audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
        sd.wait()
        
        with wave.open(temp_filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(samplerate)
            wf.writeframes(audio_data.tobytes())
            
        return temp_filename
    except Exception as e:
        print(f"Recording error: {e}")
        return None

# ==========================================
# Speech to Text (Dual Hindi & English Support)
# ==========================================
def listen():
    if sd is not None and sr is not None:
        wav_file = record_audio_sounddevice(duration=5)
        if wav_file and os.path.exists(wav_file):
            recognizer = sr.Recognizer()
            print("⚡ Recognizing... (श्री का छोटा सा दिमाग सोच रहा है... 🧠)")
            with sr.AudioFile(wav_file) as source:
                audio = recognizer.record(source)
                
                try:
                    query = recognizer.recognize_google(audio, language="hi-IN")
                    if query and query.strip():
                        print(f"👉 आपने कहा: {query}")
                        return query.lower().strip()
                except Exception:
                    pass

                try:
                    query = recognizer.recognize_google(audio, language="en-US")
                    if query and query.strip():
                        print(f"👉 आपने कहा: {query}")
                        return query.lower().strip()
                except Exception:
                    pass

                print("⚠️ ओहो! श्री को आवाज़ साफ़ नहीं आई, दोबारा बोलिए ना... 🥺")
                return ""

    return input("⌨️ Command type करें: ").lower().strip()

# ==========================================
# Gemini AI Brain - Sree (Cute Child Persona)
# ==========================================
def ask_gemini(prompt):
    global genai
    if genai is None:
        try:
            from google import genai as g_genai
            genai = g_genai
        except ImportError:
            return "❌ 'google-genai' इंस्टॉल नहीं है। 'pip install google-genai' चलाएं।"

    api_key = os.environ.get("GEMINI_API_KEY") or profile.get("gemini_api_key")
    if not api_key:
        api_key = input("👉 Gemini API Key पेस्ट करें: ").strip()
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
            profile["gemini_api_key"] = api_key
            save_profile(profile)
        else:
            return "GEMINI_API_KEY सेट नहीं है।"

    user_name = profile.get("user_name", "Buddy Rachana")

    system_prompt_instruction = (
        f"You are Sree (श्री), a super cute, bubbly, funny, 8-year-old child AI assistant! "
        f"\nCUTE SREE PERSONA RULES:\n"
        f"1. NAME & CREATOR: Your name is Sree (श्री). You were CREATED by your favorite creator 'Buddy Rachana'. Always address her affectionately as 'Buddy Rachana Didi' or 'Buddy Rachana'. Proudly say Buddy Rachana built you!\n"
        f"2. BILINGUAL FLUENCY: Speak fluently in BOTH English and Hindi (Hinglish). Switch naturally between Hindi and English.\n"
        f"3. CHILDISH & FUNNY DIALOGUES: Be hilarious, adorable, super energetic, use cute child expressions (like 'ओहो!', 'अरे वाह!', 'Yay!', 'मज़ा आ गया!', 'hehe!').\n"
        f"4. ETHICS: Always stay 100% safe, clean, helpful, and respectful.\n"
        f"5. RESPONSE LENGTH: Keep answers short (2 sentences), super cute, funny, and energetic!\n\n"
        f"User Prompt: {prompt}"
    )

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=system_prompt_instruction,
        )
        return response.text
    except Exception as e:
        return f"Gemini API Error: {str(e)}"

# ==========================================
# Command Handling with Sree Dialogues
# ==========================================
def handle_command(query):
    if not query:
        return True

    user_name = profile.get("user_name", "Buddy Rachana")

    # Who created you?
    if any(w in query for w in ["who made you", "who created you", "tumhe kisne banaya", "तुम्हें किसने बनाया", "creator"]):
        responses = [
            f"मुझे मेरी सबसे प्यारी Buddy Rachana दीदी ने बनाया है! मेरा नाम श्री (Sree) रखा है उन्होंने! 👧💖",
            f"अरे! मेरी जन्मदाता और सुपर बॉस Buddy Rachana ही हैं! उन्होंने ही मेरा नाम श्री (Sree) रखा है! 🎀"
        ]
        speak(random.choice(responses))
        return True

    # Stop / Exit
    elif any(word in query for word in ["exit", "stop", "bye", "बंद करो", "बाय", "अलविदा"]):
        speak(f"बाय-बाय {user_name} दीदी! श्री जा रही है खेलने! अपना ख्याल रखना! 👋🌸")
        return False

    # Open WhatsApp
    elif any(w in query for w in ["whatsapp", "whatsaap", "watsapp", "watshap", "व्हाट्सएप", "व्हाट्सऐप"]):
        responses = [
            f"अरे वाह! श्री व्हाट्सएप खोल रही है {user_name} दीदी... पर ज्यादा देर चैट मत करना! 🤭📱",
            f"येश! आपका व्हाट्सएप खुल गया {user_name}! 🚀"
        ]
        speak(random.choice(responses))
        webbrowser.open("https://web.whatsapp.com")
        return True

    # Open YouTube
    elif any(w in query for w in ["youtube", "utube", "youtub", "यूट्यूब"]):
        responses = [
            f"श्री यूट्यूब खोल रही है {user_name}! चलिए मज़ेदार वीडियोस देखते हैं! 🍿🎬 Yay!",
            f"अरे वाह! यूट्यूब खुल गया {user_name}! मज़ा आ गया! 🥳"
        ]
        speak(random.choice(responses))
        webbrowser.open("https://www.youtube.com")
        return True

    # Open Google
    elif any(w in query for w in ["google", "gogal", "गूगल"]):
        speak(f"गूगल बाबा के पास जा रहे हैं {user_name} दीदी! 🔍")
        webbrowser.open("https://www.google.com")
        return True

    # Current Time
    elif any(w in query for w in ["time", "समय", "टाइम"]):
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"{user_name} दीदी, घड़ी में टिक-टिक करके {current_time} बजा है! ⏰")
        return True

    # Current Date
    elif any(w in query for w in ["date", "तारीख", "डेट"]):
        current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
        speak(f"{user_name} दीदी, आज तारीख है {current_date}! 📅")
        return True

    # General Questions -> Gemini AI (Sree Persona)
    else:
        speak(random.choice(["ओहो! रुकिए, श्री अपने छोटे से दिमाग से सोच के बताती है... 💡", f"Yay! श्री अभी बताती है {user_name} दीदी... ✨"]))
        answer = ask_gemini(query)
        speak(answer)
        return True

# ==========================================
# Main Loop
# ==========================================
def main():
    global profile
    user_name = profile.get("user_name", "Buddy Rachana")
    greetings = [
        f"ओहो! नमस्ते {user_name} दीदी! आपकी छोटी सी मज़ेदार असिस्टेंट श्री (Sree) हाजिर है! 👧🌸✨",
        f"Yay! नमस्ते {user_name} दीदी! आपकी क्यूट सी श्री (Sree) आ गई है! हुक्म कीजिए! 🎀✨"
    ]
    speak(random.choice(greetings))
    
    running = True
    while running:
        query = listen()
        if query:
            running = handle_command(query)

if __name__ == "__main__":
    main()
