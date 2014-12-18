from django.core.exceptions import PermissionDenied
from django_select2 import Select2View, NO_ERR_RESP

from datacollection.models import Samples


try:
    import json
except ImportError:
    import simplejson as json


class SamplesSelect2View(Select2View):
    def check_all_permissions(self, request, *args, **kwargs):
        user = request.user
        if not (user.is_authenticated() and user.has_perms('emp.view_employees')):
            raise PermissionDenied

    def get_results(self, request, term, page, context):
        sps = Samples.objects.filter(Q(unique_id__icontains=term))
        res = [(sp.id, sp.unique_id,) for sp in sps]
        return (NO_ERR_RESP, False, res) # Any error response, Has more results, options list


from django.db.models import Q
#
# def get_series_pack(self):
#     data = self.get_data()
#     series_names = data[0][1:]
#     serieses = []
#     serieses.append({"name": series_names, "data": data[1:]})
#     return json.dumps(serieses)

from django.conf.urls.defaults import *



























