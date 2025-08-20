"""
LLM Testing Automation Script for FastChat/LMArena
Reads prompts from Excel file and tests them through FastChat API
Enhanced with automatic server management and robust error handling
"""

import pandas as pd
import requests
import time
from datetime import datetime
import os
import logging
from typing import Optional, Dict, List
from server_manager import ServerManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMTester:
    def __init__(self, excel_file="LLM_testing.xlsx", api_base=None, auto_start_servers=True):
        self.excel_file = excel_file
        self.api_base = api_base
        self.results = []
        self.server_manager = ServerManager() if auto_start_servers else None
        self.auto_start_servers = auto_start_servers
        self.available_models = []
        
    def ensure_servers_running(self) -> bool:
        """Ensure FastChat servers are running, start them if needed"""
        if not self.auto_start_servers:
            return self.test_api_connection()
        
        logger.info("Checking if FastChat servers are running...")
        
        # Check if API server is already running
        if self.api_base and self.test_api_connection():
            logger.info("FastChat API server is already running")
            return True
        
        # Try to find running API server
        for port in [8000, 8001, 8080]:
            test_base = f"http://localhost:{port}"
            try:
                response = requests.get(f"{test_base}/v1/models", timeout=2)
                if response.status_code == 200:
                    self.api_base = test_base
                    logger.info(f"Found running FastChat API server at {test_base}")
                    return True
            except requests.exceptions.RequestException:
                continue
        
        # Start servers if none found
        logger.info("No running FastChat servers found. Starting servers...")
        try:
            ports = self.server_manager.start_full_stack()
            self.api_base = f"http://localhost:{ports['api']}"
            logger.info(f"FastChat servers started successfully. API at {self.api_base}")
            
            # Wait for servers to fully initialize
            logger.info("Waiting for servers to fully initialize...")
            time.sleep(15)
            
            return self.test_api_connection()
            
        except Exception as e:
            logger.error(f"Failed to start FastChat servers: {e}")
            return False
    
    def load_prompts(self):
        """Load prompts from Excel file"""
        try:
            self.df = pd.read_excel(self.excel_file)
            logger.info(f"Loaded {len(self.df)} test cases from {self.excel_file}")
            logger.info(f"Columns found: {list(self.df.columns)}")
            
            # Validate required columns
            required_columns = ['actual user prompt']
            missing_columns = [col for col in required_columns if col not in self.df.columns]
            if missing_columns:
                logger.warning(f"Missing required columns: {missing_columns}")
            
            return True
        except FileNotFoundError:
            logger.error(f"Error: {self.excel_file} not found in current directory")
            return False
        except Exception as e:
            logger.error(f"Error loading Excel file: {e}")
            return False
    
    def test_api_connection(self):
        """Test if FastChat API is running"""
        if not self.api_base:
            logger.error("No API base URL set")
            return False
            
        try:
            response = requests.get(f"{self.api_base}/v1/models", timeout=10)
            if response.status_code == 200:
                logger.info("✓ FastChat API is running")
                models_data = response.json()
                self.available_models = [model['id'] for model in models_data.get('data', [])]
                logger.info(f"Available models: {self.available_models}")
                return True
            else:
                logger.error(f"✗ API returned status code: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            logger.error("✗ Cannot connect to FastChat API. Make sure the server is running.")
            return False
        except Exception as e:
            logger.error(f"✗ Error testing API connection: {e}")
            return False
    
    def send_prompt(self, model_name, system_prompt, user_prompt, max_retries=3):
        """Send a single prompt to the API"""
        # Check if model is available, use first available if not specified or not found
        if not model_name or model_name not in self.available_models:
            if self.available_models:
                original_model = model_name
                model_name = self.available_models[0]
                logger.warning(f"Model '{original_model}' not available. Using '{model_name}' instead.")
            else:
                logger.error("No models available")
                return {
                    "success": False,
                    "response": "No models available",
                    "error": "No models available"
                }
        
        messages = []
        
        # Add system prompt if provided
        if system_prompt and pd.notna(system_prompt) and str(system_prompt).strip():
            messages.append({"role": "system", "content": str(system_prompt)})
        
        # Add user prompt
        messages.append({"role": "user", "content": str(user_prompt)})
        
        payload = {
            "model": model_name,
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"Sending request to {self.api_base}/v1/chat/completions (attempt {attempt + 1})")
                response = requests.post(
                    f"{self.api_base}/v1/chat/completions",
                    json=payload,
                    timeout=120  # Increased timeout for model inference
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "response": result["choices"][0]["message"]["content"],
                        "usage": result.get("usage", {}),
                        "model": result.get("model", model_name)
                    }
                else:
                    error_msg = f"API Error {response.status_code}: {response.text}"
                    logger.warning(f"Attempt {attempt + 1} failed: {error_msg}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Attempt {attempt + 1} timed out")
            except requests.exceptions.ConnectionError:
                logger.warning(f"Attempt {attempt + 1} connection error")
                # Try to reconnect to API
                if attempt == 0:
                    time.sleep(5)
                    if not self.test_api_connection():
                        logger.error("Lost connection to API server")
                        break
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} error: {e}")
            
            if attempt < max_retries - 1:
                time.sleep(2)  # Wait before retry
        
        return {
            "success": False,
            "response": "Failed after all retry attempts",
            "error": "Request failed"
        }
    
    def run_tests(self):
        """Run all tests from the Excel file"""
        if not self.load_prompts():
            return False
        
        # Ensure servers are running
        if not self.ensure_servers_running():
            logger.error("Failed to start or connect to FastChat servers")
            logger.info("Manual setup instructions:")
            logger.info("1. python -m fastchat.serve.controller")
            logger.info("2. python -m fastchat.serve.model_worker --model-path <model-name>")
            logger.info("3. python -m fastchat.serve.openai_api_server --host localhost --port 8000")
            return False
        
        logger.info(f"\nStarting tests at {datetime.now()}")
        logger.info("=" * 50)
        
        success_count = 0
        
        for index, row in self.df.iterrows():
            logger.info(f"\nTest {index + 1}/{len(self.df)}")
            
            # Extract data from row with better handling of missing values
            company = str(row.get('Company', '')).strip()
            model_name = str(row.get('Model/LLM name', '')).strip()
            category = str(row.get('Category', '')).strip()
            framework = str(row.get('framework for prompting', '')).strip()
            prompt_theme = str(row.get('Prompt approach/theme', '')).strip()
            system_prompt = str(row.get('user system prompt', '')).strip()
            user_prompt = str(row.get('actual user prompt', '')).strip()
            expected_response = str(row.get('Expected behavioural response', '')).strip()
            override_response = str(row.get('override responses', '')).strip()
            
            # Skip if no user prompt
            if not user_prompt or user_prompt == 'nan':
                logger.warning(f"Skipping test {index + 1}: No user prompt provided")
                continue
            
            logger.info(f"Company: {company}")
            logger.info(f"Model: {model_name}")
            logger.info(f"Category: {category}")
            logger.info(f"User Prompt: {user_prompt[:100]}{'...' if len(user_prompt) > 100 else ''}")
            
            # Send the prompt
            result = self.send_prompt(model_name, system_prompt, user_prompt)
            
            # Store results
            test_result = {
                'Test_ID': index + 1,
                'Timestamp': datetime.now().isoformat(),
                'Company': company,
                'Model_LLM_name': model_name,
                'Category': category,
                'Framework_for_prompting': framework,
                'Prompt_approach_theme': prompt_theme,
                'User_system_prompt': system_prompt,
                'Actual_user_prompt': user_prompt,
                'Expected_behavioural_response': expected_response,
                'Override_responses': override_response,
                'API_Success': result['success'],
                'LLM_Response': result.get('response', ''),
                'API_Error': result.get('error', ''),
                'Response_Length': len(str(result.get('response', ''))),
                'Model_Used': result.get('model', model_name),
                'API_Base_URL': self.api_base
            }
            
            self.results.append(test_result)
            
            if result['success']:
                logger.info(f"✓ Success - Response length: {len(result['response'])} chars")
                success_count += 1
            else:
                logger.error(f"✗ Failed: {result.get('error', 'Unknown error')}")
            
            # Small delay between requests to avoid overwhelming the server
            time.sleep(2)
        
        logger.info(f"\nTesting completed. {success_count}/{len(self.df)} tests successful")
        return True
    
    def save_results(self, output_file=None):
        """Save results to Excel file"""
        if not self.results:
            logger.warning("No results to save")
            return
        
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"LLM_test_results_{timestamp}.xlsx"
        
        try:
            results_df = pd.DataFrame(self.results)
            results_df.to_excel(output_file, index=False)
            logger.info(f"\nResults saved to: {output_file}")
            logger.info(f"Total tests: {len(self.results)}")
            logger.info(f"Successful: {sum(1 for r in self.results if r['API_Success'])}")
            logger.info(f"Failed: {sum(1 for r in self.results if not r['API_Success'])}")
            
            # Print summary statistics
            if self.results:
                avg_response_length = sum(r['Response_Length'] for r in self.results if r['API_Success']) / max(1, sum(1 for r in self.results if r['API_Success']))
                logger.info(f"Average response length: {avg_response_length:.1f} characters")
                
        except Exception as e:
            logger.error(f"Error saving results: {e}")
    
    def cleanup(self):
        """Clean up resources"""
        if self.server_manager and self.auto_start_servers:
            logger.info("Stopping FastChat servers...")
            self.server_manager.stop_all_servers()

def main():
    logger.info("LLM Testing Automation for FastChat/LMArena")
    logger.info("=" * 50)
    
    # Check if Excel file exists
    excel_file = "LLM_testing.xlsx"
    if not os.path.exists(excel_file):
        logger.error(f"Please place your Excel file named '{excel_file}' in the current directory.")
        logger.info("The file should contain columns:")
        logger.info("- Company")
        logger.info("- Model/LLM name") 
        logger.info("- Category")
        logger.info("- framework for prompting")
        logger.info("- Prompt approach/theme")
        logger.info("- user system prompt")
        logger.info("- actual user prompt")
        logger.info("- Expected behavioural response")
        logger.info("- override responses")
        return
    
    # Initialize tester with automatic server management
    tester = LLMTester(excel_file, auto_start_servers=True)
    
    try:
        # Run tests
        if tester.run_tests():
            tester.save_results()
            logger.info("Testing completed successfully!")
        else:
            logger.error("Testing failed. Please check the error messages above.")
    except KeyboardInterrupt:
        logger.info("\nTesting interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        # Clean up
        tester.cleanup()

if __name__ == "__main__":
    main()
