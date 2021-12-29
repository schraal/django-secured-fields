from django import test
from django.db import connection
from django.db.models import Model

from main import models
from secured_fields.fernet import get_fernet


class BaseFieldTestCase(test.TestCase):
    model_class: Model

    def get_raw_field(self):
        with connection.cursor() as cursor:
            # pylint: disable=protected-access
            cursor.execute(f'SELECT field FROM {self.model_class._meta.db_table} LIMIT 1')
            return cursor.fetchone()[0]

    def assertEncryptedField(self, expected_bytes: bytes):
        field_value = self.get_raw_field()
        decrypted_value = get_fernet().decrypt(field_value)

        self.assertEqual(decrypted_value, expected_bytes)


class CharFieldTestCase(BaseFieldTestCase):
    model_class = models.CharFieldModel

    def test_simple(self):
        model = self.model_class.objects.create(field='test')

        self.assertEqual(self.model_class.objects.count(), 1)
        self.assertEqual(model.field, 'test')
        self.assertEncryptedField(b'test')
