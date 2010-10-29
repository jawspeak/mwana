from mwana.settings import *

# Zambia:
#RESULTS160_SETTINGS = {
#    'CBA_SLUG' = 'cba',
#    'PATIENT_SLUG': 'patient',
#    'CLINIC_WORKER_SLUG': 'worker',
#    # location types:
#    'CLINIC_SLUGS': ('urban_health_centre', '1st_level_hospital',
#                    'rural_health_centre', 'health_post'),
#    'ZONE_SLUG': 'zone',
#}

# Malawi:
RESULTS160_SETTINGS = {
    'CBA_SLUG': 'cba',
    'PATIENT_SLUG': 'patient',
    'CLINIC_WORKER_SLUG': 'worker',
    # location types:
    'CLINIC_SLUGS': ('clinic', 'health_centre', 'hospital', 'maternity',
                     'dispensary', 'rural_hospital', 'mental_hospital',
                     'district_hospital', 'central_hospital',
                     'voluntary_counselling', 'rehabilitation_centre'),
    'ZONE_SLUG': 'zone',
}
