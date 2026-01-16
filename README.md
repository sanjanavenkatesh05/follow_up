# Clinic Follow-up Tracker (Lite)

A lightweight Django application for managing patient follow-ups in a clinic setting. This project demonstrates core Django concepts including models, authentication, forms, and custom management commands.

## Features

- **Multi-Clinic Support**: Each user belongs to a specific clinic and can only access data relevant to their clinic.
- **Patient Follow-ups**: Track patient details, phone numbers, languages, and due dates.
- **Public View**: A publicly accessible page for patients to view their follow-up status using a secure token.
- **Logging**: Tracks views on the public page (IP address, User Agent, Timestamp).
- **Access Control**: Strict permission checks ensure data isolation between clinics.
- **CSV Import**: A management command to bulk import follow-ups.

## Setup Instructions

### Prerequisites
- Python 3.10+
- pip (Python package manager)

### Installation

1.  **Clone the repository/Extract zip**
    ```bash
    # (Navigate to the project directory)
    cd follow_up
    ```

2.  **Create and Activate Virtual Environment**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run Migrations**
    ```bash
    python manage.py migrate
    ```

5.  **Create a Superuser (Optional, for Admin access)**
    ```bash
    python manage.py createsuperuser
    ```

6.  **Run the Development Server**
    ```bash
    python manage.py runserver
    ```
    Access the app at `http://127.0.0.1:8000/`.

## Usage Guide

### Creating a Clinic & User
Since there is no public registration, you must create clinics and users via the Django Admin or Shell.

**Via Admin Panel:**
1.  Go to `http://127.0.0.1:8000/admin/` and login as superuser.
2.  Create a **Clinic**. `clinic_code` will be auto-generated.
3.  Create a **User** (in Authentication section).
4.  Create a **User Profile**, linking the User to the Clinic.

### Dashboard & Follow-ups
1.  **Login** with the user credentials you created.
2.  **Dashboard**: View all pending and done follow-ups for your clinic. Filter by status or due date.
3.  **Create Follow-up**: Click "Create New Follow-up" to add a patient.
4.  **Edit/Mark Done**: Manage existing follow-ups.

### CSV Import Command
Bulk import follow-ups using a CSV file.

**Command Format:**
```bash
python manage.py import_followups --csv <path_to_csv> --username <username>
```

**Example:**
```bash
python manage.py import_followups --csv sample.csv --username user1
```

**CSV Format:**
The CSV must contain the following headers: `patient_name`, `phone`, `language`, `due_date`, `notes`.
*   `due_date` format: `YYYY-MM-DD`
*   `language`: `en` or `hi`

### Testing
To run the automated test suite ensuring security and functionality:
```bash
python manage.py test tracker
```

## detailed Implementation Notes

### Data Models
-   **Clinic**: Represents a medical facility. Has a unique auto-generated `clinic_code`.
-   **UserProfile**: Extends the default User model to link a user to a `Clinic`.
-   **FollowUp**: The core entity containing patient info. Has a unique `public_token` for external access.
-   **PublicViewLog**: Records every access to a follow-up's public page.

### Security
-   **clinic_code** and **public_token** are generated using Python's `secrets` module for cryptographic strength.
-   **Authorization**: Views explicitly check `request.user.userprofile.clinic` against the object's clinic to prevent unauthorized access.
