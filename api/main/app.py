from datetime import datetime

from flask import Flask, request, abort, jsonify

from flask_cors import CORS
from sqlalchemy import or_

from ..auth.auth import AuthError, requires_auth

from ..db.models import Book, User, User2Book, setup_db, db_drop_and_create_all


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    with app.app_context():
        db_drop_and_create_all()

    # ROUTES
    '''
    @TODO implement health check
    '''

    @app.route('/', methods=["GET"])
    # @cross_origin
    def health_check():
        try:
            return jsonify({
                'hi': 'library'
            })
        except Exception as ex:
            print(ex)
            abort(404)

    '''
    @TODO implement endpoint
        GET /books
            it should be a public endpoint
            it should contain only the Books.format() data representation
            returns status code 200 and json {"success": True, "books": books} where books is the list of books 
            in proper format  or appropriate status code indicating reason for failure
    '''

    @app.route('/books', methods=["GET"])
    # @cross_origin
    def get_books():
        try:
            query = request.args.get('query')
            if query is None:
                books = Book.query.all()
            else:
                books = Book.query. \
                    filter(or_(Book.Title.ilike(f'%{query}%'), Book.Author.ilike(f'%{query}%'))).all()

            return jsonify({
                'success': True,
                'books': [book.format() for book in books]
            })
        except Exception as ex:
            print(ex)
            abort(404)

    '''
        @TODO implement endpoint
        GET /books/<int:book_id>
            it should be a public endpoint
            it should contain only the Books.format() data representation
            returns status code 200 and json {"success": True, "books": books} 
            where books is the list of only found book 
            in proper format  or appropriate status code indicating reason for failure
    '''

    @app.route('/books/<int:book_id>', methods=['GET'])
    # @cross_origin
    def get_book_by_id(book_id):
        book = None
        try:
            book = Book.query.filter(Book.ID == book_id).one_or_none()
        except Exception as ex:
            abort(422)
        if book is None:
            abort(404)
        try:
            return jsonify({
                'success': True,
                'books': [book.format()]
            })
        except Exception as ex:
            print(ex)
            abort(422)

    # user

    '''
        @TODO implement endpoint
        GET /users/<int:user_id/books>
            it should require get:user_books permissions
            it should contain only the extended Books data representation
            returns status code 200 and json {"success": True, "books": books} where books 
            is the list of only found book in extended (includes user_books)  
            in proper format  or appropriate status code indicating reason for failure
    '''

    @app.route('/users/<int:user_id>/books', methods=['GET'])
    @requires_auth('get:user_books')
    # @cross_origin
    def get_books_by_user_id(payload, user_id):
        user = None
        try:
            user = User.query.filter(User.ID == user_id).one_or_none()
        except Exception as ex:
            abort(422)
        if user is None:
            abort(404)

        # dictionary - extended book format
        def user_book_2_dict(ub):
            return {
                "Title": ub.book.Title,
                "Author": ub.book.Author,
                "Number_of_Exemplars": ub.book.Number_of_exemplars,
                "Start_date": ub.Start_date,
                "Due_date": ub.Due_date
            }

        try:
            return jsonify({
                'success': True,
                'books': [user_book_2_dict(ub) for ub in user.users_books]})
        except Exception as ex:
            print(ex)
            abort(422)

    '''
    @TODO implement endpoint
        GET /users/<int:user_id>/books/<int:book_id>
            it should require the 'action:book' permission
            it should add book to user_books table and decrement the number_of_exemplars attribute 
            of the book if the action is "take"
            it should to remove book from user_books table and increment the number_of_exemplars attribute 
            of the book if the action is "return"        
            returns status code 200 and json {"success": True, "user_books": user_books, book:book}
            where user_books are  is the list of user_books and book is a formatted book
            or appropriate status code indicating reason for failure
    '''

    @app.route('/users/<int:user_id>/books/<int:book_id>', methods=["PATCH"])
    @requires_auth('action:book')
    # @cross_origin
    def take_return(payload, user_id, book_id):
        body = None
        try:
            body = request.get_json()
        except Exception as ex:
            abort(422)
        if not body:
            abort(422)
        action = body.get("action", None)
        if action is None or action not in ["take", "return"]:
            abort(400)
        # get user
        user = None
        book = None
        try:
            user = User.query.filter(User.ID == user_id).one_or_none()
            book = Book.query.filter(Book.ID == book_id).one_or_none()
        except Exception as ex:
            abort(422)
        if user is None or book is None:
            abort(404)

        # take
        if (action == "take"):
            # check if user already has a book
            book_of_user = [user_book for user_book in user.users_books if user_book.Book_id == book_id]
            if book_of_user:
                abort(400)
            # check if number of exemplars is zero - all the exemplars are already taken
            if book.Number_of_exemplars == 0:
                abort(404)
            try:
                new_ub = User2Book(User_id=user_id, Book_id=book_id)
                new_ub.insert_without_commit()
                book.Number_of_exemplars -= 1
                book.update()
            except Exception as ex:
                abort(422)

        # return
        if action == "return":
            # check if user has a book
            book_of_user = [user_book for user_book in user.users_books if user_book.Book_id == book_id]
            if book_of_user == []:
                abort(400)
            try:
                book_of_user[0].delete()
                book.Number_of_exemplars += 1
                book.update()
            except Exception as ex:
                print(ex)
                abort(422)

        return jsonify({
            'success': True,
            'user_books': [ub.format() for ub in user.users_books],
            'book': book.format()
        })

    # librarian

    '''
    @TODO implement endpoint
        POST /users
            it should create a new row in the users table
            it should require the 'create:user' permission
            it should contain the user.format() data representation
            returns status code 200 and json {"success": True, "users": users} 
            where users an array containing only the newly created user
            or appropriate status code indicating reason for failure
    '''

    @app.route("/users", methods=["POST"])
    @requires_auth('create:user')
    def create_user(payload):
        try:
            new_firstname = request.json['FirstName']
            new_lastname = request.json['LastName']
            new_address = request.json['Address']
            new_phone = request.json['Phone']
            user = User(FirstName=new_firstname, LastName=new_lastname, Address=new_address, Phone=new_phone)
            user.insert()
            return jsonify(
                {
                    "success": True,
                    "users": [user.format()]
                })
        except Exception:
            abort(422)

    '''
    @TODO implement endpoint
        PATCH /users/<user_id>
            where <user_id> is the existing model id
            it should respond with a 404 error if <user_id> is not found
            it should update the corresponding row for <user_id>
            it should require the 'update:user' permission
            it should contain the user.format() data representation
            returns status code 200 and json {"success": True, "users": user} 
            where user an array containing only the updated user
            or appropriate status code indicating reason for failure
    '''

    @app.route("/users/<user_id>", methods=['PATCH'])
    @requires_auth('update:user')
    def update_user(payload, user_id):
        new_firstname = new_lastname = new_address = new_phone = None
        try:
            body = request.get_json()
            new_firstname = body.get("FirstName", None)
            new_lastname = body.get("LastName", None)
            new_address = body.get("Address", None)
            new_phone = body.get("Phone", None)
        except Exception as ex:
            print(ex)
            abort(422)

        # get user
        user = None
        try:
            user = User.query.filter(User.ID == user_id).one_or_none()
        except Exception as ex:
            abort(422)
        if user is None:
            abort(404)

        try:
            if new_firstname:
                user.FistName = new_firstname
            if new_lastname:
                user.LastName = new_lastname
            if new_address:
                user.Address = new_address
            if new_phone:
                user.Phone = new_phone

            user.update()
            return jsonify(
                {
                    "success": True,
                    "users": [user.format()]
                })
        except Exception as ex:
            print(ex)
            abort(422)

    '''
    @TODO implement endpoint
        DELETE /users/<user_id>
            where <user_id> is the existing model id
            it should respond with a 404 error if <user_id> is not found
            it should delete the corresponding row for <user_id>
            it should require the 'delete:user' permission
        returns status code 200 and json {"success": True, "delete": user_id} where id is the id of the deleted record
            or appropriate status code indicating reason for failure
    '''

    @app.route("/users/<user_id>", methods=['DELETE'])
    @requires_auth('delete:user')
    def delete_user(payload, user_id):
        user = None
        try:
            user = User.query.filter(User.ID == user_id).one_or_none()
        except Exception as ex:
            print(ex)
            abort(422)
        if user is None:
            abort(404)
        ubs = user.users_books
        if ubs is not None and len(ubs) > 0:
            abort(422)
        try:
            user.delete()
            return jsonify(
                {
                    "success": True,
                    "delete": user_id
                })
        except Exception as ex:
            print(ex)
            abort(422)

    '''
    @TODO implement endpoint
        POST /books
            it should create a new row in the books table
            it should require the 'create:book' permission
            it should contain the book.format() data representation
            returns status code 200 and json {"success": True, "books": books} 
            where books is an array containing only the newly created book
            or appropriate status code indicating reason for failure
    '''

    @app.route("/books", methods=["POST"])
    @requires_auth('create:book')
    def create_book(payload):
        try:
            new_title = request.json['Title']
            new_author = request.json['Author']
            new_num_of_exemplars = request.json['Number_of_exemplars']

            book = Book(Title=new_title, Author=new_author, Number_of_exemplars=new_num_of_exemplars)
            book.insert()
            return jsonify(
                {
                    "success": True,
                    "books": [book.format()]
                })
        except Exception as ex:
            print(ex)
            abort(422)

    '''
    @TODO implement endpoint
        PATCH /books/book_id>
            where <book_id> is the existing model book_id
            it should respond with a 404 error if <book_id> is not found
            it should update the corresponding row for <book_id>
            it should require the 'update:book' permission
            it should contain the book.format() data representation
            returns status code 200 and json {"success": True, "books": books} 
            where books an array containing only the updated book
            or appropriate status code indicating reason for failure
    '''

    @app.route("/books/<book_id>", methods=['PATCH'])
    @requires_auth('update:book')
    def update_book(payload, book_id):
        body = book = new_title = new_author = new_num_of_exemplars = None
        try:
            body = request.get_json()
            new_title = body.get("Title", None)
            new_author = body.get("Author", None)
            new_num_of_exemplars = body.get("Number_of_exemplars", None)
        except Exception as ex:
            print(ex)
            abort(422)
        # get book
        try:
            book = Book.query.filter(Book.ID == book_id).one_or_none()
        except Exception as ex:
            abort(422)
        if book is None:
            abort(404)

        try:
            if new_title:
                book.Title = new_title
            if new_author:
                book.Author = new_author
            if new_num_of_exemplars:
                book.Number_of_exemplars = new_num_of_exemplars

            book.update()
            return jsonify(
                {
                    "success": True,
                    "books": [book.format()]
                })
        except Exception as ex:
            print(ex)
            abort(422)

    '''
    @TODO implement endpoint
        DELETE /books/<book_id>
            where <book_id> is the existing model book_id
            it should respond with a 404 error if <book_id> is not found
            it should delete the corresponding row for <book_id>
            it should require the 'delete:book' permission
            returns status code 200 and json {"success": True, "delete": book_id} where 
            book_id is the book_id of the deleted record
            or appropriate status code indicating reason for failure
    '''

    @app.route("/books/<book_id>", methods=['DELETE'])
    @requires_auth('delete:book')
    def delete_book(payload, book_id):
        book = None
        try:
            book = Book.query.filter(Book.ID == book_id).one_or_none()
        except Exception as ex:
            abort(422)
        if book is None:
            abort(404)
        ubs = book.users_books
        if ubs is not None and len(ubs) > 0:
            abort(422)
        try:
            book.delete()
            return jsonify(
                {
                    "success": True,
                    "delete": book_id
                })
        except Exception as ex:
            print(ex)
            abort(422)

    '''
    
    @TODO implement endpoint
        GET /users
            it should require the 'get:users' permission
            it should contain only the users.format() data representation
            it can accept arguments: 
            if argument is query, the search is performed
            if argument is Overdue, the only the users with overdue books are returned
            returns status code 200 and json {"success": True, "users": users} where users is the list of users 
            in proper format  or appropriate status code indicating reason for failure
    '''

    @app.route('/users', methods=["GET"])
    @requires_auth('get:users')
    # @cross_origin
    def get_users(payload):
        try:
            query = request.args.get('query')
            overdue = request.args.get('overdue')
            if query is None and (overdue is None or overdue is False):
                users = User.query.all()
            elif overdue:
                # user = db.session.query(User, Role).select_from(User).join(roles_users).join(Role).filter(
                #    Role.name == 'admin').all()
                users = User.query.join(User2Book). \
                    filter(User2Book.Due_date < datetime.now()).all()
            else:
                users = User.query. \
                    filter(or_(User.FirstName.ilike(f'%{query}%'),
                               User.LastName.ilike(f'%{query}%'))).all()

            return jsonify({
                'success': True,
                'users': [user.format() for user in users]
            })
        except Exception as ex:
            print(ex)
            abort(404)

    '''
    
    @TODO implement endpoint
        GET /users/<int:user_id>
            it should require the 'get:user' permission
            it should contain only the users.format() data representation       
            returns status code 200 and json {"success": True, "user": users, "books:books} 
            where users is the list of the only user and books is the list of books belong to the user 
            in proper format  
            or appropriate status code indicating reason for failure
    '''

    @app.route('/users/<int:user_id>', methods=['GET'])
    @requires_auth('get:user')
    # @cross_origin
    def get_users_by_id(payload, user_id):
        user = None
        try:
            user = User.query.filter(User.ID == user_id).one_or_none()
        except Exception as ex:
            abort(422)
        if user is None:
            abort(404)

        def user_book_2_dict(ub):
            return {
                "Title": ub.book.Title,
                "Author": ub.book.Author,
                "Number_of_Exemplars": ub.book.Number_of_exemplars,
                "Start_date": ub.Start_date,
                "Due_date": ub.Due_date
            }

        try:
            return jsonify({
                'success': True,
                'user': user.format(),
                'books': [user_book_2_dict(ub) for ub in user.users_books]})
        except Exception as ex:
            print(ex)
            abort(422)

    # Error Handling

    '''
    @TODO implement error handlers using the @app.errorhandler(error) decorator
        each error handler should return (with approprate messages):
                 jsonify({
                        "success": False,
                        "error": 404,
                        "message": "resource not found"
                        }), 404
    
    '''

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

    @app.errorhandler(405)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 405, "message": "method not allowed"}),
            405,
        )

    '''
    @TODO implement error handler for AuthError
        error handler should conform to general task above
    '''

    @app.errorhandler(AuthError)
    def auth_error(error):
        '''Error handling for Authorization Error'''
        return jsonify({
            'success': False,
            'error': error.status_code,
            'message': error.error
        }), error.status_code

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
    # app.run()
    # app.run(host='127.0.0.1', port=5000, debug=True)
    # app.run(debug=True, host='0.0.0.0')
