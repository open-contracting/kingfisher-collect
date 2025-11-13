Removed spiders
===============

This page records the spiders removed from Kingfisher Collect.

Lapsed publications
-------------------

Spiders for publications that were available but stopped publishing, since January 2022:

-  2025-07-29: `mexico_inai_api, mexico_quintana_roo_idaip, mexico_veracruz_ivai, mexico_zacatecas_izai <https://github.com/open-contracting/kingfisher-collect/pull/1185>`__, because these institutions were eliminated:

   -  Instituto Veracruzano de Acceso a la Información y Protección de Datos Personales (INAI)
   -  Instituto de Acceso a la Información y Protección de Datos Personales de Quintana Roo (IDAIPQROO)
   -  Instituto Nacional de Transparencia, Acceso a la Información y Protección de Datos Personales (IVAI)
   -  Instituto Zacatecano de Transparencia y Acceso a la Información (IZAI)

-  2025-04-14: `mexico_durango_idaip, mexico_mexico_state_infoem, mexico_nuevo_leon_cotai, nigeria_abia_state, nigeria_enugu_state, nigeria_kano_state, panama_dgcp_bulk, panama_dgcp_records, panama_dgcp_releases, portugal_records, portugal_releases <https://github.com/open-contracting/kingfisher-collect/pull/1159>`__

   .. http://74.208.135.52:3000/edca/fiscalYears from http://contratacionesabiertas.idaip.org.mx/contratacionesabiertas/datosabiertos
   .. http://infoem.org.mx:3000/edca/contractingprocess/null from http://www.infoem.org.mx:4000/contratacionesabiertas/datosabiertos
   .. http://201.149.38.218:3000/edca/fiscalYears from http://201.149.38.218:4000/contratacionesabiertas/datosabiertos
   .. https://abiaeprocurement.ab.gov.ng
   .. https://dueprocess.en.gov.ng
   .. https://kano-eproc.eurodyn.com
   .. https://ocds.panamacompraencifras.gob.pa/Descarga?DateFrom=2023-01-01&DateTo=2023-12-31&FileType=json from https://ocds.panamacompraencifras.gob.pa/swagger/
   .. https://ocds.panamacompraencifras.gob.pa/Record
   .. https://ocds.panamacompraencifras.gob.pa/Release
   .. http://www.base.gov.pt/api/Release/GetReleases from http://www.base.gov.pt/swagger/index.html
   .. http://www.base.gov.pt/api/Record/GetRecords

-  2024-10-26: `italy_appalti_pop, mexico_grupo_aeroporto, moldova_old <https://github.com/open-contracting/kingfisher-collect/pull/1111>`__

   .. https://www.appaltipop.it/api/v1/buyers from https://www.appaltipop.it/api/v1/, also https://github.com/ondata/appaltipop
   .. http://gacmda.gacm.mx:8880/files/opendata/coleccion/concentrado05032019RELEASE.json
   .. http://opencontracting.date.gov.md/ocds-api/year/{year} from http://opencontracting.date.gov.md/downloads

-  2024-04-12: `nigeria_gombe_state <https://github.com/open-contracting/kingfisher-collect/pull/1075>`__

   .. http://gombe.stateopencontracting.com/Other-Basic/Report/Json-Report

-  2024-01-09: `mexico_puebla_itaipue, nigeria_edo_state <https://github.com/open-contracting/kingfisher-collect/pull/1047>`__

   .. http://189.240.12.27:3000 from http://189.240.12.27:4000/contratacionesabiertas/datosabiertos/
   .. https://edoocds.cloudware.ng/edo-ocds.json from http://edpms.edostate.gov.ng/ocds/

-  2023-10-04: `honduras_cost, kenya_makueni, kyrgyzstan, portugal_bulk <https://github.com/open-contracting/kingfisher-collect/pull/1030>`__

   .. https://app.sisocs.org:8080/sisocs/records from http://app.sisocs.org/protected/ocdsShow/
   .. https://opencontracting.makueni.go.ke/api/ocds/package/all from https://opencontracting.makueni.go.ke/swagger-ui/#/ocds-controller
   .. http://ocds.zakupki.gov.kg/api/tendering
   .. https://dados.gov.pt/pt/datasets/ocds-portal-base-www-base-gov-pt/

-  2022-12-13: `ecuador_emergency, mexico_oaxaca_iaip, nicaragua_solid_waste, nigeria_budeshi_*, nigeria_kaduna_state_budeshi_*, tanzania_zabuni <https://github.com/open-contracting/kingfisher-collect/pull/979>`__

   .. https://datosabiertos.compraspublicas.gob.ec/OCDS/ from https://portal.compraspublicas.gob.ec/sercop/data-estandar-ocds/
   .. http://contratacionesabiertas-iaipoaxaca-org.mx:3000 from http://contratacionesabiertas-iaipoaxaca-org.mx:4000/contratacionesabiertas/datosabiertos
   .. http://www.gekoware.com/swmp/api/ocds/20010101/20220101/
   .. https://budeshi.ng/api/releases/1/tender or https://budeshi.ng/api/record/1 from https://budeshi.ng/api/
   .. https://kadppaocds.azurewebsites.net/api/
   .. https://app.zabuni.co.tz/api/releases/tender from https://zabuni.co.tz/docs

-  2022-04-20: `afghanistan_*, indonesia_bandung <https://github.com/open-contracting/kingfisher-collect/pull/930>`__

   .. https://ocds.ageops.net
   .. https://birms.bandung.go.id/api/packages/year/{year}

-  2022-01-27: `moldova_positive_initiative <https://github.com/open-contracting/kingfisher-collect/pull/906>`__

   .. http://116.202.173.47:8080/md_covid_2020-11-06.json from https://www.tender.health/ocdsrelease

.. note::

   Since January 2022, any spider that stops working for more than six months will be deleted.

Broken publications
-------------------

Spiders for publications that became broken, since April 2024:

-  2025-04-14: `moldova <https://github.com/open-contracting/kingfisher-collect/pull/1159>`__ (returns upstream errors)
-  2025-01-02: `pakistan_ppra_api, pakistan_ppra_bulk <https://github.com/open-contracting/kingfisher-collect/pull/1137>`__ (requires paginating `HTML <https://ppra.org.pk/opendata.asp>`__)
-  2024-07-02: `mexico_sinaloa_ceaip <https://github.com/open-contracting/kingfisher-collect/pull/1093>`__ (returns no data)
-  2024-04-12: `dominican_republic_bulk <https://github.com/open-contracting/kingfisher-collect/pull/1074>`__ (the `bulk source <https://datosabiertos.dgcp.gob.do/opendata/estandar-mundial-ocds>`__ isn't in sync with the API source)
-  2024-04-05: `mexico_quien_es_quien_records <https://github.com/open-contracting/kingfisher-collect/pull/1063>`__ (pagination is broken)
