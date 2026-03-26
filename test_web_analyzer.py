"""
Test script for Web Analyzer functionality
Tests web content analysis and YKS curriculum compliance
"""

import asyncio
import logging
from core.web_analyzer import web_analyzer
from core.document_understanding import document_understanding

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_web_analyzer():
    """Test web analyzer with various scenarios"""
    
    print("Web Analyzer Test Suite")
    print("=" * 50)
    
    # Test URLs (use educational content examples)
    test_urls = [
        # Educational math content
        "https://www.khanacademy.org/math/geometry",  # Educational content
        "https://example.com/invalid-url",  # Invalid URL test
        "https://www.wikipedia.org/wiki/Mathematics",  # Wikipedia article
    ]
    
    test_cases = [
        {
            "name": "Khan Academy Geometry (Should Pass)",
            "url": "https://www.khanacademy.org/math/geometry",
            "expected_result": "success"
        },
        {
            "name": "Invalid URL (Should Fail)",
            "url": "https://invalid-domain-that-does-not-exist.com",
            "expected_result": "error"
        },
        {
            "name": "Non-educational content (Should Reject)",
            "url": "https://www.example.com",
            "expected_result": "curriculum_rejection"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print(f"URL: {test_case['url']}")
        print("-" * 40)
        
        try:
            result = await web_analyzer.analyze_website(
                url=test_case['url'],
                analysis_type="full"
            )
            
            # Analyze results
            if result.get("error"):
                print(f"Error: {result['error']}")
                if result.get("suggestion"):
                    print(f"Suggestion: {result['suggestion']}")
                test_result = "error"
            elif result.get("success"):
                curriculum_check = result.get("curriculum_check", {})
                yks_relevant = curriculum_check.get("yks_relevant", False)
                
                print(f"Analysis successful")
                print(f"YKS Relevant: {yks_relevant}")
                print(f"Subjects: {curriculum_check.get('subjects', [])}")
                print(f"Confidence: {curriculum_check.get('confidence_score', 0):.2f}")
                
                if not yks_relevant:
                    test_result = "curriculum_rejection"
                    print(f"Content rejected: {curriculum_check.get('reason', 'No reason provided')}")
                else:
                    test_result = "success"
                    content_info = result.get("content_info", {})
                    print(f"Word count: {content_info.get('word_count', 0)}")
                    print(f"Images: {content_info.get('images_count', 0)}")
                    
                    # Show analysis preview
                    analysis = result.get("educational_analysis", "")
                    if analysis:
                        print(f"Analysis preview: {analysis[:200]}...")
            else:
                print("Unexpected result structure")
                test_result = "unexpected"
            
            results.append({
                "test": test_case['name'],
                "url": test_case['url'],
                "expected": test_case['expected_result'],
                "actual": test_result,
                "passed": test_result == test_case['expected_result']
            })
            
        except Exception as e:
            print(f"Exception: {str(e)}")
            results.append({
                "test": test_case['name'],
                "url": test_case['url'],
                "expected": test_case['expected_result'],
                "actual": "exception",
                "passed": False,
                "error": str(e)
            })
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed_tests = sum(1 for r in results if r.get('passed', False))
    total_tests = len(results)
    
    for result in results:
        status = "PASS" if result.get('passed', False) else "FAIL"
        print(f"{status} - {result['test']}")
        if not result.get('passed', False):
            print(f"   Expected: {result['expected']}, Got: {result['actual']}")
            if result.get('error'):
                print(f"   Error: {result['error']}")
    
    print(f"\nResults: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("All tests passed!")
    else:
        print("Some tests failed. Check implementation.")
    
    return results

async def test_document_integration():
    """Test document understanding integration with web URLs"""
    
    print("\nDocument Integration Test")
    print("=" * 40)
    
    # Test URL processing through document understanding
    test_url = "https://www.khanacademy.org"
    
    print(f"Testing URL: {test_url}")
    
    try:
        result = await document_understanding.process_document(
            file_path=test_url,
            analysis_type="educational"
        )
        
        if result.get("error"):
            print(f"Integration Error: {result['error']}")
        else:
            print("Integration successful")
            print(f"Source type: {result.get('source_type', 'Unknown')}")
            print(f"YKS Relevant: {result.get('educational_metadata', {}).get('yks_relevant', False)}")
            
    except Exception as e:
        print(f"Integration Exception: {str(e)}")

async def main():
    """Main test function"""
    print("Starting Web Analyzer Tests...")
    
    # Test web analyzer
    web_results = await test_web_analyzer()
    
    # Test document integration
    await test_document_integration()
    
    print("\nTests completed!")

if __name__ == "__main__":
    asyncio.run(main())