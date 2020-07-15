from kingfisher_scrapy.spiders.mexico_nuevo_leon_base import \
    MexicoNuevoLeonBase


class MexicoNuevoLeonRecords(MexicoNuevoLeonBase):
    """
    Bulk download documentation
      http://si.nl.gob.mx/transparencia/acerca-del-proyecto
    Spider arguments
      sample
        Downloads the rar file and sends 10 records to kingfisher process.
    """
    name = 'mexico_nuevo_leon_records'
    file_name_contains = 'RecordPackage'
    data_type = 'record_package'
