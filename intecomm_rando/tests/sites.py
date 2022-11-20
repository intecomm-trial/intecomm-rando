from edc_sites.single_site import SingleSite

fqdn = "intecomm.clinicedc.org"

all_sites = {
    "uganda": (
        SingleSite(
            101,
            "kasangati",
            country_code="ug",
            country="uganda",
            domain=f"kasangati.ug.{fqdn}",
        ),
    )
}
