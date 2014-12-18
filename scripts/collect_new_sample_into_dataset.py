from ncbiAdapter.geo import *




__author__ = 'hanfei'
from datacollection.models import Datasets, Papers


def set_dataset_paper_by_samples():
    # set dataset's papers by its samples
    for a_dataset in Datasets.objects.all():
        if a_dataset.paper:
            continue
        try:
            a_dataset.paper = a_dataset.treats.all()[0].paper
            a_dataset.save()
        except IndexError:
            print a_dataset

            continue


def set_paper_reference_by_title():
# set a paper's reference by its title and anthors
    for a_paper in Papers.objects.filter(reference=""):
        first_author = ""
        if a_paper.authors:
            author_list = a_paper.authors.split(",")
            first_author = author_list[0].strip() if author_list else ""
            first_author += " et al," if first_author else ""
        try:
            ref = u" ".join([first_author, a_paper.title, a_paper.journal.name if a_paper.journal else "", str(a_paper.pub_date.year) if a_paper.pub_date else ""])
            a_paper.reference = ref
            a_paper.save()
        except:

            print a_paper.id
            print first_author
            raise


def add_space_between_authors():
    for a_paper in Papers.objects.all():
        if a_paper.authors:
            author_list = [i.strip(" ") for i in a_paper.authors.split(",")]
            new_format = u", ".join(author_list)
            a_paper.authors = new_format
            a_paper.save()


if __name__ == "__main__":
    createDatasets()
