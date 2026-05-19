# config/cleaning_config.py
"""
文档清洗配置

包含文档清洗和分块的所有配置参数
"""

# 页眉页脚匹配模式（正则表达式）
HEADER_FOOTER_PATTERNS = [
    r'^\s*第\s*\d+\s*页\s*/\s*共\s*\d+\s*页\s*$',  # "第 X 页 / 共 Y 页"
    r'^\s*\d+\s*/\s*\d+\s*$',                       # "X / Y"
    r'^\s*Page\s*\d+\s*of\s*\d+\s*$',               # "Page X of Y"
    r'^\s*-\s*\d+\s*-\s*$',                         # "- X -"
    r'^\s*\d+\s*$',                                 # 单独的行号
    r'^\s*版权所有.*$',                             # 版权信息
    r'^\s*Copyright.*$',                            # 英文版权
    r'^\s*CONFIDENTIAL.*$',                         # 机密标记
]

# 乱码字符匹配模式（正则表达式）
GARBLED_PATTERNS = [
    r'□+',           # 方框字符
    r'\ufffd+',      # Unicode 替换字符 
    r'[^\x00-\x7F\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\s.,;:!?()""''\-—]+',  # 非中英文标点的特殊字符
    r'\x00',         # 空字符
]

# 文本分割符（按优先级排序）
TEXT_SEPARATORS = [
    "\n\n",    # 双换行（段落分隔）
    "\n",      # 单换行
    "。",      # 中文句号
    "！",      # 中文感叹号
    "？",      # 中文问号
    "；",      # 中文分号
    "，",      # 中文逗号
    " ",       # 空格
    ""         # 字符级别
]

# 默认分块参数
DEFAULT_CHUNK_SIZE = 800          # 默认文本块大小（建议范围：500-1000）
DEFAULT_CHUNK_OVERLAP = 150       # 默认文本块重叠（建议范围：100-200）

# 清洗功能开关默认值
DEFAULT_REMOVE_EXTRA_BLANK_LINES = True   # 是否去除多余空行
DEFAULT_REMOVE_GARBLED_TEXT = True        # 是否清理乱码
DEFAULT_REMOVE_HEADER_FOOTER = True       # 是否去除页眉页脚

# 完整的清洗配置字典
CLEANING_CONFIG = {
    'chunk_size': DEFAULT_CHUNK_SIZE,
    'chunk_overlap': DEFAULT_CHUNK_OVERLAP,
    'separators': TEXT_SEPARATORS,
    'header_footer_patterns': HEADER_FOOTER_PATTERNS,
    'garbled_patterns': GARBLED_PATTERNS,
    'remove_extra_blank_lines': DEFAULT_REMOVE_EXTRA_BLANK_LINES,
    'remove_garbled_text': DEFAULT_REMOVE_GARBLED_TEXT,
    'remove_header_footer': DEFAULT_REMOVE_HEADER_FOOTER,
}
