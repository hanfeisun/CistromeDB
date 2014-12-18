from ncbiAdapter.geo import *
from datacollection.models import Samples



# Usage:
# updateExistingSamples(Samples.objects.filter(PUT_YOUR_CONDITIONS_HERE))

def main():
    updateExistingSamples(Samples.objects.filter(status='new'),
                          parse_fields=['cell type', 'cell line', 'cell pop','tissue', 'strain','disease','factor','update date','release date'])

if __name__ == "__main__":
    main()



