from django.db import models
from .import_profile import ImportProfile


class ImportProfileMapping(models.Model):
    id = models.AutoField(primary_key=True)
    import_profile_id = models.ForeignKey(ImportProfile, on_delete=models.CASCADE)
    from_file_header = models.CharField(max_length=200)
    to_transaction_header = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Import Profile Mapping"
        verbose_name_plural = "Import Profile Mappings"
