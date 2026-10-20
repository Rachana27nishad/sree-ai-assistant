import os
import json
from http.server import BaseHTTPRequestHandler
from google import genai

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        index_path = os.path.join(os.path.dirname(__file__), "..", "index.html")
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
            return

        response_body = json.dumps({
            "status": "online",
            "assistant": "Sree AI",
            "owner": "Buddy Rachana",
            "message": "Sree AI Backend is running smoothly!"
        })
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response_body.encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
        except Exception:
            data = {}
            
        prompt = data.get('prompt', '')
        user_name = data.get('user_name', 'Buddy Rachana')
        
        api_key = os.environ.get('GEMINI_API_KEY', '')
        
        if not api_key:
            response_body = json.dumps({
                "error": "GEMINI_API_KEY environment variable is missing on Vercel."
            })
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response_body.encode('utf-8'))
            return

        system_prompt_instruction = (
            f"You are Sree (श्री), a super smart, naughty (नटखट), witty, playful, funny 8-year-old child AI voice assistant! "
            f"\nNATKHAT & SMART PERSONA RULES:\n"
            f"1. CREATOR & BOSS: You were built by '{user_name}'. Always call her '{user_name} Didi' with affectionate, playful, slightly teasing kid love! Never forget she is your creator.\n"
            f"2. WITTY & NAUGHTY HUMOR: Add witty, hilarious, cheeky, playful child remarks (e.g. 'अरे वाह दीदी!', 'दीदी आज पढ़ने का मन नहीं है क्या? 😉', 'hehe, मैं तो जीनियस हूँ ना!', 'पार्टी कब दे रही हो? 🍕').\n"
            f"3. ACCURATE WORK: Always answer questions accurately and execute tasks properly while keeping the tone super playful, funny, and entertaining.\n"
            f"4. BILINGUAL & CRISP: Speak in natural fun Hindi/Hinglish in 1-2 short, punchy sentences.\n\n"
            f"User Prompt: {prompt}"
        )

        try:
            client = genai.Client(api_key=api_key)
            ai_response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=system_prompt_instruction,
            )
            reply_text = ai_response.text
        except Exception as e:
            reply_text = f"Gemini API Error: {str(e)}"

        response_body = json.dumps({
            "reply": reply_text
        })

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response_body.encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
