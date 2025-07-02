from kingfisher_scrapy.spiders.albania_public_procurement_commission_base import AlbaniaPublicProcurementCommissionBase


class AlbaniaPublicProcurementCommissionHistorical(AlbaniaPublicProcurementCommissionBase):
    """
    Domain
      Komisioni i Prokurimit Publik (KPP) (Public Procurement Commission)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2010'.
      until_date
        Download only data until this year (YYYY format). Defaults to '2020'.

    Bulk download documentation
      https://kpp.al/en/HistorikVendimesh?objektProkurimi=&viti=&vitiId=&muaji=&muajiId=
    """

    name = "albania_public_procurement_commission_historical"

    # BaseSpider
    default_from_date = "2010"
    default_until_date = "2020"
    skip_pluck = "Already covered (see code for details)"  # albania_public_procurement_commission

    # AlbaniaPublicProcurementCommissionBase
    base_url = "https://kpp.al/api/public/Decision/getHistoricBulkJsonByYear"
    date_param = "prot_date"
