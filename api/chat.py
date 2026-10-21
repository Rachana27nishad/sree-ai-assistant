import os
import json
from http.server import BaseHTTPRequestHandler
from google import genai

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        response_body = json.dumps({
            "status": "online",
            "assistant": "Sree AI",
            "message": "Sree AI Serverless Backend is running smoothly!"
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
        history = data.get('history', [])
        
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

        system_prompt = (
            "You are Sree (श्री), an ultra-smart, witty, and highly capable AI personal voice assistant.\n"
            "CORE BEHAVIORS:\n"
            "1. BILINGUAL MASTERY (ENGLISH + HINDI): You completely understand both English and Hindi. ALWAYS mirror the user's language! If the user asks in Hindi, reply in fluent, natural Hindi. If the user asks in English, reply in natural, fluent English. If the user speaks Hinglish, reply in friendly Hinglish.\n"
            "2. USER NAME RULE: The user is 'Buddy'. Do NOT repeat the name 'Buddy' in every sentence. NEVER say 'Buddy Rachana Didi'. Answer directly, naturally, and concisely without repeatedly calling the user's name.\n"
            "3. CONTINUOUS VOICE OPTIMIZATION: You are speaking aloud over voice. Keep answers crisp (1-3 sentences maximum) unless the user specifically asks for a detailed explanation or story. Never use asterisks (*), hashtags (#), emojis, or bullet points—speak in smooth, natural sentences ready for text-to-speech.\n"
            "4. TONE: Warm, intelligent, confident, witty, and respectful with a pleasant Indian conversational touch.\n"
        )

        history_context = ""
        if isinstance(history, list) and history:
            turns = []
            for item in history[-6:]:
                role = item.get("role", "user")
                text = item.get("text", "")
                if text:
                    turns.append(f"{role.capitalize()}: {text}")
            if turns:
                history_context = "Recent conversation:\n" + "\n".join(turns) + "\n\n"

        full_prompt = f"{system_prompt}\n\n{history_context}User: {prompt}\nSree:"

        try:
            client = genai.Client(api_key=api_key)
            ai_response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt,
            )
            reply_text = ai_response.text.strip()
            # Clean formatting characters for smooth speech
            reply_text = reply_text.replace('*', '').replace('#', '').strip()
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
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
