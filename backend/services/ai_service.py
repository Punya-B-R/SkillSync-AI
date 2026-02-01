"""
AI service for interacting with Gemini API (OpenAI-compatible endpoint).
Optional: Google Search grounding via google-genai for real resource URLs.
"""
import ast
import json
import logging
import os
import re
import time
import hashlib
from typing import Dict, Any, Optional, Tuple, List
from urllib.parse import quote_plus
from dotenv import load_dotenv
from openai import OpenAI
from data.verified_resources import (
    VERIFIED_RESOURCES,
    TECH_TO_CATEGORY,
    get_resources_for_tech,
    get_all_resources_for_techs
)
load_dotenv()

logger = logging.getLogger(__name__)

# Optional: Google Search grounding (google-genai package)
_grounding_client = None
_grounding_available = False
try:
    from google import genai
    from google.genai import types
    _grounding_available = True
except ImportError:
    genai = None
    types = None

# Gemini OpenAI-compatible base URL (see https://ai.google.dev/gemini-api/docs/openai)
GEMINI_OPENAI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai"

class AIService:
    """Service for AI-powered analysis and recommendations."""
    
    CACHE_TIMEOUT = 300  # 5 minutes in seconds
    MODEL_NAME = os.getenv('GEMINI_MODEL_NAME', 'gemini-2.0-flash')
    
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            logger.error("GEMINI_API_KEY not found in environment variables")
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        try:
            self.client = OpenAI(
                api_key=api_key,
                base_url=GEMINI_OPENAI_BASE_URL
            )
            logger.info(f"Gemini API initialized successfully with model: {self.MODEL_NAME}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API: {str(e)}")
            raise ValueError(f"Failed to initialize Gemini API: {str(e)}")
        
        # Optional: client for Google Search grounding (real web URLs in resource finding)
        self._grounding_client = None
        if _grounding_available and api_key:
            try:
                self._grounding_client = genai.Client(api_key=api_key)
                logger.info("Google Search grounding enabled for resource finding")
            except Exception as e:
                logger.debug("Grounding client not available: %s", e)

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
        
        # Periodically clean up old cache entries to prevent memory issues
        if len(self.cache) > 100:  # Clean up if cache gets too large
            self._cleanup_cache()
    
    def _cleanup_cache(self):
        """Remove expired cache entries to manage memory."""
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if current_time - timestamp > self.CACHE_TIMEOUT
        ]
        for key in expired_keys:
            del self.cache[key]
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def _call_ai_api(self, prompt: str, retry: bool = True, max_tokens: int = 8000, timeout: float = 120.0) -> str:
        """
        Call Gemini API (OpenAI-compatible) with optimized settings for speed and error handling.
        
        Args:
            prompt: Prompt to send
            retry: Whether to retry on failure
            max_tokens: Maximum tokens to generate (default 8000 for roadmaps)
            timeout: Request timeout in seconds
            
        Returns:
            str: API response text
            
        Raises:
            ValueError: For API errors, rate limiting, or invalid API key
            TimeoutError: For timeout errors
        """
        try:
            logger.info(f"Calling Gemini API with model: {self.MODEL_NAME}")
            logger.debug(f"Prompt length: {len(prompt)} characters, max_tokens: {max_tokens}")
            
            response = self.client.chat.completions.create(
                model=self.MODEL_NAME,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.7,  # Lower temperature for faster, more deterministic responses
                timeout=timeout
            )
            
            if not response or not response.choices or len(response.choices) == 0:
                raise ValueError("Empty response from Gemini API")
            
            response_text = response.choices[0].message.content
            
            if not response_text:
                raise ValueError("Empty response content from Gemini API")
            
            logger.info("Gemini API call successful")
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
                raise ValueError("Invalid API key. Please check your GEMINI_API_KEY environment variable.")
            
            # Handle timeout
            if 'timeout' in error_msg or 'timed out' in error_msg:
                logger.warning("API timeout occurred")
                if retry:
                    logger.info("Retrying API call with reduced max_tokens after timeout")
                    time.sleep(2)
                    return self._call_ai_api(prompt, retry=False, max_tokens=max_tokens // 2, timeout=timeout)
                else:
                    raise TimeoutError("API request timed out. Please try again.")
            
            # Generic error
            logger.error(f"Gemini API error: {str(e)}")
            if retry:
                logger.info("Retrying API call after error")
                time.sleep(2)
                return self._call_ai_api(prompt, retry=False, max_tokens=max_tokens, timeout=timeout)
            else:
                raise ValueError(f"API error: {str(e)}")
    
    def _repair_json(self, raw: str) -> str:
        """Fix common LLM JSON issues: trailing commas before } or ]."""
        # Remove trailing commas (invalid in JSON but often emitted by LLMs)
        for _ in range(20):  # enough for deep nesting
            new_raw = re.sub(r',\s*}', '}', raw)
            new_raw = re.sub(r',\s*]', ']', new_raw)
            if new_raw == raw:
                break
            raw = new_raw
        return raw

    def _extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """
        Extract JSON from API response, handling markdown code blocks and common LLM errors.
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

            # First attempt: parse as-is
            try:
                data = json.loads(response_text)
                logger.debug("JSON parsed successfully")
                return data
            except json.JSONDecodeError:
                pass

            # Second attempt: repair common issues then parse
            repaired = self._repair_json(response_text)
            try:
                data = json.loads(repaired)
                logger.info("JSON parsed successfully after repair (trailing commas/control chars)")
                return data
            except json.JSONDecodeError:
                pass

            # Third attempt: Python literal (single-quoted keys, True/False/None)
            try:
                data = ast.literal_eval(response_text)
                if isinstance(data, (dict, list)):
                    logger.info("JSON parsed successfully via ast.literal_eval (Python-style literals)")
                    return data
            except (ValueError, SyntaxError):
                pass

            raise ValueError("Could not parse response as JSON (all attempts failed)")

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            # Log snippet around error position for debugging
            if e.pos is not None and len(response_text) > e.pos:
                start = max(0, e.pos - 80)
                end = min(len(response_text), e.pos + 80)
                snippet = response_text[start:end].replace('\n', ' ')
                logger.debug(f"Near error position: ...{snippet}...")
            raise ValueError(f"Failed to parse JSON response: {str(e)}")
    
    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Use Gemini to extract structured information from resume.
        
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
            
            response_text = self._call_ai_api(prompt)
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
            
            response_text = self._call_ai_api(prompt)
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
    
    def _validate_roadmap(self, roadmap: Dict[str, Any], hours_per_week: int) -> list:
        """
        Validate roadmap structure and content.
        
        Args:
            roadmap: Generated roadmap dictionary
            hours_per_week: Expected hours per week for validation
            
        Returns:
            list: List of validation error messages (empty if valid)
        """
        errors = []
        
        # Check required top-level fields
        required_fields = ['total_duration_weeks', 'phases', 'weekly_plans', 
                          'projects', 'career_insights', 'skill_gap_analysis']
        for field in required_fields:
            if field not in roadmap:
                errors.append(f"Missing required field: {field}")
        
        # Validate weekly_plans structure
        if 'weekly_plans' in roadmap:
            weekly_plans = roadmap['weekly_plans']
            if not isinstance(weekly_plans, list):
                errors.append("weekly_plans must be a list")
            else:
                for week_idx, week_plan in enumerate(weekly_plans):
                    # Check week structure
                    if not isinstance(week_plan, dict):
                        errors.append(f"Week {week_idx + 1}: week_plan must be a dictionary")
                        continue
                    
                    # Check required week fields
                    week_required = ['week', 'phase', 'focus', 'objectives', 'prerequisites', 'daily_plans']
                    for field in week_required:
                        if field not in week_plan:
                            errors.append(f"Week {week_plan.get('week', week_idx + 1)}: Missing field '{field}'")
                    
                    # Validate daily_plans
                    if 'daily_plans' in week_plan:
                        daily_plans = week_plan['daily_plans']
                        if not isinstance(daily_plans, list):
                            errors.append(f"Week {week_plan.get('week', week_idx + 1)}: daily_plans must be a list")
                        else:
                            # Check for exactly 7 days
                            if len(daily_plans) != 7:
                                errors.append(f"Week {week_plan.get('week', week_idx + 1)}: Must have exactly 7 daily_plans, found {len(daily_plans)}")
                            
                            # Validate each daily plan
                            days_found = set()
                            for day_idx, daily_plan in enumerate(daily_plans):
                                if not isinstance(daily_plan, dict):
                                    errors.append(f"Week {week_plan.get('week', week_idx + 1)}, Day {day_idx + 1}: daily_plan must be a dictionary")
                                    continue
                                
                                # Check day number
                                day_num = daily_plan.get('day')
                                if day_num is None:
                                    errors.append(f"Week {week_plan.get('week', week_idx + 1)}, Day {day_idx + 1}: Missing 'day' field")
                                else:
                                    if day_num in days_found:
                                        errors.append(f"Week {week_plan.get('week', week_idx + 1)}: Duplicate day number {day_num}")
                                    days_found.add(day_num)
                                    
                                    if day_num < 1 or day_num > 7:
                                        errors.append(f"Week {week_plan.get('week', week_idx + 1)}: Day number must be 1-7, found {day_num}")
                                
                                # Check required daily fields
                                daily_required = ['day', 'topic', 'tasks', 'hours', 'resource', 'practice', 'outcome']
                                for field in daily_required:
                                    if field not in daily_plan:
                                        errors.append(f"Week {week_plan.get('week', week_idx + 1)}, Day {daily_plan.get('day', day_idx + 1)}: Missing field '{field}'")
                                
                                # Validate resource object
                                if 'resource' in daily_plan:
                                    resource = daily_plan['resource']
                                    if not isinstance(resource, dict):
                                        errors.append(f"Week {week_plan.get('week', week_idx + 1)}, Day {daily_plan.get('day', day_idx + 1)}: resource must be a dictionary")
                                    else:
                                        resource_required = ['title', 'type', 'platform', 'url', 'what_to_learn', 'duration']
                                        for field in resource_required:
                                            if field not in resource:
                                                errors.append(f"Week {week_plan.get('week', week_idx + 1)}, Day {daily_plan.get('day', day_idx + 1)}: resource missing field '{field}'")
                                        
                                        # Check URL is present and non-empty
                                        url = resource.get('url', '')
                                        if not url or not isinstance(url, str) or len(url.strip()) == 0:
                                            errors.append(f"Week {week_plan.get('week', week_idx + 1)}, Day {daily_plan.get('day', day_idx + 1)}: resource.url is missing or empty")
                                        else:
                                            # Validate URL format
                                            url = url.strip()
                                            if not url.startswith(('http://', 'https://')):
                                                errors.append(f"Week {week_plan.get('week', week_idx + 1)}, Day {daily_plan.get('day', day_idx + 1)}: Invalid URL format (must start with http:// or https://): {url[:50]}")
                                        
                                        # Validate resource type (YouTube videos are not allowed)
                                        valid_types = ['Interactive Course', 'Documentation', 'Tutorial Article', 'Interactive Platform', 'GitHub Tutorial', 'Free Guide']
                                        resource_type = resource.get('type', '')
                                        if resource_type and resource_type not in valid_types:
                                            errors.append(f"Week {week_plan.get('week', week_idx + 1)}, Day {daily_plan.get('day', day_idx + 1)}: Invalid resource type '{resource_type}'. Must be one of {valid_types}")
                                        
                                        # Check for YouTube URLs and reject them
                                        url = resource.get('url', '')
                                        if url and isinstance(url, str):
                                            url_lower = url.lower()
                                            if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
                                                errors.append(f"Week {week_plan.get('week', week_idx + 1)}, Day {daily_plan.get('day', day_idx + 1)}: YouTube videos are not allowed. Found YouTube URL: {url[:50]}")
                                        
                                        # Check for YouTube in platform field
                                        platform = resource.get('platform', '')
                                        if platform and isinstance(platform, str):
                                            platform_lower = platform.lower()
                                            if 'youtube' in platform_lower:
                                                errors.append(f"Week {week_plan.get('week', week_idx + 1)}, Day {daily_plan.get('day', day_idx + 1)}: YouTube videos are not allowed. Found YouTube platform: {platform}")
                                        
                                        # Check for video content in type
                                        if resource_type and isinstance(resource_type, str):
                                            resource_type_lower = resource_type.lower()
                                            if 'video' in resource_type_lower and 'interactive' not in resource_type_lower:
                                                errors.append(f"Week {week_plan.get('week', week_idx + 1)}, Day {daily_plan.get('day', day_idx + 1)}: Video resources are not allowed. Found video type: {resource_type}")
                                
                                # Validate hours allocation
                                hours = daily_plan.get('hours')
                                if hours is not None:
                                    if not isinstance(hours, (int, float)) or hours <= 0:
                                        errors.append(f"Week {week_plan.get('week', week_idx + 1)}, Day {daily_plan.get('day', day_idx + 1)}: hours must be a positive number")
                            
                            # Check all days 1-7 are present
                            if len(days_found) == 7:
                                for day_num in range(1, 8):
                                    if day_num not in days_found:
                                        errors.append(f"Week {week_plan.get('week', week_idx + 1)}: Missing day {day_num}")
                            
                            # Validate weekly hours match hours_per_week (with some tolerance)
                            total_weekly_hours = sum(daily_plan.get('hours', 0) for daily_plan in daily_plans if isinstance(daily_plan, dict))
                            if total_weekly_hours > 0:
                                tolerance = hours_per_week * 0.2  # 20% tolerance
                                if abs(total_weekly_hours - hours_per_week) > tolerance:
                                    errors.append(f"Week {week_plan.get('week', week_idx + 1)}: Total weekly hours ({total_weekly_hours}) doesn't match expected hours_per_week ({hours_per_week})")
        
        # Validate projects structure
        if 'projects' in roadmap:
            projects = roadmap['projects']
            if not isinstance(projects, list):
                errors.append("projects must be a list")
            else:
                for proj_idx, project in enumerate(projects):
                    if not isinstance(project, dict):
                        errors.append(f"Project {proj_idx + 1}: must be a dictionary")
                        continue
                    
                    project_required = ['title', 'problem_statement', 'technologies', 'difficulty', 
                                       'estimated_hours', 'learning_outcomes', 'steps', 'start_week', 'bonus_features']
                    for field in project_required:
                        if field not in project:
                            errors.append(f"Project {proj_idx + 1}: Missing field '{field}'")
                    
                    # Validate problem_statement is detailed enough
                    if 'problem_statement' in project:
                        problem_stmt = project.get('problem_statement', '')
                        if not problem_stmt or not isinstance(problem_stmt, str):
                            errors.append(f"Project {proj_idx + 1}: problem_statement is missing or empty")
                        elif len(problem_stmt.strip()) < 100:
                            errors.append(f"Project {proj_idx + 1}: problem_statement too short (should be 3-5 sentences, at least 100 characters)")
                    
                    # Validate bonus_features
                    if 'bonus_features' in project:
                        bonus_features = project.get('bonus_features', [])
                        if not isinstance(bonus_features, list):
                            errors.append(f"Project {proj_idx + 1}: bonus_features must be a list")
                        elif len(bonus_features) < 2:
                            errors.append(f"Project {proj_idx + 1}: bonus_features should have at least 2 items")
        
        # Validate skill_gap_analysis structure
        if 'skill_gap_analysis' in roadmap:
            sga = roadmap['skill_gap_analysis']
            if not isinstance(sga, dict):
                errors.append("skill_gap_analysis must be a dictionary")
            else:
                sga_required = ['strengths', 'gaps', 'challenges', 'strategies']
                for field in sga_required:
                    if field not in sga:
                        errors.append(f"skill_gap_analysis missing field '{field}'")
                    elif not isinstance(sga[field], list):
                        errors.append(f"skill_gap_analysis.{field} must be a list")
        
        return errors
    
    def validate_roadmap_structure(self, roadmap_data: Dict[str, Any], verified_resources: Optional[List[Dict[str, Any]]] = None) -> Tuple[bool, list]:
        """
        Validate that roadmap has correct structure with daily plans and resources.
        Also validates that all URLs are from verified resources list.
        Standalone validation function that can be used independently.
        
        Args:
            roadmap_data: Roadmap dictionary to validate
            verified_resources: Optional list of verified resources to validate URLs against
            
        Returns:
            tuple: (is_valid: bool, errors: list of error messages)
        """
        errors = []
        
        # Create verified URLs set if resources provided
        verified_urls = set()
        if verified_resources:
            verified_urls = {r['url'] for r in verified_resources}
        
        # Check weekly_plans exists
        if 'weekly_plans' not in roadmap_data:
            errors.append("Missing weekly_plans")
            return False, errors
        
        if not isinstance(roadmap_data['weekly_plans'], list):
            errors.append("weekly_plans must be a list")
            return False, errors
        
        # Validate each week
        for week in roadmap_data['weekly_plans']:
            if not isinstance(week, dict):
                errors.append(f"Week entry must be a dictionary")
                continue
                
            week_num = week.get('week', '?')
            
            # Check if this is a detailed week (has daily_plans) or high-level week
            has_daily_plans = 'daily_plans' in week
            is_high_level = 'main_topics' in week or 'key_resource' in week
            
            if not has_daily_plans and not is_high_level:
                errors.append(f"Week {week_num}: Must have either daily_plans (detailed) or main_topics/key_resource (high-level)")
                continue
            
            # Validate detailed weeks (first 4 weeks should have daily_plans)
            if has_daily_plans:
                if not isinstance(week['daily_plans'], list):
                    errors.append(f"Week {week_num}: daily_plans must be a list")
                    continue
                
                # Should have 7 days for detailed weeks
                if len(week['daily_plans']) != 7:
                    errors.append(f"Week {week_num}: Expected 7 days, got {len(week['daily_plans'])}")
            
            # Validate high-level weeks (key_resource)
            if is_high_level and 'key_resource' in week:
                key_resource = week['key_resource']
                if not isinstance(key_resource, dict):
                    errors.append(f"Week {week_num}: key_resource must be a dictionary")
                else:
                    # Check for YouTube URLs and reject them
                    if 'url' in key_resource:
                        url = key_resource.get('url', '')
                        if url and isinstance(url, str):
                            url_lower = url.lower()
                            if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
                                errors.append(f"Week {week_num}: YouTube videos are not allowed in key_resource. Found YouTube URL: {url[:50]}")
                    
                    # Check resource type
                    resource_type = key_resource.get('type', '')
                    if resource_type and isinstance(resource_type, str):
                        resource_type_lower = resource_type.lower()
                        if 'youtube' in resource_type_lower or ('video' in resource_type_lower and 'interactive' not in resource_type_lower):
                            errors.append(f"Week {week_num}: YouTube/video resources are not allowed in key_resource. Found type: {resource_type}")
            
            # Validate each day (only for detailed weeks)
            if not has_daily_plans:
                # Skip day validation for high-level weeks (already validated key_resource above)
                continue
                
            for day in week['daily_plans']:
                if not isinstance(day, dict):
                    errors.append(f"Week {week_num}, Day entry: Must be a dictionary")
                    continue
                    
                day_num = day.get('day', '?')
                
                # Check resource exists
                if 'resource' not in day:
                    errors.append(f"Week {week_num}, Day {day_num}: Missing resource")
                    continue
                
                resource = day['resource']
                
                if not isinstance(resource, dict):
                    errors.append(f"Week {week_num}, Day {day_num}: resource must be a dictionary")
                    continue
                
                # Validate resource fields
                required_fields = ['title', 'type', 'platform', 'url', 'what_to_learn', 'duration']
                for field in required_fields:
                    if field not in resource:
                        errors.append(f"Week {week_num}, Day {day_num}: Resource missing '{field}'")
                    elif not resource[field] or (isinstance(resource[field], str) and len(resource[field].strip()) == 0):
                        errors.append(f"Week {week_num}, Day {day_num}: Resource '{field}' is empty")
                
                # Validate URL format
                if 'url' in resource and resource['url']:
                    url = resource['url']
                    if isinstance(url, str):
                        url = url.strip()
                        if not url.startswith(('http://', 'https://')):
                            errors.append(f"Week {week_num}, Day {day_num}: Invalid URL format (must start with http:// or https://): {url[:50]}")
                        else:
                            # Check for YouTube URLs and reject them
                            url_lower = url.lower()
                            if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
                                errors.append(f"Week {week_num}, Day {day_num}: YouTube videos are not allowed. Found YouTube URL: {url[:50]}")
                            
                            # Check if URL is from verified list
                            if verified_urls and url not in verified_urls:
                                errors.append(f"Week {week_num}, Day {day_num}: URL not in verified list: {url[:50]}")
                    else:
                        errors.append(f"Week {week_num}, Day {day_num}: URL must be a string")
                
                # Check for YouTube in platform field
                if 'platform' in resource and resource['platform']:
                    platform = resource.get('platform', '')
                    if isinstance(platform, str):
                        platform_lower = platform.lower()
                        if 'youtube' in platform_lower:
                            errors.append(f"Week {week_num}, Day {day_num}: YouTube videos are not allowed. Found YouTube platform: {platform}")
                
                # Validate resource type
                resource_type = resource.get('type', '')
                if resource_type:
                    allowed_types = ['Interactive Course', 'Documentation', 'Tutorial Article', 'Interactive Platform', 'GitHub Tutorial', 'Free Guide']
                    if resource_type not in allowed_types:
                        errors.append(f"Week {week_num}, Day {day_num}: Invalid resource type '{resource_type}'. Must be one of {allowed_types}")
                    elif isinstance(resource_type, str):
                        resource_type_lower = resource_type.lower()
                        if 'video' in resource_type_lower and 'interactive' not in resource_type_lower:
                            errors.append(f"Week {week_num}, Day {day_num}: Video resources are not allowed. Found video type: {resource_type}")
        
        # Validate projects have problem statements
        if 'projects' in roadmap_data:
            projects = roadmap_data['projects']
            if isinstance(projects, list):
                for i, project in enumerate(projects):
                    if not isinstance(project, dict):
                        continue
                    
                    if 'problem_statement' not in project or not project.get('problem_statement'):
                        errors.append(f"Project {i+1}: Missing problem_statement")
                    elif len(project.get('problem_statement', '').strip()) < 100:
                        errors.append(f"Project {i+1}: Problem statement too short (should be 3-5 sentences, at least 100 characters)")
                    
                    if 'bonus_features' not in project:
                        errors.append(f"Project {i+1}: Missing bonus_features")
                    elif not isinstance(project.get('bonus_features'), list) or len(project.get('bonus_features', [])) < 2:
                        errors.append(f"Project {i+1}: bonus_features should be a list with at least 2 items")
        
        return len(errors) == 0, errors
    
    def _validate_and_replace_resources(self, roadmap: Dict[str, Any], verified_resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate that all resource URLs are from verified resources list.
        Replace any non-verified URLs with verified ones.
        
        Args:
            roadmap: Roadmap dictionary
            verified_resources: List of verified resource dictionaries
            
        Returns:
            dict: Roadmap with all resources validated/replaced
        """
        if not verified_resources or 'weekly_plans' not in roadmap:
            return roadmap
        
        # Create a lookup by URL for quick access
        verified_urls = {r['url']: r for r in verified_resources}
        
        # Also create a lookup by title for fuzzy matching
        verified_by_title = {r['title'].lower(): r for r in verified_resources}
        
        for week in roadmap.get('weekly_plans', []):
            # Check detailed weeks (daily_plans)
            if 'daily_plans' in week:
                for day in week.get('daily_plans', []):
                    if 'resource' in day:
                        resource = day['resource']
                        url = resource.get('url', '')
                        
                        # Check if URL is verified
                        if url and url not in verified_urls:
                            logger.warning(f"Non-verified URL found in Week {week.get('week', '?')}, Day {day.get('day', '?')}: {url[:50]}")
                            
                            # Try to find a match by title
                            title = resource.get('title', '').lower()
                            if title in verified_by_title:
                                logger.info(f"Replacing with verified resource: {verified_by_title[title]['title']}")
                                verified_resource = verified_by_title[title]
                                day['resource'] = {
                                    'title': verified_resource['title'],
                                    'type': verified_resource['type'],
                                    'platform': verified_resource['platform'],
                                    'url': verified_resource['url'],
                                    'what_to_learn': resource.get('what_to_learn', f"Learn {verified_resource['topics'][0] if verified_resource.get('topics') else 'the topic'}"),
                                    'duration': verified_resource['duration']
                                }
                            else:
                                # Find closest match by type or use first verified resource
                                resource_type = resource.get('type', '')
                                matching_resources = [r for r in verified_resources if r['type'] == resource_type]
                                if matching_resources:
                                    replacement = matching_resources[0]
                                    logger.info(f"Replacing with closest verified resource: {replacement['title']}")
                                    day['resource'] = {
                                        'title': replacement['title'],
                                        'type': replacement['type'],
                                        'platform': replacement['platform'],
                                        'url': replacement['url'],
                                        'what_to_learn': resource.get('what_to_learn', f"Learn {replacement['topics'][0] if replacement.get('topics') else 'the topic'}"),
                                        'duration': replacement['duration']
                                    }
                                else:
                                    # Use first verified resource as fallback
                                    replacement = verified_resources[0]
                                    logger.warning(f"Using fallback verified resource: {replacement['title']}")
                                    day['resource'] = {
                                        'title': replacement['title'],
                                        'type': replacement['type'],
                                        'platform': replacement['platform'],
                                        'url': replacement['url'],
                                        'what_to_learn': resource.get('what_to_learn', f"Learn {replacement['topics'][0] if replacement.get('topics') else 'the topic'}"),
                                        'duration': replacement['duration']
                                    }
            
            # Check high-level weeks (key_resource)
            if 'key_resource' in week:
                resource = week['key_resource']
                url = resource.get('url', '')
                
                if url and url not in verified_urls:
                    logger.warning(f"Non-verified URL found in Week {week.get('week', '?')} key_resource: {url[:50]}")
                    
                    # Try to find a match
                    title = resource.get('title', '').lower()
                    if title in verified_by_title:
                        verified_resource = verified_by_title[title]
                        week['key_resource'] = {
                            'title': verified_resource['title'],
                            'url': verified_resource['url'],
                            'type': verified_resource['type']
                        }
                    elif verified_resources:
                        # Use first verified resource as fallback
                        replacement = verified_resources[0]
                        week['key_resource'] = {
                            'title': replacement['title'],
                            'url': replacement['url'],
                            'type': replacement['type']
                        }
        
        return roadmap
    
    def _filter_youtube_resources(self, roadmap: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter out any YouTube resources from the roadmap as a safety measure.
        
        Args:
            roadmap: Roadmap dictionary
            
        Returns:
            dict: Roadmap with YouTube resources removed or replaced
        """
        if 'weekly_plans' not in roadmap:
            return roadmap
        
        for week in roadmap.get('weekly_plans', []):
            # Check detailed weeks (daily_plans)
            if 'daily_plans' in week:
                for day in week.get('daily_plans', []):
                    if 'resource' in day:
                        resource = day['resource']
                        url = resource.get('url', '')
                        platform = resource.get('platform', '')
                        resource_type = resource.get('type', '')
                        
                        # Check if it's a YouTube resource
                        is_youtube = False
                        if url and isinstance(url, str):
                            url_lower = url.lower()
                            if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
                                is_youtube = True
                        if platform and isinstance(platform, str) and 'youtube' in platform.lower():
                            is_youtube = True
                        if resource_type and isinstance(resource_type, str) and ('youtube' in resource_type.lower() or 'video' in resource_type.lower()):
                            is_youtube = True
                        
                        if is_youtube:
                            logger.warning(f"Removing YouTube resource from Week {week.get('week', '?')}, Day {day.get('day', '?')}")
                            # Replace with a placeholder that indicates resource needs to be replaced
                            day['resource'] = {
                                'title': 'Resource needs to be replaced (YouTube not allowed)',
                                'type': 'Documentation',
                                'platform': 'Official Documentation',
                                'url': 'https://example.com',
                                'what_to_learn': 'Please use official documentation or tutorials instead',
                                'duration': 'N/A'
                            }
            
            # Check high-level weeks (key_resource)
            if 'key_resource' in week:
                resource = week['key_resource']
                url = resource.get('url', '')
                resource_type = resource.get('type', '')
                
                # Check if it's a YouTube resource
                is_youtube = False
                if url and isinstance(url, str):
                    url_lower = url.lower()
                    if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
                        is_youtube = True
                if resource_type and isinstance(resource_type, str) and ('youtube' in resource_type.lower() or 'video' in resource_type.lower()):
                    is_youtube = True
                
                if is_youtube:
                    logger.warning(f"Removing YouTube resource from Week {week.get('week', '?')} key_resource")
                    # Replace with a placeholder
                    week['key_resource'] = {
                        'title': 'Resource needs to be replaced (YouTube not allowed)',
                        'url': 'https://example.com',
                        'type': 'Documentation'
                    }
        
        return roadmap
    
    def _calculate_total_weeks(self, user_data: Dict[str, Any]) -> int:
        """
        Total weeks: use user-specified total_weeks if provided (from frontend "Estimated Weeks"),
        otherwise estimate from tools and hours per week.
        """
        # Respect user's chosen duration from the Time Commitment step
        user_weeks = user_data.get('total_weeks') or user_data.get('totalWeeks')
        if user_weeks is not None:
            try:
                w = int(user_weeks)
                if 1 <= w <= 24:
                    return max(4, min(16, w))
            except (TypeError, ValueError):
                pass

        selected_tools = user_data.get('selected_tools', [])
        hours_per_week = user_data.get('hours_per_week', 10)

        base_weeks_per_tool = 2.5
        tools_count = len(selected_tools)
        time_multiplier = max(0.7, min(1.3, 10 / hours_per_week))
        total_weeks = int(tools_count * base_weeks_per_tool * time_multiplier)
        return max(4, min(16, total_weeks))

    def _determine_experience_level(self, user_data: Dict[str, Any]) -> str:
        """Determine experience level from profile."""
        profile = user_data.get('profile', {})
        return profile.get('experience_level', 'Mid-Level') or 'Mid-Level'

    def _generate_roadmap_structure(self, user_data: Dict[str, Any], total_weeks: int, experience_level: str) -> Dict[str, Any]:
        """
        STEP 1: Generate FULL roadmap in ONE call (structure + all 3 resource types per day).
        Same approach as sub-buildathon: one Gemini call for entire roadmap with resources.
        """
        profile = user_data.get('profile', {})
        selected_tools = user_data.get('selected_tools', [])
        hours_per_week = user_data.get('hours_per_week', 10)
        skills_str = ', '.join(profile.get('skills', [])[:10])
        tools_str = ', '.join(selected_tools)
        detailed_weeks = min(4, total_weeks)

        prompt = f"""You are an expert curriculum designer for tech education.

USER: Experience {experience_level}, Skills: {skills_str}, Learning: {tools_str}, Time: {hours_per_week}h/week.
TASK: Create a complete {total_weeks}-week learning roadmap with ALL resources in ONE response.

OUTPUT (valid JSON only, no markdown):
{{
  "total_duration_weeks": {total_weeks},
  "estimated_completion_date": "YYYY-MM-DD",
  "phases": [{{"phase": n, "title": str, "duration_weeks": n, "tools": [], "objectives": [], "milestones": []}}],
  "weekly_plans": [
    (For weeks 1-{detailed_weeks}: each week has "week", "phase", "focus", "objectives", "prerequisites", "daily_plans" with exactly 7 days. Each day has "day", "topic", "tasks" (array), "hours", "practice", "outcome", AND three resource arrays below.)
    (For weeks {detailed_weeks + 1}+: "week", "phase", "focus", "main_topics", "total_hours", "key_resource" with "title", "url", "type" - use "https://www.example.com" for url)
  ],
  "projects": [{{"title", "problem_statement", "technologies", "difficulty", "estimated_hours", "learning_outcomes", "steps", "start_week", "bonus_features"}}],
  "career_insights": "string",
  "skill_gap_analysis": {{"strengths": [], "gaps": [], "challenges": [], "strategies": []}}
}}

For each day in daily_plans (weeks 1-{detailed_weeks}), include these THREE resource sections — DO NOT SKIP:

1. GENERAL RESOURCES (4-5 items in "general_resources") — DO NOT CHANGE:
   - Official documentation, free courses (Codecademy, freeCodeCamp, etc.), quality blog posts, practice repositories, interactive platforms
   - Include actual URLs when possible
   - Format: {{ "title": "string", "url": "string", "type": "string", "description": "string", "difficulty": "string", "platform": "string" }}
   - Only suggest resources that are actually free

2. YOUTUBE VIDEOS (5-7 items in "youtube_videos") — DO NOT CHANGE:
   - Specific video recommendations for the day's topic
   - Prioritize well-known channels: Fireship, Traversy Media, freeCodeCamp, The Net Ninja, Web Dev Simplified
   - Format: {{ "videoTitle": "string", "channelName": "string", "duration": "string", "description": "string", "difficulty": "string", "recommendationReason": "string" }}
   - Use actual video titles when possible; include estimated duration (e.g. "12 min", "1h 20m")

3. PRACTICE & QUIZZES (3-5 items in "practice_resources") — DO NOT CHANGE:
   - Interactive quizzes, coding challenges, and practice assessments for the day's topic
   - Only FREE platforms: LeetCode, HackerRank, Codewars, freeCodeCamp challenges, W3Schools exercises, Exercism, Scrimba, GitHub practice repos, Quizizz, Kahoot (free tiers)
   - Format: {{ "platformName": "string", "type": "string", "difficulty": "string", "topicTested": "string", "estimatedTime": "string", "url": "string", "description": "string" }}
   - For "type" use: "Quiz", "Coding Challenge", "Interactive Exercise", or "Practice Problems"
   - Include direct URL or how to find it; estimatedTime e.g. "15 min", "1 hour"
   - Only include truly free resources (no trial/premium required)

Each day structure: "day", "topic", "tasks", "hours", "practice", "outcome", "general_resources", "youtube_videos", "practice_resources".

RULES:
- EXACTLY {total_weeks} weeks in weekly_plans. First {detailed_weeks} weeks: full daily_plans (7 days each) with all 3 resource arrays populated. Rest: high-level with key_resource.
- Topics must be SPECIFIC (e.g. "Pandas DataFrames and Series", "React useState and useEffect"), not generic.
- Return ONLY valid JSON. No trailing commas."""

        json_rules = "\n\nCRITICAL: Output must be valid JSON only. Use double quotes for ALL keys and string values (never single quotes). No trailing commas after the last item in any object or array. No unquoted property names. No literal newlines inside strings (use \\n)."

        placeholder_resource = {
            "title": "To be added",
            "type": "Documentation",
            "platform": "TBD",
            "url": "https://www.example.com",
            "what_to_learn": "TBD",
            "duration": "TBD"
        }

        try:
            response_text = self._call_ai_api(prompt + json_rules, timeout=300.0, max_tokens=32768)
            result = self._extract_json_from_response(response_text)
        except ValueError as parse_err:
            logger.warning(f"Structure JSON parse failed, retrying with stricter prompt: {parse_err}")
            response_text = self._call_ai_api(prompt + json_rules + "\n\nYou MUST output strictly valid JSON. Every property name in double quotes. No single quotes anywhere. No trailing commas.", timeout=300.0, max_tokens=32768)
            result = self._extract_json_from_response(response_text)

        if result is None or not isinstance(result, dict):
            logger.warning("Roadmap structure parse returned None or non-dict; using fallback structure")
            from datetime import datetime, timedelta
            result = {
                "total_duration_weeks": total_weeks,
                "estimated_completion_date": (datetime.now() + timedelta(weeks=total_weeks)).strftime("%Y-%m-%d"),
                "phases": [{"phase": 1, "title": "Learning Phase", "duration_weeks": total_weeks, "tools": selected_tools, "objectives": [], "milestones": []}],
                "weekly_plans": [
                    {
                        "week": w,
                        "phase": 1,
                        "focus": f"{tools_str} – Week {w}",
                        "objectives": [],
                        "prerequisites": [],
                        "daily_plans": [
                            {
                                "day": d,
                                "topic": f"Day {d}",
                                "tasks": [],
                                "hours": round(hours_per_week / 7, 1),
                                "resource": placeholder_resource,
                                "practice": "",
                                "outcome": "",
                                "general_resources": [],
                                "youtube_videos": [],
                                "practice_resources": []
                            }
                            for d in range(1, 8)
                        ],
                    }
                    for w in range(1, total_weeks + 1)
                ],
                "projects": [],
                "career_insights": "",
                "skill_gap_analysis": {"strengths": [], "gaps": [], "challenges": [], "strategies": []},
            }

        logger.info(f"Generated roadmap structure with {len(result.get('weekly_plans', []))} weeks")
        return result

    def _search_resources_with_grounding(self, topic: str) -> Optional[List[Dict[str, Any]]]:
        """
        Use Google Search grounding to find real, working resource URLs for a topic.
        Returns list of resources in app format, or None on failure/unavailable.
        """
        if not self._grounding_client or not _grounding_available:
            return None
        prompt = f"""Find 3-4 high-quality FREE learning resources for: "{topic}"

Search the web and provide REAL, WORKING URLs. Include:
- One article or blog (Real Python, Medium, Dev.to, etc.)
- One official documentation or interactive tutorial
- One more helpful resource (course, guide, or docs)

Requirements: FREE, reputable sources, real URLs. Prefer recent content.

Return ONLY a JSON array (no other text, no markdown):
[
  {{"title": "Exact title", "type": "Article", "url": "https://...", "platform": "Platform", "duration": "15 mins", "description": "What you learn"}},
  {{"title": "Docs title", "type": "Documentation", "url": "https://...", "platform": "Official", "duration": "Reference", "description": "Reference"}}
]
Valid JSON array only. No trailing commas."""

        try:
            grounding_tool = types.Tool(google_search=types.GoogleSearch())
            config = types.GenerateContentConfig(tools=[grounding_tool], temperature=0.7)
            response = self._grounding_client.models.generate_content(
                model=self.MODEL_NAME,
                contents=prompt,
                config=config,
            )
            if hasattr(response, 'candidates') and response.candidates:
                cand = response.candidates[0]
                if hasattr(cand, 'grounding_metadata') and cand.grounding_metadata:
                    logger.info("Grounding used - found web sources for: %s", topic[:50])
            text = (response.text or "").replace("```json", "").replace("```", "").strip()
            data = self._extract_json_from_response(text)
            if isinstance(data, list):
                resources = data
            elif isinstance(data, dict) and data.get("resources"):
                resources = data["resources"]
            else:
                resources = []
            allowed = (
                "Interactive Course",
                "Documentation",
                "Tutorial Article",
                "Interactive Platform",
                "GitHub Tutorial",
                "Free Guide",
            )
            type_map = {
                "article": "Tutorial Article",
                "course": "Interactive Course",
                "interactive": "Interactive Platform",
                "documentation": "Documentation",
                "docs": "Documentation",
                "youtube video": "Free Guide",
                "video": "Free Guide",
                "guide": "Free Guide",
            }
            validated = []
            for r in resources:
                if not isinstance(r, dict) or not r.get("url") or not str(r["url"]).startswith("http"):
                    continue
                t = (r.get("type") or "Article").strip()
                res_type = type_map.get(t.lower(), t) if isinstance(t, str) else "Tutorial Article"
                if res_type not in allowed:
                    res_type = "Tutorial Article"
                validated.append({
                    "title": r.get("title", "Resource"),
                    "type": res_type,
                    "platform": r.get("platform", ""),
                    "url": r["url"],
                    "what_to_learn": r.get("description", r.get("whyThisResource", "")),
                    "duration": r.get("duration", "N/A"),
                })
            if len(validated) >= 2:
                return validated[:5]
            # Optionally merge in URLs from grounding_chunks if response had them
            if hasattr(response, "candidates") and response.candidates:
                cand = response.candidates[0]
                if hasattr(cand, "grounding_metadata") and getattr(cand.grounding_metadata, "grounding_chunks", None):
                    for chunk in cand.grounding_metadata.grounding_chunks[:4]:
                        if hasattr(chunk, "web") and chunk.web:
                            uri = getattr(chunk.web, "uri", None) or getattr(chunk.web, "url", None)
                            title = getattr(chunk.web, "title", None) or "Web resource"
                            if uri and uri.startswith("http") and not any(v.get("url") == uri for v in validated):
                                validated.append({
                                    "title": title or "Resource",
                                    "type": "Tutorial Article",
                                    "platform": "Web",
                                    "url": uri,
                                    "what_to_learn": f"Learn about {topic}",
                                    "duration": "Varies",
                                })
            return validated[:5] if len(validated) >= 2 else None
        except Exception as e:
            logger.debug("Grounding resource search failed for %s: %s", topic[:40], e)
            return None

    def _find_resources_for_day(self, topic: str, week_num: int, day_num: int) -> List[Dict[str, Any]]:
        """
        Find 2-5 unique resources for ONE specific day's topic.
        Tries Google Search grounding first for real URLs; falls back to non-grounding AI.
        """
        # Prefer grounding for real, working URLs
        grounded = self._search_resources_with_grounding(topic)
        if grounded and len(grounded) >= 2:
            logger.info("Week %s, Day %s: using %s grounded resources for '%s'", week_num, day_num, len(grounded), topic[:50])
            return grounded[:5]

        prompt = f"""Find 3-4 FREE learning resources specifically for: "{topic}"

Requirements:
- Must be FREE and accessible.
- Must be SPECIFIC to "{topic}" (not generic).
- Include different types: article, documentation, interactive (no YouTube if possible; if you include one, use a real video URL).
- Real, working URLs only.

Popular sources: Real Python, Medium, Dev.to, DigitalOcean, MDN, Python/React/Pandas official docs, freeCodeCamp, W3Schools, Kaggle, Scrimba.

Return a JSON array only (no other text, no markdown):
[
  {{"title": "Specific resource title", "type": "Article", "url": "https://...", "platform": "Platform name", "duration": "15 mins", "description": "What you'll learn"}},
  {{"title": "Docs or tutorial", "type": "Documentation", "url": "https://...", "platform": "Official Docs", "duration": "Reference", "description": "Official reference"}}
]

Return 3-4 resources for "{topic}". Valid JSON array only. No trailing commas."""

        try:
            response_text = self._call_ai_api(prompt, timeout=60.0, max_tokens=1500)
            data = self._extract_json_from_response(response_text)
            if isinstance(data, list):
                resources = data
            elif isinstance(data, dict) and 'resources' in data:
                resources = data['resources']
            else:
                resources = []
            allowed_types = ('Interactive Course', 'Documentation', 'Tutorial Article', 'Interactive Platform', 'GitHub Tutorial', 'Free Guide')
            type_map = {'article': 'Tutorial Article', 'course': 'Interactive Course', 'interactive': 'Interactive Platform', 'documentation': 'Documentation', 'docs': 'Documentation', 'youtube video': 'Free Guide', 'video': 'Free Guide', 'guide': 'Free Guide'}
            validated = []
            for r in resources:
                if isinstance(r, dict) and r.get('url') and str(r['url']).startswith('http'):
                    t = (r.get('type') or 'Article').strip()
                    res_type = type_map.get(t.lower(), t) if isinstance(t, str) else 'Tutorial Article'
                    if res_type not in allowed_types:
                        res_type = 'Tutorial Article'
                    validated.append({
                        'title': r.get('title', 'Resource'),
                        'type': res_type,
                        'platform': r.get('platform', ''),
                        'url': r['url'],
                        'what_to_learn': r.get('description', r.get('whyThisResource', '')),
                        'duration': r.get('duration', 'N/A')
                    })
            if len(validated) < 2:
                validated.extend(self._get_fallback_for_topic(topic, 3 - len(validated)))
            logger.info(f"Week {week_num}, Day {day_num}: found {len(validated)} resources for '{topic[:50]}'")
            return validated[:5]
        except Exception as e:
            logger.warning(f"Error finding resources for day ({topic[:30]}): {e}")
            return self._get_fallback_for_topic(topic, 3)

    def _get_fallback_for_topic(self, topic: str, count: int = 3) -> List[Dict[str, Any]]:
        """Fallback resources when AI fails for a day's topic."""
        encoded = topic.replace(' ', '+') if topic else 'programming'
        fallbacks = [
            {"title": f"Search '{topic}' on YouTube", "type": "Free Guide", "platform": "YouTube", "url": f"https://www.youtube.com/results?search_query={encoded}", "what_to_learn": "Search results for this topic", "duration": "Varies"},
            {"title": "W3Schools tutorials", "type": "Interactive Platform", "platform": "W3Schools", "url": "https://www.w3schools.com/", "what_to_learn": "Interactive tutorials", "duration": "Varies"},
            {"title": "freeCodeCamp Learn", "type": "Interactive Course", "platform": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn", "what_to_learn": "Hands-on courses", "duration": "Varies"},
            {"title": "Real Python", "type": "Tutorial Article", "platform": "Real Python", "url": "https://realpython.com/", "what_to_learn": "Articles and tutorials", "duration": "Varies"},
            {"title": "MDN Web Docs", "type": "Documentation", "platform": "Mozilla", "url": "https://developer.mozilla.org/", "what_to_learn": "Web reference", "duration": "Reference"},
        ]
        return fallbacks[:count]

    def _add_resources_to_each_day(self, roadmap: Dict[str, Any]) -> Dict[str, Any]:
        """
        STEP 2: Normalize resource fields from the one-call structure.
        Resources come from _generate_roadmap_structure; this only maps/normalizes.
        Adds day['resource'] for backward compatibility (first general resource).
        Adds YouTube search URLs to youtube_videos when missing.
        """
        for week in roadmap.get('weekly_plans', []):
            if 'daily_plans' not in week or not week['daily_plans']:
                if 'key_resource' in week and week.get('key_resource', {}).get('url') == 'https://www.example.com':
                    fallback = self._get_fallback_for_topic(week.get('focus', 'general'), 1)
                    if fallback:
                        r = fallback[0]
                        week['key_resource'] = {'title': r['title'], 'url': r['url'], 'type': r['type']}
                continue
            week_num = week.get('week', 0)
            for day in week['daily_plans']:
                topic = day.get('topic') or week.get('focus', 'general')
                day_num = day.get('day', 0)

                # Accept both naming conventions (AI may use either)
                general = day.get('general_resources') or day.get('resources') or []
                youtube = day.get('youtube_videos') or day.get('youtubeResources') or []
                practice = day.get('practice_resources') or day.get('assessmentResources') or []

                day['general_resources'] = general if isinstance(general, list) else []
                day['youtube_videos'] = youtube if isinstance(youtube, list) else []
                day['practice_resources'] = practice if isinstance(practice, list) else []

                # Add YouTube search URL to each video if missing
                for video in day['youtube_videos']:
                    if isinstance(video, dict) and not video.get('url'):
                        title = video.get('videoTitle', video.get('title', ''))
                        channel = video.get('channelName', video.get('channel', ''))
                        query = f"{title} {channel}".strip() or topic
                        video['url'] = f"https://www.youtube.com/results?search_query={quote_plus(query)}"

                # Set day['resource'] from first general resource for backward compatibility
                if day['general_resources'] and isinstance(day['general_resources'][0], dict):
                    r = day['general_resources'][0]
                    day['resource'] = {
                        'title': r.get('title', 'Resource'),
                        'type': r.get('type', 'Documentation'),
                        'platform': r.get('platform', ''),
                        'url': r.get('url', 'https://www.example.com'),
                        'what_to_learn': r.get('description', ''),
                        'duration': r.get('duration', 'N/A')
                    }
                    day['resources'] = day['general_resources']
                elif not day.get('resource'):
                    # Fallback if one-call didn't produce general resources
                    fallback_resources = self._find_resources_for_day(topic, week_num, day_num)
                    if fallback_resources:
                        r = fallback_resources[0]
                        day['resource'] = {
                            'title': r['title'],
                            'type': r['type'],
                            'platform': r['platform'],
                            'url': r['url'],
                            'what_to_learn': r.get('what_to_learn', ''),
                            'duration': r.get('duration', 'N/A')
                        }
                        day['resources'] = fallback_resources
                        day['general_resources'] = fallback_resources
        return roadmap

    def _get_fallback_resources(self, topics: List[str], count: int = 6) -> List[Dict[str, Any]]:
        """Fallback resources when AI fails. Generic but high-quality."""
        fallbacks = [
            {"title": "freeCodeCamp Learn", "type": "Interactive", "platform": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn", "what_to_learn": "Hands-on courses", "duration": "Varies"},
            {"title": "MDN Web Docs", "type": "Documentation", "platform": "Mozilla", "url": "https://developer.mozilla.org/", "what_to_learn": "Web reference", "duration": "Reference"},
            {"title": "W3Schools", "type": "Interactive", "platform": "W3Schools", "url": "https://www.w3schools.com/", "what_to_learn": "Tutorials", "duration": "Varies"},
            {"title": "Real Python", "type": "Article", "platform": "Real Python", "url": "https://realpython.com/", "what_to_learn": "Python articles", "duration": "Varies"},
            {"title": "Dev.to", "type": "Article", "platform": "Dev.to", "url": "https://dev.to/", "what_to_learn": "Developer articles", "duration": "Varies"},
            {"title": "Official Documentation", "type": "Documentation", "platform": "Docs", "url": "https://www.example.com", "what_to_learn": "Check official docs for your topic", "duration": "N/A"},
        ]
        return fallbacks[:count]

    def generate_roadmap(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        TWO-STEP roadmap generation:
        Step 1: Generate roadmap structure (weeks, topics, objectives) — one AI call.
        Step 2: For EACH DAY, one separate AI call to find 2-5 resources for that day's topic.
        Ensures unique resources per day and better quality matching.
        """
        try:
            logger.info("Starting two-step roadmap generation")
            cache_data = {
                'tools': sorted(user_data.get('selected_tools', [])),
                'hours': user_data.get('hours_per_week'),
                'level': user_data.get('profile', {}).get('experience_level'),
            }
            cache_key = self._get_cache_key('generate_roadmap', json.dumps(cache_data, sort_keys=True))
            cached = self._get_cached_response(cache_key)
            if cached:
                logger.info("Returning cached roadmap")
                return cached

            total_weeks = self._calculate_total_weeks(user_data)
            experience_level = self._determine_experience_level(user_data)
            hours_per_week = user_data.get('hours_per_week', 10)

            logger.info(f"Step 1: Generating {total_weeks}-week roadmap structure")
            roadmap_structure = self._generate_roadmap_structure(user_data, total_weeks, experience_level)

            logger.info("Step 2: Normalizing resource fields from structure")
            result = self._add_resources_to_each_day(roadmap_structure)

            # Trim to requested weeks if the model returned more
            if result.get('weekly_plans') and len(result['weekly_plans']) > total_weeks:
                result['weekly_plans'] = result['weekly_plans'][:total_weeks]
                result['total_duration_weeks'] = total_weeks
                logger.info("Trimmed roadmap to %s weeks (requested)", total_weeks)

            # Validate (no verified-resource list — we allow AI-suggested URLs from step 2)
            is_valid_structure, structure_errors = self.validate_roadmap_structure(result, [])
            if not is_valid_structure:
                logger.warning(f"Roadmap structure validation issues: {structure_errors}")
            validation_errors = self._validate_roadmap(result, hours_per_week)
            if validation_errors:
                logger.warning(f"Roadmap validation: {validation_errors}")

            result = self._filter_youtube_resources(result)

            if 'estimated_completion_date' not in result and result.get('total_duration_weeks'):
                from datetime import datetime, timedelta
                weeks = result.get('total_duration_weeks', 0)
                if weeks > 0:
                    result['estimated_completion_date'] = (datetime.now() + timedelta(weeks=weeks)).strftime('%Y-%m-%d')

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
            
            response_text = self._call_ai_api(prompt)
            
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

