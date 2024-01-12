# Edlight Senior Fullstack Programmer Application - Task


## Installation

To run the application you'll need to following:
1. [Docker Desktop](https://www.docker.com/products/docker-desktop/) - This application is packaged using `docker compose` to make it easy to get it up and running regardless of your operating system. 
2. An OpenAI API Account with credits and an `API Key` (OPTIONAL) -  This application uses OpenAI's GPT-4V to analyze images and generate a description of their contents.  
    1. You can create an OpenAI API account at https://platform.openai.com/signup.
    2. Once you have an account you can generate an API key at https://platform.openai.com/api-keys
    3. Lastly, you'll need to add funds to your account at https://platform.openai.com/account/billing/overview.  A few dollars should be more than enough to test this application.

    If you do not wish to create or fund an OpenAI account, this application will generate dummy descriptions for the purposes of testing.  More on that below.


To get the application up and running (command-line snippets are for Mac and Linux from within this directory):
1. Copy `.env.example` to `.env`
    ```
    $ cp .env.example .env
    ```
2. Edit `.env` to use your OpenAI API key: `OPENAI_API_KEY=my-secret-key-for-openai`.  

    If you choose to run the application without OpenAI integration and generate dummy descriptions you can remove `OPEN_API_KEY` or set it to an empty string (`OPEN_API_KEY=""`).  When now api is provided the application will fall back to generating a dummy description.
3. Ensure that Docker Desktop is running.
4. Download and build the docker images
   ```
   $ docker compose build
   ```
   Note that this could take a little while.  This is a good time to stretch, grab a cup of coffee, and look out the window.
5. Setup the database
    ```
    docker compose exec backend python manage.py migrate
    ```
4. Start the containers 
    ```
    $ docker compose up
    ```