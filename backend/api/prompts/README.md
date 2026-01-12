# Smart Search AI Prompts

This directory contains external prompts used by the intelligent search system.

## Structure

- `category_analysis.txt` - Prompt for category analysis and mapping
- `response_generation.txt` - Prompt for final response generation to user

## Advantages of This Approach

### ✅ **Maintainability**
- Prompts can be edited without touching Python code
- Easy to version and rollback changes
- Clear separation between logic and content

### ✅ **Collaboration**
- Product Managers can edit prompts directly
- No need to know Python to adjust AI behavior
- Facilitates A/B testing of different prompt versions

### ✅ **Performance**
- Prompts are loaded once and kept in cache
- Reduces overhead of parsing large strings
- Facilitates implementation of API prompt caching

### ✅ **Debugging**
- Easy to identify which prompt is causing issues
- Logs can reference specific files
- Facilitates isolated testing of each prompt

## How to Use

```python
from prompt_manager import prompt_manager

# Load a prompt
template = prompt_manager.load_prompt("category_analysis")

# List available prompts
available = prompt_manager.list_available_prompts()

# Reload a prompt (useful in development)
template = prompt_manager.reload_prompt("category_analysis")

# Clear cache (forces reload of all prompts)
prompt_manager.clear_cache()
```

## Best Practices

1. **Versioning**: Always commit prompt changes with descriptive messages
2. **Testing**: Test prompt changes before deploying
3. **Documentation**: Document significant changes in this README
4. **Backup**: Keep previous versions of prompts that worked well

## Change History

### 2026-01-12
- ✅ Initial creation of external prompts
- ✅ Migration from inline prompts to `.txt` files
- ✅ Implementation of `PromptManager` with cache
- ✅ Translation of all prompts to English
