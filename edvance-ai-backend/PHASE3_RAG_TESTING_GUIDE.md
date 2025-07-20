# 🚀 Phase 3 Testing Guide: RAG + Agentic Assessment System

## 📋 **Complete RAG Testing Workflow**

### **Prerequisites:**
- Server running on: `http://localhost:8000`
- Valid Firebase authentication token
- Phase 1 & 2 completed successfully
- Documents ready for upload (PDF, DOCX, or TXT)

---

## 🔄 **Step-by-Step RAG Testing**

### **Step 1: Health Check** ✅
```bash
curl -X GET "http://localhost:8000/health"
```
**Expected:** `{"status": "healthy", "message": "Service is operational"}`

---

### **Step 2: Authentication** 🔐
```bash
# Login to get token
curl -X POST "http://localhost:8000/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teacher@example.com", 
    "password": "your_password"
  }'
```
**Save the `id_token` for all subsequent requests!**

---

### **Step 3: Upload Document for RAG** 📄
```bash
# Upload a PDF, DOCX, or TXT file
curl -X POST "http://localhost:8000/v1/assessments/rag/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/your/document.pdf" \
  -F "subject=Mathematics" \
  -F "grade_level=5"
```

**Expected Response:**
```json
{
  "document_id": "doc_teacher123_1640995200",
  "filename": "math_textbook.pdf", 
  "processing_status": "completed",
  "message": "Document uploaded and processed successfully. Created 45 text chunks."
}
```
**📝 SAVE THE `document_id` for tracking!**

---

### **Step 4: Check Document Processing** 📊
```bash
# Get all your uploaded documents
curl -X GET "http://localhost:8000/v1/assessments/rag/documents" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected:** List of processed documents with chunk counts and status

---

### **Step 5: Get Document Details** 🔍
```bash
# Check specific document processing details
curl -X GET "http://localhost:8000/v1/assessments/rag/documents/DOCUMENT_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected:** Detailed processing info including chunk count and status

---

### **Step 6: Search Your Content** 🔎
```bash
# Test semantic search through your uploaded content
curl -X POST "http://localhost:8000/v1/assessments/rag/content/search" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "search_query": "addition problems",
    "subject_filter": "Mathematics",
    "grade_filter": 5
  }'
```

**Expected:** Relevant text chunks from your documents with similarity scores

---

### **Step 7: Create Assessment Config** ⚙️
```bash
# Create config for RAG-based assessment
curl -X POST "http://localhost:8000/v1/assessments/configs" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "RAG Math Test - Addition",
    "subject": "Mathematics", 
    "target_grade": 5,
    "difficulty_level": "medium",
    "topic": "Addition",
    "question_count": 5,
    "time_limit_minutes": 20
  }'
```
**📝 SAVE THE `config_id` from response!**

---

### **Step 8: Generate RAG Assessment** 🤖
```bash
# Generate AI-powered assessment from your documents
curl -X POST "http://localhost:8000/v1/assessments/rag/configs/CONFIG_ID/generate-rag" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Response:**
- Assessment with AI-generated questions
- Questions based on your uploaded document content
- Contextually relevant to the specified topic and grade
- **📝 SAVE THE `assessment_id`!**

---

### **Step 9: Get RAG Assessment Details** 📋
```bash
# Get the generated assessment
curl -X GET "http://localhost:8000/v1/assessments/assessments/ASSESSMENT_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected:** Complete assessment with questions generated from your document content

---

### **Step 10: Get RAG Metadata** 🔬
```bash
# Get detailed generation metadata
curl -X GET "http://localhost:8000/v1/assessments/rag/assessments/ASSESSMENT_ID/metadata" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response:**
```json
{
  "assessment_id": "xyz-789",
  "generation_method": "rag_enhanced",
  "rag_metadata": {
    "context_chunks_used": 3,
    "ai_generated_questions": 5,
    "context_sources": [
      {
        "chunk_id": "chunk_123",
        "similarity_score": 0.87,
        "source_file": "math_textbook.pdf"
      }
    ]
  }
}
```

---

### **Step 11: Get RAG Analytics** 📈
```bash
# Get your RAG usage statistics
curl -X GET "http://localhost:8000/v1/assessments/rag/analytics/rag-stats" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected:** Statistics about your uploaded content, chunk counts, subjects, and grades

---

## 🧪 **Expected RAG Improvements**

### **Compared to Phase 2 Simple Templates:**

#### **Phase 2 Output Example:**
```json
{
  "question_text": "What is 2 + 3?",
  "options": ["4", "5", "6", "7"],
  "correct_answer": 1,
  "explanation": "2 + 3 = 5"
}
```

#### **Phase 3 RAG Output Example:**
```json
{
  "question_text": "Based on the fraction addition methods in Chapter 4, what is 1/4 + 1/8?",
  "options": ["2/12", "3/8", "2/8", "1/12"],
  "correct_answer": 1,
  "explanation": "To add fractions with different denominators, find the common denominator. The LCD of 4 and 8 is 8. Convert 1/4 to 2/8, then add: 2/8 + 1/8 = 3/8."
}
```

### **Key Improvements:**
1. **📚 Content-Based**: Questions derived from actual textbook content
2. **🎯 Contextual**: References specific chapters/sections from uploads
3. **🧠 Intelligent**: AI understands grade-appropriate complexity
4. **📖 Educational**: Explanations based on source material methodology
5. **🔄 Dynamic**: Questions change based on uploaded content

---

## 🔧 **Troubleshooting RAG Issues**

### **Document Upload Fails:**
- Check file format (PDF/DOCX/TXT only)
- Ensure file size < 50MB
- Verify sufficient storage space

### **No Questions Generated:**
- Check if document processing completed successfully
- Verify document contains relevant content for the topic
- Try with force_rag=false for fallback to simple generation

### **Poor Question Quality:**
- Upload more comprehensive source materials
- Ensure documents match the subject and grade level
- Try different topics that align better with uploaded content

### **Vector Search Returns No Results:**
- Check spelling in search queries
- Try broader search terms
- Verify documents were processed successfully

---

## ✅ **Success Criteria for Phase 3**

After completing all steps, you should have:

1. ✅ **Document Processing**: Successfully uploaded and processed documents into text chunks
2. ✅ **Semantic Search**: Found relevant content through similarity search
3. ✅ **RAG Generation**: Created assessment with questions based on your uploaded content
4. ✅ **Quality Questions**: AI-generated questions that reference your source material
5. ✅ **Metadata Tracking**: Detailed information about how questions were generated

---

## 🎯 **What Phase 3 Achieves**

- **🤖 AI-Powered**: Questions generated by advanced language models
- **📚 Document-Based**: Content derived from teacher's actual materials
- **🎯 Contextual Relevance**: Questions match uploaded content and grade level
- **🔍 Searchable Content**: Teachers can search through their uploaded materials
- **📊 Analytics**: Detailed insights into content usage and generation process
- **🚀 Scalable**: System grows with more uploaded content

---

## 📱 **Next Steps: Phase 4 Preview**

Phase 4 will add:
- **Student Assessment Interface**: Students can take RAG-generated assessments
- **Adaptive Scoring**: AI-powered answer evaluation and partial credit
- **Learning Path Generation**: Personalized recommendations based on performance
- **Real-time Analytics**: Live performance dashboards
- **Multi-modal Content**: Support for images, diagrams, and multimedia questions

**Phase 3 is complete when all 11 RAG steps work successfully!** 🎉

---

## 🔄 **Quick Test Sequence**

For rapid testing, run this sequence:

1. Login → 2. Upload Document → 3. Wait for Processing → 4. Create Config → 5. Generate RAG Assessment → 6. Verify Questions Reference Your Content

**Total Time: ~2-3 minutes for a small document**
