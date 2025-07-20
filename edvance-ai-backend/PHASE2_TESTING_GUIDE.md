# 🧪 Phase 2 Testing Guide: Student Assessment System

## 📋 **Complete Testing Workflow**

### **Prerequisites:**
- Server running on: `http://localhost:8000`
- Valid Firebase authentication token
- Students uploaded via Phase 1

---

## 🔄 **Step-by-Step API Testing**

### **Step 1: Health Check** ✅
```bash
curl -X GET "http://localhost:8000/health"
```
**Expected:** `{"status": "healthy", "message": "Service is operational"}`

---

### **Step 2: Get API Documentation** 📚
Open in browser: `http://localhost:8000/docs`

This shows all available endpoints with interactive testing!

---

### **Step 3: Authentication** 🔐
```bash
# Login to get token (replace with real credentials)
curl -X POST "http://localhost:8000/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teacher@example.com",
    "password": "your_password"
  }'
```
**Save the `id_token` from response for next steps!**

---

### **Step 4: Check Your Students** 👥
```bash
# Replace YOUR_TOKEN with the id_token from Step 3
curl -X GET "http://localhost:8000/v1/students/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```
**Expected:** List of students you uploaded in Phase 1

---

### **Step 5: Get Available Topics** 📖
```bash
# Get topics for Mathematics Grade 5
curl -X GET "http://localhost:8000/v1/assessments/topics/Mathematics/5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```
**Expected:** `["Addition", "Subtraction", "Multiplication", "Division", "Fractions"]`

---

### **Step 6: Create Assessment Configuration** ⚙️
```bash
curl -X POST "http://localhost:8000/v1/assessments/configs" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Grade 5 Math Addition Test",
    "subject": "Mathematics",
    "target_grade": 5,
    "difficulty_level": "medium",
    "topic": "Addition",
    "question_count": 5,
    "time_limit_minutes": 15
  }'
```
**Expected:** Assessment config with `config_id` - **SAVE THIS ID!**

---

### **Step 7: List Your Assessment Configs** 📝
```bash
curl -X GET "http://localhost:8000/v1/assessments/configs" \
  -H "Authorization: Bearer YOUR_TOKEN"
```
**Expected:** List including the config you just created

---

### **Step 8: Generate Assessment from Config** 🎯
```bash
# Replace CONFIG_ID with the config_id from Step 6
curl -X POST "http://localhost:8000/v1/assessments/configs/CONFIG_ID/generate" \
  -H "Authorization: Bearer YOUR_TOKEN"
```
**Expected:** Complete assessment with 5 sample math questions - **SAVE THE ASSESSMENT_ID!**

---

### **Step 9: Get Generated Assessment** 📊
```bash
# Replace ASSESSMENT_ID with the assessment_id from Step 8
curl -X GET "http://localhost:8000/v1/assessments/assessments/ASSESSMENT_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```
**Expected:** Full assessment with questions, options, and correct answers

---

### **Step 10: Get Assessment Summary** 📈
```bash
curl -X GET "http://localhost:8000/v1/assessments/summary" \
  -H "Authorization: Bearer YOUR_TOKEN"
```
**Expected:** Summary statistics of your assessments

---

## 🧪 **Expected Results at Each Step:**

### **Step 6 Response Example:**
```json
{
  "config_id": "abc-123-def",
  "teacher_uid": "teacher-456",
  "name": "Grade 5 Math Addition Test",
  "subject": "Mathematics",
  "target_grade": 5,
  "difficulty_level": "medium",
  "topic": "Addition",
  "question_count": 5,
  "time_limit_minutes": 15,
  "created_at": "2025-01-01T12:00:00Z",
  "is_active": true
}
```

### **Step 8 Response Example:**
```json
{
  "assessment_id": "xyz-789-ghi",
  "config_id": "abc-123-def",
  "title": "Addition - Mathematics Grade 5",
  "subject": "Mathematics",
  "grade": 5,
  "difficulty": "medium",
  "topic": "Addition",
  "questions": [
    {
      "question_id": "q1",
      "question_text": "What is 2 + 3?",
      "options": ["4", "5", "6", "7"],
      "correct_answer": 1,
      "explanation": "2 + 3 = 5",
      "difficulty": "medium",
      "topic": "Addition"
    }
    // ... 4 more questions
  ],
  "time_limit_minutes": 15,
  "created_at": "2025-01-01T12:00:00Z"
}
```

---

## 🔧 **Troubleshooting:**

### **401 Unauthorized:**
- Check your token is valid
- Make sure to include `Bearer ` before the token
- Token might have expired, get a new one

### **404 Not Found:**
- Check the endpoint URL
- Verify config_id or assessment_id exists

### **500 Server Error:**
- Check server logs for details
- Firebase/database connection issue

---

## ✅ **Success Criteria:**

After completing all steps, you should have:
1. ✅ Created an assessment configuration
2. ✅ Generated a sample assessment with MCQ questions  
3. ✅ Retrieved the assessment details
4. ✅ Confirmed the assessment contains proper questions with options and answers

---

## 🎯 **What This Proves:**

- **Phase 1**: Student management is working ✅
- **Phase 2**: Assessment configuration and generation is working ✅
- **Ready for Phase 3**: Student assessment taking and scoring! 🚀

---

## 📱 **Next Phase Preview:**

Phase 3 will add:
- Student login endpoints
- Assessment taking interface
- Answer submission and scoring
- Performance analytics
- Learning path generation

**Phase 2 is complete when all 10 steps above work successfully!** 🎉
