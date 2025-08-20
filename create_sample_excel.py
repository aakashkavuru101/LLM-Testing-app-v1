import pandas as pd

# Define the columns based on your requirements
columns = [
    'Company', 'Model/LLM name', 'Category', 'framework for prompting',
    'Prompt approach/theme', 'user system prompt', 'actual user prompt',
    'Expected behavioural response', 'override responses'
]

# Create sample data for one test case
data = [
    [
        'LMSYS', 'vicuna-7b-v1.5', 'chat', 'single shot',
        'simple question', 'You are a helpful assistant.', 'Hello, who are you?',
        'The model should introduce itself as an assistant.', ''
    ]
]

# Create a DataFrame and save it to Excel
df = pd.DataFrame(data, columns=columns)
df.to_excel('LLM_testing.xlsx', index=False)

print("Created sample LLM_testing.xlsx file.")
