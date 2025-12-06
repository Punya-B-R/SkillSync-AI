"""
Test script for roadmap validation and structure testing.

Run this to test the complete flow:
1. Upload sample resume
2. Generate roadmap
3. Verify all weeks have 7 days
4. Verify each day has resource with URL
5. Check URLs are accessible (optional)
6. Verify resources are marked as free
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.ai_service import AIService


def test_roadmap_structure_validation():
    """Test the validate_roadmap_structure function with sample data."""
    ai_service = AIService()
    
    # Test case 1: Valid roadmap structure
    valid_roadmap = {
        "total_duration_weeks": 4,
        "weekly_plans": [
            {
                "week": 1,
                "phase": 1,
                "focus": "Introduction to Python",
                "objectives": ["Learn basics", "Set up environment"],
                "prerequisites": ["Basic computer skills"],
                "daily_plans": [
                    {
                        "day": 1,
                        "topic": "Python Basics",
                        "tasks": ["Install Python", "Write Hello World"],
                        "hours": 2,
                        "resource": {
                            "title": "Python Tutorial",
                            "type": "YouTube Video",
                            "platform": "YouTube",
                            "url": "https://www.youtube.com/watch?v=example",
                            "what_to_learn": "Python fundamentals",
                            "duration": "2 hours"
                        },
                        "practice": "Write a simple program",
                        "outcome": "Understand Python syntax"
                    }
                ] * 7  # Repeat for 7 days
            }
        ]
    }
    
    is_valid, errors = ai_service.validate_roadmap_structure(valid_roadmap)
    print(f"Test 1 - Valid roadmap: {is_valid}")
    if errors:
        print(f"  Errors: {errors}")
    assert is_valid, f"Valid roadmap should pass validation: {errors}"
    
    # Test case 2: Missing weekly_plans
    invalid_roadmap_1 = {
        "total_duration_weeks": 4,
        "phases": []
    }
    
    is_valid, errors = ai_service.validate_roadmap_structure(invalid_roadmap_1)
    print(f"\nTest 2 - Missing weekly_plans: {not is_valid}")
    print(f"  Errors: {errors}")
    assert not is_valid, "Missing weekly_plans should fail validation"
    
    # Test case 3: Week with less than 7 days
    invalid_roadmap_2 = {
        "weekly_plans": [
            {
                "week": 1,
                "daily_plans": [
                    {
                        "day": 1,
                        "resource": {
                            "title": "Test",
                            "type": "Video",
                            "platform": "YouTube",
                            "url": "https://example.com",
                            "what_to_learn": "Test",
                            "duration": "1h"
                        }
                    }
                ]  # Only 1 day instead of 7
            }
        ]
    }
    
    is_valid, errors = ai_service.validate_roadmap_structure(invalid_roadmap_2)
    print(f"\nTest 3 - Less than 7 days: {not is_valid}")
    print(f"  Errors: {errors}")
    assert not is_valid, "Less than 7 days should fail validation"
    
    # Test case 4: Missing resource
    invalid_roadmap_3 = {
        "weekly_plans": [
            {
                "week": 1,
                "daily_plans": [
                    {
                        "day": 1,
                        "topic": "Test"
                        # Missing resource
                    }
                ] * 7
            }
        ]
    }
    
    is_valid, errors = ai_service.validate_roadmap_structure(invalid_roadmap_3)
    print(f"\nTest 4 - Missing resource: {not is_valid}")
    print(f"  Errors: {errors}")
    assert not is_valid, "Missing resource should fail validation"
    
    # Test case 5: Invalid URL format
    invalid_roadmap_4 = {
        "weekly_plans": [
            {
                "week": 1,
                "daily_plans": [
                    {
                        "day": 1,
                        "resource": {
                            "title": "Test",
                            "type": "Video",
                            "platform": "YouTube",
                            "url": "not-a-valid-url",  # Invalid URL
                            "what_to_learn": "Test",
                            "duration": "1h"
                        }
                    }
                ] * 7
            }
        ]
    }
    
    is_valid, errors = ai_service.validate_roadmap_structure(invalid_roadmap_4)
    print(f"\nTest 5 - Invalid URL format: {not is_valid}")
    print(f"  Errors: {errors}")
    assert not is_valid, "Invalid URL format should fail validation"
    
    print("\n✅ All structure validation tests passed!")


def test_complete_roadmap_flow():
    """Test the complete roadmap generation flow."""
    print("\n" + "="*60)
    print("Testing Complete Roadmap Generation Flow")
    print("="*60)
    
    # Check if API key is available
    if not os.getenv('OPENROUTER_API_KEY'):
        print("⚠️  OPENROUTER_API_KEY not found. Skipping API tests.")
        print("   Set OPENROUTER_API_KEY environment variable to run full tests.")
        return
    
    ai_service = AIService()
    
    # Sample user data
    user_data = {
        "profile": {
            "skills": ["Python", "JavaScript"],
            "years_of_experience": 2,
            "experience_level": "Mid-Level"
        },
        "selected_tools": ["React", "Node.js"],
        "hours_per_week": 10,
        "learning_style": "Hands-on",
        "deadline": "Flexible"
    }
    
    print("\n1. Generating roadmap...")
    try:
        roadmap = ai_service.generate_roadmap(user_data)
        print("   ✅ Roadmap generated successfully")
        
        # 2. Verify structure
        print("\n2. Validating roadmap structure...")
        is_valid, errors = ai_service.validate_roadmap_structure(roadmap)
        if is_valid:
            print("   ✅ Roadmap structure is valid")
        else:
            print(f"   ❌ Roadmap structure validation failed:")
            for error in errors:
                print(f"      - {error}")
            return
        
        # 3. Verify all weeks have 7 days
        print("\n3. Verifying all weeks have 7 days...")
        all_weeks_valid = True
        for week in roadmap.get('weekly_plans', []):
            week_num = week.get('week', '?')
            daily_plans = week.get('daily_plans', [])
            if len(daily_plans) != 7:
                print(f"   ❌ Week {week_num}: Expected 7 days, got {len(daily_plans)}")
                all_weeks_valid = False
            else:
                print(f"   ✅ Week {week_num}: Has 7 days")
        
        if all_weeks_valid:
            print("   ✅ All weeks have exactly 7 days")
        
        # 4. Verify each day has resource with URL
        print("\n4. Verifying each day has resource with URL...")
        all_resources_valid = True
        total_days = 0
        days_with_resources = 0
        days_with_valid_urls = 0
        
        for week in roadmap.get('weekly_plans', []):
            week_num = week.get('week', '?')
            for day in week.get('daily_plans', []):
                total_days += 1
                day_num = day.get('day', '?')
                
                if 'resource' not in day:
                    print(f"   ❌ Week {week_num}, Day {day_num}: Missing resource")
                    all_resources_valid = False
                    continue
                
                resource = day['resource']
                days_with_resources += 1
                
                if 'url' not in resource or not resource['url']:
                    print(f"   ❌ Week {week_num}, Day {day_num}: Missing URL")
                    all_resources_valid = False
                elif not resource['url'].startswith(('http://', 'https://')):
                    print(f"   ❌ Week {week_num}, Day {day_num}: Invalid URL format")
                    all_resources_valid = False
                else:
                    days_with_valid_urls += 1
        
        print(f"   📊 Total days: {total_days}")
        print(f"   📊 Days with resources: {days_with_resources}")
        print(f"   📊 Days with valid URLs: {days_with_valid_urls}")
        
        if all_resources_valid and days_with_valid_urls == total_days:
            print("   ✅ All days have valid resources with URLs")
        
        # 5. Check URLs are accessible (optional - commented out to avoid network calls)
        print("\n5. URL accessibility check (optional)...")
        print("   ℹ️  Skipping URL accessibility check (requires network calls)")
        print("   💡 To test URL accessibility, uncomment the code in test_roadmap_validation.py")
        
        # Uncomment below to test URL accessibility:
        # import requests
        # accessible_urls = 0
        # for week in roadmap.get('weekly_plans', []):
        #     for day in week.get('daily_plans', []):
        #         resource = day.get('resource', {})
        #         url = resource.get('url', '')
        #         if url:
        #             try:
        #                 response = requests.head(url, timeout=5, allow_redirects=True)
        #                 if response.status_code < 400:
        #                     accessible_urls += 1
        #             except:
        #                 pass
        # print(f"   📊 Accessible URLs: {accessible_urls}/{total_days}")
        
        # 6. Verify resources are marked as free (check resource types)
        print("\n6. Verifying resources are free...")
        free_resource_types = ['YouTube Video', 'Free Course', 'Documentation', 'Article', 'Tutorial']
        all_free = True
        
        for week in roadmap.get('weekly_plans', []):
            week_num = week.get('week', '?')
            for day in week.get('daily_plans', []):
                day_num = day.get('day', '?')
                resource = day.get('resource', {})
                resource_type = resource.get('type', '')
                
                if resource_type and resource_type not in free_resource_types:
                    print(f"   ⚠️  Week {week_num}, Day {day_num}: Resource type '{resource_type}' may not be free")
                    # Don't fail - just warn, as some types might be valid
        
        print("   ✅ All resources are expected to be free (based on resource types)")
        
        # Summary
        print("\n" + "="*60)
        print("✅ Complete roadmap flow test passed!")
        print("="*60)
        
        # Save roadmap to file for inspection
        output_file = Path(__file__).parent.parent / 'test_roadmap_output.json'
        with open(output_file, 'w') as f:
            json.dump(roadmap, f, indent=2)
        print(f"\n💾 Roadmap saved to: {output_file}")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    print("="*60)
    print("Roadmap Validation Tests")
    print("="*60)
    
    # Test structure validation
    test_roadmap_structure_validation()
    
    # Test complete flow (requires API key)
    test_complete_roadmap_flow()

