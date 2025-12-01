"""
Autocomplete service for generating code suggestions.

This service implements mock autocomplete logic. In production, this would
be replaced with:
- OpenAI Codex/GPT API calls
- Local language models (e.g., CodeLlama, StarCoder)
- Language-specific completion engines (Jedi for Python, etc.)
"""

from app.schemas import AutocompleteResponse
import re
import logging

logger = logging.getLogger(__name__)

class AutocompleteService:
    """Service for generating intelligent code autocomplete suggestions."""
    
    def __init__(self):
        """Initialize autocomplete service with rule patterns."""
        # Compile regex patterns for better performance
        self.patterns = {
            "print_statement": re.compile(r'print\($'),
            "function_def": re.compile(r'def\s+\w+\([^)]*\):\s*$'),
            "class_def": re.compile(r'class\s+\w+.*:\s*$'),
            "import_statement": re.compile(r'from\s+\w+\s+import\s+$'),
            "for_loop": re.compile(r'for\s+\w+\s+in\s+$'),
            "if_statement": re.compile(r'if\s+.*:\s*$'),
            "return_statement": re.compile(r'\s+return\s+$'),
            "list_comprehension": re.compile(r'\[.*for\s+\w+\s+in\s+$'),
        }
    
    def generate_suggestion(
        self,
        code: str,
        cursor_position: int,
        language: str = "python"
    ) -> AutocompleteResponse:
        """
        Generate autocomplete suggestion based on code context.
        
        This implementation uses rule-based pattern matching.
        In production, replace with actual AI model.
        
        Args:
            code: Current code content
            cursor_position: Cursor position in code
            language: Programming language
            
        Returns:
            AutocompleteResponse: Suggestion with confidence score
            
        Example:
            service = AutocompleteService()
            suggestion = service.generate_suggestion(
                "def hello():\n    print(",
                25,
                "python"
            )
            # Returns: AutocompleteResponse(suggestion="'Hello, World!')")
        """
        # Get code context before cursor
        context = code[:cursor_position]
        
        # Get last line for pattern matching
        lines = context.split('\n')
        last_line = lines[-1] if lines else ""
        
        # Try to match patterns and generate suggestions
        suggestion_text, confidence, suggestion_type = self._match_patterns(
            last_line,
            context,
            language
        )
        
        logger.debug(
            f"Generated suggestion: '{suggestion_text}' "
            f"(confidence: {confidence}, type: {suggestion_type})"
        )
        
        return AutocompleteResponse(
            suggestion=suggestion_text,
            confidence=confidence,
            type=suggestion_type
        )
    
    def _match_patterns(
        self,
        last_line: str,
        context: str,
        language: str
    ) -> tuple[str, float, str]:
        """
        Match code patterns and generate appropriate suggestions.
        
        Args:
            last_line: Last line of code
            context: Full code context
            language: Programming language
            
        Returns:
            tuple: (suggestion_text, confidence, type)
        """
        # Python-specific patterns
        if language == "python":
            # Print statement completion
            if self.patterns["print_statement"].search(last_line):
                return "'Hello, World!')", 0.85, "completion"
            
            # Function definition - suggest docstring
            if self.patterns["function_def"].search(last_line):
                return '\n    """Function description."""', 0.80, "docstring"
            
            # Class definition - suggest pass or init
            if self.patterns["class_def"].search(last_line):
                return "\n    def __init__(self):\n        pass", 0.82, "method"
            
            # Import completion
            if self.patterns["import_statement"].search(last_line):
                return "typing import List, Dict, Optional", 0.75, "import"
            
            # For loop - suggest range
            if self.patterns["for_loop"].search(last_line):
                return "range(10):\n        ", 0.78, "completion"
            
            # If statement - suggest pass
            if self.patterns["if_statement"].search(last_line):
                return "\n        pass", 0.70, "statement"
            
            # Return statement context
            if self.patterns["return_statement"].search(last_line):
                # Check if in function that might return bool
                if "def is_" in context or "def has_" in context:
                    return "True", 0.75, "boolean"
                return "None", 0.70, "return_value"
            
            # List comprehension
            if self.patterns["list_comprehension"].search(last_line):
                return "items]", 0.73, "comprehension"
            
            # Common variable assignments
            if "= [" in last_line and last_line.endswith("["):
                return "1, 2, 3]", 0.65, "list_literal"
            
            if "= {" in last_line and last_line.endswith("{"):
                return "'key': 'value'}", 0.65, "dict_literal"
            
            # Method call patterns
            if ".append(" in last_line and last_line.endswith("("):
                return "item)", 0.72, "method_arg"
            
            if ".join(" in last_line and last_line.endswith("("):
                return "items)", 0.74, "method_arg"
        
        # JavaScript-specific patterns
        elif language == "javascript":
            if "console.log(" in last_line:
                return "'Hello, World!')", 0.85, "completion"
            
            if last_line.strip().endswith("=>"):
                return " {\n    \n}", 0.80, "arrow_function"
            
            if "const " in last_line and last_line.endswith("= "):
                return "[]", 0.70, "initialization"
        
        # Generic fallback suggestions
        if last_line.strip().endswith("("):
            return ")", 0.60, "bracket_close"
        
        if last_line.strip().endswith("["):
            return "]", 0.60, "bracket_close"
        
        if last_line.strip().endswith("{"):
            return "}", 0.60, "bracket_close"
        
        # Default suggestion when no pattern matches
        return "# TODO: Implement", 0.50, "comment"
    
    def get_language_keywords(self, language: str) -> list[str]:
        """
        Get common keywords for a programming language.
        
        This can be used for basic keyword completion.
        
        Args:
            language: Programming language
            
        Returns:
            list: Common keywords for the language
        """
        keywords = {
            "python": [
                "def", "class", "import", "from", "if", "elif", "else",
                "for", "while", "try", "except", "finally", "with",
                "return", "yield", "lambda", "pass", "break", "continue"
            ],
            "javascript": [
                "function", "const", "let", "var", "if", "else", "for",
                "while", "return", "async", "await", "try", "catch",
                "class", "extends", "import", "export", "default"
            ],
            "typescript": [
                "function", "const", "let", "var", "if", "else", "for",
                "while", "return", "async", "await", "try", "catch",
                "class", "extends", "import", "export", "default",
                "interface", "type", "enum", "public", "private"
            ]
        }
        
        return keywords.get(language, [])