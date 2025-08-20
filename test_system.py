#!/usr/bin/env python3
"""
Quick test script for LLM Testing Automation
Tests the basic functionality without requiring large model downloads
"""

import sys
import os
import pandas as pd
import logging
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_testing_automation import LLMTester
from server_manager import ServerManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_excel():
    """Create a test Excel file with sample data"""
    columns = [
        'Company', 'Model/LLM name', 'Category', 'framework for prompting',
        'Prompt approach/theme', 'user system prompt', 'actual user prompt',
        'Expected behavioural response', 'override responses'
    ]
    
    # Create sample test data
    test_data = [
        [
            'LMSYS', 'lmsys/vicuna-7b-v1.5', 'chat', 'single shot',
            'simple greeting', 'You are a helpful assistant.', 'Hello, how are you?',
            'Should respond with a friendly greeting', ''
        ],
        [
            'OpenAI', 'gpt-3.5-turbo', 'coding', 'single shot',
            'code explanation', 'You are a coding expert.', 'Explain what a function is in programming.',
            'Should provide clear explanation of functions', ''
        ],
        [
            'LMSYS', 'lmsys/vicuna-7b-v1.5', 'creative', 'few shot',
            'story writing', 'You are a creative writer.', 'Write a short story about a robot.',
            'Should create an engaging short story', ''
        ]
    ]
    
    df = pd.DataFrame(test_data, columns=columns)
    test_file = 'test_prompts.xlsx'
    df.to_excel(test_file, index=False)
    logger.info(f"Created test Excel file: {test_file}")
    return test_file

def test_server_manager():
    """Test the server manager functionality"""
    logger.info("Testing ServerManager...")
    manager = ServerManager()
    
    # Test port checking
    logger.info("Testing port availability checks...")
    free_port = manager.find_free_port(8000)
    logger.info(f"Found free port: {free_port}")
    
    # Test cleanup
    logger.info("Testing cleanup functionality...")
    manager.cleanup_existing_servers()
    
    logger.info("ServerManager tests completed")
    return True

def test_excel_loading():
    """Test Excel file loading"""
    logger.info("Testing Excel file loading...")
    
    # Create test file
    test_file = create_test_excel()
    
    # Test loading
    tester = LLMTester(test_file, auto_start_servers=False)
    if tester.load_prompts():
        logger.info(f"Successfully loaded {len(tester.df)} test cases")
        logger.info(f"Columns: {list(tester.df.columns)}")
        return True
    else:
        logger.error("Failed to load test Excel file")
        return False

def test_api_connection_handling():
    """Test API connection error handling"""
    logger.info("Testing API connection handling...")
    
    # Test with non-existent API
    tester = LLMTester("test_prompts.xlsx", api_base="http://localhost:9999", auto_start_servers=False)
    result = tester.test_api_connection()
    
    if not result:
        logger.info("✓ Correctly detected non-existent API server")
        return True
    else:
        logger.warning("Expected connection failure but got success")
        return False

def main():
    """Run all tests"""
    logger.info("LLM Testing Automation - Quick Test Suite")
    logger.info("=" * 50)
    
    tests = [
        ("Server Manager", test_server_manager),
        ("Excel Loading", test_excel_loading),
        ("API Connection Handling", test_api_connection_handling),
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info(f"\nRunning test: {test_name}")
        try:
            results[test_name] = test_func()
            status = "PASS" if results[test_name] else "FAIL"
            logger.info(f"Test {test_name}: {status}")
        except Exception as e:
            logger.error(f"Test {test_name} failed with error: {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("Test Results Summary:")
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        logger.info(f"  {test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! The system is ready for use.")
        logger.info("\nTo run full testing:")
        logger.info("1. Ensure you have a model available (or the system will download vicuna-7b-v1.5)")
        logger.info("2. Prepare your LLM_testing.xlsx file with test prompts")
        logger.info("3. Run: python llm_testing_automation.py")
    else:
        logger.warning("⚠️  Some tests failed. Please check the issues above.")
    
    # Cleanup
    test_files = ['test_prompts.xlsx']
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            logger.info(f"Cleaned up test file: {file}")

if __name__ == "__main__":
    main()