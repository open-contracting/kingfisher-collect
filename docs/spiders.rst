Spiders
=======

In Kingfisher Collect, there is one spider per data source. Each data source exposes its data in different ways, contains data from different years, and covers different stages of the contracting process.

.. _spider-metadata:

Spider metadata
---------------

Below, we provide some of this information (metadata) for each spider. The meaning of the metadata is:

.. list-table::
   :header-rows: 1

   * - Metadata
     - Description
   * - Domain
     - The name of the IT system, jurisdiction, agency or program that is publishing the data. Some spiders have the same domain, in which case the difference between them is indicated in the suffix to the spider's name:

       .. list-table::
          :header-rows: 1

          * - Suffix
            - Description
          * - ``_releases``
            - Downloads individual releases or release packages
          * - ``_records``
            - Downloads individual records or record packages
          * - ``_bulk``
            - The data source is bulk data
          * - ``_historical``
            - The data source is historical data

   * - Caveats
     - Any noteworthy API or dataset limitations.
   * - Spider arguments
     - The :ref:`spider-arguments` the spider supports.
   * - Environment variables
     - The environment variables required to run the spider. If a data source requires account registration, a link is provided. You can set environment variables as, for example:

       .. code-block:: bash

          env NAME1=VALUE1 NAME2=VALUE2 scrapy crawl spider_name
   * - API documentation
     - The URL of the API's documentation.
   * - Bulk download documentation
     - The URL of any bulk download documentation.
   * - Swagger API documentation
     - The URL of the API's documentation, using `Swagger <https://swagger.io>`__.
   * - API endpoints
     - If official API documentation is unavailable, we provide some brief documentation.

.. _spider-arguments:

Spider arguments
----------------

A spider's behavior can be changed by setting *spider arguments*:

.. code-block:: bash

   scrapy crawl colombia -a NAME=VALUE

You can set multiple spider arguments:

.. code-block:: bash

   scrapy crawl colombia -a from_date=2015-01-01 -a until_date=2019-12-31

All spiders support these arguments:

.. list-table::
   :header-rows: 1

   * - Name
     - Description
     - Format
   * - ``sample``
     - Set the number of files and file items to download.
     - integer
   * - ``path``
     - Path components to append to each URL, if filters are implemented within the path. See also: :ref:`filter`.
     - string
   * - ``qs:*``
     - Query string parameters to append to each URL, for example: ``qs:parameter1=value1``. See also: :ref:`filter`.
     - string

.. note::

   If a source publishes release packages or record packages, the ``sample`` argument refers to the number of packages to download. 
 
   However, if a source publishes files that either:
 
   - Contain multiple release packages or record packages
   - Contain multiple releases or records that are not within a package

   Each file will be split into multiple file items. In this case, the ``sample`` argument refers to the number of file items (packages, releases or records) to download.

Some spiders support these arguments:

.. list-table::
   :header-rows: 1

   * - Name
     - Description
     - Format
   * - ``from_date``
     - Download data from this date onward. The spider might describe specific semantics (e.g. the relevant date is the date the contract was signed). Otherwise, the relevant date is the release date.
     - See spider
   * - ``until_date``
     - Download data until this date. The spider might describe specific semantics (e.g. the relevant date is the date the contract was signed). Otherwise, the relevant date is the release date.
     - See spider
   * - ``portal``
     - Download data from this portal.
     - See spider
   * - ``publisher``
     - Download data by this publisher.
     - See spider
   * - ``system``
     - Download data from this system.
     - See spider

Available data sources by country
---------------------------------

.. Do not edit past this line. Instead, run: `scrapy updatedocs`

Albania
~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.albania_public_procurement_commission.AlbaniaPublicProcurementCommission
   :no-members:

.. code-block:: bash

   scrapy crawl albania_public_procurement_commission

Argentina
~~~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.argentina_buenos_aires.ArgentinaBuenosAires
   :no-members:

.. code-block:: bash

   scrapy crawl argentina_buenos_aires

.. autoclass:: kingfisher_scrapy.spiders.argentina_mendoza_province_bulk.ArgentinaMendozaProvinceBulk
   :no-members:

.. code-block:: bash

   scrapy crawl argentina_mendoza_province_bulk

.. autoclass:: kingfisher_scrapy.spiders.argentina_vialidad.ArgentinaVialidad
   :no-members:

.. code-block:: bash

   scrapy crawl argentina_vialidad

Armenia
~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.armenia.Armenia
   :no-members:

.. code-block:: bash

   scrapy crawl armenia

Australia
~~~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.australia.Australia
   :no-members:

.. code-block:: bash

   scrapy crawl australia

.. autoclass:: kingfisher_scrapy.spiders.australia_new_south_wales.AustraliaNewSouthWales
   :no-members:

.. code-block:: bash

   scrapy crawl australia_new_south_wales

Austria
~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.austria_digiwhist.AustriaDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl austria_digiwhist

Belgium
~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.belgium_digiwhist.BelgiumDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl belgium_digiwhist

Bolivia
~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.bolivia_agetic.BoliviaAgetic
   :no-members:

.. code-block:: bash

   scrapy crawl bolivia_agetic

Bulgaria
~~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.bulgaria_digiwhist.BulgariaDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl bulgaria_digiwhist

Canada
~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.canada_buyandsell.CanadaBuyandsell
   :no-members:

.. code-block:: bash

   scrapy crawl canada_buyandsell

.. autoclass:: kingfisher_scrapy.spiders.canada_montreal.CanadaMontreal
   :no-members:

.. code-block:: bash

   scrapy crawl canada_montreal

.. autoclass:: kingfisher_scrapy.spiders.canada_quebec.CanadaQuebec
   :no-members:

.. code-block:: bash

   scrapy crawl canada_quebec

Chile
~~~~~

.. autoclass:: kingfisher_scrapy.spiders.chile_compra_api_records.ChileCompraAPIRecords
   :no-members:

.. code-block:: bash

   scrapy crawl chile_compra_api_records

.. autoclass:: kingfisher_scrapy.spiders.chile_compra_api_releases.ChileCompraAPIReleases
   :no-members:

.. code-block:: bash

   scrapy crawl chile_compra_api_releases

.. autoclass:: kingfisher_scrapy.spiders.chile_compra_bulk.ChileCompraBulk
   :no-members:

.. code-block:: bash

   scrapy crawl chile_compra_bulk

.. autoclass:: kingfisher_scrapy.spiders.chile_public_works_bulk.ChilePublicWorksBulk
   :no-members:

.. code-block:: bash

   scrapy crawl chile_public_works_bulk

Colombia
~~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.colombia_ani_records.ColombiaANIRecords
   :no-members:

.. code-block:: bash

   scrapy crawl colombia_ani_records

.. autoclass:: kingfisher_scrapy.spiders.colombia_api.ColombiaAPI
   :no-members:

.. code-block:: bash

   scrapy crawl colombia_api

.. autoclass:: kingfisher_scrapy.spiders.colombia_bulk.ColombiaBulk
   :no-members:

.. code-block:: bash

   scrapy crawl colombia_bulk

Costa Rica
~~~~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.costa_rica_poder_judicial_records.CostaRicaPoderJudicialRecords
   :no-members:

.. code-block:: bash

   scrapy crawl costa_rica_poder_judicial_records

.. autoclass:: kingfisher_scrapy.spiders.costa_rica_poder_judicial_releases.CostaRicaPoderJudicialReleases
   :no-members:

.. code-block:: bash

   scrapy crawl costa_rica_poder_judicial_releases

Croatia
~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.croatia.Croatia
   :no-members:

.. code-block:: bash

   scrapy crawl croatia

.. autoclass:: kingfisher_scrapy.spiders.croatia_digiwhist.CroatiaDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl croatia_digiwhist

Cyprus
~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.cyprus_digiwhist.CyprusDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl cyprus_digiwhist

Czech Republic
~~~~~~~~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.czech_republic_digiwhist.CzechRepublicDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl czech_republic_digiwhist

Denmark
~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.denmark_digiwhist.DenmarkDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl denmark_digiwhist

Dominican Republic
~~~~~~~~~~~~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.dominican_republic_api.DominicanRepublicAPI
   :no-members:

.. code-block:: bash

   scrapy crawl dominican_republic_api

Ecuador
~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.ecuador_sercop_api.EcuadorSERCOPAPI
   :no-members:

.. code-block:: bash

   scrapy crawl ecuador_sercop_api

.. autoclass:: kingfisher_scrapy.spiders.ecuador_sercop_bulk.EcuadorSERCOPBulk
   :no-members:

.. code-block:: bash

   scrapy crawl ecuador_sercop_bulk

Estonia
~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.estonia_digiwhist.EstoniaDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl estonia_digiwhist

Europe
~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.europe_ted_digiwhist.EuropeTEDDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl europe_ted_digiwhist

Finland
~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.finland_digiwhist.FinlandDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl finland_digiwhist

France
~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.france.France
   :no-members:

.. code-block:: bash

   scrapy crawl france

.. autoclass:: kingfisher_scrapy.spiders.france_digiwhist.FranceDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl france_digiwhist

Georgia
~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.georgia_digiwhist.GeorgiaDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl georgia_digiwhist

.. autoclass:: kingfisher_scrapy.spiders.georgia_opendata.GeorgiaOpendata
   :no-members:

.. code-block:: bash

   scrapy crawl georgia_opendata

.. autoclass:: kingfisher_scrapy.spiders.georgia_records.GeorgiaRecords
   :no-members:

.. code-block:: bash

   scrapy crawl georgia_records

.. autoclass:: kingfisher_scrapy.spiders.georgia_releases.GeorgiaReleases
   :no-members:

.. code-block:: bash

   scrapy crawl georgia_releases

Germany
~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.germany.Germany
   :no-members:

.. code-block:: bash

   scrapy crawl germany

.. autoclass:: kingfisher_scrapy.spiders.germany_digiwhist.GermanyDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl germany_digiwhist

Ghana
~~~~~

.. autoclass:: kingfisher_scrapy.spiders.ghana.Ghana
   :no-members:

.. code-block:: bash

   scrapy crawl ghana

Greece
~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.greece_digiwhist.GreeceDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl greece_digiwhist

Guatemala
~~~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.guatemala_bulk.GuatemalaBulk
   :no-members:

.. code-block:: bash

   scrapy crawl guatemala_bulk

Honduras
~~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.honduras_iaip.HondurasIAIP
   :no-members:

.. code-block:: bash

   scrapy crawl honduras_iaip

.. autoclass:: kingfisher_scrapy.spiders.honduras_oncae.HondurasONCAE
   :no-members:

.. code-block:: bash

   scrapy crawl honduras_oncae

.. autoclass:: kingfisher_scrapy.spiders.honduras_portal_api_records.HondurasPortalAPIRecords
   :no-members:

.. code-block:: bash

   scrapy crawl honduras_portal_api_records

.. autoclass:: kingfisher_scrapy.spiders.honduras_portal_api_releases.HondurasPortalAPIReleases
   :no-members:

.. code-block:: bash

   scrapy crawl honduras_portal_api_releases

.. autoclass:: kingfisher_scrapy.spiders.honduras_portal_bulk.HondurasPortalBulk
   :no-members:

.. code-block:: bash

   scrapy crawl honduras_portal_bulk

.. autoclass:: kingfisher_scrapy.spiders.honduras_sefin_api.HondurasSEFINAPI
   :no-members:

.. code-block:: bash

   scrapy crawl honduras_sefin_api

.. autoclass:: kingfisher_scrapy.spiders.honduras_sefin_bulk.HondurasSEFINBulk
   :no-members:

.. code-block:: bash

   scrapy crawl honduras_sefin_bulk

Hungary
~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.hungary_digiwhist.HungaryDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl hungary_digiwhist

Iceland
~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.iceland_digiwhist.IcelandDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl iceland_digiwhist

India
~~~~~

.. autoclass:: kingfisher_scrapy.spiders.india_assam.IndiaAssam
   :no-members:

.. code-block:: bash

   scrapy crawl india_assam

.. autoclass:: kingfisher_scrapy.spiders.india_assam_civic_data_lab.IndiaAssamCivicDataLab
   :no-members:

.. code-block:: bash

   scrapy crawl india_assam_civic_data_lab

.. autoclass:: kingfisher_scrapy.spiders.india_himachal_pradesh_civic_data_lab.IndiaHimachalPradeshCivicDataLab
   :no-members:

.. code-block:: bash

   scrapy crawl india_himachal_pradesh_civic_data_lab

Indonesia
~~~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.indonesia_opentender.IndonesiaOpentender
   :no-members:

.. code-block:: bash

   scrapy crawl indonesia_opentender

Ireland
~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.ireland_digiwhist.IrelandDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl ireland_digiwhist

Italy
~~~~~

.. autoclass:: kingfisher_scrapy.spiders.italy_anac.ItalyANAC
   :no-members:

.. code-block:: bash

   scrapy crawl italy_anac

.. autoclass:: kingfisher_scrapy.spiders.italy_digiwhist.ItalyDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl italy_digiwhist

.. autoclass:: kingfisher_scrapy.spiders.italy_ministry_of_infrastructure_and_transport.ItalyMinistryOfInfrastructureAndTransport
   :no-members:

.. code-block:: bash

   scrapy crawl italy_ministry_of_infrastructure_and_transport

Kenya
~~~~~

.. autoclass:: kingfisher_scrapy.spiders.kenya_ppra.KenyaPPRA
   :no-members:

.. code-block:: bash

   scrapy crawl kenya_ppra

Kosovo
~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.kosovo.Kosovo
   :no-members:

.. code-block:: bash

   scrapy crawl kosovo

Latvia
~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.latvia_digiwhist.LatviaDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl latvia_digiwhist

Lithuania
~~~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.lithuania_digiwhist.LithuaniaDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl lithuania_digiwhist

Luxembourg
~~~~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.luxembourg_digiwhist.LuxembourgDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl luxembourg_digiwhist

Malta
~~~~~

.. autoclass:: kingfisher_scrapy.spiders.malta.Malta
   :no-members:

.. code-block:: bash

   scrapy crawl malta

.. autoclass:: kingfisher_scrapy.spiders.malta_digiwhist.MaltaDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl malta_digiwhist

Mexico
~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.mexico_administracion_publica_federal_api.MexicoAdministracionPublicaFederalAPI
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_administracion_publica_federal_api

.. autoclass:: kingfisher_scrapy.spiders.mexico_administracion_publica_federal_bulk.MexicoAdministracionPublicaFederalBulk
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_administracion_publica_federal_bulk

.. autoclass:: kingfisher_scrapy.spiders.mexico_aguascalientes_plataforma_digital_estatal.MexicoAguascalientesPlataformaDigitalEstatal
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_aguascalientes_plataforma_digital_estatal

.. autoclass:: kingfisher_scrapy.spiders.mexico_aguascalientes_sesea_plataforma_digital_nacional.MexicoAguascalientesSESEAPlataformaDigitalNacional
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_aguascalientes_sesea_plataforma_digital_nacional

.. autoclass:: kingfisher_scrapy.spiders.mexico_durango_idaip.MexicoDurangoIDAIP
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_durango_idaip

.. autoclass:: kingfisher_scrapy.spiders.mexico_guadalajara.MexicoGuadalajara
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_guadalajara

.. autoclass:: kingfisher_scrapy.spiders.mexico_guanajuato_iacip.MexicoGuanajuatoIACIP
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_guanajuato_iacip

.. autoclass:: kingfisher_scrapy.spiders.mexico_inai_api.MexicoINAIAPI
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_inai_api

.. autoclass:: kingfisher_scrapy.spiders.mexico_mexico_city_infocdmx.MexicoMexicoCityINFOCDMX
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_mexico_city_infocdmx

.. autoclass:: kingfisher_scrapy.spiders.mexico_mexico_state_infoem.MexicoMexicoStateINFOEM
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_mexico_state_infoem

.. autoclass:: kingfisher_scrapy.spiders.mexico_mexico_state_sesaemm_plataforma_digital_nacional.MexicoMexicoStateSESAEMMPlataformaDigitalNacional
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_mexico_state_sesaemm_plataforma_digital_nacional

.. autoclass:: kingfisher_scrapy.spiders.mexico_michoacan_sesea_plataforma_digital_nacional.MexicoMichoacanSESEAPlataformaDigitalNacional
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_michoacan_sesea_plataforma_digital_nacional

.. autoclass:: kingfisher_scrapy.spiders.mexico_nuevo_leon.MexicoNuevoLeon
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_nuevo_leon

.. autoclass:: kingfisher_scrapy.spiders.mexico_nuevo_leon_cotai.MexicoNuevoLeonCOTAI
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_nuevo_leon_cotai

.. autoclass:: kingfisher_scrapy.spiders.mexico_nuevo_leon_infra_abierta_records.MexicoNuevoLeonInfraAbiertaRecords
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_nuevo_leon_infra_abierta_records

.. autoclass:: kingfisher_scrapy.spiders.mexico_nuevo_leon_infra_abierta_releases.MexicoNuevoLeonInfraAbiertaReleases
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_nuevo_leon_infra_abierta_releases

.. autoclass:: kingfisher_scrapy.spiders.mexico_puebla_state_seseap_plataforma_digital_nacional.MexicoPueblaStateSESEAPPlataformaDigitalNacional
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_puebla_state_seseap_plataforma_digital_nacional

.. autoclass:: kingfisher_scrapy.spiders.mexico_quien_es_quien_releases.MexicoQuienEsQuienReleases
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_quien_es_quien_releases

.. autoclass:: kingfisher_scrapy.spiders.mexico_quintana_roo_idaip.MexicoQuintanaRooIDAIP
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_quintana_roo_idaip

.. autoclass:: kingfisher_scrapy.spiders.mexico_quintana_roo_sesaeqroo_plataforma_digital_nacional.MexicoQuintanaRooSESAEQROOPlataformaDigitalNacional
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_quintana_roo_sesaeqroo_plataforma_digital_nacional

.. autoclass:: kingfisher_scrapy.spiders.mexico_shcp_plataforma_digital_nacional.MexicoSHCPPlataformaDigitalNacional
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_shcp_plataforma_digital_nacional

.. autoclass:: kingfisher_scrapy.spiders.mexico_veracruz_ivai.MexicoVeracruzIVAI
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_veracruz_ivai

.. autoclass:: kingfisher_scrapy.spiders.mexico_veracruz_state_sesea_plataforma_digital_nacional.MexicoVeracruzStateSESEAPlataformaDigitalNacional
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_veracruz_state_sesea_plataforma_digital_nacional

.. autoclass:: kingfisher_scrapy.spiders.mexico_yucatan_inaip.MexicoYucatanINAIP
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_yucatan_inaip

.. autoclass:: kingfisher_scrapy.spiders.mexico_zacatecas_izai.MexicoZacatecasIZAI
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_zacatecas_izai

Moldova
~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.moldova.Moldova
   :no-members:

.. code-block:: bash

   scrapy crawl moldova

Nepal
~~~~~

.. autoclass:: kingfisher_scrapy.spiders.nepal.Nepal
   :no-members:

.. code-block:: bash

   scrapy crawl nepal

.. autoclass:: kingfisher_scrapy.spiders.nepal_dhangadhi.NepalDhangadhi
   :no-members:

.. code-block:: bash

   scrapy crawl nepal_dhangadhi

Netherlands
~~~~~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.netherlands.Netherlands
   :no-members:

.. code-block:: bash

   scrapy crawl netherlands

.. autoclass:: kingfisher_scrapy.spiders.netherlands_digiwhist.NetherlandsDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl netherlands_digiwhist

Nigeria
~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.nigeria_abia_state.NigeriaAbiaState
   :no-members:

.. code-block:: bash

   scrapy crawl nigeria_abia_state

.. autoclass:: kingfisher_scrapy.spiders.nigeria_anambra_state.NigeriaAnambraState
   :no-members:

.. code-block:: bash

   scrapy crawl nigeria_anambra_state

.. autoclass:: kingfisher_scrapy.spiders.nigeria_cross_river_state_records.NigeriaCrossRiverStateRecords
   :no-members:

.. code-block:: bash

   scrapy crawl nigeria_cross_river_state_records

.. autoclass:: kingfisher_scrapy.spiders.nigeria_cross_river_state_releases.NigeriaCrossRiverStateReleases
   :no-members:

.. code-block:: bash

   scrapy crawl nigeria_cross_river_state_releases

.. autoclass:: kingfisher_scrapy.spiders.nigeria_ebonyi_state.NigeriaEbonyiState
   :no-members:

.. code-block:: bash

   scrapy crawl nigeria_ebonyi_state

.. autoclass:: kingfisher_scrapy.spiders.nigeria_ekiti_state.NigeriaEkitiState
   :no-members:

.. code-block:: bash

   scrapy crawl nigeria_ekiti_state

.. autoclass:: kingfisher_scrapy.spiders.nigeria_enugu_state.NigeriaEnuguState
   :no-members:

.. code-block:: bash

   scrapy crawl nigeria_enugu_state

.. autoclass:: kingfisher_scrapy.spiders.nigeria_kano_state.NigeriaKanoState
   :no-members:

.. code-block:: bash

   scrapy crawl nigeria_kano_state

.. autoclass:: kingfisher_scrapy.spiders.nigeria_lagos_state.NigeriaLagosState
   :no-members:

.. code-block:: bash

   scrapy crawl nigeria_lagos_state

.. autoclass:: kingfisher_scrapy.spiders.nigeria_osun_state.NigeriaOsunState
   :no-members:

.. code-block:: bash

   scrapy crawl nigeria_osun_state

.. autoclass:: kingfisher_scrapy.spiders.nigeria_oyo_state.NigeriaOyoState
   :no-members:

.. code-block:: bash

   scrapy crawl nigeria_oyo_state

.. autoclass:: kingfisher_scrapy.spiders.nigeria_plateau_state.NigeriaPlateauState
   :no-members:

.. code-block:: bash

   scrapy crawl nigeria_plateau_state

.. autoclass:: kingfisher_scrapy.spiders.nigeria_portal.NigeriaPortal
   :no-members:

.. code-block:: bash

   scrapy crawl nigeria_portal

North Macedonia
~~~~~~~~~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.north_macedonia_digiwhist.NorthMacedoniaDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl north_macedonia_digiwhist

Norway
~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.norway_digiwhist.NorwayDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl norway_digiwhist

Openopps
~~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.openopps.Openopps
   :no-members:

.. code-block:: bash

   env KINGFISHER_OPENOPPS_USERNAME=... KINGFISHER_OPENOPPS_PASSWORD=... scrapy crawl openopps

Pakistan
~~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.pakistan_ppra_api.PakistanPPRAAPI
   :no-members:

.. code-block:: bash

   scrapy crawl pakistan_ppra_api

.. autoclass:: kingfisher_scrapy.spiders.pakistan_ppra_bulk.PakistanPPRABulk
   :no-members:

.. code-block:: bash

   scrapy crawl pakistan_ppra_bulk

Panama
~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.panama_dgcp_bulk.PanamaDGCPBulk
   :no-members:

.. code-block:: bash

   scrapy crawl panama_dgcp_bulk

.. autoclass:: kingfisher_scrapy.spiders.panama_dgcp_records.PanamaDGCPRecords
   :no-members:

.. code-block:: bash

   scrapy crawl panama_dgcp_records

.. autoclass:: kingfisher_scrapy.spiders.panama_dgcp_releases.PanamaDGCPReleases
   :no-members:

.. code-block:: bash

   scrapy crawl panama_dgcp_releases

Paraguay
~~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.paraguay_dncp_records.ParaguayDNCPRecords
   :no-members:

.. code-block:: bash

   env KINGFISHER_PARAGUAY_DNCP_REQUEST_TOKEN=... scrapy crawl paraguay_dncp_records

.. autoclass:: kingfisher_scrapy.spiders.paraguay_dncp_releases.ParaguayDNCPReleases
   :no-members:

.. code-block:: bash

   env KINGFISHER_PARAGUAY_DNCP_REQUEST_TOKEN=... scrapy crawl paraguay_dncp_releases

.. autoclass:: kingfisher_scrapy.spiders.paraguay_hacienda.ParaguayHacienda
   :no-members:

.. code-block:: bash

   env KINGFISHER_PARAGUAY_HACIENDA_REQUEST_TOKEN=... KINGFISHER_PARAGUAY_HACIENDA_CLIENT_SECRET=... scrapy crawl paraguay_hacienda

Peru
~~~~

.. autoclass:: kingfisher_scrapy.spiders.peru_compras.PeruCompras
   :no-members:

.. code-block:: bash

   scrapy crawl peru_compras

.. autoclass:: kingfisher_scrapy.spiders.peru_compras_bulk.PeruComprasBulk
   :no-members:

.. code-block:: bash

   scrapy crawl peru_compras_bulk

.. autoclass:: kingfisher_scrapy.spiders.peru_osce_api_records.PeruOSCEAPIRecords
   :no-members:

.. code-block:: bash

   scrapy crawl peru_osce_api_records

.. autoclass:: kingfisher_scrapy.spiders.peru_osce_api_releases.PeruOSCEAPIReleases
   :no-members:

.. code-block:: bash

   scrapy crawl peru_osce_api_releases

.. autoclass:: kingfisher_scrapy.spiders.peru_osce_bulk.PeruOSCEBulk
   :no-members:

.. code-block:: bash

   scrapy crawl peru_osce_bulk

Poland
~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.poland_digiwhist.PolandDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl poland_digiwhist

Portugal
~~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.portugal_digiwhist.PortugalDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl portugal_digiwhist

.. autoclass:: kingfisher_scrapy.spiders.portugal_records.PortugalRecords
   :no-members:

.. code-block:: bash

   scrapy crawl portugal_records

.. autoclass:: kingfisher_scrapy.spiders.portugal_releases.PortugalReleases
   :no-members:

.. code-block:: bash

   scrapy crawl portugal_releases

Romania
~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.romania_digiwhist.RomaniaDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl romania_digiwhist

Rwanda
~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.rwanda.Rwanda
   :no-members:

.. code-block:: bash

   scrapy crawl rwanda

Serbia
~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.serbia_digiwhist.SerbiaDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl serbia_digiwhist

Slovakia
~~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.slovakia_digiwhist.SlovakiaDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl slovakia_digiwhist

Slovenia
~~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.slovenia.Slovenia
   :no-members:

.. code-block:: bash

   scrapy crawl slovenia

.. autoclass:: kingfisher_scrapy.spiders.slovenia_digiwhist.SloveniaDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl slovenia_digiwhist

South Africa
~~~~~~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.south_africa_national_treasury_api.SouthAfricaNationalTreasuryAPI
   :no-members:

.. code-block:: bash

   scrapy crawl south_africa_national_treasury_api

Spain
~~~~~

.. autoclass:: kingfisher_scrapy.spiders.spain_digiwhist.SpainDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl spain_digiwhist

.. autoclass:: kingfisher_scrapy.spiders.spain_zaragoza.SpainZaragoza
   :no-members:

.. code-block:: bash

   scrapy crawl spain_zaragoza

Sweden
~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.sweden_digiwhist.SwedenDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl sweden_digiwhist

Switzerland
~~~~~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.switzerland_digiwhist.SwitzerlandDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl switzerland_digiwhist

Uganda
~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.uganda_releases.UgandaReleases
   :no-members:

.. code-block:: bash

   scrapy crawl uganda_releases

Ukraine
~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.ukraine.Ukraine
   :no-members:

.. code-block:: bash

   scrapy crawl ukraine

United Kingdom
~~~~~~~~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.united_kingdom_contracts_finder_records.UnitedKingdomContractsFinderRecords
   :no-members:

.. code-block:: bash

   scrapy crawl united_kingdom_contracts_finder_records

.. autoclass:: kingfisher_scrapy.spiders.united_kingdom_contracts_finder_releases.UnitedKingdomContractsFinderReleases
   :no-members:

.. code-block:: bash

   scrapy crawl united_kingdom_contracts_finder_releases

.. autoclass:: kingfisher_scrapy.spiders.united_kingdom_digiwhist.UnitedKingdomDigiwhist
   :no-members:

.. code-block:: bash

   scrapy crawl united_kingdom_digiwhist

.. autoclass:: kingfisher_scrapy.spiders.united_kingdom_fts.UnitedKingdomFTS
   :no-members:

.. code-block:: bash

   scrapy crawl united_kingdom_fts

.. autoclass:: kingfisher_scrapy.spiders.united_kingdom_fts_test.UnitedKingdomFTSTest
   :no-members:

.. code-block:: bash

   scrapy crawl united_kingdom_fts_test

.. autoclass:: kingfisher_scrapy.spiders.united_kingdom_scotland.UnitedKingdomScotland
   :no-members:

.. code-block:: bash

   scrapy crawl united_kingdom_scotland

.. autoclass:: kingfisher_scrapy.spiders.united_kingdom_wales.UnitedKingdomWales
   :no-members:

.. code-block:: bash

   scrapy crawl united_kingdom_wales

Uruguay
~~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.uruguay_historical.UruguayHistorical
   :no-members:

.. code-block:: bash

   scrapy crawl uruguay_historical

.. autoclass:: kingfisher_scrapy.spiders.uruguay_records.UruguayRecords
   :no-members:

.. code-block:: bash

   scrapy crawl uruguay_records

.. autoclass:: kingfisher_scrapy.spiders.uruguay_releases.UruguayReleases
   :no-members:

.. code-block:: bash

   scrapy crawl uruguay_releases

Zambia
~~~~~~

.. autoclass:: kingfisher_scrapy.spiders.zambia.Zambia
   :no-members:

.. code-block:: bash

   scrapy crawl zambia
