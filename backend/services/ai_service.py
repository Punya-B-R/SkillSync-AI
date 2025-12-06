"""
AI service for interacting with OpenRouter API (Llama 3.3 70B).
"""
import os
import json
import logging
import time
import hashlib
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered analysis and recommendations."""
    
    CACHE_TIMEOUT = 300  # 5 minutes in seconds
    MODEL_NAME = "meta-llama/llama-3.3-70b-instruct:free"
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    
    def __init__(self):
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            logger.error("OPENROUTER_API_KEY not found in environment variables")
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
        
        try:
            # Initialize OpenAI client for OpenRouter
            # Using simple initialization to avoid version conflicts
            import httpx
            self.client = OpenAI(
                api_key=api_key,
                base_url=self.OPENROUTER_BASE_URL
            )
            logger.info(f"OpenRouter API initialized successfully with model: {self.MODEL_NAME}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenRouter API: {str(e)}")
            raise ValueError(f"Failed to initialize OpenRouter API: {str(e)}")
        
        # Response cache: {cache_key: (response, timestamp)}
        self.cache = {}
    
    def _get_cache_key(self, method_name: str, *args, **kwargs) -> str:
        """Generate cache key from method name and arguments."""
        cache_data = {
            'method': method_name,
            'args': str(args),
            'kwargs': str(sorted(kwargs.items()))
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[Any]:
        """Get cached response if still valid."""
        if cache_key in self.cache:
            response, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.CACHE_TIMEOUT:
                logger.debug(f"Cache hit for key: {cache_key}")
                return response
            else:
                # Remove expired cache entry
                del self.cache[cache_key]
                logger.debug(f"Cache expired for key: {cache_key}")
        return None
    
    def _cache_response(self, cache_key: str, response: Any):
        """Cache response with current timestamp."""
        self.cache[cache_key] = (response, time.time())
        logger.debug(f"Cached response for key: {cache_key}")
    
    def _call_openrouter_api(self, prompt: str, retry: bool = True) -> str:
        """
        Call OpenRouter API with error handling and retry logic.
        
        Args:
            prompt: Prompt to send to OpenRouter
            retry: Whether to retry on failure
            
        Returns:
            str: API response text
            
        Raises:
            ValueError: For API errors, rate limiting, or invalid API key
            TimeoutError: For timeout errors
        """
        try:
            logger.info(f"Calling OpenRouter API with model: {self.MODEL_NAME}")
            logger.debug(f"Prompt length: {len(prompt)} characters")
            
            response = self.client.chat.completions.create(
                model=self.MODEL_NAME,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                timeout=120.0  # 120 second timeout (2 minutes) for longer AI responses
            )
            
            if not response or not response.choices or len(response.choices) == 0:
                raise ValueError("Empty response from OpenRouter API")
            
            response_text = response.choices[0].message.content
            
            if not response_text:
                raise ValueError("Empty response content from OpenRouter API")
            
            logger.info("OpenRouter API call successful")
            return response_text.strip()
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # Handle rate limiting
            if 'quota' in error_msg or 'rate limit' in error_msg or '429' in error_msg:
                logger.warning("Rate limit exceeded")
                raise ValueError("API rate limit exceeded. Please try again in a few moments.")
            
            # Handle invalid API key
            if 'api key' in error_msg or 'authentication' in error_msg or 'invalid' in error_msg or '401' in error_msg:
                logger.error("Invalid API key")
                raise ValueError("Invalid API key. Please check your OPENROUTER_API_KEY environment variable.")
            
            # Handle timeout
            if 'timeout' in error_msg or 'timed out' in error_msg:
                logger.warning("API timeout occurred")
                if retry:
                    logger.info("Retrying API call after timeout")
                    time.sleep(2)
                    return self._call_openrouter_api(prompt, retry=False)
                else:
                    raise TimeoutError("API request timed out. Please try again.")
            
            # Generic error
            logger.error(f"OpenRouter API error: {str(e)}")
            if retry:
                logger.info("Retrying API call after error")
                time.sleep(2)
                return self._call_openrouter_api(prompt, retry=False)
            else:
                raise ValueError(f"API error: {str(e)}")
    
    def _extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """
        Extract JSON from API response, handling markdown code blocks.
        
        Args:
            response_text: Raw response text from API
            
        Returns:
            dict: Parsed JSON data
            
        Raises:
            ValueError: If JSON parsing fails
        """
        try:
            # Remove markdown code blocks if present
            if '```json' in response_text:
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()
            elif '```' in response_text:
                start = response_text.find('```') + 3
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()
            
            # Parse JSON
            data = json.loads(response_text)
            logger.debug("JSON parsed successfully")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            logger.debug(f"Response text: {response_text[:500]}")
            raise ValueError(f"Failed to parse JSON response: {str(e)}")
    
    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Use OpenRouter (Llama 3.3) to extract structured information from resume.
        
        Args:
            resume_text: Text content of resume
            
        Returns:
            dict: Structured resume analysis with skills, experience, etc.
        """
        try:
            logger.info("Starting resume analysis")
            
            # Check cache
            cache_key = self._get_cache_key('analyze_resume', resume_text)
            cached = self._get_cached_response(cache_key)
            if cached:
                return cached
            
            prompt = f"""
Analyze this resume and extract information in JSON format:

Resume Text:
{resume_text}

Extract:
1. Technical skills (list all programming languages, frameworks, tools, platforms)
2. Years of experience (total professional experience)
3. Current role/title
4. Experience level (Junior/Mid-Level/Senior/Lead)
5. Domain expertise (e.g., Web Dev, Data Science, Cloud, etc.)
6. Recent technologies used (last 2 years)
7. Strongest skills (top 5)

Return ONLY valid JSON:

{{
  "skills": ["skill1", "skill2", ...],
  "years_of_experience": number,
  "current_role": "string",
  "experience_level": "string",
  "domains": ["domain1", "domain2"],
  "recent_tech": ["tech1", "tech2"],
  "top_skills": ["skill1", "skill2", ...]
}}
"""
            
            response_text = self._call_openrouter_api(prompt)
            result = self._extract_json_from_response(response_text)
            
            # Validate required fields
            required_fields = ['skills', 'years_of_experience', 'current_role', 
                             'experience_level', 'domains', 'recent_tech', 'top_skills']
            for field in required_fields:
                if field not in result:
                    logger.warning(f"Missing field in response: {field}")
                    result[field] = [] if 'skills' in field or 'tech' in field or 'domains' in field else ""
            
            # Cache result
            self._cache_response(cache_key, result)
            
            logger.info("Resume analysis completed successfully")
            return result
            
        except (ValueError, TimeoutError) as e:
            logger.error(f"Resume analysis failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in analyze_resume: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to analyze resume: {str(e)}")
    
    def recommend_domains(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Based on user profile, recommend technology domains to explore.
        
        Args:
            profile: User profile dict from analyze_resume
            
        Returns:
            dict: Recommended domains with details
        """
        try:
            logger.info("Starting domain recommendations")
            
            # Check cache
            cache_key = self._get_cache_key('recommend_domains', json.dumps(profile, sort_keys=True))
            cached = self._get_cached_response(cache_key)
            if cached:
                return cached
            
            prompt = f"""
Given this professional profile:

Current Skills: {profile.get('skills', [])}
Experience Level: {profile.get('experience_level', 'Unknown')}
Years of Experience: {profile.get('years_of_experience', 0)}
Current Domains: {profile.get('domains', [])}

Recommend 6-8 technology domains they should consider learning, focusing on:
- High market demand
- Natural skill progression from their current expertise
- Emerging technologies
- Career growth potential

For each domain, provide:
- Name
- Why it's recommended for them specifically
- Difficulty level (Easy/Moderate/Challenging based on their background)
- Market demand (High/Medium)
- Key tools/technologies in this domain (5-8 tools)

Return ONLY valid JSON:

{{
  "recommendations": [
    {{
      "domain": "string",
      "reason": "string",
      "difficulty": "string",
      "market_demand": "string",
      "key_tools": [
        {{
          "name": "string",
          "description": "string",
          "learning_time_weeks": number
        }}
      ]
    }}
  ]
}}
"""
            
            response_text = self._call_openrouter_api(prompt)
            result = self._extract_json_from_response(response_text)
            
            # Validate structure
            if 'recommendations' not in result:
                logger.warning("Missing 'recommendations' field in response")
                result['recommendations'] = []
            
            # Cache result
            self._cache_response(cache_key, result)
            
            logger.info(f"Domain recommendations completed: {len(result.get('recommendations', []))} recommendations")
            return result
            
        except (ValueError, TimeoutError) as e:
            logger.error(f"Domain recommendation failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in recommend_domains: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to recommend domains: {str(e)}")
    
    def generate_roadmap(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized learning roadmap.
        
        Args:
            user_data: Dict containing profile, selected_tools, hours_per_week, learning_style, deadline
            
        Returns:
            dict: Complete roadmap with phases, schedule, resources, projects, etc.
        """
        try:
            logger.info("Starting roadmap generation")
            
            # Check cache
            cache_key = self._get_cache_key('generate_roadmap', json.dumps(user_data, sort_keys=True))
            cached = self._get_cached_response(cache_key)
            if cached:
                return cached
            
            profile = user_data.get('profile', {})
            selected_tools = user_data.get('selected_tools', [])
            hours_per_week = user_data.get('hours_per_week', 10)
            learning_style = user_data.get('learning_style', 'Balanced')
            deadline = user_data.get('deadline', 'Flexible')
            
            prompt = f"""
Create a detailed, personalized learning roadmap for this professional:

PROFILE:
- Current Skills: {profile.get('skills', [])}
- Experience: {profile.get('years_of_experience', 0)} years
- Level: {profile.get('experience_level', 'Unknown')}

LEARNING GOALS:
- Target Tools: {selected_tools}
- Available Time: {hours_per_week} hours/week
- Learning Style: {learning_style}
- Deadline: {deadline}

Generate a comprehensive roadmap with:

1. LEARNING PHASES (3-4 phases):
   - Phase number and title
   - Duration in weeks
   - Tools covered in this phase
   - Key learning objectives
   - Milestones to achieve
   - Weekly hour breakdown

2. WEEKLY SCHEDULE (for first 4 weeks in detail):
   - Week number
   - Primary focus
   - Specific daily tasks
   - Learning resources to use
   - Practice exercises
   - Time allocation

3. CURATED RESOURCES (for each tool):
   - Resource title
   - Type (Course/Video/Article/Documentation/Book)
   - Platform (Coursera/YouTube/Medium/Official Docs)
   - URL (real URLs to actual resources)
   - Difficulty level
   - Estimated time to complete
   - Why this resource (brief explanation)
   - Is it free? (true/false)

4. PROJECT IDEAS (3-5 hands-on projects):
   - Project title
   - Description
   - Technologies used
   - Complexity level
   - Estimated time
   - Learning outcomes
   - Step-by-step guidance

5. CAREER INSIGHTS:
   - How these skills fit together
   - Career paths possible
   - Market value of this skill combination
   - Tips for success

6. SKILL GAP ANALYSIS:
   - What they already know that helps
   - New concepts they'll need to learn
   - Potential challenges
   - How to overcome them

Return ONLY valid JSON with this exact structure:

{{
  "total_duration_weeks": number,
  "estimated_completion_date": "string",
  "phases": [
    {{
      "phase_number": number,
      "title": "string",
      "duration_weeks": number,
      "tools_covered": ["tool1", "tool2"],
      "learning_objectives": ["obj1", "obj2"],
      "milestones": ["milestone1", "milestone2"],
      "weekly_hours": number
    }}
  ],
  "weekly_schedule": [
    {{
      "week_number": number,
      "primary_focus": "string",
      "daily_tasks": ["task1", "task2"],
      "resources": ["resource1", "resource2"],
      "practice_exercises": ["exercise1", "exercise2"],
      "time_allocation": "string"
    }}
  ],
  "resources": [
    {{
      "title": "string",
      "type": "string",
      "platform": "string",
      "url": "string",
      "difficulty": "string",
      "estimated_time": "string",
      "why_this_resource": "string",
      "is_free": boolean
    }}
  ],
  "projects": [
    {{
      "title": "string",
      "description": "string",
      "technologies": ["tech1", "tech2"],
      "complexity": "string",
      "estimated_time": "string",
      "learning_outcomes": ["outcome1", "outcome2"],
      "steps": ["step1", "step2"]
    }}
  ],
  "career_insights": "string",
  "skill_gap_analysis": {{
    "strengths": ["strength1", "strength2"],
    "gaps": ["gap1", "gap2"],
    "challenges": ["challenge1", "challenge2"],
    "strategies": ["strategy1", "strategy2"]
  }}
}}

Be specific, practical, and realistic. Use real resource URLs.
"""
            
            response_text = self._call_openrouter_api(prompt)
            result = self._extract_json_from_response(response_text)
            
            # Validate required fields
            required_fields = ['total_duration_weeks', 'phases', 'weekly_schedule', 
                             'resources', 'projects', 'career_insights', 'skill_gap_analysis']
            for field in required_fields:
                if field not in result:
                    logger.warning(f"Missing field in roadmap response: {field}")
                    if field == 'skill_gap_analysis':
                        result[field] = {'strengths': [], 'gaps': [], 'challenges': [], 'strategies': []}
                    elif field in ['phases', 'weekly_schedule', 'resources', 'projects']:
                        result[field] = []
                    else:
                        result[field] = ""
            
            # Cache result
            self._cache_response(cache_key, result)
            
            logger.info("Roadmap generation completed successfully")
            return result
            
        except (ValueError, TimeoutError) as e:
            logger.error(f"Roadmap generation failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in generate_roadmap: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to generate roadmap: {str(e)}")
    
    def chat_assistant(self, message: str, context: Dict[str, Any]) -> str:
        """
        Handle chat queries about the roadmap.
        
        Args:
            message: User's question/message
            context: Dict containing roadmap data, user profile, conversation history
            
        Returns:
            str: AI response text
        """
        try:
            logger.info("Processing chat message")
            
            # Check cache (with message included)
            cache_key = self._get_cache_key('chat_assistant', message, json.dumps(context, sort_keys=True))
            cached = self._get_cached_response(cache_key)
            if cached:
                return cached
            
            profile = context.get('profile', {})
            roadmap_summary = context.get('roadmap_summary', '')
            history = context.get('history', [])
            
            # Format conversation history
            history_text = ""
            if history:
                history_text = "\n".join([f"User: {h.get('user', '')}\nAssistant: {h.get('assistant', '')}" 
                                        for h in history[-5:]])  # Last 5 exchanges
            
            prompt = f"""
You are a friendly career mentor helping a professional with their learning journey.

USER PROFILE:
{json.dumps(profile, indent=2) if profile else 'Not available'}

THEIR ROADMAP:
{roadmap_summary if roadmap_summary else 'Not available'}

CONVERSATION HISTORY:
{history_text if history_text else 'No previous conversation'}

USER QUESTION:
{message}

Provide a helpful, encouraging, and specific answer. Be conversational and supportive.
If they ask about timeline, difficulty, resources, or strategy, give actionable advice.
Keep response under 200 words.
"""
            
            response_text = self._call_openrouter_api(prompt)
            
            # Clean up response (remove markdown if present)
            if response_text.startswith('```'):
                lines = response_text.split('\n')
                response_text = '\n'.join([line for line in lines if not line.strip().startswith('```')])
            
            response_text = response_text.strip()
            
            # Cache result
            self._cache_response(cache_key, response_text)
            
            logger.info("Chat response generated successfully")
            return response_text
            
        except (ValueError, TimeoutError) as e:
            logger.error(f"Chat assistant failed: {str(e)}")
            # Return user-friendly error message
            return f"I apologize, but I'm having trouble processing your request right now. {str(e)} Please try again in a moment."
        except Exception as e:
            logger.error(f"Unexpected error in chat_assistant: {str(e)}", exc_info=True)
            return "I encountered an unexpected error. Please try rephrasing your question or try again later."

