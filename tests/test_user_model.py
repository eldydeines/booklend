#--------------------------------------------------------------------------#
#  Capstone Project:  BookLandia
#
#  User Model Tests: 
#  - Instance 
#  - Relationships
#  - Registration
#  - Authentication
#  
#  Referenced - Warbler GitHub Test Cases
#  By: Eldy Deines  Date: 8/13/2021
#--------------------------------------------------------------------------#


#--------------------------------------------------------------------------#
#                           Import Necessary Libraries 
#--------------------------------------------------------------------------#

import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User

os.environ['DATABASE_URL'] = "postgresql:///booklend-test"

from app import app

db.create_all()


class UserModelTestCase(TestCase):
    """Test user model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()

        #Setup user1, user2, and user3
        user1 = User.register(username="fake_user1",password="faker1pwd", email="faker1@faker.com", 
                first_name="John", last_name="Hancock", address1="address1", address2="address2", town="town", 
                state="TX", zip="12345", phone="777-111-3333", profile="Books", fav_book="Fav Book", fav_author="Fav Auth")
        self.user1 = user1
        self.user1.user_id = user1.user_id
        
        user2 = User.register(username="fake_user2",password="faker2pwd", email="faker2@faker.com", first_name="Jane", last_name="Hancock", 
                address1="address1", address2="address2", town="town", state="CA", zip="23456", phone="888-111-3333", profile="Coffee", fav_book="Fav Book", fav_author=None)
        self.user2 = user2
        self.user2.user_id = user2.user_id
        
        user3 = User.register(username="fake_user3",password="faker3pwd", email="faker3@faker.com", first_name="Jack", last_name="Monk", 
                address1="address1", address2="address2", town="town", state="CO", zip="12345", phone="999-111-3333", profile="Coffee and books", fav_book=None, fav_author="Fav Auth")
        self.user3 = user3
        self.user3.user_id = user3.user_id
        
        db.session.commit()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            username="testuser",
            password="HASHED_PASSWORD",
            first_name="Jackie",
            last_name="Monk",
            address1="123 Monk Lane",
            town="Monkey Town",
            state="WA",
            zip="88888",
            email="jackie@test.com"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no status, no borrowers, no lenders
        self.assertEqual(len(u.status), 0)
        self.assertEqual(len(u.borrower), 0)
        self.assertEqual(len(u.lender), 0)
        self.assertEqual(len(u.borrow_ee), 0)


    def test_user_borrowing(self):
        """Does user1 borrow from user2"""

        #Make user1 borrow from user2
        self.user1.borrow_ee.append(self.user2)
        db.session.commit()

        #check 
        self.assertEqual(len(self.user1.borrow_ee), 1)
        

    def test_is_lending(self):
        """Does user 1 lend to user2"""
        
        #Make user1 lend to user2
        self.user1.lender.append(self.user2)
        db.session.commit()

        #check 
        self.assertEqual(len(self.user1.lender), 1)

    def test_register_user1(self):
        """Test registration for user1"""
        
        self.assertEqual(self.user1.username, "fake_user1")
        self.assertEqual(self.user1.email, "faker1@faker.com")
        self.assertNotEqual(self.user1.password, "faker1pwd")
        self.assertEqual(self.user1.profile,"Books")
        self.assertIsNone(self.user1.avg_rating, None)

    def test_register_user2(self):
        """Testing registration for another user"""
        
        #None value for username should raise error
        invalid_user_1 = User.register(username=None,password="faker1pwd",email="faker1@faker.com", first_name="Jane", 
            last_name="Hancock", address1="address1", town="town", state="CA", zip="23456", address2="", phone="345-333-3333",
            profile=None, fav_book=None, fav_author=None)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.add(invalid_user_1)
            db.session.commit()
        #with exception need to rollback commit
        db.session.rollback()


        invalid_user_2 = User.register(username="fake_user1",password="faker1pwd",email=None, first_name="Jane", 
            last_name="Hancock", address1="address1", town="town", state="CA", zip="23456", address2="", phone="345-333-3333",
            profile=None, fav_book=None, fav_author=None)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.add(invalid_user_2)
            db.session.commit()
        #with exception need to rollback commit
        db.session.rollback()
  
    def test_authenticate(self):
        """Testing validation User.authenticate function"""

        #Send bad info
        status_returned_bad_info = User.authenticate("fake_user3","faker1pwd")
        self.assertFalse(status_returned_bad_info)

    def tearDown(self):
        """Clean Up Data"""
        User.query.delete()
        db.session.commit()