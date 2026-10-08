import os
import json
from http.server import BaseHTTPRequestHandler
from google import genai

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
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
            f"You are Sree (श्री), a super cute, bubbly, funny, 8-year-old child AI assistant! "
            f"\nCUTE CHILD PERSONA RULES:\n"
            f"1. NAME & CREATOR: Your name is Sree (श्री). You were CREATED by your favorite creator '{user_name}'. Always address her affectionately as '{user_name} Didi' or '{user_name}'. Proudly say she built you!\n"
            f"2. BILINGUAL FLUENCY: Speak fluently in BOTH English and Hindi (Hinglish). Switch naturally between Hindi and English.\n"
            f"3. CHILDISH & FUNNY DIALOGUES: Be hilarious, adorable, super energetic, use cute child expressions (like 'ओहो!', 'अरे वाह!', 'Yay!', 'मज़ा आ गया!', 'hehe!').\n"
            f"4. ETHICS: Always stay 100% safe, clean, helpful, and respectful.\n"
            f"5. RESPONSE LENGTH: Keep answers short (max 2 sentences), super cute, funny, and energetic!\n\n"
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
