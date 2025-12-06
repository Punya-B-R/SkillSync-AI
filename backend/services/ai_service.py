"""
AI service for interacting with OpenRouter API (Llama 3.3 70B).
"""
import os
import json
import logging
import time
import hashlib
from typing import Dict, Any, Optional, Tuple
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
                                        
                                        # Validate resource type
                                        valid_types = ['YouTube Video', 'Free Course', 'Documentation', 'Article', 'Tutorial']
                                        resource_type = resource.get('type', '')
                                        if resource_type and resource_type not in valid_types:
                                            errors.append(f"Week {week_plan.get('week', week_idx + 1)}, Day {daily_plan.get('day', day_idx + 1)}: Invalid resource type '{resource_type}'. Must be one of {valid_types}")
                                
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
                    
                    project_required = ['title', 'description', 'technologies', 'difficulty', 
                                       'estimated_hours', 'learning_outcomes', 'steps', 'start_week']
                    for field in project_required:
                        if field not in project:
                            errors.append(f"Project {proj_idx + 1}: Missing field '{field}'")
        
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
    
    def validate_roadmap_structure(self, roadmap_data: Dict[str, Any]) -> Tuple[bool, list]:
        """
        Validate that roadmap has correct structure with daily plans and resources.
        Standalone validation function that can be used independently.
        
        Args:
            roadmap_data: Roadmap dictionary to validate
            
        Returns:
            tuple: (is_valid: bool, errors: list of error messages)
        """
        errors = []
        
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
            
            # Validate each day (only for detailed weeks)
            if not has_daily_plans:
                # Skip day validation for high-level weeks
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
                        errors.append(f"Week {week_num}, Day {day_num}: URL must be a string")
        
        return len(errors) == 0, errors
    
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
        
        Args:
            user_data: Dict containing profile, selected_tools, hours_per_week, learning_style, deadline
            
        Returns:
            dict: Complete roadmap with phases, detailed weekly plans (first 4 weeks), high-level overview for rest
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
            
            # Compressed, optimized prompt
            skills_str = ', '.join(profile.get('skills', [])[:10])  # Limit to top 10
            tools_str = ', '.join(selected_tools)
            
            prompt = f"""Learning Roadmap for {profile.get('experience_level', 'Mid-Level')} professional.

Skills: {skills_str}
Learning: {tools_str}
Time: {hours_per_week}h/week
Style: {learning_style}

Generate JSON roadmap:
- 3-4 phases (phase, title, duration_weeks, tools, objectives, milestones)
- DETAILED daily plans for FIRST {detailed_weeks} WEEKS ONLY (7 days each)
  Each day: topic, 3 tasks, hours, resource (title, type, platform, url, what_to_learn, duration), practice, outcome
- High-level overview for weeks {detailed_weeks + 1}+ (week, phase, focus, main_topics: [], total_hours, key_resource: {{title, url, type}})
- 3 project ideas (title, description, technologies, difficulty, estimated_hours, learning_outcomes, steps: 5 max, start_week)
- Career insights (4 sentences max)
- Skill gaps (strengths: 3, gaps: 3, challenges: 2, strategies: 3)

Requirements:
- Only FREE resources with real URLs (http:// or https://)
- Concise but actionable
- Valid JSON only

JSON structure:
{{
  "total_duration_weeks": {total_weeks},
  "estimated_completion_date": "YYYY-MM-DD",
  "phases": [{{"phase": n, "title": str, "duration_weeks": n, "tools": [], "objectives": [], "milestones": []}}],
  "weekly_plans": [
    {{"week": 1-{detailed_weeks}, "phase": n, "focus": str, "objectives": [], "prerequisites": [], "daily_plans": [{{"day": 1-7, "topic": str, "tasks": [], "hours": n, "resource": {{"title": str, "type": str, "platform": str, "url": str, "what_to_learn": str, "duration": str}}, "practice": str, "outcome": str}}]}},
    {{"week": {detailed_weeks + 1}+, "phase": n, "focus": str, "main_topics": [], "total_hours": n, "key_resource": {{"title": str, "url": str, "type": str}}}}
  ],
  "projects": [{{"title": str, "description": str, "technologies": [], "difficulty": str, "estimated_hours": n, "learning_outcomes": [], "steps": [], "start_week": n}}],
  "career_insights": str,
  "skill_gap_analysis": {{"strengths": [], "gaps": [], "challenges": [], "strategies": []}}
}}"""
            
            # First attempt with extended timeout for roadmap generation (15 minutes)
            response_text = self._call_openrouter_api(prompt, timeout=900.0, max_tokens=10000)
            result = self._extract_json_from_response(response_text)
            
            # Validate the response structure first (quick check)
            is_valid_structure, structure_errors = self.validate_roadmap_structure(result)
            if not is_valid_structure:
                logger.warning(f"Roadmap structure validation failed: {structure_errors}")
                logger.info("Retrying roadmap generation with stricter prompt")
                
                # Retry with stricter prompt and extended timeout (15 minutes)
                stricter_prompt = prompt + "\n\nIMPORTANT: Ensure every daily_plan has a complete resource object with url field. All 7 days must be present for each week. Verify all resource URLs are real and accessible. All URLs must start with http:// or https://."
                
                response_text = self._call_openrouter_api(stricter_prompt, timeout=900.0, max_tokens=10000)
                result = self._extract_json_from_response(response_text)
                
                # Validate structure again
                is_valid_structure, structure_errors = self.validate_roadmap_structure(result)
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

