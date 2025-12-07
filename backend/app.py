"""
Flask application entry point for Career Roadmap Generator API.
"""
import logging
import os
from flask import Flask, jsonify
from flask_cors import CORS
from api.routes import api_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure CORS for frontend
# Get allowed origins from environment variable or use defaults
allowed_origins = os.getenv('ALLOWED_ORIGINS', '').split(',') if os.getenv('ALLOWED_ORIGINS') else []
# Add default localhost origins for development
default_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]
# Combine and filter out empty strings
all_origins = [origin.strip() for origin in allowed_origins + default_origins if origin.strip()]

CORS(app, resources={
    r"/api/*": {
        "origins": all_origins,
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configure session
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'

# Register API blueprint
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'message': 'Career Roadmap Generator API',
        'version': '1.0.0'
    })

# Global error handler
@app.errorhandler(Exception)
def handle_error(error):
    """Global error handler for all exceptions."""
    logger.error(f"Unhandled error: {str(error)}", exc_info=True)
    
    error_type = type(error).__name__
    status_code = 500
    
    # Map specific errors to status codes
    if hasattr(error, 'code'):
        status_code = error.code
    elif '404' in str(error) or 'Not Found' in str(error):
        status_code = 404
    elif '400' in str(error) or 'Bad Request' in str(error):
        status_code = 400
    
    return jsonify({
        'success': False,
        'message': 'An unexpected error occurred. Please try again.',
        'error': error_type,
        'error_message': str(error) if app.config.get('DEBUG') else 'Internal server error'
    }), status_code

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'message': 'Endpoint not found',
        'error': 'NOT_FOUND'
    }), 404

@app.errorhandler(400)
def bad_request(error):
    """Handle 400 errors."""
    return jsonify({
        'success': False,
        'message': 'Bad request',
        'error': 'BAD_REQUEST'
    }), 400

def check_openrouter_status():
    """Check if OpenRouter API is accessible."""
    try:
        from services.ai_service import AIService
        ai_service = AIService()
        return True, ai_service.MODEL_NAME
    except Exception as e:
        return False, str(e)

if __name__ == '__main__':
    # Check OpenRouter status on startup
    logger.info("=" * 60)
    logger.info("Starting Career Roadmap Generator API")
    logger.info("=" * 60)
    
    api_ok, model_info = check_openrouter_status()
    
    if api_ok:
        logger.info(f"✓ OpenRouter API: Connected")
        logger.info(f"✓ Model: {model_info}")
    else:
        logger.warning(f"✗ OpenRouter API: Not connected - {model_info}")
        logger.warning("  Make sure OPENROUTER_API_KEY is set in .env file")
    
    logger.info("=" * 60)
    logger.info("Available Endpoints:")
    logger.info("  GET  /                    - Health check")
    logger.info("  GET  /api/health          - API & OpenRouter status")
    logger.info("  POST /api/upload-resume   - Upload and parse resume")
    logger.info("  POST /api/analyze-resume  - Analyze resume with AI")
    logger.info("  POST /api/recommend-domains - Get domain recommendations")
    logger.info("  POST /api/generate-roadmap - Generate learning roadmap")
    logger.info("  POST /api/chat            - AI chat assistant")
    logger.info("=" * 60)
    logger.info("Server starting on http://localhost:5000")
    logger.info("Press CTRL+C to quit")
    logger.info("=" * 60)
    
    app.run(debug=True, port=5000, host='0.0.0.0')

