#!/usr/bin/env python3
"""
Quick Start Guide for LLM Testing Automation
Run this script to get started with the system
"""

import os
import sys

def print_banner():
    print("🚀 LLM Testing Automation System")
    print("=" * 50)
    print("Connect to LMArena/FastChat locally for free LLM testing!")
    print()

def check_files():
    print("📁 Checking required files...")
    files = {
        'llm_testing_automation.py': 'Main automation script',
        'server_manager.py': 'FastChat server management',
        'LLM_testing.xlsx': 'Sample test prompts',
        'README_LLM_TESTING.md': 'Complete documentation'
    }
    
    all_present = True
    for file, description in files.items():
        if os.path.exists(file):
            print(f"✅ {file} - {description}")
        else:
            print(f"❌ {file} - {description} (MISSING)")
            all_present = False
    
    return all_present

def show_quick_start():
    print("\n🚀 Quick Start Options:")
    print()
    print("1️⃣  RUN DEMO (No model download needed):")
    print("   python demo.py")
    print()
    print("2️⃣  CREATE TEST EXCEL FILE:")
    print("   python create_sample_excel.py")
    print()
    print("3️⃣  RUN FULL SYSTEM (Downloads model if needed):")
    print("   python llm_testing_automation.py")
    print()
    print("4️⃣  RUN TESTS TO VALIDATE SETUP:")
    print("   python test_system.py")
    print()

def show_manual_setup():
    print("🔧 Manual Setup (if you prefer):")
    print()
    print("Terminal 1: python -m fastchat.serve.controller")
    print("Terminal 2: python -m fastchat.serve.model_worker --model-path lmsys/vicuna-7b-v1.5") 
    print("Terminal 3: python -m fastchat.serve.openai_api_server --host localhost --port 8000")
    print("Terminal 4: python llm_testing_automation.py")
    print()

def show_excel_format():
    print("📊 Excel File Format:")
    print("Your Excel file should have these columns:")
    columns = [
        'Company', 'Model/LLM name', 'Category', 'framework for prompting',
        'Prompt approach/theme', 'user system prompt', 'actual user prompt',
        'Expected behavioural response', 'override responses'
    ]
    for i, col in enumerate(columns, 1):
        print(f"  {i:2d}. {col}")
    print()

def show_troubleshooting():
    print("🛠️  Common Issues:")
    print()
    print("❓ Port conflicts (Error 10048):")
    print("   → The system automatically handles this")
    print("   → Or run: python -c \"from server_manager import ServerManager; ServerManager().cleanup_existing_servers()\"")
    print()
    print("❓ Model download slow/fails:")
    print("   → Ensure stable internet connection")
    print("   → Check available disk space (7B models need ~13GB)")
    print("   → Try smaller model: fastchat-t5-3b-v1.0")
    print()
    print("❓ Out of memory:")
    print("   → Use smaller models")
    print("   → Close other applications")
    print("   → Consider cloud/GPU instances")
    print()

def main():
    print_banner()
    
    if not check_files():
        print("\n❌ Some required files are missing. Please check your installation.")
        return
    
    show_quick_start()
    show_excel_format()
    show_manual_setup()
    show_troubleshooting()
    
    print("📖 For detailed documentation, see: README_LLM_TESTING.md")
    print()
    print("🎯 Recommended first step: python demo.py")
    print("   (Shows the system working without downloading models)")

if __name__ == "__main__":
    main()