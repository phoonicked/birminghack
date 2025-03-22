from flask import Flask
from routes.tts_routes import tts_bp
from routes.llm_routes import llm_bp

def create_app():
    app = Flask(__name__)
    
    app.register_blueprint(tts_bp)
    app.register_blueprint(llm_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
