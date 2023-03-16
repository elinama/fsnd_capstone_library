import unittest
from flask import Config
from api.main.app import create_app
from api.db.models import database_path, setup_db, database_filename, db
import os
import json


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = database_path


class CapstoneTestCase(unittest.TestCase):

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = database_filename
        self.database_path = database_path
        self.USER_HEADER = {
            'Authorization': 'bearer ' + os.environ['USER_JWT']
        }
        self.LIBRARIAN_HEADER = {
            'Authorization': 'bearer ' + os.environ['LIBRARIAN_JWT']
        }
        self.app.config['TESTING'] = True
        self.headers = {'Content-Type': 'application/json'}

        self.app.config['SQLALCHEMY_DATABASE_URI_TEST'] = self.database_path
        setup_db(self.app)
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        """Executed after reach test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_health(self):
        res = self.client().get('/books')
        self.assertEqual(res.status_code, 200)

    def test_get_books(self):
        res = self.client().get('/books')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['books'])
        self.assertTrue(len(data['books']))

    def test_401_get_books_post(self):
        res = self.client().post('/books')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message']['code'], "authorization_header_missing")

    def test_get_book_by_id(self):
        res = self.client().get('/books/1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['books'])
        self.assertTrue(len(data['books']))

    def test_404_get_book_by_id_wrong_id(self):
        res = self.client().get('/books/10')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    def test_get_book_by_query(self):
        res = self.client().get('/books?query=Jane')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['books'])
        self.assertTrue(len(data['books']))

    def test_get_book_by_query_not_found(self):
        res = self.client().get('/books?query=Janne')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertFalse(data['books'])

# -----------------------------------------------
# User Tests
# -----------------------------------------------
    def test_get_users_books(self):
        res = self.client().get('/users/1/books', headers=self.USER_HEADER)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['books']))

    def test_404_get_users_books_wrong_user(self):
        res = self.client().get('/users/10/books', headers=self.USER_HEADER)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    def test_401_get_users_books_without_header(self):
        res = self.client().get('/users/1/books')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message']['code'], "authorization_header_missing")

    def test_422_patch_userbook_no_action(self):
        res = self.client().patch('/users/1/books/3', headers=self.USER_HEADER)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "unprocessable")

    def test_400_patch_userbook_wrong_action(self):
        res = self.client().patch('/users/1/books/3', headers=self.USER_HEADER, json={"action": "blah"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "bad request")

    def test_404_patch_userbook_book_doesnt_exist(self):
        res = self.client().patch('/users/1/books/10', headers=self.USER_HEADER, json={"action": "take"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    def test_404_patch_userbook_user_doesnt_exist(self):
        res = self.client().patch('/users/10/books/3', headers=self.USER_HEADER, json={"action": "take"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    def test_400_patch_userbook_book_taken(self):
        res = self.client().patch('/users/1/books/1', headers=self.USER_HEADER, json={"action": "take"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "bad request")

    def test_400_patch_userbook_book_returned(self):
        res = self.client().patch('/users/1/books/3', headers=self.USER_HEADER, json={"action": "return"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "bad request")

    def test_404_patch_userbook_take_taken_book(self):
        res = self.client().patch('/users/1/books/4', headers=self.USER_HEADER, json={"action": "take"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    def test_patch_userbook_take_book(self):
        res = self.client().patch('/users/1/books/3', headers=self.USER_HEADER, json={"action": "take"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['user_books'])
        self.assertEqual(len(data['user_books']), 3)
        self.assertTrue(data['book'])
        self.assertEqual(data['book']['Number_of_exemplars'], 9)

    def test_patch_userbook_return_book(self):
        res = self.client().patch('/users/1/books/2', headers=self.USER_HEADER, json={"action": "return"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['user_books'])
        self.assertEqual(len(data['user_books']), 1)
        self.assertTrue(data['book'])
        self.assertEqual(data['book']['Number_of_exemplars'], 11)

# -----------------------------------------------
# Librarian Tests
# -----------------------------------------------

    def test_get_users(self):
        res = self.client().get('/users', headers=self.LIBRARIAN_HEADER)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['users'])
        self.assertTrue(len(data['users']))

    def test_401_get_users_get(self):
        res = self.client().get('/users', headers=self.USER_HEADER)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message']['code'], "unauthorized")

    def test_get_users_with_overdue_books(self):
        res = self.client().get('/users?overdue=True', headers=self.LIBRARIAN_HEADER)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['users']), 1)
        self.assertTrue(data['users'])

    def test_get_users_by_query(self):
        res = self.client().get('/users?query=Elina', headers=self.LIBRARIAN_HEADER)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['users']), 1)
        self.assertTrue(data['users'])

    def test_get_users_by_query_not_found(self):
        res = self.client().get('/users?query=Elinor', headers=self.LIBRARIAN_HEADER)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['users']), 0)
        self.assertFalse(data['users'])

    def test_get_users_with_books(self):
        res = self.client().get('/users/1', headers=self.LIBRARIAN_HEADER)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['books'])
        self.assertEqual(len(data['books']), 2)
        self.assertTrue(data['books'][0]['Author'])
        self.assertTrue(data['books'][0]['Title'])
        self.assertTrue(data['books'][0]['Number_of_Exemplars'])
        self.assertTrue(data['books'][0]['Start_date'])
        self.assertTrue(data['books'][0]['Due_date'])
        self.assertTrue(data['user'])

    def test_404_get_users_with_books_wrong_id(self):
        res = self.client().get('/users/10', headers=self.LIBRARIAN_HEADER)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    def test_create_user(self):
        res = self.client().post('/users', headers=self.LIBRARIAN_HEADER, json={
                "FirstName": "Jane",
                "LastName": "Smith",
                "Address": "bbbbbb",
                "Phone": "1212121"
            })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['users'])
        self.assertEqual(len(data['users']), 1)

    def test_401_create_users_post(self):
        res = self.client().post('/users', headers=self.USER_HEADER)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message']['code'], "unauthorized")

    def test_create_book(self):
        res = self.client().post('/books', headers=self.LIBRARIAN_HEADER, json={
                "Title": "My book",
                "Author": "Elina Maliarsky",
                "Number_of_exemplars": 11
            })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['books'])
        self.assertEqual(len(data['books']), 1)

    def test_401_create_books_post(self):
        res = self.client().post('/books', headers=self.USER_HEADER)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message']['code'], "unauthorized")

    def test_update_user(self):
        res = self.client().patch('/users/2', headers=self.LIBRARIAN_HEADER, json={
            "Phone": "88888"
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['users'])
        self.assertEqual(data['users'][0]["Phone"], "88888")

    def test_update_book(self):
        res = self.client().patch('/books/1', headers=self.LIBRARIAN_HEADER, json={
            "Number_of_exemplars": "12"
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['books'])
        self.assertEqual(data['books'][0]["Number_of_exemplars"], 12)

    def test_404_update_user(self):
        res = self.client().patch('/users/21', headers=self.LIBRARIAN_HEADER, json={
            "Phone": "88888"
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    def test_404_update_book(self):
        res = self.client().patch('/books/11', headers=self.LIBRARIAN_HEADER, json={
            "Number_of_exemplars": "12"
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    def test_delete_user(self):
        res = self.client().delete('/users/3', headers=self.LIBRARIAN_HEADER)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['delete'])
        self.assertEqual(data['delete'], '3')

    def test_delete_book(self):
        res = self.client().delete('/books/4', headers=self.LIBRARIAN_HEADER)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['delete'])
        self.assertEqual(data['delete'], '4')

    def test_404_delete_user(self):
        res = self.client().delete('/users/21', headers=self.LIBRARIAN_HEADER)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    def test_404_delete_book(self):
        res = self.client().delete('/books/11', headers=self.LIBRARIAN_HEADER)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    def test_422_delete_user(self):
        res = self.client().delete('/users/1', headers=self.LIBRARIAN_HEADER)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "unprocessable")

    def test_422_delete_book(self):
        res = self.client().delete('/books/1', headers=self.LIBRARIAN_HEADER)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "unprocessable")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main(verbosity=1)
