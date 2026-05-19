"""
文档加载器使用示例
"""

from PDFLoader import PDFDocumentLoader
from TextLoader import TextDocumentLoader
from WordLoader import WordDocumentLoader
from UniversalLoader import UniversalDocumentLoader
from BatchLoader import BatchDocumentLoader


def example_pdf_loader():
    """PDF加载器使用示例"""
    print("=== PDF加载器示例 ===")
    
    loader = PDFDocumentLoader(
        file_path="data/sample.pdf",
        chunk_size=1000,
        chunk_overlap=200
    )
    
    splits = loader.load_and_split()
    
    if splits:
        print(f"\n第一个文档块内容:\n{splits[0].page_content[:200]}...")
        print(f"\n元数据: {splits[0].metadata}")
    
    metadata = loader.get_metadata()
    print(f"\n文档元数据: {metadata}")


def example_text_loader():
    """文本加载器使用示例"""
    print("\n=== 文本加载器示例 ===")
    
    loader = TextDocumentLoader(
        file_path="data/sample.txt",
        chunk_size=800,
        chunk_overlap=150
    )
    
    splits = loader.load_and_split()
    
    if splits:
        print(f"\n第一个文档块内容:\n{splits[0].page_content[:200]}...")
    
    metadata = loader.get_metadata()
    print(f"\n文档元数据: {metadata}")


def example_word_loader():
    """Word加载器使用示例"""
    print("\n=== Word加载器示例 ===")
    
    loader = WordDocumentLoader(
        file_path="data/sample.docx",
        chunk_size=1000,
        chunk_overlap=200
    )
    
    splits = loader.load_and_split()
    
    if splits:
        print(f"\n第一个文档块内容:\n{splits[0].page_content[:200]}...")


def example_universal_loader():
    """通用加载器使用示例"""
    print("\n=== 通用加载器示例 ===")
    
    file_paths = [
        "data/sample.pdf",
        "data/sample.txt",
        "data/sample.docx"
    ]
    
    for file_path in file_paths:
        try:
            loader = UniversalDocumentLoader(
                file_path=file_path,
                chunk_size=1000,
                chunk_overlap=200
            )
            
            splits = loader.load_and_split()
            print(f"\n文件 {file_path}: 生成 {len(splits)} 个文档块")
            
        except Exception as e:
            print(f"\n加载文件 {file_path} 失败: {e}")


def example_batch_loader():
    """批量加载器使用示例"""
    print("\n=== 批量加载器示例 ===")
    
    batch_loader = BatchDocumentLoader(
        directory_path="data/documents",
        chunk_size=1000,
        chunk_overlap=200,
        max_workers=4
    )
    
    stats = batch_loader.get_directory_stats()
    print(f"目录统计: {stats}")
    
    all_splits = batch_loader.load_all_documents()
    
    print(f"\n总共加载 {len(all_splits)} 个文档块")


if __name__ == "__main__":
    # example_pdf_loader()
    # example_text_loader()
    # example_word_loader()
    # example_universal_loader()
    example_batch_loader()
