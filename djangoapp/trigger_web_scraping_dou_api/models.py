from django.db import models

class JournalJsonArrayOfDOU(models.Model):
    id = models.AutoField(primary_key=True)
    pubName = models.CharField(max_length=255)
    urlTitle = models.CharField(max_length=255, unique=True)
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
    
    
    
class DetailSingleJournalOfDOU(models.Model):
    id = models.AutoField(primary_key=True)
    versao_certificada = models.URLField()
    publicado_dou_data = models.DateField()
    edicao_dou_data = models.CharField(max_length=10)
    secao_dou_data = models.CharField(max_length=10)
    orgao_dou_data = models.TextField()
    title = models.CharField(max_length=255)
    paragrafos = models.TextField()
    assina = models.CharField(max_length=255)
    cargo = models.CharField(max_length=255)
    

    def __str__(self):
        return f"{self.versao_certificada} - {self.title}"
   
