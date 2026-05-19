# config/loader_config.py
"""
文档加载器配置

包含所有文档加载器的配置参数
"""

# PDF加载器配置
PDF_LOADER_CONFIG = {
    'chunk_size': 1000,
    'chunk_overlap': 200,
    'separators': ["\n\n", "\n", " ", ""],
}

# 文本加载器配置
TEXT_LOADER_CONFIG = {
    'chunk_size': 1000,
    'chunk_overlap': 200,
    'separators': ["\n\n", "\n", " ", ""],
    'default_encoding': 'utf-8',  # 编码检测失败时的默认编码
}

# Word加载器配置
WORD_LOADER_CONFIG = {
    'chunk_size': 1000,
    'chunk_overlap': 200,
    'separators': ["\n\n", "\n", " ", ""],
    'supported_extensions': ['.docx'],  # 支持的Word文件格式
}

# 通用加载器配置
UNIVERSAL_LOADER_CONFIG = {
    'chunk_size': 1000,
    'chunk_overlap': 200,
    'supported_extensions': {
        '.pdf': 'pdf',
        '.txt': 'text',
        '.docx': 'word',
        '.md': 'text',
        '.csv': 'text',
        '.json': 'text',
    },
}

# 批量加载器配置
BATCH_LOADER_CONFIG = {
    'chunk_size': 1000,
    'chunk_overlap': 200,
    'max_workers': 4,  # 最大并行工作线程数
    'supported_extensions': {'.pdf', '.txt', '.docx', '.md', '.csv', '.json'},
}

# 完整的加载器配置字典
LOADER_CONFIG = {
    'pdf': PDF_LOADER_CONFIG,
    'text': TEXT_LOADER_CONFIG,
    'word': WORD_LOADER_CONFIG,
    'universal': UNIVERSAL_LOADER_CONFIG,
    'batch': BATCH_LOADER_CONFIG,
}
