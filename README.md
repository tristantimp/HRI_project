# **Companion Robot That Adapts Through Cognitive Play**  
### *Human-Robot Interaction for Social Robots (2024/2025)*  

This repository contains the code for our final project, which focuses on creating a companion robot capable of:  
1. **Conversing** with the user.  
2. **Evaluating** their cognitive level.  
3. **Selecting and initiating** a game tailored to that cognitive level.  

---

## **Setup Instructions**  

### **1. API Key Configuration**  
The project uses the ChatGPT API for conversational abilities.  
- Navigate to the file: `utils/extra.py`.  
- Replace the placeholder with your ChatGPT API key.  

```python   
api_key = "your_api_key_here"  
```

### **2. Run Main**  
Install the packages in requirements.txt and run the main script with
```python   
pip install -r requirements.txt
python main.py  
```