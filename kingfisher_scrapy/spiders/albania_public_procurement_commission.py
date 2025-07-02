from kingfisher_scrapy.spiders.albania_public_procurement_commission_base import AlbaniaPublicProcurementCommissionBase


class AlbaniaPublicProcurementCommission(AlbaniaPublicProcurementCommissionBase):
    """
    Domain
      Komisioni i Prokurimit Publik (KPP) (Public Procurement Commission)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2021'.
      until_date
        Download only data until this year (YYYY format). Defaults to the current year.

    Bulk download documentation
      https://kpp.al/en/Historiku?nrVendimi=&OperatoriEkonmik=&idOperatori=&autoritetiKotraktues=&id=
    """

    name = "albania_public_procurement_commission"

    # BaseSpider
    default_from_date = "2021"

    # AlbaniaPublicProcurementCommissionBase
    base_url = "https://kpp.al/api/public/Decision/getBulkJsonByYear"
    date_param = "decision_date"
