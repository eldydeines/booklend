#--------------------------------------------------------------------------#
#  Capstone Project:  BookLandia
#
#  Book Model Tests: 
#  - Instance 
#  - Relationships
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
from models import db, Book

os.environ['DATABASE_URL'] = "postgresql:///booklend-test"

from app import app

db.create_all()

class BookModelTestCase(TestCase):
    """Test book model."""

    def setUp(self):
        """Create test client, add sample data."""

        Book.query.delete()

        #Setup user1, user2, and user3
        book1 = Book(key="bookkey/999999",title="Romeo and Juliet", author="Shakespeare", description="Two star crossed romantics", 
                subjects="Romance, Fiction")
        self.book1 = book1

        db.session.commit()

        self.client = app.test_client()

    def test_book_model(self):
        """Does basic model work?"""

        # Book values
        self.assertEqual(self.book1.key,"bookkey/999999")
        self.assertEqual(self.book1.author,"Shakespeare")
        self.assertIsNone(self.book1.published_year)
        self.assertIsNone(self.book1.avg_rating)

        # Book should have no status, no borrowers, no lenders
        self.assertEqual(len(self.book1.status), 0)
        self.assertEqual(len(self.book1.user), 0)


    def test_book_uniqueness(self):
        """Testing only one unique book can only be added once"""
        good_book = Book(key="bookkey/999999",title="Romeo and Juliet", author="Shakespeare", description="Two star crossed romantics", 
                subjects="Romance, Fiction")
        db.session.add(good_book)
        db.session.commit()

        invalid_book = Book(key="bookkey/999999",title="Romeo and Juliet", author="Shakespeare", description="Two star crossed romantics", 
                subjects="Romance, Fiction")
        #if we try to commit another book with the same key, it will raise error
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.add(invalid_book)
            db.session.commit()
        #with exception need to rollback commit
        db.session.rollback()

    def tearDown(self):
        """Clean Up Data"""
        Book.query.delete()
        db.session.commit()
 