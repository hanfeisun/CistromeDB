from datacollection.models import Samples
from ncbiAdapter.geo import updateExistingSamples

updateExistingSamples(Samples.objects.filter(status="encode"),parse_fields=['update date', 'release date','description', 'other_ids','name','paper'])
