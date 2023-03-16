import os
from datetime import datetime, timedelta

from babel.dates import format_datetime
from sqlalchemy import Column, String, Integer, ForeignKey
from flask_sqlalchemy import SQLAlchemy
import json
import dateutil.parser

database_filename = "library.db"
project_dir = os.path.dirname(os.path.abspath(__file__))
database_path = "sqlite:///{}".format(os.path.join(project_dir, database_filename))

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.jinja_env.filters['datetime'] = format_datetime
    db.app = app
    db.init_app(app)

def shutdown_db(app):
    db.session.remove()
    db.drop_all()
    #app.app_context().pop()



# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_dates(value, datetime_format='medium'):
    if isinstance(value, str):
        print('here')
        date = dateutil.parser.parse(value)
    else:
        date = value
    if datetime_format == 'full':
        datetime_format = "EEEE MMMM, d, y 'at' h:mma"
    elif datetime_format == 'medium':
        datetime_format = "EE MM, dd, y h:mma"
    return format_datetime(date, datetime_format, locale='en')


def db_refresh_session():
    print('here')
    db.session.flush()


'''
db_drop_and_create_all()
    drops the database tables and starts fresh
    can be used to initialize a clean database
    !!NOTE you can change the database_filename variable to have multiple versions of a database
'''


def db_drop_and_create_all():
    db.drop_all()
    db.create_all()
    # add one demo row which is helping in POSTMAN test
    book = Book(Title='Anne of Green Gables', Author='L.M. Mongomery')
    book.insert()

    book = Book(Title='Jane Eyre', Author='Charlotte Bronte')
    book.insert()

    book = Book(Title='Pride and Prejudice', Author='Jane Austen')
    book.insert()

    book = Book(Title='Dracula', Author='Bram Stoker', Number_of_exemplars=0)
    book.insert()

    user = User(FirstName='Elina', LastName='Maliarsky', Phone='11111', Address='aaaaa')
    user.insert()

    user = User(FirstName='John', LastName='Smith', Phone='22222', Address='bbbbb')
    user.insert()

    user = User(FirstName='Jane', LastName='Smith', Phone='33333', Address='ccccc')
    user.insert()

    user_book = User2Book(User_id=1, Book_id=1, Start_date=datetime(2023, 3, 11, 0, 0, 0),
                          Due_date=datetime(2023, 3, 21, 0, 0, 0))
    user_book.insert()

    user_book = User2Book(User_id=1, Book_id=2, Start_date=datetime(2023, 3, 13, 0, 0, 0),
                          Due_date=datetime(2023, 3, 22, 0, 0, 0))
    user_book.insert()

    user_book = User2Book(User_id=2, Book_id=3, Start_date=datetime(2023, 3, 1, 0, 0, 0),
                          Due_date=datetime(2023, 3, 11, 0, 0, 0))
    user_book.insert()


# ROUTES

'''
Book
a persistent book entity, extends the base SQLAlchemy Model
'''


class Book(db.Model):
    __tablename__ = 'Books'
    # Auto-incrementing, unique primary key
    ID = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    # String Title
    Title = Column(String(120), nullable=False)
    # String Author
    Author = Column(String(120), nullable=False)
    # String Edition
    Number_of_exemplars = Column(Integer, default=10, nullable=False)
    #users_books = db.relationship('User2Book', back_populates='book', lazy=True)
    users_books = db.relationship('User2Book', backref="book")

    '''
    insert()
        inserts a new book into a database
        the book must have a unique name
        the model must have a unique id or null id
        EXAMPLE
            book = Book(title=req_title, author=req_author,edition=req_edition)
            drink.insert()
    '''

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def insert_without_commit(self):
        db.session.add(self)

    '''
    delete()
        deletes a new model into a database
        the model must exist in the database
        EXAMPLE
            book = Book.query.filter(Book.id == id).one_or_none()
            book.delete()
    '''

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def delete_without_commit(self):
        db.session.delete(self)

    '''
    update()
        updates a new model into a database
        the model must exist in the database
        EXAMPLE
            book = Book.query.filter(Book.id == id).one_or_none()
            book.Edition = '2nd'
            drink.update()
    '''

    def update(self):
        db.session.commit()

    def format(self):
        return {
            'ID': self.ID,
            'Title': self.Title,
            'Author': self.Author,
            'Number_of_exemplars': self.Number_of_exemplars
        }

    def __repr__(self):
        return json.dumps(self.format())


'''
User
a persistent user entity, extends the base SQLAlchemy Model
'''


class User(db.Model):
    __tablename__ = 'Users'
    # Auto-incrementing, unique primary key
    ID = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    # String FirstName
    FirstName = Column(String(120), nullable=False)
    # String LastName
    LastName = Column(String(120), nullable=False)
    # string Phone
    Phone = Column(String(120), nullable=False)
    # String Edition
    Address = Column(String(240), nullable=False)
    users_books = db.relationship('User2Book', backref="user")

    '''
    insert()
        inserts a new model into a database
        the model must have a unique name
        the model must have a unique id or null id
        EXAMPLE
            user = User(FirstName=req_fname, LastName=req_LastName,Phone=req_phone, Address=req_address)
            user.insert()
    '''

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def insert_without_commit(self):
        db.session.add(self)

    '''
    delete()
        deletes a new model into a database
        the model must exist in the database
        EXAMPLE
            user = User.query.filter(User.id == id).one_or_none()
            user.delete()
    '''

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def delete_without_commit(self):
        db.session.delete(self)

    '''
    update()
        updates a new model into a database
        the model must exist in the database
        EXAMPLE
            user = User.query.filter(User.id == id).one_or_none()
            user.Address = 'Baker street 221B'
            user.update()
    '''

    def update(self):
        db.session.commit()

    def format(self):
        return {
            'ID': self.ID,
            'FirstName': self.FirstName,
            'LastName': self.LastName,
            'Phone': self.Phone,
            'Address': self.Address
        }

    def __repr__(self):
        return json.dumps(self.format())


'''
User2Book
a persistent User2Book entity, extends the base SQLAlchemy Model
'''


class User2Book(db.Model):
    __tablename__ = 'Users_books'
    ID = db.Column(Integer(), primary_key=True, autoincrement=True, nullable=False)
    # UserID
    User_id = Column(Integer(), ForeignKey('Users.ID'), nullable=False)
    # Book_ID
    Book_id = Column(Integer(), ForeignKey('Books.ID'), nullable=False)
    # StartDate
    Start_date = db.Column(db.Date, default=datetime.now(), nullable=False)
    # DueDate
    Due_date = db.Column(db.Date, default=datetime.now() + timedelta(days=10), nullable=False)
    # relationships
    #user = db.relationship('User', back_populates='users_books')
    #book = db.relationship('Book', back_populates='users_books')

    '''
    insert()
        inserts a new model into a database
        the model must have a unique name
        the model must have a unique id or null id
        
    '''

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def insert_without_commit(self):
        db.session.add(self)

    '''
    delete()
        deletes a new model into a database
        the model must exist in the database
       
    '''

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def delete_without_commit(self):
        db.session.delete(self)

    '''
    update()
        updates a new model into a database
        the model must exist in the database
       
    '''

    def update(self):
        db.session.commit()

    def format(self):
        return {
            'UserID': self.User_id,
            'BookID': self.Book_id,
            'StartDate': str(self.Start_date),
            'DueDate': str(self.Due_date)
        }

    def __repr__(self):
        return json.dumps(self.format())
