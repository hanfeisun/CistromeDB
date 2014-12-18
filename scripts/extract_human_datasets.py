__author__ = 'hanfei'
from datacollection import models

for a_dataset in models.Datasets.objects.all():
    if not a_dataset.treats.all():
        continue
    else:
        t = a_dataset.treats.all()[0]
        assert isinstance(t, models.Samples)
        print a_dataset.id, \
            ";", \
            t.species.name if t.species else None, \
            ";", \
            t.factor.name if t.factor else None, \
            ";", \
            t.cell_line.name if t.cell_line else None, \
            ";", \
            t.cell_pop.name if t.cell_pop else None, \
            ";", \
            t.cell_type.name if t.cell_type else None, \
            ";", \
            t.tissue_type.name if t.tissue_type else None, \
            ";", \
            t.disease_state.name if t.disease_state else None, \
            ";", \
            t.unique_id, \
            ";", \
            t.series_id


