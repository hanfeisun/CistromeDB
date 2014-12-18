from ncbiAdapter.geo import *
from datacollection.models import Samples


def my_update_condition(uid):
    try:
        the_sample = Samples.objects.get(unique_id=uid)
        return False
    except Samples.DoesNotExist:
        return True



updateExistingSamples(need_update=my_update_condition)



