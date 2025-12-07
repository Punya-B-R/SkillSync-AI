"""
AI service for interacting with OpenRouter API (Llama 3.3 70B).
"""
import os
import json
import logging
import time
import hashlib
from typing import Dict, Any, Optional, Tuple, List
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
    
    def _call_openrouter_api(self, prompt: str, retry: bool = True, max_tokens: int = 8000, timeout: float = 120.0) -> str:
        """
        Call OpenRouter API with optimized settings for speed and error handling.
        
        Args:
            prompt: Prompt to send to OpenRouter
            retry: Whether to retry on failure
            max_tokens: Maximum tokens to generate (default 8000 for roadmaps)
            timeout: Request timeout in seconds (default 120s, increased to 180s for roadmaps)
            
        Returns:
            str: API response text
            
        Raises:
            ValueError: For API errors, rate limiting, or invalid API key
            TimeoutError: For timeout errors
        """
        try:
            logger.info(f"Calling OpenRouter API with model: {self.MODEL_NAME}")
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
                    logger.info("Retrying API call with reduced max_tokens after timeout")
                    time.sleep(2)
                    # Retry with reduced max_tokens for faster response
                    return self._call_openrouter_api(prompt, retry=False, max_tokens=max_tokens // 2, timeout=timeout)
                else:
                    raise TimeoutError("API request timed out. Please try again.")
            
            # Generic error
            logger.error(f"OpenRouter API error: {str(e)}")
            if retry:
                logger.info("Retrying API call after error")
                time.sleep(2)
                return self._call_openrouter_api(prompt, retry=False, max_tokens=max_tokens, timeout=timeout)
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
                        warnings.append(f"Project {i+1}: Missing bonus_features")
                    elif not isinstance(project.get('bonus_features'), list) or len(project.get('bonus_features', [])) < 2:
                        warnings.append(f"Project {i+1}: bonus_features should be a list with at least 2 items")
        
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
        Calculate estimated total weeks needed based on tools and hours per week.
        
        Args:
            user_data: User data with selected_tools and hours_per_week
            
        Returns:
            int: Estimated total weeks
        """
        selected_tools = user_data.get('selected_tools', [])
        hours_per_week = user_data.get('hours_per_week', 10)
        
        # Rough estimate: 2-3 weeks per tool, adjusted by hours per week
        base_weeks_per_tool = 2.5
        tools_count = len(selected_tools)
        
        # Adjust based on hours per week (more hours = faster)
        time_multiplier = max(0.7, min(1.3, 10 / hours_per_week))
        
        total_weeks = int(tools_count * base_weeks_per_tool * time_multiplier)
        
        # Ensure minimum 4 weeks and maximum 16 weeks
        return max(4, min(16, total_weeks))
    
    def generate_roadmap(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized learning roadmap with detailed daily plans for first 4 weeks only.
        This significantly reduces generation time while giving users immediate actionable content.
        
        Roadmap includes:
        - NO YouTube videos (only interactive courses, documentation, articles, tutorials)
        - Projects with detailed problem statements explaining the "why"
        - Bonus features for each project
        
        Args:
            user_data: Dict containing:
            - profile: User profile with skills, experience level, etc.
            - selected_tools: List of tools/technologies to learn
            - hours_per_week: Hours per week for learning
            - learning_style: Learning style preference
            - deadline: Optional deadline
            
        Returns:
            dict: Complete roadmap with phases, detailed weekly plans (first 4 weeks), high-level overview for rest,
                  projects with problem statements, career insights, and skill gap analysis
        """
        try:
            logger.info("Starting optimized roadmap generation")
            
            # Check cache with optimized key (only relevant fields)
            cache_data = {
                'tools': sorted(user_data.get('selected_tools', [])),
                'hours': user_data.get('hours_per_week'),
                'style': user_data.get('learning_style'),
                'level': user_data.get('profile', {}).get('experience_level'),
                'skills_count': len(user_data.get('profile', {}).get('skills', []))
            }
            cache_key = self._get_cache_key('generate_roadmap', json.dumps(cache_data, sort_keys=True))
            cached = self._get_cached_response(cache_key)
            if cached:
                logger.info("Returning cached roadmap")
                return cached
            
            profile = user_data.get('profile', {})
            selected_tools = user_data.get('selected_tools', [])
            hours_per_week = user_data.get('hours_per_week', 10)
            learning_style = user_data.get('learning_style', 'Balanced')
            deadline = user_data.get('deadline', 'Flexible')
            
            # Calculate total weeks needed
            total_weeks = self._calculate_total_weeks(user_data)
            detailed_weeks = min(4, total_weeks)
            
            # Gather all verified resources for selected tools
            available_resources = []
            for tool in selected_tools:
                resources = get_resources_for_tech(tool)
                available_resources.extend(resources)
            
            # Remove duplicates
            seen_urls = set()
            unique_resources = []
            for resource in available_resources:
                if resource['url'] not in seen_urls:
                    seen_urls.add(resource['url'])
                    unique_resources.append(resource)
            
            logger.info(f"Found {len(unique_resources)} unique verified resources for {len(selected_tools)} technologies")
            
            # Convert to JSON string to include in prompt
            resources_json = json.dumps(unique_resources, indent=2)
            
            # Detailed prompt with verified resources
            skills_str = ', '.join(profile.get('skills', [])[:10])  # Limit to top 10
            tools_str = ', '.join(selected_tools)
            
            prompt = f"""Learning Roadmap for {profile.get('experience_level', 'Mid-Level')} professional.

Skills: {skills_str}
Learning: {tools_str}
Time: {hours_per_week}h/week
Style: {learning_style}

AVAILABLE VERIFIED RESOURCES (you MUST use ONLY these resources):
{resources_json}

Generate JSON roadmap:

1. 3-4 phases with objectives

2. Detailed daily plans for FIRST {detailed_weeks} WEEKS ONLY (7 days each):
   Each day needs:
   - Day number, topic, tasks (3-4), hours
   - ONE resource from the AVAILABLE VERIFIED RESOURCES list above
     * CRITICAL: Use the EXACT url from the resources provided
     * Match the resource to the day's topic/tasks
     * Copy title, type, platform, url, duration exactly as provided
     * Add "what_to_learn" field explaining what to focus on from this resource for this day
   - Practice exercise
   - Expected outcome

3. High-level overview for remaining weeks:
   - Focus, main topics, hours, 1 key resource (from verified list)

4. PROJECT IDEAS (3 projects with specific problem statements):
   Each project needs:
   - Title
   - Problem statement (3-5 sentences: what problem, who uses it, value, learning benefit)
   - Technologies (from selected tools)
   - Difficulty, estimated_hours
   - Learning outcomes (3-4 items)
   - Implementation steps (5-7 detailed steps)
   - Start week
   - Bonus features (2-3 optional features)

5. Career insights (4 sentences)

6. Skill gap analysis (3 strengths, 3 gaps, 2 challenges, 3 strategies)

CRITICAL RULES:
- ONLY use resources from the AVAILABLE VERIFIED RESOURCES list
- NEVER generate or invent resource URLs
- Copy URLs EXACTLY as provided in the list
- If no perfect match exists, use the closest relevant resource
- Each day must have a different resource (no repeats in same week)
- Resources should progress from beginner to advanced topics

PROJECT PROBLEM STATEMENT EXAMPLE:
{{
  "title": "Decentralized Task Marketplace",
  "problem_statement": "Freelance platforms charge high fees (20-30%) and have centralized control over payments, leading to delayed payouts and disputes. This project creates a blockchain-based task marketplace where clients and freelancers interact directly through smart contracts, ensuring automatic payment release upon task completion and reducing fees to near-zero. This is valuable for learning how to build real-world dApps that solve trust issues in peer-to-peer transactions. It demonstrates practical use of smart contracts, IPFS for file storage, and Web3 wallet integration.",
  "technologies": ["Solidity", "Ethers.js", "React", "IPFS"],
  "difficulty": "Intermediate",
  "estimated_hours": 40,
  "learning_outcomes": [
    "Build and deploy smart contracts with escrow logic",
    "Integrate Web3 wallets (MetaMask) with React frontend",
    "Store and retrieve files using IPFS",
    "Handle blockchain transactions and events"
  ],
  "steps": [
    "Design smart contract architecture for task creation, bidding, and escrow",
    "Write and test Solidity contracts with dispute resolution mechanism",
    "Build React frontend with wallet connection and task listing UI",
    "Integrate IPFS for storing task descriptions and deliverables",
    "Implement task lifecycle: creation, bidding, acceptance, completion, payment",
    "Add event listeners for blockchain events and update UI in real-time",
    "Deploy to testnet and conduct end-to-end testing"
  ],
  "start_week": 6,
  "bonus_features": [
    "Reputation system based on completed tasks",
    "Multi-signature escrow for high-value tasks",
    "Search and filter functionality with tags"
  ]
}}

Return ONLY valid JSON:
{{
  "total_duration_weeks": {total_weeks},
  "estimated_completion_date": "YYYY-MM-DD",
  "phases": [{{"phase": n, "title": str, "duration_weeks": n, "tools": [], "objectives": [], "milestones": []}}],
  "weekly_plans": [
    {{
      "week": 1-{detailed_weeks},
      "phase": n,
      "focus": str,
      "objectives": [],
      "prerequisites": [],
      "daily_plans": [
        {{
          "day": 1-7,
          "topic": str,
          "tasks": [],
          "hours": n,
          "resource": {{
            "title": "EXACT title from verified list",
            "type": "EXACT type from verified list",
            "platform": "EXACT platform from verified list",
            "url": "EXACT url from verified list",
            "what_to_learn": "What to focus on from this resource today",
            "duration": "EXACT duration from verified list"
          }},
          "practice": str,
          "outcome": str
        }}
      ]
    }},
    {{
      "week": {detailed_weeks + 1}+,
      "phase": n,
      "focus": str,
      "main_topics": [],
      "total_hours": n,
      "key_resource": {{
        "title": "from verified list",
        "url": "from verified list",
        "type": "from verified list"
      }}
    }}
  ],
  "projects": [
    {{
      "title": str,
      "problem_statement": str,
      "technologies": [],
      "difficulty": str,
      "estimated_hours": n,
      "learning_outcomes": [],
      "steps": [],
      "start_week": n,
      "bonus_features": []
    }}
  ],
  "career_insights": str,
  "skill_gap_analysis": {{
    "strengths": [],
    "gaps": [],
    "challenges": [],
    "strategies": []
  }}
}}"""
            
            # First attempt with extended timeout for roadmap generation (15 minutes)
            response_text = self._call_openrouter_api(prompt, timeout=900.0, max_tokens=10000)
            result = self._extract_json_from_response(response_text)
            
            # Validate the response structure first (quick check)
            is_valid_structure, structure_errors = self.validate_roadmap_structure(result, unique_resources)
            if not is_valid_structure:
                logger.warning(f"Roadmap structure validation failed: {structure_errors}")
                logger.info("Retrying roadmap generation with stricter prompt")
                
                # Retry with stricter prompt and extended timeout (15 minutes)
                stricter_prompt = prompt + "\n\nIMPORTANT: Ensure every daily_plan has a complete resource object with url field. All 7 days must be present for each week. CRITICAL: You MUST select resource URLs ONLY from the VERIFIED RESOURCES list provided above. DO NOT create or invent URLs. All URLs must be from the verified list. DO NOT include any YouTube videos or YouTube links. All projects must include detailed problem_statement and bonus_features fields."
                
                response_text = self._call_openrouter_api(stricter_prompt, timeout=900.0, max_tokens=10000)
                result = self._extract_json_from_response(response_text)
                
                # Validate structure again
                is_valid_structure, structure_errors = self.validate_roadmap_structure(result, unique_resources)
                if not is_valid_structure:
                    logger.error(f"Roadmap structure validation failed after retry: {structure_errors}")
                    raise ValueError(f"Generated roadmap failed structure validation: {structure_errors}")
            
            # Full validation (includes hours, projects, etc.)
            validation_errors = self._validate_roadmap(result, hours_per_week)
            
            if validation_errors:
                logger.warning(f"Roadmap validation failed: {validation_errors}")
                # Don't retry again if structure is valid but other validations fail
                # Log as warning but don't fail - structure is most important
                logger.warning("Roadmap structure is valid but some fields may be missing or incorrect")
            
            # Filter out any YouTube resources that might have slipped through
            result = self._filter_youtube_resources(result)
            
            # Validate that all URLs are from our verified list and replace any hallucinated URLs
            if 'weekly_plans' in result:
                verified_urls = {r['url'] for r in unique_resources}
                
                for week in result['weekly_plans']:
                    if 'daily_plans' in week:
                        for day in week['daily_plans']:
                            if 'resource' in day and 'url' in day['resource']:
                                url = day['resource']['url']
                                if url not in verified_urls:
                                    # If AI hallucinated a URL, replace with a verified one
                                    logger.warning(f"Hallucinated URL detected: {url}")
                                    # Find a replacement from verified resources
                                    replacement = unique_resources[0] if unique_resources else None
                                    if replacement:
                                        day['resource'] = {
                                            'title': replacement['title'],
                                            'type': replacement['type'],
                                            'platform': replacement['platform'],
                                            'url': replacement['url'],
                                            'what_to_learn': day['resource'].get('what_to_learn', 
                                                f"Study {replacement['topics'][0] if replacement.get('topics') else 'the topic'}"),
                                            'duration': replacement['duration']
                                        }
                    
                    # Check key_resource in high-level weeks
                    if 'key_resource' in week and 'url' in week['key_resource']:
                        url = week['key_resource']['url']
                        if url not in verified_urls:
                            logger.warning(f"Hallucinated URL in key_resource: {url}")
                            if unique_resources:
                                replacement = unique_resources[0]
                                week['key_resource'] = {
                                    'title': replacement['title'],
                                    'url': replacement['url'],
                                    'type': replacement['type']
                                }
            
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

