# Streamlit Application Template

This repository provides a **ready-to-use Streamlit application template** designed to help you focus on **integrating your pages and features** rather than spending time on setting up the basic structure, sidebars, or hiding default Streamlit features. Everything is already set up for you!

## Features

- **Pre-configured Sidebar Menu**: A customizable sidebar menu is already implemented using `streamlit-option-menu`.
- **Hidden Default Features**: The default Streamlit features (like the deploy button, main menu, and footer) are hidden for a cleaner UI.
- **Modular Structure**: The application is organized into a modular structure with separate folders for pages (`app_pages`) and utilities (`utils`).
- **Google Analytics Integration**: Optional Google Analytics integration is included.
- **Virtual Environment Setup**: Easy setup with a virtual environment and `requirements.txt`.

## Project Structure

Here’s how the project is organized:

my_streamlit_app/

│
├── main.py

├── app_pages/ # Contains all the pages of the application
│ ├── init.py
│ ├── home.py
│ ├── account.py
│ ├── chat.py
│ ├── files.py
│ ├── model_selector.py
│ └── newpage.py
└── utils/ # Contains utility functions and configurations
├── init.py
├── streamlit_style.py # Custom styles to hide default Streamlit features
└── analytics.py # Google Analytics integration

## Getting Started

Follow these steps to set up and run the application on your local machine.

### Step 1: Create a Virtual Environment

Create a virtual environment to isolate the project dependencies:

```bash
python -m venv your-name

```

Step 2: Activate the Virtual Environment
Activate the virtual environment:

On Windows:

```bash

.\venv\Scripts\activate

```
On macOS/Linux:

```bash

source venv/bin/activate

```

Step 3: Install Dependencies
Install the required dependencies using pip:

```bash

pip install -r requirements.txt

```


Step 4: Run the Application
Start the Streamlit application:

```bash

streamlit run main.py

```

Customization
Adding New Pages
To add a new page:

Create a new Python file in the app_pages folder (e.g., new_page.py).

Define a function app() in the file that contains the page content.

Import the page in main.py and add it to the MultiApp class:

python
```bash

from app_pages import new_page

multi_app.add_app("New Page", new_page.app)

```
Hiding Default Streamlit Features
The default Streamlit features (like the deploy button and main menu) are hidden using custom CSS in utils/streamlit_style.py. You can modify this file to customize the styles further.

Google Analytics Integration
To enable Google Analytics:

Add your Google Analytics tag to the .env file:

```bash

analytics_tag=UA-XXXXXXXXX-X

```
The script will be automatically injected into the application.

Why Use This Template?
Save Time: No need to set up the basic structure or hide default Streamlit features.

Focus on Integration: Spend your time integrating your pages and features instead of configuring the app.

Modular and Scalable: The project is organized into modules, making it easy to scale and maintain.