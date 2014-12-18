
from ncbiAdapter.geo import *
from datacollection.models import Samples

def main():
    recheckExistingSamples(Samples.objects.filter(status='inherited'))

if __name__ == "__main__":
    main()

