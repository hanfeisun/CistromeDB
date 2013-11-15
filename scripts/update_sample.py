from ncbiAdapter.geo import *
from datacollection.models import Samples


def my_update_condition(uid):
    try:
        the_sample = Samples.objects.get(unique_id=uid)
        if the_sample.status == "new":
            return True
        else:
            return False
    except Samples.DoesNotExist:
        return False


update_samples(parse_fields=['factor'],
               update_condition=my_update_condition)


