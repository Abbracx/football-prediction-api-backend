# football-prediction-api-backend

This project is a backend for a football prediction API. It is built using Django,  and is designed to provide a platform for making predictions about football matches.

### Main Function Points
Provides a backend API for making football predictions
Allows users to access and analyze data related to football matches
Supports features such as user authentication, data storage, and API endpoints

### Technology Stack
Python
Django
Docker
Docker Compose

Here are the steps to install the **Football Prediction API Backend**:

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Abbracx/football-prediction-api-backend.git
   cd football-prediction-api-backend
   ```

2. **Set Up a Virtual Environment**
   It is recommended to use a virtual environment to manage dependencies.
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   Install the required packages using pip.
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Database**
   Make sure to configure your database settings in the `base.py` or `development.py` file. You may need to create a database and update the connection details.

5. **Run Migrations**
   Apply database migrations to set up the initial database schema.
   
   ```bash
   python manage.py makemigrations users
   ```

   ```bash
   python manage.py makemigrations league
   ```

   ```bash
   python manage.py migrate
   ```

6. **Create a Superuser**
   (Optional) Create an admin user to access the admin panel.
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the Server**
   Start the Django development server.
   ```bash
   python manage.py runserver
   ```

8. **Access the API**
   You can now access the API at `http://127.0.0.1:8000/`.

### Additional Notes
- Ensure you have Docker and Docker Compose installed if you wish to run the application in a containerized environment.
- Refer to the project documentation for specific configurations and advanced settings.

Feel free to ask if you need further assistance!
