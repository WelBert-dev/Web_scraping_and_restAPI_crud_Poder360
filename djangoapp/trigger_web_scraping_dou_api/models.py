from django.db import models

class JournalJsonArrayOfDOU(models.Model):
    id = models.AutoField(primary_key=True)
    pubName = models.CharField(null=True)
    urlTitle = models.CharField(unique=True)
    numberPage = models.IntegerField(null=True)
    subTitulo = models.TextField(null=True)
    titulo = models.TextField(null=True)
    title = models.TextField(null=True)
    pubDate = models.DateField(null=True)
    content = models.TextField(null=True)
    editionNumber = models.IntegerField(null=True)
    hierarchyLevelSize = models.IntegerField(null=True)
    artType = models.CharField(null=True)
    pubOrder = models.CharField(null=True)
    hierarchyStr = models.TextField(null=True)
    hierarchyList = models.JSONField(null=True)

    def __str__(self):
        return f"{self.pubName} - {self.pubDate}"
    
    
    
class DetailSingleJournalOfDOU(models.Model):
    id = models.AutoField(primary_key=True)
    versao_certificada = models.URLField(unique=False)
    publicado_dou_data = models.DateField(null=True)
    edicao_dou_data = models.CharField(null=True)
    secao_dou_data = models.CharField(null=True)
    orgao_dou_data = models.TextField(null=True)
    title = models.CharField(unique=False)
    paragrafos = models.TextField(null=True)
    assina = models.CharField(null=True)
    cargo = models.CharField(null=True)
    

    def __str__(self):
        return f"{self.versao_certificada} - {self.title}"
   
