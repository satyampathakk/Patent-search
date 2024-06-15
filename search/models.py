from django.db import models

# Create your models here.
class SearchData(models.Model):  # Define your model here
    search_text = models.CharField(max_length=255)  # Adjust field length as needed
    keywords = models.TextField(blank=True)  # Store extracted keywords
    patent_data = models.TextField(blank=True)  # Store scraped patent data
    results = models.TextField(blank=True)  # Store final response from genai model

    def __str__(self):
        return f"Search: {self.search_text}"