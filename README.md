# **Code Vipassana Result Validation App**

A Flask-based application for managing code lab result submissions, validating screenshots using Vertex AI (Gemini), and managing developer leaderboards.

## **Features**

### **For Owners**

* **Season Management:** Create seasons and sessions with validation criteria (start/end dates, codelab links, expected result descriptions).  
* **Credential Generation:** Bulk generate unique username/password pairs for developers (up to 50,000 at a time) and download as CSV.  
* **Leaderboard:** View developer rankings based on successful submissions.

### **For Developers**

* **Dashboard:** View active seasons and assigned sessions.  
* **Submission:** Upload screenshots for validation.  
* **AI Validation:** Real-time validation of uploaded screenshots against the owner's description using Gemini 1.5 Flash.  
* **Stats:** View personal stats (Score and Seasons participated).  
* **Retry Logic:** 5-attempt limit with automatic intervention requests upon failure.

## **Tech Stack**

* **Backend:** Python Flask  
* **Database:** Google BigQuery  
* **AI/Validation:** Google Vertex AI (Gemini 1.5 Flash)  
* **Deployment:** Google Cloud Run

## **Prerequisites**

* Google Cloud Project with Billing Enabled.  
* gcloud CLI installed and configured.  
* APIs Enabled: Vertex AI, BigQuery, Cloud Run, Artifact Registry.
