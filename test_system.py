"""
Simple test script to verify system functionality
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.gemini_client import gemini_client
from core.rag_system import rag_system  
from core.agents import agent_system
from config import settings

async def test_gemini_client():
    """Test Gemini client"""
    print("[TEST] Testing Gemini Client...")
    try:
        response = await gemini_client.generate_content(
            prompt="Merhaba, nasılsın?",
            system_instruction="Sen yardımcı bir AI asistanısın."
        )
        print(f"[PASS] Gemini Client: {response['text'][:100]}...")
        return True
    except Exception as e:
        print(f"[FAIL] Gemini Client Error: {str(e)}")
        return False

async def test_rag_system():
    """Test RAG system"""
    print("[TEST] Testing RAG System...")
    try:
        # Test search (even if no data loaded)
        results = await rag_system.search("matematik", n_results=3)
        print(f"[PASS] RAG System: Found {len(results)} results")
        return True
    except Exception as e:
        print(f"[FAIL] RAG System Error: {str(e)}")
        return False

async def test_agent_system():
    """Test agent system"""
    print("[TEST] Testing Agent System...")
    try:
        response = await agent_system.process_message(
            message="Merhaba, matematik konusunda yardıma ihtiyacım var.",
            context={"test": True}
        )
        print(f"[PASS] Agent System: {response['response'][:100]}...")
        return True
    except Exception as e:
        print(f"[FAIL] Agent System Error: {str(e)}")
        return False

async def main():
    """Main test function"""
    print("[INFO] Promptitron Unified System Test")
    print("=" * 50)
    
    # Test configuration
    print(f"[CONFIG] Configuration:")
    print(f"   - App Name: {settings.APP_NAME}")
    print(f"   - Version: {settings.APP_VERSION}")
    print(f"   - Gemini Model: {settings.GEMINI_MODEL}")
    print(f"   - Debug Mode: {settings.DEBUG}")
    print()
    
    # Test each component
    tests = [
        ("Gemini Client", test_gemini_client),
        ("RAG System", test_rag_system),
        ("Agent System", test_agent_system)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[ERROR] {test_name} - Unexpected Error: {str(e)}")
            results.append((test_name, False))
        print()
    
    # Summary
    print("[SUMMARY] Test Summary:")
    print("-" * 30)
    passed = 0
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n[RESULT] Total: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("[SUCCESS] All tests passed! System is ready.")
    else:
        print("[WARNING] Some tests failed. Check configuration and dependencies.")
    
    return passed == len(results)

if __name__ == "__main__":
    # Check if Google API key is set
    if not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY == "":
        print("[ERROR] Error: GOOGLE_API_KEY not set in environment variables")
        print("Please set your Google API key in .env file")
        sys.exit(1)
    
    # Run tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)