import asyncio
import zipfile
import io
from app.services.document_service import document_service

class MockUploadFile:
    def __init__(self, filename: str, content: bytes, content_type: str):
        self.filename = filename
        self.content_type = content_type
        self.file = io.BytesIO(content)
        self.size = len(content)
    
    async def read(self, size: int = -1) -> bytes:
        return self.file.read(size)
    
    def seek(self, offset: int, whence: int = 0):
        return self.file.seek(offset, whence)

async def create_test_zip():
    """Create a test ZIP file with multiple documents."""
    # Create a ZIP file in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add multiple test files with different types
        zip_file.writestr("lesson1.txt", "This is lesson 1 about Python basics and variables.")
        zip_file.writestr("lesson2.txt", "This is lesson 2 about Python functions and loops.")
        zip_file.writestr("assignment.txt", "Assignment: Create a program that calculates grades.")
        zip_file.writestr("notes/week1.txt", "Week 1 notes on programming fundamentals.")
        zip_file.writestr("notes/week2.txt", "Week 2 notes on data structures.")
        
        # Add some files that should be skipped
        zip_file.writestr("large_file.xyz", "x" * (60 * 1024 * 1024))  # Too large (60MB)
        zip_file.writestr("unsupported.exe", "This is an executable file")  # Unsupported type
        zip_file.writestr(".hidden_file", "This is a hidden file")  # Hidden file
        zip_file.writestr("__MACOSX/._metadata", "Mac metadata")  # Mac system file
    
    zip_content = zip_buffer.getvalue()
    return zip_content

async def test_zip_upload():
    print("Creating test ZIP file...")
    zip_content = await create_test_zip()
    
    # Create mock ZIP upload file
    zip_file = MockUploadFile(
        filename="computer_science_materials.zip",
        content=zip_content,
        content_type="application/zip"
    )
    
    try:
        print("Testing ZIP file upload and extraction...")
        
        # Test ZIP upload
        result = await document_service.upload_document(
            file=zip_file,
            subject="Computer Science",
            teacher_uid="test_teacher_123"
        )
        
        print("ZIP Upload Result:")
        print(f"  ZIP Filename: {result.zip_filename}")
        print(f"  ZIP File Size: {result.zip_file_size} bytes")
        print(f"  Total Files Found: {result.total_files_found}")
        print(f"  Files Processed: {result.files_processed}")
        print(f"  Files Skipped: {result.files_skipped}")
        print(f"  Files Failed: {result.files_failed}")
        print(f"  Upload Status: {result.upload_status}")
        print(f"  Subject: {result.subject}")
        
        print(f"\nExtracted Files Details:")
        for i, file_info in enumerate(result.extracted_files, 1):
            print(f"  {i}. {file_info.filename}")
            print(f"     Status: {file_info.extraction_status}")
            print(f"     Document ID: {file_info.document_id}")
            print(f"     File Size: {file_info.file_size} bytes")
            print(f"     File Type: {file_info.file_type}")
            if file_info.storage_url:
                print(f"     Storage URL: {file_info.storage_url}")
            if file_info.error_message:
                print(f"     Error: {file_info.error_message}")
            print()
        
        # Summary
        print(f"Summary: {result.files_processed}/{result.total_files_found} files successfully processed")
        if result.files_skipped > 0:
            print(f"  {result.files_skipped} files were skipped (unsupported type or too large)")
        if result.files_failed > 0:
            print(f"  {result.files_failed} files failed to process")
        
        # Wait for background processing
        print("\nWaiting for background indexing...")
        await asyncio.sleep(5)
        
        print("\nZIP extraction and indexing completed!")
        
    except Exception as e:
        print(f"Error during ZIP upload: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_zip_upload())
