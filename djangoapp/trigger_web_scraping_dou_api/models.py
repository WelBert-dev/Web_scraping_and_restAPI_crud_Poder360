from django.db import models

class JournalJsonArrayOfDOU(models.Model):
    pubName = models.CharField(max_length=255)
    urlTitle = models.CharField(max_length=255, primary_key=True, unique=True)
    numberPage = models.IntegerField()
    subTitulo = models.TextField()
    titulo = models.TextField()
    title = models.TextField()
    pubDate = models.DateField()
    content = models.TextField()
    editionNumber = models.IntegerField()
    hierarchyLevelSize = models.IntegerField()
    artType = models.CharField(max_length=255)
    pubOrder = models.CharField(max_length=255)
    hierarchyStr = models.TextField()
    hierarchyList = models.JSONField()

    def __str__(self):
        return f"{self.pubName} - {self.pubDate}"
   
