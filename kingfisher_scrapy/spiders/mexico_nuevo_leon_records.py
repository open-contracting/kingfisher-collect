from kingfisher_scrapy.spiders.mexico_nuevo_leon_base import MexicoNuevoLeonBase


class MexicoNuevoLeonRecords(MexicoNuevoLeonBase):
    """
    Bulk download documentation
      http://si.nl.gob.mx/transparencia/acerca-del-proyecto
    Spider arguments
      sample
        Downloads the rar file and send the set number of records to kingfisher process.
    """
    name = 'mexico_nuevo_leon_records'
    file_name_must_contain = 'RecordPackage'
    data_type = 'record_package'
    skip_pluck = 'Already covered (see code for details)'  # mexico_nuevo_leon_releases
