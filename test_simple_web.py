"""
Simple web analysis test
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.web_analyzer import web_analyzer

async def test_simple():
    """Simple test for web analyzer"""
    print("Testing Web Analyzer...")
    
    # Test with Wikipedia article about Hücre (Cell)
    url = "https://tr.wikipedia.org/wiki/H%C3%BCcre"
    
    print(f"Analyzing: {url}")
    
    try:
        result = await web_analyzer.analyze_website(url, analysis_type="quick")
        
        if result.get("error"):
            print(f"Error: {result['error']}")
            if result.get("suggestion"):
                print(f"Suggestion: {result['suggestion']}")
        elif result.get("success"):
            curriculum_check = result.get("curriculum_check", {})
            print(f"YKS Relevant: {curriculum_check.get('yks_relevant', False)}")
            print(f"Subjects: {curriculum_check.get('subjects', [])}")
            print(f"Confidence: {curriculum_check.get('confidence_score', 0):.2f}")
            
            if curriculum_check.get('yks_relevant'):
                content_info = result.get("content_info", {})
                print(f"Word count: {content_info.get('word_count', 0)}")
                print("✅ Analysis successful!")
            else:
                print("❌ Content not YKS relevant")
        else:
            print("Unexpected result")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_simple())