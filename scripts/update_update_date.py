from datacollection.models import Samples
from ncbiAdapter.geo import updateExistingSamples
def my_update_condition(uid):
    if uid.startswith("GSM"):
        return True
    else:
        return False

updateExistingSamples(Samples.objects.filter(unique_id__startswith="GSM"),parse_fields=['update date', 'release date'])
