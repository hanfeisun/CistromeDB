"""
Synopsis: Given a newdc Samples object, tries to generate a configuration 
file that will run w/ Tao's pipeline script
"""
import os
import shutil
import ConfigParser

import datacollection
import settings

def mock_conf(config, assembly):
    """replaces pipeline tools w/ mock tools found in pipeline/mock_tools"""
    #expects to be in the toplevel w/ settings.CONF_TEMPLATE_DIR
    mock_tools_path = os.path.join("/".join(settings.CONF_TEMPLATE_DIR.split("/")[:-1]), "mock_tools")
    config.set("samtools", "samtools_chrom_len_path",
               os.path.join(mock_tools_path, "static_libraries", 
                            "chromLen", "%s.len" % assembly))
    config.set("samtools", "samtools_main",
               os.path.join(mock_tools_path, "mock_samtools"))

    config.set("seqpos", "seqpos_main",
               os.path.join(mock_tools_path, "mock_MDSeqPos.py"))

    config.set("macs", "bedgraphtobigwig_main",
               os.path.join(mock_tools_path, "mock_bedGraphToBigWig"))

    config.set("macs", "macs_main",
               os.path.join(mock_tools_path, "mock_macs14"))

    config.set("bowtie", "bowtie_genome_index_path",
               os.path.join(mock_tools_path, "indexes", assembly))
    config.set("bowtie", "bowtie_main",
               os.path.join(mock_tools_path, "mock_bowtie"))

    config.set("conservation", "conserv_plot_phast_path",
               os.path.join(mock_tools_path, "static_libraries",
                            "conservation", assembly, "placental"))
    config.set("conservation", "conserv_plot_main",
               os.path.join(mock_tools_path, "mock_conservation_plot.py"))

    config.set("correlation", "wig_correlation_main",
               os.path.join(mock_tools_path, "mock_wig_correlation.py"))

    config.set("ceas", "ceas_main",
               os.path.join(mock_tools_path, "mock_ceas"))
    config.set("ceas", "ceas_genetable_path",
               os.path.join(mock_tools_path, "static_libraries", "ceaslib",
                            "GeneTable", assembly))

    config.set("bedtools", "dhs_bed_path",
               os.path.join(mock_tools_path, "dhs", "%s.bed" % assembly))
    config.set("bedtools", "intersectbed_main",
               os.path.join(mock_tools_path, "mock_intersectBed"))

    config.set("venn", "venn_diagram_main",
               os.path.join(mock_tools_path, "mock_venn_diagram.py"))
    

def real_conf(config, assembly):
    """Given a configuraton and an assembly, this fn will set the config
    with the right file paths according to the assembly"""
    #NOTE: we should draw the path from some settings.py!
    config.set("samtools", "samtools_chrom_len_path",
               "/data/CistromeAP/static_libraries/chromLen/%s.len" % assembly)
    config.set("bowtie", "bowtie_genome_index_path",
               "/data/CistromeAP/static_libraries/indexes/%s" % assembly)

    if assembly == "hg19":
        sub_path = "hg19/placentalMammals/"
    else:
        sub_path = "%s/placental/" % assembly
    config.set("conservation", "conserv_plot_phast_path",
               "/data/CistromeAP/static_libraries/conservation/%s" % sub_path)

    config.set("ceas", "ceas_genetable_path",
               "/data/CistromeAP/static_libraries/ceaslib/GeneTable/%s" % assembly)    
    #NOTE:**we really need proper dhs files, not just ncor_5pm_peaks.bed **


def generate(sample, user, dir=".", use_mock=False):
    """Generates configuration files for the pipeline. uses the templates, 
    overrides the templates w/ the given values and writes the conf file
    NOTE: right now just chip-seq conf files!
    use_mock = generate a conf file that use mock tools
    """
    config = ConfigParser.ConfigParser()
    temp_file = open(os.path.join(settings.CONF_TEMPLATE_DIR, "seq.conf"))
    config.readfp(temp_file)
    #temp_file.close()
    
    #override the configurations here
    config.set("sample", "sample_id", sample.id)
    config.set("sample", "username", user.username)

    treatments = []
    if sample.treatments:
        treatments = [datacollection.models.Datasets.objects.get(pk=id) \
                          for id in sample.treatments.split(",")]

    controls = []
    if sample.controls:
        controls = [datacollection.models.Datasets.objects.get(pk=id) \
                        for id in sample.controls.split(",")]

    assembly = treatments[0].assembly.name
    config.set("sample", "assembly_name", assembly)
    
    config.set("data", "treatment_seq_file_path", 
               ",".join([t.raw_file.path for t in treatments]))
    config.set("data", "control_seq_file_path", 
               ",".join([c.raw_file.path for c in controls]))

    #need to override alot more here!
    if use_mock:
        mock_conf(config, assembly)
    else: 
        real_conf(config, assembly)

    if not os.path.exists(dir):
        os.makedirs(dir)
    f = open(os.path.join(dir, "sample%s.conf" % sample.id), "w")
    config.write(f)
    f.close()
    
    return f
