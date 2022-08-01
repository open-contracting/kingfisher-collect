from kingfisher_scrapy.spiders.european_dynamics_saas_base import EuropeanDynamicsSaasBase


class NigeriaLagosState(EuropeanDynamicsSaasBase):
    """
    Domain
      Nigeria Lagos State Open Contracting Portal
    """
    name = 'nigeria_lagos_state'

    # EuropeanDynamicsSassBase
    base_url = 'https://lagosppaocds.azurewebsites.net/'
