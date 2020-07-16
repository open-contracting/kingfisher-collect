from kingfisher_scrapy.spiders.mexico_nuevo_leon_base import MexicoNuevoLeonBase


class MexicoNuevoLeonReleases(MexicoNuevoLeonBase):
    """
    Bulk download documentation
      http://si.nl.gob.mx/transparencia/acerca-del-proyecto
    Spider arguments
      sample
        Downloads the rar file and sends 10 releases to kingfisher process.
    """
    name = 'mexico_nuevo_leon_releases'
    file_name_must_contain = 'ReleasePackage'
    data_type = 'release_package'
