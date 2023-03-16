# Full Stack Library API
An API to simplify the administration of library. The man actors are guests (public permissions), users and librarian.

## API Authentication and Authorization
There are three roles associated with API:
1. Guest (without roles):
    - Can view and search for books
    - Can view certain book
2. Users:
    - All permissions of gusts and
    - Get all user's book  
    - Take or return a book
2. Librarian
    - All permissions a guests and users have and
    - Add, update or delete book
    - Add, update or delete user's info
    - Get all users
    - Search within users (by first or last name)
    - Get list of all users with overdue books
   
## Hosting (TODO)
App is hosted [here](https://ben-capstone-fsnd.herokuapp.com/)

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Environment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virtual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/) is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) and [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) are libraries to handle the lightweight sqlite database. Since we want you to focus on auth, we handle the heavy lift for you in `./src/database/models.py`. We recommend skimming this code first so you know how to interface with the Drink model.

- [jose](https://python-jose.readthedocs.io/en/latest/) JavaScript Object Signing and Encryption for JWTs. Useful for encoding, decoding, and verifying JWTS.

## Tests

To run the unittests, first CD into the Capstone folder and run the following commands:

setup.sh or linux or setup.bash for windows, it will write environment variables

python -m api.test_app

You should be outside the api folder

In addition, postman file with tests is supplied, import "Library.postman_collection" and run it.   


## Running the server

From within the `./api/main` directory first ensure you are working using your created virtual environment.

Each time you open a new terminal session, run:

```bash
export FLASK_APP=app.py;
```
```win cmd
set FLASK_APP=app.py;
```

To run the server, execute:

```bash
flask run --reload
```

The `--reload` flag will detect file changes and restart the server automatically.
## Database Setup
The app is configured to run with Postgres but any relational database that is supported by SQLAlchemy will work. 
the database is LiteSQL db and supplied with the project (library.db)

## Running the Server
To run the server, execute:
`flask run --reload`
(The reload flag is optional)
 
# Endpoints
### GET '/'
- returns a JSON object representing what could be the home page
Example: 
```
{
	"hi":"library"
}
```

### GET '/books'
- returns a JSON object of all books stored in the database
Example: 
```
{
    "books": [
        {
            "id": 1,
            "Title": "Jane Eyre",
            "Author": Charlotte Bronte,
            "Number_of_exemplars": 10
        }
    ],....
    "success": true
}
```

### GET '/books?query=Jane'
- returns a JSON object of books with 'Jane' in author's name o title
Example 
```
{
    "books": [
        "books": [
        {
            "id": 1,
            "Title": "Jane Eyre",
            "Author": Charlotte Bronte,
            "Number_of_exemplars": 10
        },
        {
            "id": 2,
            "Title": "Prie and Prejudice",
            "Author": Jane Austen,
            "Number_of_exemplars": 10
        }
    ],...
    "success": true
}
```

### GET '/books/1'
- returns a JSON object with a book's information
Example: 
```
{
    "books": [
        {
            "id": 1,
            "Title": "Jane Eyre",
            "Author": Charlotte Bronte,
            "Number_of_exemplars": 10
        }
    ]
    "success": true
}
```

### GET /users/1/books>
- returns JSON object of books of the curtain user
Example:
```
{
    "books": [
        {
            "id": 1,
            "Title": "Jane Eyre",
            "Author": Charlotte Bronte,
            "Number_of_exemplars": 10
        }
    ],...
    "success": true
}
```

### PATCH '/users/1/books/3
{ "action": "take"}

- Creates a new row un users_books table
- decrements number_of_exemplars attribute of book object   
- Returns JSON object of user_books and book information
Example:
```
{
    "book": {
        "Author": "Jane Austen",
        "ID": 3,
        "Number_of_exemplars": 9,
        "Title": "Pride and Prejudice"
    },
    "success": true,
    "user_books": [
        {
            "BookID": 1,
            "DueDate": "2023-03-21",
            "StartDate": "2023-03-11",
            "UserID": 1
        },
        {
            "BookID": 2,
            "DueDate": "2023-03-22",
            "StartDate": "2023-03-13",
            "UserID": 1
        },
        {
            "BookID": 3,
            "DueDate": "2023-03-25",
            "StartDate": "2023-03-15",
            "UserID": 1
        }
    ]
}
```

### PATCH '/users/1/books/3
{ "action": "return"}

- Removes a row from users_books table
- increments number_of_exemplars attribute of book object   
- Returns JSON object of user_books and book information
Example:
```
{
    "book": {
        "Author": "Jane Austen",
        "ID": 3,
        "Number_of_exemplars": 10,
        "Title": "Pride and Prejudice"
    },
    "success": true,
    "user_books": [
        {
            "BookID": 1,
            "DueDate": "2023-03-21",
            "StartDate": "2023-03-11",
            "UserID": 1
        },
        {
            "BookID": 2,
            "DueDate": "2023-03-22",
            "StartDate": "2023-03-13",
            "UserID": 1
        }
    ]
}
```

### GET /users>
- returns JSON object of users
Example:
```
{
    "users": [
        {
            "id": 1,
            "FirstName": "Elina",
            "LastName": "Maliarsky",
            "Address": "aaaaaaa",
            "Phone": 111111
            
        }
    ],...
    "success": true
}
```

### GET /users?query=Elina>
- returns JSON object of users
Example:
```
{
    "users": [
        {
            "id": 1,
            "FirstName": "Elina",
            "LastName": "Maliarsky",
            "Address": "aaaaaaa",
            "Phone": 111111
            
        }
    ],...
    "success": true
}
```

### GET /users?overdue=true>
- returns JSON object of users
Example:
```
{
    "users": [
        {
            "id": 2,
            "FirstName": "John",
            "LastName": "Smith",
            "Address": "bbbbbbb",
            "Phone": 222222
            
        }
    ],...
    "success": true
}
```

### GET /users/1/books>
- returns JSON object of user's info and his/her books
Example:
```
{
    "books": [
        {
            "Author": "L.M. Mongomery",
            "Due_date": "Tue, 21 Mar 2023 00:00:00 GMT",
            "Number_of_Exemplars": 10,
            "Start_date": "Sat, 11 Mar 2023 00:00:00 GMT",
            "Title": "Anne of Green Gables"
        },
        {
            "Author": "Charlotte Bronte",
            "Due_date": "Wed, 22 Mar 2023 00:00:00 GMT",
            "Number_of_Exemplars": 10,
            "Start_date": "Mon, 13 Mar 2023 00:00:00 GMT",
            "Title": "Jane Eyre"
        }
    ],
    "success": true,
    "user": {
        "Address": "aaaaa",
        "FirstName": "Elina",
        "ID": 1,
        "LastName": "Maliarsky",
        "Phone": "11111"
    }
}
```



### POST '/users'
- creates a new user in the database
- returns JSON object with user's info
Example:
```
{
    "users": [
        {
            "id": 2,
            "FirstName": "John",
            "LastName": "Smith",
            "Address": "bbbbbbb",
            "Phone": 222222
            
        }
    ],...
    "success": true
}
```

### PATCH '/users/1'
- Updates user with corresponding ID
- returns JSON object with user's info
Example:
```
{
    "users": [
        {
            "id": 2,
            "FirstName": "John",
            "LastName": "Smith",
            "Address": "bbbbbbb",
            "Phone": 222222
            
        }
    ]
    "success": true
}
```


### DELETE '/users/1'
- Deletes corresponding user 
- Returns users ID and success message
Example:
```
{
    "delete": 1,
    "success": true
}
```


### POST '/books'
- creates a new book in the database
- returns JSON object with books's info
Example:
```
{
    {
    "books": [
        {
            "id": 1,
            "Title": "Jane Eyre",
            "Author": Charlotte Bronte,
            "Number_of_exemplars": 10
        }
    ]
    "success": true
}

```

### PATCH '/books/1'
- Updates the book with corresponding ID
- returns JSON object with book's info
Example:
```
{
    {
    "books": [
        {
            "id": 1,
            "Title": "Jane Eyre",
            "Author": Charlotte Bronte,
            "Number_of_exemplars": 10
        }
    ]
    "success": true
}
```


### DELETE '/books/1'
- Deletes corresponding book 
- Returns users ID and success message
Example:
```
{
    "delete": 1,
    "success": true
}
```