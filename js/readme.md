# Student Performance Analyzer (JavaScript)

##  What the Program Does

The program takes student data (marks + attendance) and performs the following:

- Calculates total marks for each student
- Calculates average marks
- Finds highest scorer in each subject
- Computes subject-wise average scores
- Identifies the class topper
- Assigns grades based on performance and conditions

---

##  Logic

I used:

- Array of objects → to store student data
- Nested loops → to go through subjects
- Functions → to break logic into reusable parts
- Conditions → for grade calculation and fail rules

Instead of writing everything in one block, I divided logic into small functions to make it easier to debug and understand.

---

##  Grade Rules Implemented

- A → 85 and above  
- B → 70 to 84  
- C → 50 to 69  
- Fail → below 50  

Additional fail conditions:
- If any subject ≤ 40  
- If attendance < 75  

