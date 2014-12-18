__author__ = 'hanfei'
from ncbiAdapter.geo import sync_samples

sync_samples(refresh=True)

from scripts import set_series_id_by_other_id
set_series_id_by_other_id.main()