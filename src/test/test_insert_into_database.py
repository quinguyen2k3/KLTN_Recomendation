import unittest
from unittest.mock import MagicMock
from src.database.insert_into_database import InsertIntoDB


class TestInsertIntoDB(unittest.TestCase):

    def setUp(self):
        self.db = InsertIntoDB()
        self.session_mock = MagicMock()
        self.db.driver.session = MagicMock(return_value=self.session_mock)
        self.session_mock.__enter__.return_value = self.session_mock

    def test_check_user_in_database(self):
        self.session_mock.run.return_value.single.return_value = None
        self.assertFalse(self.db.check_user_in_database('123'))

        self.session_mock.run.return_value.single.return_value = True
        self.assertTrue(self.db.check_user_in_database('123'))

    def test_check_product_in_database(self):
        self.session_mock.run.return_value.single.return_value = None
        self.assertFalse(self.db.check_product_in_database('101'))

        self.session_mock.run.return_value.single.return_value = True
        self.assertTrue(self.db.check_product_in_database('101'))

    def test_check_category_in_database(self):
        self.session_mock.run.return_value.single.return_value = None
        self.assertFalse(self.db.check_category_in_database('Electronics'))

        self.session_mock.run.return_value.single.return_value = True
        self.assertTrue(self.db.check_category_in_database('Electronics'))

    def test_create_user_node(self):
        user_details = {
            'id': '123',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        self.db.create_user_node(user_details)
        self.session_mock.run.assert_called()

    def test_create_product_node(self):
        product_details = {
            'id': '101',
            'name': 'Smartphone'
        }
        self.db.create_product_node(product_details)
        self.session_mock.run.assert_called()

    def test_create_category_node(self):
        category_details = {'name': 'Electronics'}
        self.db.create_category_node(category_details)
        self.session_mock.run.assert_called()

    def test_create_relationship_user_to_product(self):
        user_details = {'id': '123'}
        product_details = {'id': '101'}
        self.db.create_relationship_user_to_product(user_details, product_details)
        self.session_mock.run.assert_called()

    def test_create_relationship_products_to_categories(self):
        category_details = {'name': 'Electronics'}
        product_details = {'id': '101'}
        self.db.create_relationship_products_to_categories(category_details, product_details)
        self.session_mock.run.assert_called()


if __name__ == '__main__':
    unittest.main()
