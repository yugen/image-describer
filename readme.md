# Edlight Senior Fullstack Programmer Application - Task

This repository contains my submission for the programming assignment for the Senior Fullstack developer position at EdLIght.

The submission assumes the following, based on the [instructions](https://docs.google.com/document/d/1Mo7GnUfcQ8p--IuXcLoRKxI40dhkBrn3wXblukrZ5N0/edit):
* A user interface (i.e. Frontend) was not expected as part of the assignment.
* The actual descriptions of images returned by the image analysis were not as important as displaying the ability to integrate with one of the public image analysis services.
* URLS of endpoints were required to match those defined in the [Technical Requirements](https://docs.google.com/document/d/1Mo7GnUfcQ8p--IuXcLoRKxI40dhkBrn3wXblukrZ5N0/edit)
* Additional endpoints are acceptable

See [Usage](#usage) for API documentation.

See [Installation](#installation) for instructions on and requirements to set this API up locally.

See [TODOs](#TODOs) for opportunities to improve this API.

## Usage
You can use the following endpoints to upload/analyze, browse, and comment on images:
### Endpoints

#### `POST: /analyze-image`
Accepts an image file, stores it, and gets a description from the image analysis service.
#### Params
    * `file`: (file upload) - the image file you want to store and analyze.
#### Response
##### Success
This endpoint returns a JSON object representing the image including:
* `id: int` - The numeric identifier of the image
* `file: str ` - The relative path of the image to the MEDIA_ROOT
* `description: [null|str]` - The description, if any has been added by the image analysis.
* `analyzed: bool` - Whether the image has been analyzed.

##### Errors
* `422` Status - validation errors.
    * `errors: object`
        * `<param>: array` - keys are parameters that failed validation; values are an array of error messages.
    
---

#### `GET: /image/<image_id>`
Given an image ID, show the image and a page of comments

#### Params
* `image_id: int` - A path parameter to identify the image record
* `comment_page: int = 1` [OPTIONAL] - the page of comments you would like.  Defaults to the first page if not provided.

#### Response
##### Success
This endpoint returns a JSON object representing the image including:
* `id: int` - The numeric identifier of the image
* `file: str ` - The relative path of the image to the MEDIA_ROOT
* `description: [null|str]` - The description, if any has been added by the image analysis.
* `analyzed: bool` - Whether the image has been analyzed.
* `comments: object` - page comments w/ metadata:
    * `num_pages: int` - Number of pages of comments available
    * `data: array` - A list of comments sorted by creation date.  Each comment is an object containing:
        * `id: int` - Numeric identifier of the comment
        * `content: str` - The content of the comment
        * `created_at: datetime`  - The date and time the comment was created

##### Errors
* `404` - Image record with id was not found
* `416` - The comment page specified was out of range. For example if `num_pages` is `4` and `?comment_page=5`, the endpoint will fail with a `416` status code. 

---

### `GET: images`

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

## TODOs
Given the time-limited nature of this assignment, there are many things that could/should be done to this application before it is considered complete:
1. Image analysis should be handled using a task queue (i.e. `celery`).
2. Prompts to OpenAI GPT-4v should be tailored to provide the best description for the business goals.  Collaboration with domain experts is required to determine those goals, and craft the most effective prompt.
3. Automate API documentation generation
3. Implement API Authentication
    * registration
    * login
    * endpoint protection

