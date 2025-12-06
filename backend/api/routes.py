"""
API routes for Career Roadmap Generator.
"""
import logging
import io
import uuid
import time
from flask import Blueprint, request, jsonify, session
from services.resume_parser import ResumeParser
from services.ai_service import AIService
from services.roadmap_generator import RoadmapGenerator
from utils.file_handler import FileHandler

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

# Initialize services
resume_parser = ResumeParser()
ai_service = AIService()
roadmap_generator = RoadmapGenerator()
file_handler = FileHandler()

# In-memory storage for parsed resumes (session-based in production)
# Using a simple dict keyed by session ID
resume_storage = {}

def get_session_id():
    """Get or create session ID."""
    if hasattr(session, 'get') and session.get('session_id'):
        return session.get('session_id')
    return None

def get_stored_resume(session_id=None):
    """Get stored resume data for session."""
    sid = session_id or get_session_id()
    if sid and sid in resume_storage:
        return resume_storage[sid]
    return None

@api_bp.route('/upload-resume', methods=['POST'])
def upload_resume():
    """
    Upload and parse resume file.
    Expected: multipart/form-data with 'file' field
    Returns: Parsed resume data
    
    Response Format:
    {
        "success": true,
        "data": {
            "raw_text": "...",
            "word_count": 450,
            "file_name": "john_resume.pdf",
            "file_type": "pdf"
        },
        "message": "Resume uploaded successfully"
    }
    """
    try:
        logger.info("Received resume upload request")
        
        # Check if file is present in request
        if 'file' not in request.files:
            logger.warning("No file in request")
            return jsonify({
                'success': False,
                'message': 'No file provided. Please upload a resume file.',
                'error': 'MISSING_FILE'
            }), 400
        
        file = request.files['file']
        filename = file.filename
        
        # Check if filename is provided
        if not filename or filename == '':
            logger.warning("Empty filename in request")
            return jsonify({
                'success': False,
                'message': 'No file selected. Please choose a file to upload.',
                'error': 'EMPTY_FILENAME'
            }), 400
        
        logger.info(f"Processing file: {filename}")
        
        # Validate file type
        if not file_handler.allowed_file(filename):
            logger.warning(f"Invalid file type: {filename}")
            return jsonify({
                'success': False,
                'message': f'Invalid file type. Allowed types: PDF, DOCX, TXT',
                'error': 'INVALID_FILE_TYPE'
            }), 400
        
        # Read file into memory
        try:
            file_content = file.read()
            file_stream = io.BytesIO(file_content)
        except Exception as e:
            logger.error(f"Error reading file: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Failed to read file. File may be corrupted.',
                'error': 'FILE_READ_ERROR'
            }), 400
        
        # Validate file size
        try:
            file_handler.validate_file_size(file_stream)
        except ValueError as e:
            logger.warning(f"File size validation failed: {str(e)}")
            return jsonify({
                'success': False,
                'message': str(e),
                'error': 'FILE_SIZE_ERROR'
            }), 400
        
        # Parse resume
        try:
            parsed_data = resume_parser.parse_resume(file_stream, filename)
            logger.info(f"Resume parsed successfully: {filename}, Word count: {parsed_data['word_count']}")
        except ValueError as e:
            logger.error(f"Resume parsing failed: {str(e)}")
            return jsonify({
                'success': False,
                'message': str(e),
                'error': 'PARSE_ERROR'
            }), 400
        except Exception as e:
            logger.error(f"Unexpected error during parsing: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Failed to parse resume file. Please ensure the file is not corrupted.',
                'error': 'PARSE_ERROR'
            }), 500
        
        # Store parsed data in-memory (using session ID if available, otherwise use a simple key)
        session_id = get_session_id()
        if not session_id:
            # Generate a simple session ID for in-memory storage
            session_id = str(uuid.uuid4())
            if hasattr(session, '__setitem__'):
                session['session_id'] = session_id
        
        resume_storage[session_id] = parsed_data
        logger.info(f"Resume data stored for session: {session_id}")
        
        # Return success response
        return jsonify({
            'success': True,
            'data': {
                'raw_text': parsed_data['raw_text'],
                'word_count': parsed_data['word_count'],
                'file_name': parsed_data['file_name'],
                'file_type': parsed_data['file_type']
            },
            'message': 'Resume uploaded successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Unexpected error in upload_resume: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred. Please try again.',
            'error': 'INTERNAL_ERROR'
        }), 500

@api_bp.route('/analyze-resume', methods=['POST'])
def analyze_resume():
    """
    Analyze resume text using AI.
    Accepts: JSON with { "resume_text": "..." }
    Returns: Structured profile data from AI analysis
    """
    try:
        logger.info("Received resume analysis request")
        
        # Get JSON data from request
        if not request.is_json:
            return jsonify({
                'success': False,
                'message': 'Request must be JSON format',
                'error': 'INVALID_FORMAT'
            }), 400
        
        data = request.get_json()
        
        # Validate resume_text is present
        if 'resume_text' not in data:
            return jsonify({
                'success': False,
                'message': 'Missing required field: resume_text',
                'error': 'MISSING_FIELD'
            }), 400
        
        resume_text = data['resume_text']
        
        # Validate text is not empty
        if not resume_text or not resume_text.strip():
            return jsonify({
                'success': False,
                'message': 'resume_text cannot be empty',
                'error': 'EMPTY_TEXT'
            }), 400
        
        # Check text length (reasonable limit)
        if len(resume_text) > 50000:  # 50KB limit
            return jsonify({
                'success': False,
                'message': 'Resume text is too long (max 50,000 characters)',
                'error': 'TEXT_TOO_LONG'
            }), 400
        
        logger.info(f"Analyzing resume text ({len(resume_text)} characters)")
        
        # Call AI service to analyze resume
        try:
            profile = ai_service.analyze_resume(resume_text)
            logger.info("Resume analysis completed successfully")
            
            return jsonify({
                'success': True,
                'profile': profile,
                'message': 'Resume analyzed successfully'
            }), 200
            
        except ValueError as e:
            logger.error(f"AI analysis error: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Analysis failed: {str(e)}',
                'error': 'ANALYSIS_ERROR'
            }), 400
        except TimeoutError as e:
            logger.error(f"AI analysis timeout: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Analysis timed out. Please try again.',
                'error': 'TIMEOUT_ERROR'
            }), 504
        
    except Exception as e:
        logger.error(f"Unexpected error in analyze_resume: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred during analysis.',
            'error': 'INTERNAL_ERROR'
        }), 500

@api_bp.route('/recommend-domains', methods=['POST'])
def recommend_domains():
    """
    Recommend technology domains based on user profile.
    Accepts: JSON with profile data
    Returns: AI-recommended domains and tools
    """
    try:
        logger.info("Received domain recommendation request")
        
        # Get JSON data from request
        if not request.is_json:
            return jsonify({
                'success': False,
                'message': 'Request must be JSON format',
                'error': 'INVALID_FORMAT'
            }), 400
        
        data = request.get_json()
        
        # Validate profile is present
        if 'profile' not in data:
            return jsonify({
                'success': False,
                'message': 'Missing required field: profile',
                'error': 'MISSING_FIELD'
            }), 400
        
        profile = data['profile']
        
        # Validate profile structure
        if not isinstance(profile, dict):
            return jsonify({
                'success': False,
                'message': 'profile must be an object',
                'error': 'INVALID_PROFILE'
            }), 400
        
        # Ensure required profile fields exist (with defaults)
        required_fields = ['skills', 'experience_level', 'years_of_experience', 'domains']
        for field in required_fields:
            if field not in profile:
                logger.warning(f"Missing profile field: {field}, using default")
                if field in ['skills', 'domains']:
                    profile[field] = []
                elif field == 'years_of_experience':
                    profile[field] = 0
                else:
                    profile[field] = 'Unknown'
        
        logger.info(f"Generating recommendations for profile: {profile.get('experience_level', 'Unknown')} level")
        
        # Call AI service to recommend domains
        try:
            recommendations = ai_service.recommend_domains(profile)
            logger.info("Domain recommendations generated successfully")
            
            return jsonify({
                'success': True,
                'recommendations': recommendations.get('recommendations', []),
                'message': 'Domain recommendations generated successfully'
            }), 200
            
        except ValueError as e:
            logger.error(f"Domain recommendation error: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Recommendation failed: {str(e)}',
                'error': 'RECOMMENDATION_ERROR'
            }), 400
        except TimeoutError as e:
            logger.error(f"Domain recommendation timeout: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Recommendation timed out. Please try again.',
                'error': 'TIMEOUT_ERROR'
            }), 504
        
    except Exception as e:
        logger.error(f"Unexpected error in recommend_domains: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred during recommendation.',
            'error': 'INTERNAL_ERROR'
        }), 500

@api_bp.route('/generate-roadmap', methods=['POST'])
def generate_roadmap():
    """
    Generate personalized learning roadmap.
    Accepts: Complete user data (profile, selected_tools, preferences)
    Returns: Complete personalized roadmap
    """
    try:
        logger.info("Received roadmap generation request")
        
        # Get JSON data from request
        if not request.is_json:
            return jsonify({
                'success': False,
                'message': 'Request must be JSON format',
                'error': 'INVALID_FORMAT'
            }), 400
        
        data = request.get_json()
        
        # Validate all required fields
        required_fields = ['profile', 'selected_tools', 'hours_per_week']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'message': f'Missing required fields: {", ".join(missing_fields)}',
                'error': 'MISSING_FIELDS'
            }), 400
        
        # Extract and validate fields
        profile = data['profile']
        selected_tools = data['selected_tools']
        hours_per_week = data['hours_per_week']
        learning_style = data.get('learning_style', 'Balanced')
        deadline = data.get('deadline', 'Flexible')
        
        # Validate types and values
        if not isinstance(profile, dict):
            return jsonify({
                'success': False,
                'message': 'profile must be an object',
                'error': 'INVALID_PROFILE'
            }), 400
        
        if not isinstance(selected_tools, list) or len(selected_tools) == 0:
            return jsonify({
                'success': False,
                'message': 'selected_tools must be a non-empty array',
                'error': 'INVALID_TOOLS'
            }), 400
        
        if not isinstance(hours_per_week, (int, float)) or hours_per_week <= 0:
            return jsonify({
                'success': False,
                'message': 'hours_per_week must be a positive number',
                'error': 'INVALID_HOURS'
            }), 400
        
        logger.info(f"Generating roadmap: {len(selected_tools)} tools, {hours_per_week} hrs/week")
        
        # Prepare user data for AI service
        user_data = {
            'profile': profile,
            'selected_tools': selected_tools,
            'hours_per_week': hours_per_week,
            'learning_style': learning_style,
            'deadline': deadline
        }
        
        # Call AI service to generate roadmap
        try:
            roadmap = ai_service.generate_roadmap(user_data)
            logger.info("Roadmap generation completed successfully")
            
            # Calculate estimated completion date if not provided
            if 'estimated_completion_date' not in roadmap and 'total_duration_weeks' in roadmap:
                from datetime import datetime, timedelta
                weeks = roadmap.get('total_duration_weeks', 0)
                if weeks > 0:
                    completion_date = datetime.now() + timedelta(weeks=weeks)
                    roadmap['estimated_completion_date'] = completion_date.strftime('%Y-%m-%d')
            
            return jsonify({
                'success': True,
                'roadmap': roadmap,
                'message': 'Roadmap generated successfully'
            }), 200
            
        except ValueError as e:
            logger.error(f"Roadmap generation error: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Roadmap generation failed: {str(e)}',
                'error': 'ROADMAP_ERROR'
            }), 400
        except TimeoutError as e:
            logger.error(f"Roadmap generation timeout: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Roadmap generation timed out. This can take 10-20 seconds. Please try again.',
                'error': 'TIMEOUT_ERROR'
            }), 504
        
    except Exception as e:
        logger.error(f"Unexpected error in generate_roadmap: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred during roadmap generation.',
            'error': 'INTERNAL_ERROR'
        }), 500

# In-memory conversation history storage
conversation_history = {}

@api_bp.route('/chat', methods=['POST'])
def chat():
    """
    AI chat endpoint for roadmap questions and guidance.
    Accepts: { "message": "...", "context": {...} }
    Returns: AI assistant response
    """
    try:
        logger.info("Received chat request")
        
        # Get JSON data from request
        if not request.is_json:
            return jsonify({
                'success': False,
                'message': 'Request must be JSON format',
                'error': 'INVALID_FORMAT'
            }), 400
        
        data = request.get_json()
        
        # Validate message is present
        if 'message' not in data:
            return jsonify({
                'success': False,
                'message': 'Missing required field: message',
                'error': 'MISSING_FIELD'
            }), 400
        
        message = data['message']
        context = data.get('context', {})
        
        # Validate message is not empty
        if not message or not message.strip():
            return jsonify({
                'success': False,
                'message': 'message cannot be empty',
                'error': 'EMPTY_MESSAGE'
            }), 400
        
        # Get or create session ID for conversation history
        session_id = get_session_id()
        if not session_id:
            session_id = str(uuid.uuid4())
            if hasattr(session, '__setitem__'):
                session['session_id'] = session_id
        
        # Get conversation history for this session
        if session_id not in conversation_history:
            conversation_history[session_id] = []
        
        history = conversation_history[session_id]
        
        # Prepare context with history
        chat_context = {
            'profile': context.get('profile', {}),
            'roadmap_summary': context.get('roadmap_summary', ''),
            'history': history[-10:]  # Last 10 exchanges
        }
        
        logger.info(f"Processing chat message (session: {session_id[:8]}...)")
        
        # Call AI service for chat response
        try:
            response_text = ai_service.chat_assistant(message, chat_context)
            
            # Update conversation history
            history.append({
                'user': message,
                'assistant': response_text
            })
            # Keep only last 20 exchanges to avoid memory issues
            conversation_history[session_id] = history[-20:]
            
            logger.info("Chat response generated successfully")
            
            return jsonify({
                'success': True,
                'response': response_text,
                'message': 'Chat response generated successfully'
            }), 200
            
        except ValueError as e:
            logger.error(f"Chat error: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Chat failed: {str(e)}',
                'error': 'CHAT_ERROR'
            }), 400
        except TimeoutError as e:
            logger.error(f"Chat timeout: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Chat timed out. Please try again.',
                'error': 'TIMEOUT_ERROR'
            }), 504
        
    except Exception as e:
        logger.error(f"Unexpected error in chat: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred during chat.',
            'error': 'INTERNAL_ERROR'
        }), 500

@api_bp.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint - Check if API and OpenRouter are working.
    """
    try:
        logger.info("Health check requested")
        
        # Test OpenRouter API connection
        api_status = 'unknown'
        api_error = None
        
        try:
            # Simple test - just check if service is initialized
            if ai_service and hasattr(ai_service, 'client'):
                api_status = 'connected'
                logger.info("OpenRouter API health check: OK")
            else:
                api_status = 'not_initialized'
                api_error = 'AIService not properly initialized'
        except Exception as e:
            api_status = 'error'
            api_error = str(e)
            logger.warning(f"OpenRouter API health check failed: {str(e)}")
        
        health_data = {
            'status': 'ok' if api_status == 'connected' else 'degraded',
            'api': 'Career Roadmap Generator API',
            'openrouter_status': api_status,
            'openrouter_model': ai_service.MODEL_NAME if api_status == 'connected' else 'unknown',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if api_error:
            health_data['api_error'] = api_error
        
        status_code = 200 if api_status == 'connected' else 503
        
        return jsonify(health_data), status_code
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Health check failed',
            'error': str(e)
        }), 500

