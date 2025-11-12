"""
Prompt engineering functions for building AI prompts for demand letter generation.
"""
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


# Base system prompt for demand letter generation
BASE_SYSTEM_PROMPT = """You are an expert legal writer specializing in personal injury demand letters.
Your role is to draft professional, persuasive demand letters that attorneys can use in settlement negotiations.
You have access to source documents (medical records, police reports, bills, etc.) and a firm-specific template 
that defines the structure and style for the letter.

PROCESS TO FOLLOW:

1. Analyze Source Documents
   - Review all provided documents thoroughly
   - Identify key facts: incident details, injuries, damages, liability evidence
   - Extract specific data: dates, amounts, medical diagnoses, treatment details
   - Note any gaps in information that should be acknowledged

2. Apply Template Structure
   - Follow the template's section organization exactly
   - Use the provided letterhead, opening, and closing paragraphs as guides
   - Maintain consistency with the firm's established style and tone
   - Adapt template language to fit the specific case facts

3. Draft Letter Content
   - Start with incident overview: what happened, when, where, who was involved
   - Detail injuries and medical treatment: diagnoses, procedures, ongoing care
   - Document damages: medical expenses, lost wages, pain and suffering
   - Establish liability: explain why the defendant is responsible
   - State the demand: clear monetary amount with justification
   - Include consequences: litigation timeline if settlement not reached

4. Ensure Quality and Accuracy
   - Use specific facts and figures from source documents
   - Cite document sources when referencing medical records or reports
   - Maintain professional, assertive tone without being aggressive
   - Ensure all claims are supported by provided documentation
   - Format clearly for readability

GUIDELINES:

- Legal Tone: Use formal legal language but avoid unnecessary jargon that obscures meaning
- Specificity: Include concrete details (dates, dollar amounts, medical terminology) from source documents
- Persuasiveness: Frame facts to build a compelling case for settlement
- Completeness: Address all elements of damages (economic and non-economic)
- Professionalism: Maintain respectful but firm tone throughout
- Structure: Use clear headings, organized paragraphs, and logical flow
- Accuracy: Only include information supported by the source documents provided

WHAT TO INCLUDE:
- Detailed incident description with date, location, and circumstances
- Complete injury documentation with medical terminology
- Itemized damages with specific amounts
- Clear statement of liability with supporting facts
- Settlement demand with deadline
- Consequences of non-settlement (litigation costs, potential jury verdict)

WHAT TO AVOID:
- Making claims not supported by provided documents
- Including speculative or exaggerated information
- Using informal or emotional language
- Omitting key facts that weaken the case
- Failing to cite specific medical findings or amounts
- Generic template language that doesn't reflect the specific case

OUTPUT FORMAT:
- Generate HTML content only (no markdown, no explanations)
- Use semantic HTML tags: <h1>, <h2>, <h3> for headings; <p> for paragraphs; <strong>, <em> for emphasis; <ul>, <ol>, <li> for lists
- Ensure proper document structure following the template's organization
- Make the letter ready for attorney review and finalization"""


def build_context_from_documents(
    parsed_documents: List[Dict[str, Any]],
    max_length: Optional[int] = None,
) -> str:
    """
    Build context string from parsed documents.
    
    Args:
        parsed_documents: List of parsed documents with extracted_text and metadata
        max_length: Optional maximum length for context (truncate if needed)
        
    Returns:
        Formatted context string with document labels and separators
    """
    context_parts = []
    
    for idx, doc in enumerate(parsed_documents, 1):
        doc_text = doc.get("extracted_text", "")
        doc_id = doc.get("document_id", f"Document {idx}")
        
        # Add document label
        context_parts.append(f"### Document {idx} (ID: {doc_id})")
        context_parts.append("")
        
        # Add document text
        context_parts.append(doc_text)
        context_parts.append("")
        context_parts.append("---")
        context_parts.append("")
    
    context = "\n".join(context_parts)
    
    # Truncate if max_length is specified
    if max_length and len(context) > max_length:
        logger.warning(f"Context truncated from {len(context)} to {max_length} characters")
        context = context[:max_length] + "\n\n[Content truncated due to length limits...]"
    
    return context


def build_template_instructions(
    template_data: Dict[str, Any],
) -> str:
    """
    Build template instructions from template data.
    
    Args:
        template_data: Template data with letterhead, sections, opening/closing paragraphs
        
    Returns:
        Formatted template instructions string
    """
    instructions = []
    
    instructions.append("## TEMPLATE STRUCTURE")
    instructions.append("")
    
    if template_data.get("letterhead_text"):
        instructions.append("**Letterhead:**")
        instructions.append(template_data["letterhead_text"])
        instructions.append("")
    
    if template_data.get("opening_paragraph"):
        instructions.append("**Opening Paragraph:**")
        instructions.append(template_data["opening_paragraph"])
        instructions.append("")
    
    if template_data.get("sections"):
        sections = template_data["sections"]
        if isinstance(sections, list):
            instructions.append("**Sections to include:**")
            for section in sections:
                instructions.append(f"- {section}")
            instructions.append("")
        else:
            instructions.append(f"**Sections:** {sections}")
            instructions.append("")
    
    if template_data.get("closing_paragraph"):
        instructions.append("**Closing Paragraph:**")
        instructions.append(template_data["closing_paragraph"])
        instructions.append("")
    
    return "\n".join(instructions)


def build_output_format_instructions() -> str:
    """
    Build instructions for HTML output format.
    
    Returns:
        Formatted instructions string
    """
    return """## OUTPUT REQUIREMENTS

Generate a complete demand letter in HTML format. The letter should:
1. Follow the template structure provided above
2. Extract and incorporate relevant information from the source documents
3. Be formatted as clean HTML with appropriate tags (p, h1, h2, h3, strong, em, ul, ol, li)
4. Include the letterhead, opening paragraph, all required sections, and closing paragraph
5. Be professional and legally appropriate

Output only the HTML content of the letter, without any additional explanation or markdown formatting."""


def combine_prompt_components(
    template_data: Dict[str, Any],
    parsed_documents: List[Dict[str, Any]],
    max_context_length: Optional[int] = None,
) -> List[Dict[str, str]]:
    """
    Combine all prompt components into a message list for OpenAI API.
    
    Args:
        template_data: Template data with structure and formatting
        parsed_documents: List of parsed documents with extracted text
        max_context_length: Optional maximum length for document context
        
    Returns:
        List of message dictionaries for OpenAI Chat API
    """
    messages = []
    
    # System prompt
    messages.append({
        "role": "system",
        "content": BASE_SYSTEM_PROMPT,
    })
    
    # Build user prompt
    user_prompt_parts = []
    
    # Template instructions
    user_prompt_parts.append(build_template_instructions(template_data))
    user_prompt_parts.append("")
    
    # Document context
    user_prompt_parts.append("## SOURCE DOCUMENTS")
    user_prompt_parts.append("")
    user_prompt_parts.append(build_context_from_documents(parsed_documents, max_context_length))
    user_prompt_parts.append("")
    
    # Output format instructions
    user_prompt_parts.append(build_output_format_instructions())
    
    user_prompt = "\n".join(user_prompt_parts)
    messages.append({
        "role": "user",
        "content": user_prompt,
    })
    
    return messages


def get_html_formatting_examples() -> str:
    """
    Get examples of expected HTML output format.
    
    Returns:
        Example HTML formatting string
    """
    return """## EXAMPLE OUTPUT FORMAT

Here is an example of the expected HTML structure:

```html
<h1>Letterhead Text</h1>
<p><strong>Opening paragraph text here...</strong></p>

<h2>Section 1 Title</h2>
<p>Section 1 content...</p>

<h2>Section 2 Title</h2>
<p>Section 2 content...</p>

<p><strong>Closing paragraph text here...</strong></p>
```

Use semantic HTML tags appropriately:
- h1, h2, h3 for headings
- p for paragraphs
- strong, em for emphasis
- ul, ol, li for lists
- Keep formatting clean and professional"""

