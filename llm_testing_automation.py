"""
LLM Testing Automation Script for FastChat/LMArena
Reads prompts from Excel file and tests them through FastChat API
"""

import pandas as pd
import requests
import time
from datetime import datetime
import os

class LLMTester:
    def __init__(self, excel_file="LLM_testing.xlsx", api_base="http://localhost:8001"):
        self.excel_file = excel_file
        self.api_base = api_base
        self.results = []
        
    def load_prompts(self):
        """Load prompts from Excel file"""
        try:
            self.df = pd.read_excel(self.excel_file)
            print(f"Loaded {len(self.df)} test cases from {self.excel_file}")
            print(f"Columns found: {list(self.df.columns)}")
            return True
        except FileNotFoundError:
            print(f"Error: {self.excel_file} not found in current directory")
            return False
        except Exception as e:
            print(f"Error loading Excel file: {e}")
            return False
    
    def test_api_connection(self):
        """Test if FastChat API is running"""
        try:
            response = requests.get(f"{self.api_base}/v1/models", timeout=5)
            if response.status_code == 200:
                print("✓ FastChat API is running")
                models = response.json()
                print(f"Available models: {[model['id'] for model in models.get('data', [])]}")
                return True
            else:
                print(f"✗ API returned status code: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("✗ Cannot connect to FastChat API. Make sure the server is running.")
            return False
        except Exception as e:
            print(f"✗ Error testing API connection: {e}")
            return False
    
    def send_prompt(self, model_name, system_prompt, user_prompt, max_retries=3):
        """Send a single prompt to the API"""
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
                response = requests.post(
                    f"{self.api_base}/v1/chat/completions",
                    json=payload,
                    timeout=60
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
                    print(f"Attempt {attempt + 1} failed: {error_msg}")
                    
            except requests.exceptions.Timeout:
                print(f"Attempt {attempt + 1} timed out")
            except Exception as e:
                print(f"Attempt {attempt + 1} error: {e}")
            
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
        
        if not self.test_api_connection():
            print("Please start FastChat server first:")
            print("1. python -m fastchat.serve.controller")
            print("2. python -m fastchat.serve.model_worker --model-path <model-name>")
            print("3. python -m fastchat.serve.openai_api_server --host localhost --port 8000")
            return False
        
        print(f"\nStarting tests at {datetime.now()}")
        print("=" * 50)
        
        for index, row in self.df.iterrows():
            print(f"\nTest {index + 1}/{len(self.df)}")
            
            # Extract data from row
            company = row.get('Company', '')
            model_name = row.get('Model/LLM name', '')
            category = row.get('Category', '')
            framework = row.get('framework for prompting', '')
            prompt_theme = row.get('Prompt approach/theme', '')
            system_prompt = row.get('user system prompt', '')
            user_prompt = row.get('actual user prompt', '')
            expected_response = row.get('Expected behavioural response', '')
            override_response = row.get('override responses', '')
            
            print(f"Company: {company}")
            print(f"Model: {model_name}")
            print(f"Category: {category}")
            print(f"User Prompt: {str(user_prompt)[:100]}...")
            
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
                'Model_Used': result.get('model', model_name)
            }
            
            self.results.append(test_result)
            
            if result['success']:
                print(f"✓ Success - Response length: {len(result['response'])} chars")
            else:
                print(f"✗ Failed: {result.get('error', 'Unknown error')}")
            
            # Small delay between requests
            time.sleep(1)
        
        return True
    
    def save_results(self, output_file=None):
        """Save results to Excel file"""
        if not self.results:
            print("No results to save")
            return
        
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"LLM_test_results_{timestamp}.xlsx"
        
        results_df = pd.DataFrame(self.results)
        results_df.to_excel(output_file, index=False)
        print(f"\nResults saved to: {output_file}")
        print(f"Total tests: {len(self.results)}")
        print(f"Successful: {sum(1 for r in self.results if r['API_Success'])}")
        print(f"Failed: {sum(1 for r in self.results if not r['API_Success'])}")

def main():
    print("LLM Testing Automation for FastChat/LMArena")
    print("=" * 50)
    
    # Check if Excel file exists
    excel_file = "LLM_testing.xlsx"
    if not os.path.exists(excel_file):
        print(f"Please place your Excel file named '{excel_file}' in the current directory.")
        print("The file should contain columns:")
        print("- Company")
        print("- Model/LLM name") 
        print("- Category")
        print("- framework for prompting")
        print("- Prompt approach/theme")
        print("- user system prompt")
        print("- actual user prompt")
        print("- Expected behavioural response")
        print("- override responses")
        return
    
    # Initialize tester
    tester = LLMTester(excel_file)
    
    # Run tests
    if tester.run_tests():
        tester.save_results()
    else:
        print("Testing failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
