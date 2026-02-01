"""
Resource Generator - Generates 3 types of learning resources using Gemini API.
Uses EXACT prompts from the resource project (sub-buildathon) for consistency.

Resource types:
1. General learning resources (docs, articles, courses)
2. YouTube videos (5-7 curated videos)
3. Practice/Quiz resources (LeetCode, HackerRank, etc.)
"""
import os
import re
import json
import ast
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_OPENAI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai"


class ResourceGenerator:
    """Generates learning resources for roadmap topics using Gemini."""

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
            logger.info(f"ResourceGenerator initialized with model: {self.MODEL_NAME}")
        except Exception as e:
            logger.error(f"Failed to initialize ResourceGenerator: {str(e)}")
            raise ValueError(f"Failed to initialize ResourceGenerator: {str(e)}")

    def _call_gemini(self, prompt: str, max_tokens: int = 4096, timeout: float = 60.0) -> str:
        """Call Gemini API with same config as resource project (temperature 0.7)."""
        try:
            response = self.client.chat.completions.create(
                model=self.MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7,
                timeout=timeout
            )
            if not response or not response.choices or len(response.choices) == 0:
                raise ValueError("Empty response from Gemini API")
            text = response.choices[0].message.content
            if not text:
                raise ValueError("Empty response content from Gemini API")
            return text.strip()
        except Exception as e:
            logger.error(f"Gemini API call failed: {str(e)}")
            raise

    def _extract_json(self, text: str) -> Any:
        """Extract and parse JSON from response, handling markdown and common LLM errors."""
        try:
            # Remove markdown code blocks
            if '```json' in text:
                start = text.find('```json') + 7
                end = text.find('```', start)
                text = text[start:end].strip()
            elif '```' in text:
                start = text.find('```') + 3
                end = text.find('```', start)
                text = text[start:end].strip()

            # Repair trailing commas
            for _ in range(20):
                new_text = re.sub(r',\s*}', '}', text)
                new_text = re.sub(r',\s*]', ']', new_text)
                if new_text == text:
                    break
                text = new_text

            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass

            try:
                return ast.literal_eval(text)
            except (ValueError, SyntaxError):
                pass

            raise ValueError("Could not parse response as JSON")
        except Exception as e:
            logger.error(f"JSON extraction failed: {str(e)}")
            raise

    def generate_general_resources(self, topic: str) -> List[Dict[str, Any]]:
        """
        Generate 3-4 general learning resources (docs, articles, courses).
        Uses EXACT prompt format from resource project promptTemplates.js.
        """
        prompt = f"""Generate 4-5 GENERAL LEARNING RESOURCES for the topic: "{topic}"

REQUIREMENTS (DO NOT CHANGE):
- Official documentation, free courses (Codecademy, freeCodeCamp, etc.), quality blog posts, practice repositories, interactive platforms
- Include actual URLs when possible
- Only suggest resources that are actually free

Format each resource as:
{{ "title": "string", "url": "string", "type": "string", "description": "string", "difficulty": "string", "platform": "string" }}

Return ONLY a valid JSON array (no markdown, no extra text):
[
  {{ "title": "Resource title", "url": "https://...", "type": "Documentation", "description": "What you learn", "difficulty": "Beginner", "platform": "Official Docs" }},
  {{ "title": "Another resource", "url": "https://...", "type": "Tutorial Article", "description": "Covers X and Y", "difficulty": "Intermediate", "platform": "Real Python" }}
]

Return 4-5 resources for "{topic}". Valid JSON array only. No trailing commas."""

        try:
            response_text = self._call_gemini(prompt, max_tokens=2000)
            data = self._extract_json(response_text)
            if isinstance(data, list):
                return data[:5]
            if isinstance(data, dict) and 'resources' in data:
                return data['resources'][:5]
            return []
        except Exception as e:
            logger.warning(f"generate_general_resources failed for '{topic[:40]}': {e}")
            return []

    def generate_youtube_videos(self, topic: str) -> List[Dict[str, Any]]:
        """
        Generate 5-7 YouTube video recommendations.
        Uses EXACT prompt format from resource project promptTemplates.js.
        """
        prompt = f"""Generate 5-7 YOUTUBE VIDEO recommendations for the topic: "{topic}"

REQUIREMENTS (DO NOT CHANGE):
- Specific video recommendations for the day's topic
- Prioritize well-known channels: Fireship, Traversy Media, freeCodeCamp, The Net Ninja, Web Dev Simplified
- Use actual video titles when possible; include estimated duration (e.g. "12 min", "1h 20m")

Format each video as:
{{ "videoTitle": "string", "channelName": "string", "duration": "string", "description": "string", "difficulty": "string", "recommendationReason": "string" }}

Return ONLY a valid JSON array (no markdown, no extra text):
[
  {{ "videoTitle": "Exact Video Title", "channelName": "Channel Name", "duration": "15 min", "description": "Covers X", "difficulty": "Beginner", "recommendationReason": "Clear explanation" }},
  {{ "videoTitle": "Another Video", "channelName": "Another Channel", "duration": "45 min", "description": "Hands-on tutorial", "difficulty": "Intermediate", "recommendationReason": "Project-based" }}
]

Return 5-7 videos for "{topic}". Valid JSON array only. No trailing commas."""

        try:
            response_text = self._call_gemini(prompt, max_tokens=2000)
            data = self._extract_json(response_text)
            if isinstance(data, list):
                videos = data[:7]
                # Add search URL for each video (YouTube doesn't provide direct API URLs)
                for v in videos:
                    if isinstance(v, dict) and not v.get('url'):
                        query = f"{v.get('videoTitle', '')} {v.get('channelName', '')}".strip()
                        v['url'] = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                return videos
            if isinstance(data, dict) and 'youtubeResources' in data:
                return data['youtubeResources'][:7]
            return []
        except Exception as e:
            logger.warning(f"generate_youtube_videos failed for '{topic[:40]}': {e}")
            return []

    def generate_practice_resources(self, topic: str) -> List[Dict[str, Any]]:
        """
        Generate 3-5 practice/quiz resources (LeetCode, HackerRank, etc.).
        Uses EXACT prompt format from resource project promptTemplates.js.
        """
        prompt = f"""Generate 3-5 PRACTICE & QUIZZES for the topic: "{topic}"

REQUIREMENTS (DO NOT CHANGE):
- Interactive quizzes, coding challenges, and practice assessments for the day's topic
- Only FREE platforms: LeetCode, HackerRank, Codewars, freeCodeCamp challenges, W3Schools exercises, Exercism, Scrimba, GitHub practice repos, Quizizz, Kahoot (free tiers)
- For "type" use: "Quiz", "Coding Challenge", "Interactive Exercise", or "Practice Problems"
- Include direct URL or how to find it; estimatedTime e.g. "15 min", "1 hour"
- Only include truly free resources (no trial/premium required)

Format each as:
{{ "platformName": "string", "type": "string", "difficulty": "string", "topicTested": "string", "estimatedTime": "string", "url": "string", "description": "string" }}

Return ONLY a valid JSON array (no markdown, no extra text):
[
  {{ "platformName": "LeetCode", "type": "Coding Challenge", "difficulty": "Easy", "topicTested": "Arrays", "estimatedTime": "30 min", "url": "https://leetcode.com/...", "description": "Practice array problems" }},
  {{ "platformName": "freeCodeCamp", "type": "Interactive Exercise", "difficulty": "Beginner", "topicTested": "Basic concepts", "estimatedTime": "1 hour", "url": "https://freecodecamp.org/...", "description": "Hands-on exercises" }}
]

Return 3-5 practice resources for "{topic}". Valid JSON array only. No trailing commas."""

        try:
            response_text = self._call_gemini(prompt, max_tokens=2000)
            data = self._extract_json(response_text)
            if isinstance(data, list):
                return data[:5]
            if isinstance(data, dict) and 'assessmentResources' in data:
                return data['assessmentResources'][:5]
            return []
        except Exception as e:
            logger.warning(f"generate_practice_resources failed for '{topic[:40]}': {e}")
            return []

    def generate_all_resources_for_day(self, topic: str, day_info: dict) -> dict:
        """
        Generate all 3 types of resources for a single day's topic.

        Args:
            topic: The day's learning topic
            day_info: Dict with 'week', 'day', 'hours' (optional, for context)

        Returns:
            {
                "general_resources": [...],
                "youtube_videos": [...],
                "practice_resources": [...]
            }
        """
        logger.info(f"Generating resources for Week {day_info.get('week', '?')}, Day {day_info.get('day', '?')}: {topic[:50]}")

        general = self.generate_general_resources(topic)
        youtube = self.generate_youtube_videos(topic)
        practice = self.generate_practice_resources(topic)

        return {
            "general_resources": general,
            "youtube_videos": youtube,
            "practice_resources": practice,
        }
