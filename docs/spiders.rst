Spiders
=======

.. _spider-arguments:

Spider arguments
----------------

A spider's behavior can be changed by setting *spider arguments*. For example:

.. code-block:: shell-session

   scrapy crawl colombia -a NAME=VALUE

You can set multiple spider arguments. For example:

.. code-block:: shell-session

   scrapy crawl colombia -a from_date=2015-01-01 -a until_date=2019-12-31

All spiders support these arguments:

.. list-table::
   :header-rows: 1

   * - Name
     - Description
     - Value type
   * - ``sample``
     - Sets the number of files and file items to download
     - integer

Some spiders support these arguments:

.. list-table::
   :header-rows: 1

   * - Name
     - Description
     - Value format
   * - ``from_date``
     - Download data from this date onward. The spider might describe more specific semantics (e.g. the relevant date is the date the contract was signed).
     - See spider for date format
   * - ``until_date``
     - Download data until this date. The spider might describe more specific semantics (e.g. the relevant date is the date the contract was signed).
     - See spider for date format
   * - ``year``
     - Download data from this yera.
     - integer
   * - ``start_page``
     - Download data from this page onward.
     - integer
   * - ``publisher``
     - Download data by this publisher.
     - See spider for possible values
   * - ``system``
     - Download data from this system.
     - See spider for possible values

.. Do not edit past this line. Instead, run: `scrapy updatedocs`

Afghanistan
-----------

.. autoclass:: kingfisher_scrapy.spiders.afghanistan_records.AfghanistanRecords
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.afghanistan_releases.AfghanistanReleases
   :no-members:

Argentina
---------

.. autoclass:: kingfisher_scrapy.spiders.argentina_buenos_aires.ArgentinaBuenosAires
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.argentina_vialidad.ArgentinaVialidad
   :no-members:

Armenia
-------

.. autoclass:: kingfisher_scrapy.spiders.armenia.Armenia
   :no-members:

Australia
---------

.. autoclass:: kingfisher_scrapy.spiders.australia.Australia
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.australia_nsw.AustraliaNSW
   :no-members:

Canada
------

.. autoclass:: kingfisher_scrapy.spiders.canada_buyandsell.CanadaBuyAndSell
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.canada_montreal.CanadaMontreal
   :no-members:

Chile
-----

.. autoclass:: kingfisher_scrapy.spiders.chile_compra_bulk.ChileCompraBulk
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.chile_compra_records.ChileCompraRecords
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.chile_compra_releases.ChileCompraReleases
   :no-members:

Colombia
--------

.. autoclass:: kingfisher_scrapy.spiders.colombia.Colombia
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.colombia_bulk.ColombiaBulk
   :no-members:

Costa Rica
----------

.. autoclass:: kingfisher_scrapy.spiders.costa_rica_poder_judicial_records.CostaRicaPoderJudicialRecords
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.costa_rica_poder_judicial_releases.CostaRicaPoderJudicialReleases
   :no-members:

Digiwhist
---------

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_armenia.DigiwhistArmenia
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_austria.DigiwhistAustria
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_belgium.DigiwhistBelgium
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_bulgaria.DigiwhistBulgaria
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_croatia.DigiwhistCroatia
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_cyprus.DigiwhistCyprus
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_czech_republic.DigiwhistCzechRepublic
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_denmark.DigiwhistDenmarkRepublic
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_estonia.DigiwhistEstoniaRepublic
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_finland.DigiwhistFinlandRepublic
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_france.DigiwhistFranceRepublic
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_georgia.DigiwhistGeorgiaRepublic
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_germany.DigiwhistGermanyRepublic
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_greece.DigiwhistGreeceRepublic
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_hungary.DigiwhistHungaryRepublic
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_iceland.DigiwhistIcelandRepublic
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_ireland.DigiwhistIrelandRepublic
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_italy.DigiwhistItalyRepublic
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_latvia.DigiwhistLatviaRepublic
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_lithuania.DigiwhistLithuaniaRepublic
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_luxembourg.DigiwhistLuxembourgRepublic
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_malta.DigiwhistMaltaRepublic
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_netherlands.DigiwhistNetherlandsRepublic
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_norway.DigiwhistNorwayRepublic
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_poland.DigiwhistPolandRepublic
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_portugal.DigiwhistPortugalRepublic
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_romania.DigiwhistRomaniaRepublic
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_serbia.DigiwhistSerbiaRepublic
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_slovakia.DigiwhistSlovakiaRepublic
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_slovenia.DigiwhistSloveniaRepublic
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_spain.DigiwhistSpainRepublic
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_sweden.DigiwhistSwedenRepublic
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_switzerland.DigiwhistSwitzerlandRepublic
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.digiwhist_united_kingdom.DigiwhistUnitedKingdomRepublic
   :no-members:

Dominican Republic
------------------

.. autoclass:: kingfisher_scrapy.spiders.dominican_republic.DominicanRepublic
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.dominican_republic_api.DominicanRepublicPortal
   :no-members:

Ecuador
-------

.. autoclass:: kingfisher_scrapy.spiders.ecuador_emergency.EcuadorEmergency
   :no-members:

France
------

.. autoclass:: kingfisher_scrapy.spiders.france.France
   :no-members:

Georgia
-------

.. autoclass:: kingfisher_scrapy.spiders.georgia_opendata.GeorgiaOpenData
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.georgia_records.GeorgiaRecords
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.georgia_releases.GeorgiaReleases
   :no-members:

Honduras
--------

.. autoclass:: kingfisher_scrapy.spiders.honduras_cost.HondurasCoST
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.honduras_oncae.HondurasONCAE
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.honduras_portal_bulk_files.HondurasPortalBulkFiles
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.honduras_portal_records.HondurasPortalRecords
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.honduras_portal_releases.HondurasPortalReleases
   :no-members:

Indonesia
---------

.. autoclass:: kingfisher_scrapy.spiders.indonesia_bandung.IndonesiaBandung
   :no-members:

Kenya
-----

.. autoclass:: kingfisher_scrapy.spiders.kenya_makueni.KenyaMakueni
   :no-members:

Kyrgyzstan
----------

.. autoclass:: kingfisher_scrapy.spiders.kyrgyzstan.Kyrgyzstan
   :no-members:

Malta
-----

.. autoclass:: kingfisher_scrapy.spiders.malta.Malta
   :no-members:

Mexico
------

.. autoclass:: kingfisher_scrapy.spiders.mexico_administracion_publica_federal.MexicoAdministracionPublicaFederal
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.mexico_grupo_aeroporto.MexicoGrupoAeroporto
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.mexico_inai.MexicoINAI
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.mexico_inai_portal.MexicoINAIPortal
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.mexico_nuevo_leon_records.MexicoNuevoLeonRecords
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.mexico_nuevo_leon_releases.MexicoNuevoLeonReleases
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.mexico_quien_es_quien.MexicoQuienEsQuien
   :no-members:

Moldova
-------

.. autoclass:: kingfisher_scrapy.spiders.moldova.Moldova
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.moldova_mtender.MoldovaMTender
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.moldova_old.MoldovaOld
   :no-members:

Nepal
-----

.. autoclass:: kingfisher_scrapy.spiders.nepal_dhangadhi.NepalDhangadhi
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.nepal_portal.NepalPortal
   :no-members:

Nicaragua
---------

.. autoclass:: kingfisher_scrapy.spiders.nicaragua_solid_waste.NicaraguaSolidWaste
   :no-members:

Nigeria
-------

.. autoclass:: kingfisher_scrapy.spiders.nigeria_budeshi_records.NigeriaBudeshiRecords
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.nigeria_budeshi_releases.NigeriaBudeshiReleases
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.nigeria_portal.NigeriaPortal
   :no-members:

Openopps
--------

.. autoclass:: kingfisher_scrapy.spiders.openopps.OpenOpps
   :no-members:

Paraguay
--------

.. autoclass:: kingfisher_scrapy.spiders.paraguay_dncp_records.ParaguayDNCPRecords
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.paraguay_dncp_releases.ParaguayDNCPReleases
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.paraguay_hacienda.ParaguayHacienda
   :no-members:

Portugal
--------

.. autoclass:: kingfisher_scrapy.spiders.portugal.Portugal
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.portugal_records.PortugalRecords
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.portugal_releases.PortugalReleases
   :no-members:

Scotland
--------

.. autoclass:: kingfisher_scrapy.spiders.scotland_public_contracts.ScotlandPublicContracts
   :no-members:

Spain
-----

.. autoclass:: kingfisher_scrapy.spiders.spain_zaragoza.SpainZaragoza
   :no-members:

Uganda
------

.. autoclass:: kingfisher_scrapy.spiders.uganda_releases.Uganda
   :no-members:

Uk
--

.. autoclass:: kingfisher_scrapy.spiders.uk_contracts_finder.UKContractsFinder
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.uk_fts.UKFTS
   :no-members:

Uruguay
-------

.. autoclass:: kingfisher_scrapy.spiders.uruguay_historical.UruguayHistorical
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.uruguay_records.UruguayRecords
   :no-members:

.. autoclass:: kingfisher_scrapy.spiders.uruguay_releases.UruguayReleases
   :no-members:

Zambia
------

.. autoclass:: kingfisher_scrapy.spiders.zambia.Zambia
   :no-members:
