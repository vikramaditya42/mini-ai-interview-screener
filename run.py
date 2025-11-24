"""
Convenience script to run the application.
"""
import os
import sys

def check_env_file():
    """Check if .env file exists."""
    if not os.path.exists('.env'):
        print("❌ Error: .env file not found!")
        print("📝 Please copy .env.example to .env and add your GEMINI_API_KEY")
        print("\nRun: cp .env.example .env")
        sys.exit(1)
    
    # Check if API key is set
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv('GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY') == 'your_gemini_api_key_here':
        print("❌ Error: GEMINI_API_KEY not configured!")
        print("📝 Please edit .env file and add your actual Gemini API key")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Starting AI Interview Screener...")
    
    check_env_file()
    
    print("✅ Environment configured")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\n")
    
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
