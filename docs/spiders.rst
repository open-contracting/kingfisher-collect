Spiders
=======

.. _spider-metadata:

Spider metadata
---------------

Below, we provide some metadata for each spider. The meaning of the metadata is:

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Metadata
     - Description
   * - Domain
     - The name of the IT system, jurisdiction, agency or program that is publishing the data. Some spiders have the same domain, in which case the difference between them is indicated in the suffix to the spider's name:

       .. list-table::
          :header-rows: 1
          :widths: auto

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
   :widths: auto

   * - Name
     - Description
     - Format
   * - ``sample``
     - Set the number of files and file items to download.
     - integer

Some spiders support these arguments:

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Name
     - Description
     - Format
   * - ``from_date``
     - Download data from this date onward. The spider might describe specific semantics (e.g. the relevant date is the date the contract was signed).
     - See spider
   * - ``until_date``
     - Download data until this date. The spider might describe specific semantics (e.g. the relevant date is the date the contract was signed).
     - See spider
   * - ``year``
     - Download data from this year.
     - integer
   * - ``start_page``
     - Download data from this page onward.
     - integer
   * - ``publisher``
     - Download data by this publisher.
     - See spider
   * - ``system``
     - Download data from this system.
     - See spider

.. Do not edit past this line. Instead, run: `scrapy updatedocs`

Afghanistan
-----------

.. autoclass:: kingfisher_scrapy.spiders.afghanistan_records.AfghanistanRecords
   :no-members:

.. code-block:: bash

   scrapy crawl afghanistan_records

.. autoclass:: kingfisher_scrapy.spiders.afghanistan_releases.AfghanistanReleases
   :no-members:

.. code-block:: bash

   scrapy crawl afghanistan_releases

Argentina
---------

.. autoclass:: kingfisher_scrapy.spiders.argentina_buenos_aires.ArgentinaBuenosAires
   :no-members:

.. code-block:: bash

   scrapy crawl argentina_buenos_aires

.. autoclass:: kingfisher_scrapy.spiders.argentina_vialidad.ArgentinaVialidad
   :no-members:

.. code-block:: bash

   scrapy crawl argentina_vialidad

Armenia
-------

.. autoclass:: kingfisher_scrapy.spiders.armenia.Armenia
   :no-members:

.. code-block:: bash

   scrapy crawl armenia

Australia
---------

.. autoclass:: kingfisher_scrapy.spiders.australia.Australia
   :no-members:

.. code-block:: bash

   scrapy crawl australia

.. autoclass:: kingfisher_scrapy.spiders.australia_nsw.AustraliaNSW
   :no-members:

.. code-block:: bash

   scrapy crawl australia_nsw

Canada
------

.. autoclass:: kingfisher_scrapy.spiders.canada_buyandsell.CanadaBuyAndSell
   :no-members:

.. code-block:: bash

   scrapy crawl canada_buyandsell

.. autoclass:: kingfisher_scrapy.spiders.canada_montreal.CanadaMontreal
   :no-members:

.. code-block:: bash

   scrapy crawl canada_montreal

Chile
-----

.. autoclass:: kingfisher_scrapy.spiders.chile_compra_bulk.ChileCompraBulk
   :no-members:

.. code-block:: bash

   scrapy crawl chile_compra_bulk

.. autoclass:: kingfisher_scrapy.spiders.chile_compra_records.ChileCompraRecords
   :no-members:

.. code-block:: bash

   scrapy crawl chile_compra_records

.. autoclass:: kingfisher_scrapy.spiders.chile_compra_releases.ChileCompraReleases
   :no-members:

.. code-block:: bash

   scrapy crawl chile_compra_releases

Colombia
--------

.. autoclass:: kingfisher_scrapy.spiders.colombia.Colombia
   :no-members:

.. code-block:: bash

   scrapy crawl colombia

.. autoclass:: kingfisher_scrapy.spiders.colombia_bulk.ColombiaBulk
   :no-members:

.. code-block:: bash

   scrapy crawl colombia_bulk

Costa Rica
----------

.. autoclass:: kingfisher_scrapy.spiders.costa_rica_poder_judicial_records.CostaRicaPoderJudicialRecords
   :no-members:

.. code-block:: bash

   scrapy crawl costa_rica_poder_judicial_records

.. autoclass:: kingfisher_scrapy.spiders.costa_rica_poder_judicial_releases.CostaRicaPoderJudicialReleases
   :no-members:

.. code-block:: bash

   scrapy crawl costa_rica_poder_judicial_releases

Digiwhist
---------

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_armenia.DigiwhistArmenia
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_armenia

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_austria.DigiwhistAustria
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_austria

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_belgium.DigiwhistBelgium
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_belgium

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_bulgaria.DigiwhistBulgaria
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_bulgaria

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_croatia.DigiwhistCroatia
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_croatia

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_cyprus.DigiwhistCyprus
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_cyprus

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_czech_republic.DigiwhistCzechRepublic
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_czech_republic

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_denmark.DigiwhistDenmarkRepublic
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_denmark

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_estonia.DigiwhistEstoniaRepublic
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_estonia

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_finland.DigiwhistFinlandRepublic
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_finland

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_france.DigiwhistFranceRepublic
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_france

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_georgia.DigiwhistGeorgiaRepublic
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_georgia

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_germany.DigiwhistGermanyRepublic
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_germany

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_greece.DigiwhistGreeceRepublic
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_greece

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_hungary.DigiwhistHungaryRepublic
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_hungary

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_iceland.DigiwhistIcelandRepublic
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_iceland

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_ireland.DigiwhistIrelandRepublic
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_ireland

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_italy.DigiwhistItalyRepublic
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_italy

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_latvia.DigiwhistLatviaRepublic
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_latvia

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_lithuania.DigiwhistLithuaniaRepublic
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_lithuania

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_luxembourg.DigiwhistLuxembourgRepublic
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_luxembourg

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_malta.DigiwhistMaltaRepublic
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_malta

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_netherlands.DigiwhistNetherlandsRepublic
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_netherlands

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_norway.DigiwhistNorwayRepublic
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_norway

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_poland.DigiwhistPolandRepublic
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_poland

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_portugal.DigiwhistPortugalRepublic
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_portugal

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_romania.DigiwhistRomaniaRepublic
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_romania

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_serbia.DigiwhistSerbiaRepublic
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_serbia

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_slovakia.DigiwhistSlovakiaRepublic
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_slovakia

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_slovenia.DigiwhistSloveniaRepublic
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_slovenia

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_spain.DigiwhistSpainRepublic
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_spain

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_sweden.DigiwhistSwedenRepublic
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_sweden

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_switzerland.DigiwhistSwitzerlandRepublic
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_switzerland

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_united_kingdom.DigiwhistUnitedKingdomRepublic
   :no-members:

.. code-block:: bash

   scrapy crawl digiwhist_united_kingdom

Dominican Republic
------------------

.. autoclass:: kingfisher_scrapy.spiders.dominican_republic.DominicanRepublic
   :no-members:

.. code-block:: bash

   scrapy crawl dominican_republic

.. autoclass:: kingfisher_scrapy.spiders.dominican_republic_api.DominicanRepublicPortal
   :no-members:

.. code-block:: bash

   scrapy crawl dominican_republic_api

Ecuador
-------

.. autoclass:: kingfisher_scrapy.spiders.ecuador_emergency.EcuadorEmergency
   :no-members:

.. code-block:: bash

   scrapy crawl ecuador_emergency

France
------

.. autoclass:: kingfisher_scrapy.spiders.france.France
   :no-members:

.. code-block:: bash

   scrapy crawl france

Georgia
-------

.. autoclass:: kingfisher_scrapy.spiders.georgia_opendata.GeorgiaOpenData
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

Honduras
--------

.. autoclass:: kingfisher_scrapy.spiders.honduras_cost.HondurasCoST
   :no-members:

.. code-block:: bash

   scrapy crawl honduras_cost

.. autoclass:: kingfisher_scrapy.spiders.honduras_oncae.HondurasONCAE
   :no-members:

.. code-block:: bash

   scrapy crawl honduras_oncae

.. autoclass:: kingfisher_scrapy.spiders.honduras_portal_bulk_files.HondurasPortalBulkFiles
   :no-members:

.. code-block:: bash

   scrapy crawl honduras_portal_bulk_files

.. autoclass:: kingfisher_scrapy.spiders.honduras_portal_records.HondurasPortalRecords
   :no-members:

.. code-block:: bash

   scrapy crawl honduras_portal_records

.. autoclass:: kingfisher_scrapy.spiders.honduras_portal_releases.HondurasPortalReleases
   :no-members:

.. code-block:: bash

   scrapy crawl honduras_portal_releases

Indonesia
---------

.. autoclass:: kingfisher_scrapy.spiders.indonesia_bandung.IndonesiaBandung
   :no-members:

.. code-block:: bash

   scrapy crawl indonesia_bandung

Kenya
-----

.. autoclass:: kingfisher_scrapy.spiders.kenya_makueni.KenyaMakueni
   :no-members:

.. code-block:: bash

   scrapy crawl kenya_makueni

Kyrgyzstan
----------

.. autoclass:: kingfisher_scrapy.spiders.kyrgyzstan.Kyrgyzstan
   :no-members:

.. code-block:: bash

   scrapy crawl kyrgyzstan

Malta
-----

.. autoclass:: kingfisher_scrapy.spiders.malta.Malta
   :no-members:

.. code-block:: bash

   scrapy crawl malta

Mexico
------

.. autoclass:: kingfisher_scrapy.spiders.mexico_administracion_publica_federal.MexicoAdministracionPublicaFederal
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_administracion_publica_federal

.. autoclass:: kingfisher_scrapy.spiders.mexico_grupo_aeroporto.MexicoGrupoAeroporto
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_grupo_aeroporto

.. autoclass:: kingfisher_scrapy.spiders.mexico_inai.MexicoINAI
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_inai

.. autoclass:: kingfisher_scrapy.spiders.mexico_inai_portal.MexicoINAIPortal
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_inai_portal

.. autoclass:: kingfisher_scrapy.spiders.mexico_nuevo_leon_records.MexicoNuevoLeonRecords
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_nuevo_leon_records

.. autoclass:: kingfisher_scrapy.spiders.mexico_nuevo_leon_releases.MexicoNuevoLeonReleases
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_nuevo_leon_releases

.. autoclass:: kingfisher_scrapy.spiders.mexico_quien_es_quien.MexicoQuienEsQuien
   :no-members:

.. code-block:: bash

   scrapy crawl mexico_quien_es_quien

Moldova
-------

.. autoclass:: kingfisher_scrapy.spiders.moldova.Moldova
   :no-members:

.. code-block:: bash

   scrapy crawl moldova

.. autoclass:: kingfisher_scrapy.spiders.moldova_mtender.MoldovaMTender
   :no-members:

.. code-block:: bash

   scrapy crawl moldova_mtender

.. autoclass:: kingfisher_scrapy.spiders.moldova_old.MoldovaOld
   :no-members:

.. code-block:: bash

   scrapy crawl moldova_old

Nepal
-----

.. autoclass:: kingfisher_scrapy.spiders.nepal_dhangadhi.NepalDhangadhi
   :no-members:

.. code-block:: bash

   scrapy crawl nepal_dhangadhi

.. autoclass:: kingfisher_scrapy.spiders.nepal_portal.NepalPortal
   :no-members:

.. code-block:: bash

   scrapy crawl nepal_portal

Nicaragua
---------

.. autoclass:: kingfisher_scrapy.spiders.nicaragua_solid_waste.NicaraguaSolidWaste
   :no-members:

.. code-block:: bash

   scrapy crawl nicaragua_solid_waste

Nigeria
-------

.. autoclass:: kingfisher_scrapy.spiders.nigeria_budeshi_records.NigeriaBudeshiRecords
   :no-members:

.. code-block:: bash

   scrapy crawl nigeria_budeshi_records

.. autoclass:: kingfisher_scrapy.spiders.nigeria_budeshi_releases.NigeriaBudeshiReleases
   :no-members:

.. code-block:: bash

   scrapy crawl nigeria_budeshi_releases

.. autoclass:: kingfisher_scrapy.spiders.nigeria_portal.NigeriaPortal
   :no-members:

.. code-block:: bash

   scrapy crawl nigeria_portal

Openopps
--------

.. autoclass:: kingfisher_scrapy.spiders.openopps.OpenOpps
   :no-members:

.. code-block:: bash

   env KINGFISHER_OPENOPPS_USERNAME=... KINGFISHER_OPENOPPS_PASSWORD=... scrapy crawl openopps

Paraguay
--------

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

Portugal
--------

.. autoclass:: kingfisher_scrapy.spiders.portugal.Portugal
   :no-members:

.. code-block:: bash

   scrapy crawl portugal

.. autoclass:: kingfisher_scrapy.spiders.portugal_records.PortugalRecords
   :no-members:

.. code-block:: bash

   scrapy crawl portugal_records

.. autoclass:: kingfisher_scrapy.spiders.portugal_releases.PortugalReleases
   :no-members:

.. code-block:: bash

   scrapy crawl portugal_releases

Scotland
--------

.. autoclass:: kingfisher_scrapy.spiders.scotland_public_contracts.ScotlandPublicContracts
   :no-members:

.. code-block:: bash

   scrapy crawl scotland_public_contracts

Spain
-----

.. autoclass:: kingfisher_scrapy.spiders.spain_zaragoza.SpainZaragoza
   :no-members:

.. code-block:: bash

   scrapy crawl spain_zaragoza

Uganda
------

.. autoclass:: kingfisher_scrapy.spiders.uganda_releases.Uganda
   :no-members:

.. code-block:: bash

   scrapy crawl uganda_releases

Uk
--

.. autoclass:: kingfisher_scrapy.spiders.uk_contracts_finder.UKContractsFinder
   :no-members:

.. code-block:: bash

   scrapy crawl uk_contracts_finder

.. autoclass:: kingfisher_scrapy.spiders.uk_fts.UKFTS
   :no-members:

.. code-block:: bash

   scrapy crawl uk_fts

Uruguay
-------

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
------

.. autoclass:: kingfisher_scrapy.spiders.zambia.Zambia
   :no-members:

.. code-block:: bash

   scrapy crawl zambia
