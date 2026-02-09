from django.db import models
from django.contrib.auth.models import User


class SearchData(models.Model):
    """Legacy model - kept for backward compatibility."""
    search_text = models.CharField(max_length=255)
    keywords = models.TextField(blank=True)
    patent_data = models.TextField(blank=True)
    results = models.TextField(blank=True)

    def __str__(self):
        return f"Search: {self.search_text}"


class SearchHistory(models.Model):
    """Store user patent searches with full details."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='searches')
    search_text = models.TextField()
    keywords_extracted = models.CharField(max_length=500)
    patent_data = models.TextField()
    analysis_result = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
        verbose_name_plural = 'Search Histories'
    
    def __str__(self):
        return f"{self.user.username} - {self.search_text[:50]}"