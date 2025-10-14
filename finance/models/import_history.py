from django.db import models


class ImportHistory(models.Model):
    id = models.AutoField(primary_key=True)
    import_profile_id = models.ForeignKey('ImportProfile', on_delete=models.CASCADE)
    filename = models.CharField(max_length=1000, null=False)
    created = models.DateTimeField(auto_now_add=True)
    completion_datetime = models.DateTimeField(null=True)

    class Meta:
        verbose_name = "Import History"
        verbose_name_plural = "Import Histories"
