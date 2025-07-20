import asyncio
from app.services.document_service import document_service
from fastapi import UploadFile
import io

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

async def test_upload():
    # Create test content
    test_content = b'This is a test document for indexing in Vertex AI Search. It contains educational content about programming concepts.'
    
    # Create a mock UploadFile
    upload_file = MockUploadFile(
        filename='/Users/km/Desktop/adv_react.pdf',
        content=test_content,
        content_type='text/plain'
    )
    
    try:
        # Test document upload
        result = await document_service.upload_document(
            file=upload_file,
            subject='Computer Science',
            teacher_uid='test_teacher_123'
        )
        
        print('Upload result:')
        print(f'  Document ID: {result.document_id}')
        print(f'  Filename: {result.filename}')
        print(f'  Storage URL: {result.storage_url}')
        print(f'  Upload status: {result.upload_status}')
        
        # Check if indexing task ID exists (it might not be in the response model)
        if hasattr(result, 'indexing_task_id') and result.indexing_task_id:
            print(f'  Indexing task ID: {result.indexing_task_id}')
        else:
            print('  Background indexing started (no task ID in response)')
        
        # Wait a moment for background processing
        import time
        time.sleep(3)
        
        # Check indexing status
        status = await document_service.get_indexing_status(result.document_id)
        print(f'  Indexing status: {status}')
        
    except Exception as e:
        print(f'Error during upload: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_upload())
