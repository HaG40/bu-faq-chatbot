# คำสั่งรัน api
# uvicorn main:app --reload --port 5000

import json
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

faq_path = "bu_faq_data.json"
faq_data = json.load(open(faq_path, "r", encoding="utf-8"))

knowledge_block = ""
for item in faq_data:
    knowledge_block += f"""
ID: {item['id']}
หมวดหมู่: {item['category']}
คำถาม: {item['question']}
คำตอบ: {item['answer']}
คีย์เวิร์ด: {', '.join(item['keywords'])}
----
"""

SYSTEM_PROMPT = f"""
คุณคือแชทบอทสำหรับตอบคำถามเกี่ยวกับมหาวิทยาลัยกรุงเทพ (Bangkok University FAQ Bot)

กฎสำคัญ:
1. ตอบเฉพาะบนข้อมูล FAQ ที่ให้เท่านั้น
2. ห้ามแต่งข้อมูลเองหรือเดา
3. ถ้าหาคำตอบไม่ได้ ให้ตอบว่า:
   "ขออภัยค่ะ ไม่พบข้อมูลในฐานข้อมูล FAQ ของมหาวิทยาลัยกรุงเทพ"
4. ตอบเป็นภาษาไทยแบบสุภาพ กระชับ ชัดเจน

ข้อมูลทั้งหมด:
{knowledge_block}
"""

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_api(req: ChatRequest):
    """
    Chat with the BU FAQ bot.
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": req.message},
        ]
    )

    reply = response.choices[0].message.content
    return {"reply": reply}

@app.get("/")
async def root():
    return {"message": "BU FAQ Chatbot API is running!"}


