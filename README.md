# PACExplorer
An educational game using data from NASA's PACE Mission

2024 NASA Space Apps Challenge - Kaohsiung
`#PACE #NASA #Plankton #Aerosol #Cloud #Ocean #Ecosystem`


## Development
Suggested Python version is: `3.9`

### Clone the project

```bash
git clone https://github.com/heyaustin/PACExplorer.git
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Setup environmental variables

Run the following Python codes and record `secret_key`
```python
from django.core.management.utils import get_random_secret_key
secret_key = get_random_secret_key()
print(secret_key)
```

Create `.env` file and add the following variables, where `Django_SECRET_KEY` is the `secret_key` you just generated.
```bash
Django_SECRET_KEY=secret_key

secret=""
client_id=""

DEV=""
```

### Run the project

Run DB migration
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```
Run server
```bash
python3 manage.py runserver
```

### Open the game website

Enter the following url in the browser

```bash
http://localhost:8000/
```

## Purpose of folders

- base - Main web development
  - api - API settings (Our website currently does not support RESTful)
  - migrations - Update the database
  - template - To override the front-end componenets in the folder `templates` in the main directory
  - models.py - Database settings
  - forms.py - To override the default form format of Django 
  - admin.py - Settings of the backend monitor system
  - urls.py - Set up valid URL and the corresponding view functions
  - views.py - Website core logic implementation
- pace - Backend settings
- template - Web templates to be overridden by files in base/template
- static - Include static resources, such as images, audio, .css, .js, fonts
...

## Required dependencies

Please see `requirements.txt` for more details

- django v4.2.1
- pillow v10.0.0
- line-bot-sdk v3.2.0
- Bootstrap v5.1.3
- python-dotenv v0.21.0
...

## Contributors
- Austin
- Will Cheng
- YuehHsi
- Favicon: <a href="https://www.freepik.com/icon/travel_12694655">Icon by Ylivdesign</a>
