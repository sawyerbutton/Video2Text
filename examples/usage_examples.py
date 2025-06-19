#!/usr/bin/env python3
"""
MP4ToText Usage Examples
Demonstrates various usage patterns and configurations for different platforms.
"""

import sys
import subprocess
from pathlib import Path

class UsageExamples:
    """Collection of usage examples for MP4ToText."""
    
    def __init__(self):
        self.script_name = "mp4_to_text.py"
        
    def basic_usage(self):
        """Basic usage examples."""
        print("=== Basic Usage Examples ===\n")
        
        examples = [
            {
                "description": "Process all videos in a directory",
                "command": f"python {self.script_name} -i ./input_videos -o ./output_texts"
            },
            {
                "description": "Use specific Whisper model",
                "command": f"python {self.script_name} -i ./videos -o ./texts -m large-v3"
            },
            {
                "description": "Specify language for better accuracy",
                "command": f"python {self.script_name} -i ./videos -o ./texts -l zh"
            },
            {
                "description": "Skip already processed files",
                "command": f"python {self.script_name} -i ./videos -o ./texts --skip-existing"
            }
        ]
        
        for example in examples:
            print(f"• {example['description']}:")
            print(f"  {example['command']}\n")
    
    def advanced_usage(self):
        """Advanced usage examples."""
        print("=== Advanced Usage Examples ===\n")
        
        examples = [
            {
                "description": "Parallel processing with 2 workers",
                "command": f"python {self.script_name} -i ./videos -o ./texts -w 2"
            },
            {
                "description": "Force CPU usage (disable GPU)",
                "command": f"python {self.script_name} -i ./videos -o ./texts -d cpu"
            },
            {
                "description": "Use configuration file",
                "command": f"python {self.script_name} --config config/my_config.ini"
            },
            {
                "description": "Verbose output for debugging",
                "command": f"python {self.script_name} -i ./videos -o ./texts --verbose"
            },
            {
                "description": "Quiet mode for scripts",
                "command": f"python {self.script_name} -i ./videos -o ./texts --quiet"
            },
            {
                "description": "Keep temporary files for inspection",
                "command": f"python {self.script_name} -i ./videos -o ./texts --no-cleanup"
            }
        ]
        
        for example in examples:
            print(f"• {example['description']}:")
            print(f"  {example['command']}\n")
    
    def platform_specific_examples(self):
        """Platform-specific usage examples."""
        print("=== Platform-Specific Examples ===\n")
        
        # Windows examples
        print("Windows:")
        windows_examples = [
            {
                "description": "Process videos from Desktop",
                "command": f'python {self.script_name} -i "C:\\Users\\Username\\Desktop\\Videos" -o "C:\\Users\\Username\\Desktop\\Texts"'
            },
            {
                "description": "Use UNC network path",
                "command": f'python {self.script_name} -i "\\\\server\\videos" -o "\\\\server\\texts"'
            }
        ]
        
        for example in windows_examples:
            print(f"  • {example['description']}:")
            print(f"    {example['command']}")
        print()
        
        # macOS examples
        print("macOS:")
        macos_examples = [
            {
                "description": "Process videos from Downloads",
                "command": f"python {self.script_name} -i ~/Downloads/Videos -o ~/Documents/Transcripts"
            },
            {
                "description": "Use Apple Silicon GPU (MPS)",
                "command": f"python {self.script_name} -i ./videos -o ./texts -d mps"
            }
        ]
        
        for example in macos_examples:
            print(f"  • {example['description']}:")
            print(f"    {example['command']}")
        print()
        
        # Linux examples
        print("Linux:")
        linux_examples = [
            {
                "description": "Process videos from home directory",
                "command": f"python {self.script_name} -i /home/user/Videos -o /home/user/Transcripts"
            },
            {
                "description": "Use CUDA GPU",
                "command": f"python {self.script_name} -i ./videos -o ./texts -d cuda"
            }
        ]
        
        for example in linux_examples:
            print(f"  • {example['description']}:")
            print(f"    {example['command']}")
        print()
    
    def batch_processing_examples(self):
        """Batch processing examples."""
        print("=== Batch Processing Examples ===\n")
        
        # Create batch script examples
        print("Windows Batch Script (process_videos.bat):")
        batch_script = '''@echo off
echo Starting video transcription...
python mp4_to_text.py -i "input_videos" -o "output_texts" -m medium -l auto --skip-existing
if %ERRORLEVEL% EQU 0 (
    echo Transcription completed successfully!
) else (
    echo Transcription failed with error code %ERRORLEVEL%
)
pause'''
        print(batch_script)
        print()
        
        print("Linux/macOS Shell Script (process_videos.sh):")
        shell_script = '''#!/bin/bash
echo "Starting video transcription..."
python3 mp4_to_text.py -i "input_videos" -o "output_texts" -m medium -l auto --skip-existing

if [ $? -eq 0 ]; then
    echo "Transcription completed successfully!"
else
    echo "Transcription failed with error code $?"
fi'''
        print(shell_script)
        print()
    
    def configuration_examples(self):
        """Configuration file examples."""
        print("=== Configuration Examples ===\n")
        
        print("High-performance configuration (config_performance.ini):")
        perf_config = '''[PROCESSING]
model_name = large-v3
device = auto
max_workers = 2
skip_existing = true
cleanup_temp = true

[AUDIO]
sample_rate = 16000
channels = 1
quality = high

[LOGGING]
level = INFO
console_output = true'''
        print(perf_config)
        print()
        
        print("Low-resource configuration (config_lowres.ini):")
        lowres_config = '''[PROCESSING]
model_name = tiny
device = cpu
max_workers = 1
skip_existing = true
cleanup_temp = true

[AUDIO]
sample_rate = 16000
channels = 1
quality = medium

[LOGGING]
level = WARNING
console_output = true'''
        print(lowres_config)
        print()
    
    def troubleshooting_commands(self):
        """Troubleshooting and diagnostic commands."""
        print("=== Troubleshooting Commands ===\n")
        
        commands = [
            {
                "description": "Check system information",
                "command": f"python {self.script_name} --system-info"
            },
            {
                "description": "List available models",
                "command": f"python {self.script_name} --list-models"
            },
            {
                "description": "Test with tiny model first",
                "command": f"python {self.script_name} -i ./test_video -o ./test_output -m tiny -v"
            },
            {
                "description": "Force CPU if GPU issues",
                "command": f"python {self.script_name} -i ./videos -o ./texts -d cpu"
            },
            {
                "description": "Run with verbose logging",
                "command": f"python {self.script_name} -i ./videos -o ./texts -v"
            }
        ]
        
        for cmd in commands:
            print(f"• {cmd['description']}:")
            print(f"  {cmd['command']}\n")
    
    def python_api_examples(self):
        """Python API usage examples."""
        print("=== Python API Examples ===\n")
        
        api_example = '''# Import the modules
from core import ConfigManager, FileManager, AudioProcessor, WhisperTranscriber

# Create configuration
config = ConfigManager()
config.processing_config.input_dir = "./videos"
config.processing_config.output_dir = "./texts"
config.processing_config.model_name = "medium"

# Initialize components
file_manager = FileManager(config.processing_config.input_dir, 
                          config.processing_config.output_dir)
audio_processor = AudioProcessor("./temp")
transcriber = WhisperTranscriber(config.processing_config.model_name)

# Process a single file
video_path = Path("./test_video.mp4")
audio_path = audio_processor.extract_audio(video_path)
result = transcriber.transcribe(audio_path)
output_path = file_manager.get_output_path(video_path)
transcriber.save_result(result, output_path)

print(f"Transcription saved to: {output_path}")'''
        
        print(api_example)
        print()
    
    def performance_optimization(self):
        """Performance optimization examples."""
        print("=== Performance Optimization ===\n")
        
        optimizations = [
            {
                "scenario": "High-end system with NVIDIA GPU",
                "command": f"python {self.script_name} -i ./videos -o ./texts -m large-v3 -d cuda -w 1"
            },
            {
                "scenario": "Apple Silicon Mac",
                "command": f"python {self.script_name} -i ./videos -o ./texts -m large -d mps -w 1"
            },
            {
                "scenario": "Multi-core CPU system",
                "command": f"python {self.script_name} -i ./videos -o ./texts -m medium -d cpu -w 3"
            },
            {
                "scenario": "Low-memory system",
                "command": f"python {self.script_name} -i ./videos -o ./texts -m small -d cpu -w 1"
            },
            {
                "scenario": "Quick testing",
                "command": f"python {self.script_name} -i ./videos -o ./texts -m tiny -w 1"
            }
        ]
        
        for opt in optimizations:
            print(f"• {opt['scenario']}:")
            print(f"  {opt['command']}\n")
    
    def show_all_examples(self):
        """Show all examples."""
        self.basic_usage()
        self.advanced_usage()
        self.platform_specific_examples()
        self.batch_processing_examples()
        self.configuration_examples()
        self.troubleshooting_commands()
        self.python_api_examples()
        self.performance_optimization()


def main():
    """Main function to demonstrate usage examples."""
    examples = UsageExamples()
    
    if len(sys.argv) > 1:
        example_type = sys.argv[1].lower()
        
        if example_type == "basic":
            examples.basic_usage()
        elif example_type == "advanced":
            examples.advanced_usage()
        elif example_type == "platform":
            examples.platform_specific_examples()
        elif example_type == "batch":
            examples.batch_processing_examples()
        elif example_type == "config":
            examples.configuration_examples()
        elif example_type == "troubleshooting":
            examples.troubleshooting_commands()
        elif example_type == "api":
            examples.python_api_examples()
        elif example_type == "performance":
            examples.performance_optimization()
        else:
            print(f"Unknown example type: {example_type}")
            print("Available types: basic, advanced, platform, batch, config, troubleshooting, api, performance")
    else:
        examples.show_all_examples()


if __name__ == "__main__":
    main() 