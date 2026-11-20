# How to Run Sujhav साथी Independently (Offline & Without AI)

**Author:** Sahil Kumar | **College:** IIT Patna (3rd Year) | **Internship:** Codec Technologies  
**Project Folder:** `C:\Users\dell\Downloads\E-commere Recommendation System`

---

## ⚡ Method 1: The Easiest 1-Click Method (Recommended)

In your project folder, you have two batch scripts:

1. **Double-click `run_backend.bat`**
   * A black command prompt window will open.
   * You will see: `Recommender successfully loaded: 17665 products... Running on http://127.0.0.1:5000`.
   * **Keep this window open!**

2. **Double-click `run_frontend.bat`**
   * A second command prompt window will open.
   * You will see: `VITE ready in ... http://localhost:5173/`.
   * **Keep this window open!**

3. **Open Your Browser:**
   * Go to: **[http://localhost:5173/](http://localhost:5173/)**
   * The complete Sujhav साथी app is now running!

---

## 💻 Method 2: Manual Terminal Commands (PowerShell / CMD / VS Code)

You need **two terminal tabs/windows**:

### Terminal 1 (Start Flask Backend):
```powershell
cd "C:\Users\dell\Downloads\E-commere Recommendation System"
python backend\app.py
```
*Wait until it prints:* `Running on http://127.0.0.1:5000`

---

### Terminal 2 (Start React Frontend):
```powershell
cd "C:\Users\dell\Downloads\E-commere Recommendation System\frontend"
npm run dev
```
*Wait until it prints:* `Local: http://localhost:5173/`

---

### Open in Browser:
Visit: `http://localhost:5173/`

---

## 🔄 How to Setup on a Fresh Computer (or If Moved)

If you copy this folder to another PC or upload it to GitHub and clone it:

### Step 1: Install Python & Node.js
* Download & install **Python 3.10+** (check "Add Python to PATH" during install).
* Download & install **Node.js (LTS)** from [nodejs.org](https://nodejs.org/).

### Step 2: Install Backend Dependencies
Open PowerShell in the project root folder:
```powershell
pip install -r backend\requirements.txt
```

### Step 3: Install Frontend Dependencies
```powershell
cd frontend
npm install
cd ..
```

### Step 4: Run the System
```powershell
# In Terminal 1:
python backend\app.py

# In Terminal 2:
cd frontend
npm run dev
```

---

## 📂 Key Project Files for Your Internship & Viva
* **Main Project Report:** `PROJECT_REPORT.md` (Detailed 13-step pipeline, ML math, and evaluation)
* **Interview & Viva Q&A:** `INTERVIEW_AND_VIVA_QUESTIONS.md` (25+ viva questions with answers)
* **Project README:** `README.md` (Complete architecture & portfolio guide)
* **API Collection:** `backend\postman_collection.json` (For Postman API testing)
* **Backend Source:** `backend\app.py` & `backend\models\recommender.py`
* **Frontend Source:** `frontend\src\` (React components, pages, charts)
