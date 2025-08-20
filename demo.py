#!/usr/bin/env python3
"""
LLM Testing Demo - Mock Server Mode
Demonstrates the LLM testing system without requiring actual model downloads
Uses a mock FastChat API server for testing the automation flow
"""

import threading
import time
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import pandas as pd
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_testing_automation import LLMTester

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MockFastChatAPIHandler(BaseHTTPRequestHandler):
    """Mock FastChat API server for demonstration"""
    
    def log_message(self, format, *args):
        """Suppress default HTTP server logging"""
        pass
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/v1/models':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "object": "list",
                "data": [
                    {
                        "id": "lmsys/vicuna-7b-v1.5",
                        "object": "model",
                        "created": 1677610602,
                        "owned_by": "lmsys"
                    },
                    {
                        "id": "mock-model-fast",
                        "object": "model", 
                        "created": 1677610602,
                        "owned_by": "demo"
                    }
                ]
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/v1/chat/completions':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode())
            
            # Extract the user prompt
            messages = request_data.get('messages', [])
            user_message = None
            system_message = None
            
            for msg in messages:
                if msg['role'] == 'user':
                    user_message = msg['content']
                elif msg['role'] == 'system':
                    system_message = msg['content']
            
            # Generate mock responses based on content
            response_content = self._generate_mock_response(user_message, system_message)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "id": "chatcmpl-demo123",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": request_data.get('model', 'mock-model'),
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": response_content
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": len(user_message.split()) if user_message else 0,
                    "completion_tokens": len(response_content.split()),
                    "total_tokens": len(user_message.split()) + len(response_content.split()) if user_message else len(response_content.split())
                }
            }
            
            # Simulate some processing time
            time.sleep(0.5)
            
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def _generate_mock_response(self, user_message, system_message=None):
        """Generate contextual mock responses"""
        user_lower = user_message.lower() if user_message else ""
        
        if "hello" in user_lower or "who are you" in user_lower:
            return "Hello! I'm a helpful AI assistant created for demonstration purposes. I'm here to help with your questions and tasks."
        
        elif "function" in user_lower and ("python" in user_lower or "programming" in user_lower):
            return """A Python function is a reusable block of code that performs a specific task. Here's a simple example:

```python
def greet(name):
    return f"Hello, {name}!"

# Usage
message = greet("Alice")
print(message)  # Output: Hello, Alice!
```

Functions help organize code and avoid repetition."""
        
        elif "machine learning" in user_lower and "marvel" in user_lower:
            return """Great question! Let me explain machine learning using Marvel characters:

🤖 **Iron Man (Tony Stark)** = The Machine Learning Engineer who builds and trains models
🛡️ **Captain America** = Supervised Learning - learns from labeled examples (right vs wrong)
🔮 **Doctor Strange** = Unsupervised Learning - finds hidden patterns without guidance
🕷️ **Spider-Man** = Reinforcement Learning - learns through trial and error (with great power...)
📊 **FRIDAY** = The trained model that makes predictions and assists
🧠 **Professor X** = Neural Networks - complex interconnected decision-making

Just like the Avengers work together, different ML techniques combine to solve complex problems!"""
        
        elif "birthday party" in user_lower:
            return """Here's a step-by-step plan for a 10-year-old's birthday party:

**Phase 1: Planning (2-3 weeks before)**
1. Set date, time, and location
2. Create guest list (8-12 kids ideal)
3. Choose theme (superheroes, princesses, sports, etc.)
4. Send invitations

**Phase 2: Preparations (1 week before)**
5. Plan activities/games (treasure hunt, musical chairs)
6. Order/prepare food (pizza, cake, healthy snacks)
7. Buy decorations and party favors
8. Confirm RSVPs

**Phase 3: Party Day**
9. Set up decorations 2 hours before
10. Prepare activity stations
11. Welcome guests and start activities
12. Serve food and cake
13. Open presents
14. Send thank-you notes later

**Pro tip:** Have a backup indoor activity ready!"""
        
        elif "photosynthesis" in user_lower:
            return """Photosynthesis is like cooking for plants! Here's the simple version:

🌱 **What it is:** Plants make their own food using sunlight
🍯 **The Recipe:**
- Sunlight (energy) 
- Water (from roots)
- Carbon dioxide (from air)
- Special green stuff called chlorophyll

🔄 **The Process:**
1. Leaves capture sunlight like solar panels
2. Roots drink water from soil
3. Tiny holes in leaves breathe in carbon dioxide
4. Chlorophyll mixes everything together
5. Plant makes sugar (food) and releases oxygen

🌍 **Why it matters:** Plants give us the oxygen we breathe and food we eat. It's like nature's kitchen that keeps Earth alive!"""
        
        elif "roses" in user_lower and "flowers" in user_lower and "red" in user_lower:
            return """Let me think through this step by step:

**Given statements:**
1. All roses are flowers
2. Some flowers are red

**Question:** Can we conclude that some roses are red?

**Logical analysis:**
- We know roses are a subset of flowers
- We know some flowers (in general) are red
- BUT we don't know specifically if any of those red flowers are roses

**Conclusion:** No, we cannot logically conclude that some roses are red from these statements alone. The red flowers could all be non-roses (like tulips, carnations, etc.).

**What we'd need:** A statement like "some roses are red" or "some of the red flowers are roses" to make that conclusion."""
        
        elif "time-traveling scientist" in user_lower:
            return """**The Temporal Paradox**

Dr. Elena Vasquez adjusted her chronometer one last time. The laboratory hummed with energy as the temporal displacement chamber powered up. She had spent twenty years perfecting this moment.

"Final checks complete," she whispered, stepping into the shimmering portal. "Destination: 1905, Einstein's miracle year."

The world blurred into streams of light and shadow. When reality solidified, she stood in a cluttered patent office in Bern. A young man with wild hair looked up from his desk, startled.

"Excuse me, but who—?"

"Mr. Einstein," Elena smiled, pulling out a worn notebook. "I believe you're working on something about time and space. I have some questions about relative simultaneity."

Albert's eyes widened as he saw equations in her notebook that wouldn't be discovered for decades. "How did you...?"

Elena's chronometer began beeping frantically. The return window was closing.

"Time," she said, backing toward the fading portal, "is more fragile than you think."

As she vanished, Albert stared at the empty air, then at his own papers. Perhaps time truly was relative after all."""
        
        elif "remote work" in user_lower:
            return """**Remote Work Analysis**

**PROS:**
✅ **Flexibility:** Better work-life balance, no commute time
✅ **Cost Savings:** Reduced transportation, meals, work clothes
✅ **Productivity:** Fewer office distractions, personalized workspace
✅ **Access to Talent:** Companies can hire globally
✅ **Environmental Impact:** Less commuting reduces carbon footprint
✅ **Health Benefits:** More time for exercise, better meal prep

**CONS:**
❌ **Isolation:** Reduced social interaction, potential loneliness
❌ **Communication:** Harder to collaborate, misunderstandings
❌ **Work-Life Boundaries:** Difficulty separating work and personal time
❌ **Career Development:** Fewer mentorship opportunities, visibility issues
❌ **Technical Challenges:** Internet connectivity, equipment costs
❌ **Team Cohesion:** Harder to build company culture

**Verdict:** Remote work offers significant benefits but requires intentional effort to address its challenges. Hybrid models often provide the best of both worlds."""
        
        else:
            return f"Thank you for your question about '{user_message[:50]}...'. This is a mock response from the demonstration system. In a real setup, this would be processed by an actual language model like Vicuna, GPT, or other LLMs available through FastChat."

def start_mock_server(port=8000):
    """Start the mock FastChat API server"""
    server = HTTPServer(('localhost', port), MockFastChatAPIHandler)
    logger.info(f"Mock FastChat API server starting on http://localhost:{port}")
    
    def run_server():
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait a moment for server to start
    time.sleep(1)
    return server

def create_demo_excel():
    """Create a demo Excel file for testing"""
    columns = [
        'Company', 'Model/LLM name', 'Category', 'framework for prompting',
        'Prompt approach/theme', 'user system prompt', 'actual user prompt',
        'Expected behavioural response', 'override responses'
    ]
    
    data = [
        [
            'LMSYS', 'lmsys/vicuna-7b-v1.5', 'chat', 'single shot',
            'greeting', 'You are a helpful assistant.', 'Hello, who are you?',
            'Should introduce itself as an assistant', ''
        ],
        [
            'LMSYS', 'lmsys/vicuna-7b-v1.5', 'coding', 'single shot',
            'code explanation', 'You are a programming expert.', 'What is a Python function? Give me a simple example.',
            'Should explain functions with code example', ''
        ],
        [
            'LMSYS', 'lmsys/vicuna-7b-v1.5', 'creative', 'few shot',
            'metaphor-based explanation', 'You are a creative educator who uses Marvel universe metaphors.',
            'Explain machine learning using Marvel characters as examples.',
            'Should use Marvel characters creatively', ''
        ],
        [
            'LMSYS', 'lmsys/vicuna-7b-v1.5', 'agentic', 'multishot',
            'problem solving', 'You are an AI agent that breaks down problems into steps.',
            'How would you plan a birthday party for a 10-year-old?',
            'Should provide structured step-by-step plan', ''
        ]
    ]
    
    df = pd.DataFrame(data, columns=columns)
    demo_file = 'demo_tests.xlsx'
    df.to_excel(demo_file, index=False)
    logger.info(f"Created demo Excel file: {demo_file}")
    return demo_file

def main():
    """Run the demonstration"""
    logger.info("🚀 LLM Testing Automation - Live Demo")
    logger.info("=" * 60)
    logger.info("This demo shows the system working with a mock API server")
    logger.info("(no actual model downloads required)")
    logger.info("")
    
    try:
        # Start mock server
        server = start_mock_server(8000)
        
        # Create demo Excel file
        demo_file = create_demo_excel()
        
        # Initialize tester (disable auto server start since we have our mock)
        logger.info("Initializing LLM Tester...")
        tester = LLMTester(demo_file, api_base="http://localhost:8000", auto_start_servers=False)
        
        # Run the tests
        logger.info("Starting demonstration tests...")
        if tester.run_tests():
            tester.save_results("demo_results.xlsx")
            logger.info("\n🎉 Demo completed successfully!")
            logger.info("Check 'demo_results.xlsx' for detailed results")
        else:
            logger.error("Demo failed")
            
    except KeyboardInterrupt:
        logger.info("\nDemo interrupted by user")
    except Exception as e:
        logger.error(f"Demo failed with error: {e}")
    finally:
        # Cleanup
        for file in ['demo_tests.xlsx']:
            if os.path.exists(file):
                os.remove(file)
                logger.info(f"Cleaned up: {file}")
    
    logger.info("\n📋 Summary:")
    logger.info("- Mock API server simulated real FastChat responses")
    logger.info("- Excel file processing and result generation working")
    logger.info("- System ready for use with actual FastChat servers")
    logger.info("\n🚀 To use with real models: python llm_testing_automation.py")

if __name__ == "__main__":
    main()