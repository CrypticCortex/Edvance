import asyncio
from app.services.vertex_rag_service import vertex_rag_service

async def test_search():
    print("Testing Vertex AI Search functionality...")
    
    try:
        # Search for documents
        results = await vertex_rag_service.search_documents(
            query="react",
            teacher_uid="test_teacher_123",
            subject_filter="Computer Science",
            limit=5
        )
        
        print(f"Search Results ({len(results)} found):")
        for i, result in enumerate(results, 1):
            print(f"  {i}. Document ID: {result['document_id']}")
            print(f"     Title: {result['title']}")
            print(f"     Subject: {result['subject']}")
            print(f"     Snippet: {result['snippet']}")
            print(f"     Relevance: {result['relevance_score']}")
            print()
        
        if not results:
            print("No results found. This might be normal if documents are still being indexed.")
        
    except Exception as e:
        print(f"Error during search: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_search())
