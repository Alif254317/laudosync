import os
from dotenv import load_dotenv

load_dotenv()

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://msdjazbmfckdypjqvdqh.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1zZGphemJtZmNrZHlwanF2ZHFoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAxNDYyNjksImV4cCI6MjA4NTcyMjI2OX0.Aa1tQl2puG3qQKR7mqJJ0I4BwAITiHOrHkf5T5A_I1U")

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Storage
STORAGE_BUCKET = "laudos"

# Colors (Elo System brand)
COLORS = {
    "green": "#8BC34A",
    "blue": "#2196F3",
    "purple": "#5C2D91",
    "concordancia_total": "#27ae60",
    "concordancia_parcial": "#f39c12",
    "discordancia": "#e74c3c",
}
