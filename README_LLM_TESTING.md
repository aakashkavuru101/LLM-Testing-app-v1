# LLM Testing Automation System

A comprehensive system for automated testing of Large Language Models (LLMs) using FastChat/LMArena. This system allows you to run batch tests from Excel files against locally hosted LLM models for free.

## Features

- ✅ **Automatic Server Management**: Starts and manages FastChat servers with port conflict resolution
- ✅ **Excel-Based Testing**: Read test prompts from structured Excel files
- ✅ **Robust Error Handling**: Retry logic, connection recovery, and graceful failure handling
- ✅ **Comprehensive Logging**: Detailed logs for debugging and monitoring
- ✅ **Multiple Model Support**: Test against various LLM models locally
- ✅ **Results Export**: Detailed test results exported to Excel with timestamps and metadata
- ✅ **Port Conflict Resolution**: Automatically handles port conflicts and server cleanup

## Quick Start

### 1. Install Dependencies

The system will automatically install required dependencies. You may also install them manually:

```bash
pip install pandas openpyxl psutil requests
```

### 2. Prepare Your Test Data

Create or use the provided `LLM_testing.xlsx` file with the following columns:

| Column Name | Description | Example |
|-------------|-------------|---------|
| Company | AI model company | LMSYS, OpenAI, Anthropic |
| Model/LLM name | Model identifier | lmsys/vicuna-7b-v1.5 |
| Category | Test category | chat, coding, creative, agentic |
| framework for prompting | Prompting approach | single shot, few shot, multishot |
| Prompt approach/theme | Theme or style | metaphor-based, simple explanation |
| user system prompt | System message | You are a helpful assistant |
| actual user prompt | The test prompt | Hello, who are you? |
| Expected behavioural response | Expected behavior | Should introduce itself |
| override responses | Override settings | (optional) |

### 3. Generate Sample Excel File

```bash
python create_sample_excel.py
```

This creates a comprehensive `LLM_testing.xlsx` file with 8 diverse test scenarios.

### 4. Run the Tests

```bash
python llm_testing_automation.py
```

The system will:
1. Automatically start FastChat servers (controller, model worker, API server)
2. Load your test prompts from the Excel file
3. Execute each test against the available models
4. Save detailed results to a timestamped Excel file

### 5. Manual Server Management (Optional)

If you prefer to manage servers manually:

```bash
# Terminal 1: Start controller
python -m fastchat.serve.controller

# Terminal 2: Start model worker (downloads model if needed)
python -m fastchat.serve.model_worker --model-path lmsys/vicuna-7b-v1.5

# Terminal 3: Start API server
python -m fastchat.serve.openai_api_server --host localhost --port 8000

# Terminal 4: Run tests with auto-start disabled
python -c "
from llm_testing_automation import LLMTester
tester = LLMTester('LLM_testing.xlsx', api_base='http://localhost:8000', auto_start_servers=False)
tester.run_tests()
tester.save_results()
"
```

## System Architecture

### Components

1. **ServerManager** (`server_manager.py`)
   - Handles FastChat server lifecycle
   - Port conflict resolution
   - Process management and cleanup

2. **LLMTester** (`llm_testing_automation.py`)
   - Excel file processing
   - API communication
   - Test execution and results collection

3. **Test System** (`test_system.py`)
   - Validation and smoke tests
   - System health checks

### Server Stack

```
┌─────────────────┐
│   Your Script   │
└─────────┬───────┘
          │ HTTP Requests
┌─────────▼───────┐
│ OpenAI API      │ :8000
│ Server          │
└─────────┬───────┘
          │ Internal API
┌─────────▼───────┐
│ Controller      │ :21001
└─────────┬───────┘
          │ Worker Management
┌─────────▼───────┐
│ Model Worker    │ :21002+
│ (with LLM)      │
└─────────────────┘
```

## Configuration

### Environment Variables

- `CUDA_VISIBLE_DEVICES`: Control GPU usage for models
- `HF_HOME`: Hugging Face cache directory

### Model Configuration

The default model is `lmsys/vicuna-7b-v1.5`. To use different models:

1. **Edit the server_manager.py** and change the default model in `start_full_stack()`
2. **Update your Excel file** with the appropriate model names
3. **For custom models**, ensure they're compatible with FastChat

### Common Models

- `lmsys/vicuna-7b-v1.5` (Default, good balance)
- `lmsys/vicuna-13b-v1.5` (Better quality, needs more resources)
- `lmsys/fastchat-t5-3b-v1.0` (Lightweight)
- `microsoft/DialoGPT-medium` (Conversation focused)

## Troubleshooting

### Port Conflicts (Error 10048)

The system automatically handles port conflicts, but if you encounter issues:

```bash
# Kill all FastChat processes
python -c "
from server_manager import ServerManager
manager = ServerManager()
manager.cleanup_existing_servers()
"
```

### Model Download Issues

Models are downloaded automatically on first use. Ensure you have:
- Stable internet connection
- Sufficient disk space (7B models need ~13GB)
- Hugging Face access (public models don't need authentication)

### Memory Issues

For large models:
- Use smaller models like `fastchat-t5-3b-v1.0`
- Reduce batch size in testing
- Monitor system memory usage

### Connection Issues

If the API server won't start:
1. Check if ports are free: `netstat -an | grep :8000`
2. Verify model worker registered: Check controller logs
3. Wait longer for model loading (especially on first run)

## Example Results

The system generates detailed Excel reports with:

- Test execution timestamps
- Model responses and metadata
- Success/failure status
- Response length statistics
- API performance metrics
- Error details for failed tests

## Advanced Usage

### Custom Test Categories

Add your own test categories in the Excel file:

- **Code Generation**: Programming tasks
- **Creative Writing**: Story/content creation
- **Mathematical Reasoning**: Math problem solving
- **Factual Q&A**: Knowledge retrieval
- **Instruction Following**: Complex multi-step tasks

### Batch Processing

For large test suites:
1. Split Excel files by category
2. Run tests in parallel (different models)
3. Use the results aggregation features

### Integration

The system can be integrated into:
- CI/CD pipelines for model testing
- Research workflows for model comparison
- Educational environments for LLM exploration

## Contributing

This system is designed to be extensible. Key areas for contribution:

- Additional model workers (vLLM, TensorRT-LLM)
- Enhanced prompt engineering features
- Result analysis and visualization
- Performance optimization

## License

This project follows the same license as FastChat (Apache 2.0).

---

## Support

For issues:
1. Run the test suite: `python test_system.py`
2. Check system logs for detailed error information
3. Verify your Excel file format matches the required columns
4. Ensure sufficient system resources for your chosen models

Happy testing! 🚀