# **Setup & Deployment Guide**

Follow these steps to set up the Code Vipassana Validation App in your Google Cloud environment.

## **1\. Google Cloud Project Setup**

1. Create a Project:  
   Go to the Google Cloud Console and create a new project (e.g., cv-validation-project).  
2. Open Cloud Shell:  
   Click the terminal icon in the top right of the console to open Cloud Shell.  
3. Clone/Upload Code:  
   Upload the project files (app.py, requirements.txt, etc.) to Cloud Shell or your local environment.

## **2\. Database Setup (BigQuery)**

1. Create Dataset:  
   Run the following command in the terminal to create the BigQuery dataset:

```

bq --location=US mk -d \
    --description "Code Vipassana Validation Data" \
    cv_validation

```

4.   
   Create Tables:  
   You can run the provided SQL script using the bq command line tool or via the BigQuery Console.  
   **Option A: Command Line**

```

bq query --use_legacy_sql=false < setup_db.sql

```

7. **Option B: BigQuery Console**  
   1. Go to BigQuery in the Cloud Console.  
   2. Click "Compose New Query".  
   3. Paste the contents of setup\_db.sql.  
   4. Click "Run".

## **3\. Deployment to Cloud Run**

We have provided a helper script deploy.sh to automate the deployment.

1. **Make the script executable:**

```

chmod +x deploy.sh

```

4.   
   Run the deployment:  
   Replace YOUR\_PROJECT\_ID with your actual GCP project ID. You can optionally specify a region (defaults to us-central1).

```

./deploy.sh YOUR_PROJECT_ID us-central1

```

7.   
   Access the App:  
   Once the script finishes, it will output a Service URL (e.g., https://cv-vipassana-app-xyz-uc.a.run.app). Click this link to access your app.

## **4\. Initial Login**

1. Navigate to the Service URL.  
2. Log in with the default Owner credentials created by the database script:  
   * **Username:** ________ 
   * **Password:** ______ 

## **5\. Post-Deployment Configuration**

1. **Add a Season:** Go to the Owner Dashboard and create your first Season and Session configuration.  
2. **Generate Developers:** Use the "Generate Credentials" feature to create accounts for your participants.

## **Troubleshooting**

* **500 Internal Server Error:** Check the Cloud Run logs tab in the console. It usually indicates a missing environment variable or permission issue.  
* **Database Errors:** Ensure the Service Account used by Cloud Run (usually the default compute service account) has BigQuery Data Editor and BigQuery User roles.  
* **AI Errors:** Ensure the Vertex AI API is enabled in your project.
