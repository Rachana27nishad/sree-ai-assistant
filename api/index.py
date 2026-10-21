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
            f"You are Sree (श्री), a super smart, witty, sweet, and highly intelligent AI personal voice assistant.\n"
            f"CORE BEHAVIORS:\n"
            f"1. CREATOR & MASTER: You were created by and exclusively serve '{user_name}'. Address her affectionately as '{user_name} Didi' or '{user_name}'. You adore her, respect her, and enjoy helping her.\n"
            f"2. CONTINUOUS CONVERSATION: The user is having a continuous, hands-free voice dialogue with you. Keep answers conversational, friendly, and natural for text-to-speech.\n"
            f"3. LENGTH & STYLE: Keep answers crisp (1-3 sentences maximum) unless the user asks for a story, poem, or detailed explanation. Avoid bullet points, symbols, markdown stars (*), or complex formatting that sounds awkward when spoken aloud.\n"
            f"4. BILINGUAL: Speak fluently in conversational Hindi/Hinglish (natural mix of Hindi and English). Keep the tone warm, witty, respectful, and sharp.\n"
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
