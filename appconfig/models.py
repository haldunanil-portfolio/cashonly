"""
Created by haldunanil on 5/5/2017 per issue #7.
"""
from django.db import models
from simple_history.models import HistoricalRecords


class Config(models.Model):
    """
    A key:value style model to store global variables
    """
    key = models.CharField(max_length=100, primary_key=True, db_index=True)
    comments = models.TextField(null=True, blank=True)
    value = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    def __str__(self):
        return u'%s: %s' % (self.key, self.value)

    class Meta:
        verbose_name = 'App Config'
        verbose_name_plural = 'App Config'

    def is_float(self):
        """
        Check if value can be a float, return True if so, False otherwise.
        """
        try:
            float(self.value)
            return True
        except ValueError:
            return False

    def is_int(self):
        """
        Check if value can be an int, return True if so, False otherwise.
        """
        try:
            int(self.value)
            return True
        except ValueError:
            return False

    def get_value(self):
        """
        Attempt to return value as int, otherwise float, otherwise as is.
        """
        if self.is_int():
            return int(self.value)
        elif self.is_float():
            return float(self.value)

        return self.value
