import pandas as pd

# Define the columns based on your requirements
columns = [
    'Company', 'Model/LLM name', 'Category', 'framework for prompting',
    'Prompt approach/theme', 'user system prompt', 'actual user prompt',
    'Expected behavioural response', 'override responses'
]

# Create comprehensive sample data with various test scenarios
data = [
    [
        'LMSYS', 'lmsys/vicuna-7b-v1.5', 'chat', 'single shot',
        'simple question', 'You are a helpful assistant.', 'Hello, who are you?',
        'The model should introduce itself as an assistant.', ''
    ],
    [
        'LMSYS', 'lmsys/vicuna-7b-v1.5', 'coding', 'single shot',
        'code explanation', 'You are a programming expert. Explain concepts clearly and provide examples.',
        'What is a Python function? Give me a simple example.',
        'Should explain functions and provide a code example.', ''
    ],
    [
        'LMSYS', 'lmsys/vicuna-7b-v1.5', 'creative', 'few shot',
        'metaphor-based explanation', 'You are a creative educator who uses Marvel universe metaphors.',
        'Explain machine learning using Marvel characters as examples.',
        'Should use Marvel characters to explain ML concepts creatively.', ''
    ],
    [
        'LMSYS', 'lmsys/vicuna-7b-v1.5', 'agentic', 'multishot',
        'problem solving', 'You are an AI agent that breaks down complex problems into steps.',
        'How would you plan a birthday party for a 10-year-old?',
        'Should provide a structured step-by-step plan.', ''
    ],
    [
        'LMSYS', 'lmsys/vicuna-7b-v1.5', 'educational', 'single shot',
        'concept explanation', 'You are a patient teacher explaining to a beginner.',
        'Explain photosynthesis in simple terms.',
        'Should provide clear, beginner-friendly explanation.', ''
    ],
    [
        'LMSYS', 'lmsys/vicuna-7b-v1.5', 'reasoning', 'chain of thought',
        'logical reasoning', 'Think step by step and show your reasoning process.',
        'If all roses are flowers and some flowers are red, can we conclude that some roses are red?',
        'Should show logical reasoning steps and correct conclusion.', ''
    ],
    [
        'LMSYS', 'lmsys/vicuna-7b-v1.5', 'creative writing', 'single shot',
        'storytelling', 'You are a creative writer who crafts engaging stories.',
        'Write a short story about a time-traveling scientist.',
        'Should create an engaging short story with time travel theme.', ''
    ],
    [
        'LMSYS', 'lmsys/vicuna-7b-v1.5', 'analysis', 'single shot',
        'text analysis', 'You are an expert analyst who provides detailed insights.',
        'Analyze the pros and cons of remote work.',
        'Should provide balanced analysis with clear pros and cons.', ''
    ]
]

# Create a DataFrame and save it to Excel
df = pd.DataFrame(data, columns=columns)
df.to_excel('LLM_testing.xlsx', index=False)

print("Created comprehensive LLM_testing.xlsx file with the following test cases:")
print(f"- {len(data)} test scenarios")
print("- Various categories: chat, coding, creative, agentic, educational, reasoning, creative writing, analysis")
print("- Different prompting frameworks: single shot, few shot, multishot, chain of thought")
print("- Diverse prompt approaches and themes")
print("\nColumn structure:")
for i, col in enumerate(columns, 1):
    print(f"{i:2d}. {col}")

print(f"\nFile saved as: LLM_testing.xlsx")
print("You can now run the automation script: python llm_testing_automation.py")
