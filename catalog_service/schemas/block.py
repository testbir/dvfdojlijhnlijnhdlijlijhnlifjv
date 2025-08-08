# catalog_service/schemas/block.py

from pydantic import BaseModel, validator
from typing import Optional

# Поддерживаемые языки программирования
SUPPORTED_LANGUAGES = {
    'python': 'Python',
    'javascript': 'JavaScript',
    'typescript': 'TypeScript', 
    'tsx': 'TypeScript React',
    'jsx': 'JavaScript React',
    'html': 'HTML',
    'css': 'CSS',
    'scss': 'SCSS',
    'sass': 'Sass',
    'sql': 'SQL',
    'json': 'JSON',
    'xml': 'XML',
    'yaml': 'YAML',
    'bash': 'Bash',
    'shell': 'Shell',
    'java': 'Java',
    'csharp': 'C#',
    'cpp': 'C++',
    'c': 'C',
    'go': 'Go',
    'rust': 'Rust',
    'php': 'PHP',
    'ruby': 'Ruby',
    'swift': 'Swift',
    'kotlin': 'Kotlin',
    'markdown': 'Markdown',
    'dockerfile': 'Dockerfile',
    'plaintext': 'Plain Text'
}

class ContentBlockSchema(BaseModel):
    id: int
    title: Optional[str]
    type: str
    content: str
    order: int
    video_preview: Optional[str] = None
    language: Optional[str] = None  # Новое поле

    class Config:
        orm_mode = True
        
        
class ContentBlockCreateSchema(BaseModel):
    type: str  # text, video, code, image
    title: str
    content: str
    order: int
    video_preview: Optional[str] = None
    language: Optional[str] = None  # Новое поле
    
    @validator('language')
    def validate_language(cls, v, values):
        # Валидация только для блоков типа 'code'
        if values.get('type') == 'code' and v and v not in SUPPORTED_LANGUAGES:
            raise ValueError(f'Unsupported language. Choose from: {", ".join(SUPPORTED_LANGUAGES.keys())}')
        return v


class BlockOrderUpdate(BaseModel):
    block_id: int
    order: int
