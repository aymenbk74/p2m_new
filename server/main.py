import os
import json
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
from google import genai
from sqlalchemy import or_
from sqlalchemy.orm import Session
from database import get_db
from models import Product

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = []

def parse_gemini_filters(text: str) -> dict:
    """Extract JSON filters from Gemini response."""
    try:
        clean_text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except json.JSONDecodeError:
        print(f"Failed to parse JSON: {text}")
        return {}
    except Exception as e:
        print(f"Error parsing filters: {e}")
        return {}

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        # --- AI & SEARCH LOGIC WITH BACKUP ---
        filters = {}
        ai_reply_text = ""
        
        try:
            # 1. Try Gemini Analysis
            analysis_prompt = f"""
            Tu es un expert e-commerce. Analyse cette requête : "{request.message}"
            
            EXTRAIT les filtres sous format JSON strict :
            {{
                "search": "mots-clés principaux (ex: robe rouge)",
                "max_price": nombre ou null (ex: 50)
            }}
            Réponds UNIQUEMENT le JSON.
            """
            analysis_response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=analysis_prompt
            )
            filters = parse_gemini_filters(analysis_response.text)
            print(f"🔍 [AI] Filtres extraits : {filters}")
            
        except Exception as e:
            print(f"⚠️ [AI WARNING] Gemini Analysis Failed: {e}")
            print("🔄 Switching to Keyword Search Fallback")
            # Simple Fallback Logic
            msg_lower = request.message.lower()
            filters["search"] = msg_lower # Use whole message as search term
            filters["max_price"] = None

        # 2. Query Database
        query = db.query(Product)
        
        search_term = filters.get("search")
        if search_term:
            query = query.filter(
                or_(
                    Product.name.ilike(f"%{search_term}%"),
                    Product.description.ilike(f"%{search_term}%"),
                    Product.category.ilike(f"%{search_term}%"),
                    Product.brand.ilike(f"%{search_term}%") # Added Brand search
                )
            )
            
        products_found = query.limit(5).all()
        
        # Prepare product list
        products_data = []
        for p in products_found:
            # Get available sizes from variants with positive stock
            available_sizes = [v.size for v in p.variants if v.stock_quantity > 0]
            
            # Get first variant for price/image
            variant = p.variants[0] if p.variants else None
            price = variant.price if variant else 0
            
            products_data.append({
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "price": float(price),
                "image": p.image_url,
                "sizes": available_sizes # New field
            })

        # 3. Generate Response (AI or Fallback)
        try:
           # Restore History
            formatted_history = []
            for msg in request.history:
                role = "user" if msg.get("role") == "user" else "model"
                content = msg.get("parts", "")
                formatted_history.append({"role": role, "parts": [{"text": content}]})

            chat_session = client.chats.create(
                model="gemini-2.5-flash",
                config={
                    "system_instruction": f"Tu es un assistant shopping. J'ai trouvé {len(products_data)} produits. Présente-les."
                },
                history=formatted_history
            )
            reply_response = chat_session.send_message(
                f"Produits trouvés : {json.dumps(products_data)}. Requête client: {request.message}"
            )
            ai_reply_text = reply_response.text

        except Exception as e:
            print(f"⚠️ [AI WARNING] Gemini Chat Failed: {e}")
            if len(products_data) > 0:
                ai_reply_text = f"✨ J'ai trouvé {len(products_data)} articles qui pourraient vous plaire ! Jetez un œil ci-dessous. 👇"
            else:
                ai_reply_text = "Désolé, je n'ai rien trouvé pour le moment. Essayez une autre recherche (ex: 'Robe', 'Manteau')."

        return {
            "reply": ai_reply_text,
            "products": products_data
        }

    except Exception as e:
        print(f"DEBUG ERROR: {e}")
        # In production, don't expose detail
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)