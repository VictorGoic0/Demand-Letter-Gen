"""
Common utility functions for the application.
"""
import uuid
import re
import html
from datetime import datetime
from typing import Optional
from html.parser import HTMLParser


def generate_uuid() -> str:
    """
    Generate a new UUID string.
    
    Returns:
        UUID string in standard format
    """
    return str(uuid.uuid4())


def format_datetime(dt: datetime, format_string: Optional[str] = None) -> str:
    """
    Format a datetime object as a string.
    
    Args:
        dt: Datetime object to format
        format_string: Optional format string (default: ISO format)
        
    Returns:
        Formatted datetime string
    """
    if format_string is None:
        return dt.isoformat()
    return dt.strftime(format_string)


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human-readable string.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Human-readable file size string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    # Format to 1 decimal place if needed
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize a filename by removing or replacing invalid characters.
    
    Args:
        filename: Original filename
        max_length: Maximum length of the sanitized filename
        
    Returns:
        Sanitized filename safe for filesystem use
    """
    # Remove path components
    filename = filename.split("/")[-1].split("\\")[-1]
    
    # Remove leading/trailing whitespace and dots
    filename = filename.strip(" .")
    
    # Replace invalid characters with underscore
    # Invalid characters: < > : " / \ | ? *
    invalid_chars = r'[<>:"/\\|?*]'
    filename = re.sub(invalid_chars, "_", filename)
    
    # Remove control characters
    filename = re.sub(r'[\x00-\x1f\x7f]', "", filename)
    
    # Replace multiple consecutive underscores with single underscore
    filename = re.sub(r'_+', "_", filename)
    
    # Remove leading/trailing underscores
    filename = filename.strip("_")
    
    # Ensure filename is not empty
    if not filename:
        filename = "file"
    
    # Truncate to max_length if needed
    if len(filename) > max_length:
        # Try to preserve extension
        if "." in filename:
            name, ext = filename.rsplit(".", 1)
            max_name_length = max_length - len(ext) - 1
            if max_name_length > 0:
                filename = f"{name[:max_name_length]}.{ext}"
            else:
                filename = filename[:max_length]
        else:
            filename = filename[:max_length]
    
    return filename


class HTMLSanitizer(HTMLParser):
    """
    HTML sanitizer that removes potentially dangerous tags and attributes.
    """
    # Allowed HTML tags
    ALLOWED_TAGS = {
        "p", "br", "strong", "em", "u", "b", "i", "ul", "ol", "li",
        "h1", "h2", "h3", "h4", "h5", "h6", "div", "span", "blockquote",
        "a", "table", "thead", "tbody", "tr", "td", "th",
    }
    
    # Allowed attributes per tag
    ALLOWED_ATTRIBUTES = {
        "a": ["href", "title"],
        "table": ["class"],
        "td": ["colspan", "rowspan"],
        "th": ["colspan", "rowspan"],
    }
    
    def __init__(self):
        super().__init__()
        self.result = []
        self.tag_stack = []
    
    def handle_starttag(self, tag, attrs):
        """Handle opening tags."""
        tag_lower = tag.lower()
        
        if tag_lower in self.ALLOWED_TAGS:
            self.tag_stack.append(tag_lower)
            attrs_dict = dict(attrs)
            allowed_attrs = self.ALLOWED_ATTRIBUTES.get(tag_lower, [])
            
            # Filter attributes
            filtered_attrs = {
                k: v for k, v in attrs_dict.items()
                if k.lower() in allowed_attrs
            }
            
            # Build tag string
            attr_string = ""
            if filtered_attrs:
                attr_parts = [f'{k}="{html.escape(v)}"' for k, v in filtered_attrs.items()]
                attr_string = " " + " ".join(attr_parts)
            
            self.result.append(f"<{tag_lower}{attr_string}>")
    
    def handle_endtag(self, tag):
        """Handle closing tags."""
        tag_lower = tag.lower()
        
        if tag_lower in self.ALLOWED_TAGS and tag_lower in self.tag_stack:
            # Remove from stack
            while self.tag_stack and self.tag_stack[-1] != tag_lower:
                self.tag_stack.pop()
            if self.tag_stack:
                self.tag_stack.pop()
            
            self.result.append(f"</{tag_lower}>")
    
    def handle_data(self, data):
        """Handle text content."""
        self.result.append(html.escape(data))
    
    def handle_entityref(self, name):
        """Handle named entities."""
        self.result.append(f"&{name};")
    
    def handle_charref(self, name):
        """Handle numeric entities."""
        self.result.append(f"&#{name};")
    
    def get_sanitized(self) -> str:
        """Get the sanitized HTML string."""
        return "".join(self.result)


def sanitize_html(html_content: str) -> str:
    """
    Sanitize HTML content by removing dangerous tags and attributes.
    
    Args:
        html_content: HTML content to sanitize
        
    Returns:
        Sanitized HTML string
    """
    if not html_content:
        return ""
    
    sanitizer = HTMLSanitizer()
    sanitizer.feed(html_content)
    return sanitizer.get_sanitized()


def parse_file_size(size_string: str) -> int:
    """
    Parse a human-readable file size string to bytes.
    
    Args:
        size_string: Human-readable size (e.g., "1.5 MB", "500 KB")
        
    Returns:
        Size in bytes
        
    Raises:
        ValueError: If the size string cannot be parsed
    """
    size_string = size_string.strip().upper()
    
    # Match pattern: number followed by unit
    match = re.match(r'^(\d+(?:\.\d+)?)\s*([KMGT]?B?)$', size_string)
    if not match:
        raise ValueError(f"Invalid file size format: {size_string}")
    
    size_value = float(match.group(1))
    unit = match.group(2) or "B"
    
    multipliers = {
        "B": 1,
        "KB": 1024,
        "MB": 1024 ** 2,
        "GB": 1024 ** 3,
        "TB": 1024 ** 4,
    }
    
    if unit not in multipliers:
        raise ValueError(f"Unknown file size unit: {unit}")
    
    return int(size_value * multipliers[unit])

