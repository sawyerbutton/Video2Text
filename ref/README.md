# Video2Text Reference Documentation

This directory contains comprehensive reference documentation for the Video2Text project, designed for developers, contributors, and Claude Code assistance.

## Documentation Index

### Quick Reference

**[quickstart.md](quickstart.md)** - 30-second to 5-minute quick start guide
- Installation steps
- Common commands
- Quick troubleshooting
- Most common use cases

**Perfect for:** First-time users, quick reference

---

### Architecture & Design

**[architecture.md](architecture.md)** - Complete system architecture
- System overview and design patterns
- Core module documentation (platform_utils, config_manager, file_manager, audio_processor, transcriber)
- Data flow diagrams
- Technology stack
- Performance characteristics
- Migration notes (OpenAI Whisper → faster-whisper)

**Perfect for:** Understanding system design, contributing code, architecture decisions

---

### API Documentation

**[api-reference.md](api-reference.md)** - Complete API reference
- Core module APIs with parameters and return types
- CLI interface documentation
- Configuration file formats
- Return codes and error handling
- Code examples for each API

**Perfect for:** Integrating Video2Text into other projects, writing scripts

---

### Model Reference

**[models.md](models.md)** - Comprehensive model documentation
- Detailed specs for all 8 Whisper models (tiny, base, small, medium, large, large-v2, large-v3, turbo)
- Model selection guide by use case, hardware, and language
- Compute type documentation (float32, float16, int8, int8_float16)
- Language support matrix
- Performance benchmarks and comparisons
- Model download and storage information

**Perfect for:** Choosing the right model, optimizing performance, understanding trade-offs

---

### Workflow Guide

**[workflows.md](workflows.md)** - Step-by-step workflows
- Quick start workflow
- Automated processing workflows
- Batch processing patterns
- Subtitle generation
- Meeting transcription
- Podcast processing
- Production workflows
- Integration examples
- Troubleshooting workflows

**Perfect for:** Learning how to use the tool effectively, solving specific use cases

---

## Documentation Purpose

These reference documents are designed to:

1. **Help users** get started quickly and solve common problems
2. **Guide developers** working on the codebase
3. **Support Claude Code** in providing accurate assistance
4. **Document architecture** decisions and design patterns
5. **Provide examples** for common integration scenarios

## Quick Navigation

### I want to...

**Get started quickly**
→ [quickstart.md](quickstart.md)

**Understand the system architecture**
→ [architecture.md](architecture.md)

**Use the API in my code**
→ [api-reference.md](api-reference.md)

**Choose the right model**
→ [models.md](models.md)

**Learn common workflows**
→ [workflows.md](workflows.md)

**Read user documentation**
→ [../README.md](../README.md)

**See project summary**
→ [../docs/PROJECT_SUMMARY.md](../docs/PROJECT_SUMMARY.md)

## Documentation Standards

All reference documentation follows these standards:

- **Markdown format** for easy reading and rendering
- **Code examples** with syntax highlighting
- **Clear headings** for easy navigation
- **Cross-references** between documents
- **Practical examples** for real-world use
- **Performance data** where applicable
- **Up-to-date** with latest codebase (faster-whisper v1.0.0)

## Contributing to Documentation

When updating the project, please also update relevant documentation:

1. **Code changes** → Update [api-reference.md](api-reference.md)
2. **Architecture changes** → Update [architecture.md](architecture.md)
3. **New models** → Update [models.md](models.md)
4. **New workflows** → Update [workflows.md](workflows.md)
5. **Breaking changes** → Update all relevant docs + [quickstart.md](quickstart.md)

## Documentation Coverage

### Core Modules (100% documented)
- ✅ platform_utils.py - [architecture.md](architecture.md), [api-reference.md](api-reference.md)
- ✅ config_manager.py - [architecture.md](architecture.md), [api-reference.md](api-reference.md)
- ✅ file_manager.py - [architecture.md](architecture.md), [api-reference.md](api-reference.md)
- ✅ audio_processor.py - [architecture.md](architecture.md), [api-reference.md](api-reference.md)
- ✅ transcriber.py - [architecture.md](architecture.md), [api-reference.md](api-reference.md)

### Tools (100% documented)
- ✅ auto_process.py - [workflows.md](workflows.md), [api-reference.md](api-reference.md)
- ✅ auto_process_large.py - [workflows.md](workflows.md)
- ✅ quick_check.py - [quickstart.md](quickstart.md)

### Models (100% documented)
- ✅ All 8 models documented in [models.md](models.md)
- ✅ Compute types documented
- ✅ Performance benchmarks included

### Workflows (100% documented)
- ✅ Quick start workflow
- ✅ Automated workflows
- ✅ Batch processing
- ✅ Subtitle generation
- ✅ Production workflows
- ✅ Integration patterns

## Version Information

**Documentation Version:** 1.0.0
**Project Version:** 1.0.0
**Last Updated:** 2024-11
**faster-whisper Migration:** Complete

## External Resources

- **Project README:** [../README.md](../README.md)
- **GitHub Repository:** https://github.com/your-username/Video2Text
- **faster-whisper:** https://github.com/guillaumekln/faster-whisper
- **OpenAI Whisper:** https://github.com/openai/whisper
- **FFmpeg:** https://ffmpeg.org/

## For Claude Code

This reference documentation is specifically organized to help Claude Code provide accurate assistance:

**CLAUDE.md** in the project root contains:
- Quick reference for common questions
- File location guide
- Key code patterns
- Development guidelines

When assisting users:
1. Check **[CLAUDE.md](../CLAUDE.md)** for quick answers
2. Reference specific documentation files for detailed information
3. Use code examples from **[api-reference.md](api-reference.md)**
4. Follow workflows from **[workflows.md](workflows.md)**
5. Reference architecture from **[architecture.md](architecture.md)**

---

**Need help?** Start with [quickstart.md](quickstart.md) or check the main [README.md](../README.md)
