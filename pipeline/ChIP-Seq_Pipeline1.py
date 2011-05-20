#!/usr/bin/env python
# Time-stamp: <2011-03-26 23:48:03 Tao Liu>

"""Script Description: A demo ChIP-seq pipeline script. From reads
mapping to motif analysis. It will do 4 validity checks before running
the pipeline.

Copyright (c) 2011 Tao Liu <taoliu@jimmy.harvard.edu>

This code is free software; you can redistribute it and/or modify it
under the terms of the BSD License (see the file COPYING included with
the distribution).

@status:  experimental
@version: $Revision$
@author:  Tao Liu
@contact: taoliu@jimmy.harvard.edu
"""

# ------------------------------------
# python modules
# ------------------------------------

import os
import sys
import re
from optparse import OptionParser
import ConfigParser
import string
import logging
from subprocess import call as subpcall
from os.path import join as pjoin

# ------------------------------------
# constants
# ------------------------------------

logfhd = open("log","w")

logging.basicConfig(level=20,
                    format='%(levelname)-5s @ %(asctime)s: %(message)s ',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    stream=sys.stderr,
                    filemode="w"
                    )

error   = logging.critical		# function alias
warn    = logging.warning

def info(a):
    logging.info(a)
    logfhd.write(a+"\n")
    logfhd.flush()

# ------------------------------------
# Classes
# ------------------------------------

# ------------------------------------
# Misc functions
# ------------------------------------

def read_config(configFile):
    """Read configuration file and parse it into a dictionary.

    In the dictionary, the key is the section name plus option name like: data.data.treatment_seq_file_path.
    """
    configs = {}
    
    configParser = ConfigParser.ConfigParser()

    if len(configParser.read(configFile)) == 0:
        raise IOError("%s not found!" % configFile)
    
    for sec in configParser.sections():
        secName = string.lower(sec)
        for opt in configParser.options(sec):
            optName = string.lower(opt)
            configs[secName + "." + optName] = string.strip(configParser.get(sec, opt))
    
    return configs

def check_conf_validity(configs):
    """A configuration validity test. Return false if any required option is not valid.

    """
    if not configs["sample.sample_id"].isdigit():
        error("Config Validity Check: sample id -- %s should be specified and be an integer!" % configs["sample.sample_id"])
        return False
    if not configs["sample.assembly_name"]:
        error("Config Validity Check: assembly name -- %s should be specified!")
        return False
    else:
        an = configs["sample.assembly_name"]
        if not an.startswith("hg") and not an.startswith("mm"):
            error("Config Validity Check: assembly name -- %s should be human or mouse!" % an)
            return False
        elif not an[2:].isdigit():
            error("Config Validity Check: assembly name -- %s should be UCSC dbkey!" % an)
            return False
        elif an.startswith("hg"):
            configs["sample.species"] = "hs"
            info("Species is 'human'")            
        elif an.startswith("mm"):
            configs["sample.species"] = "mm"
            info("Species is 'mouse'")

    #USERNAMES are required
    if "sample.username" not in configs:
        error("Config Validity Check: sample.username must be specified!")
        return False
            
    rdt = configs["data.raw_data_type"]
    if rdt != "seq" and rdt != "alignment": # and rdt != "peakcalls":
        error("Config Validity Check: raw data type -- %s should be either seq, alignment!" % rdt)
        return False

    rdf = configs["data.raw_data_format"]
    # check if the raw data format matches raw data type
    if rdt == "seq":
        if ( rdf != "fastq" and rdf != "fasta" and rdf != "sequences"):
            error("Config Validity Check: raw data is seq, then data format -- %s should be either fastq, fasta or sequences!" % rdf)
            return False            
        elif ( configs["data.treatment_seq_file_path"] == "" ): #or configs["data.control_seq_file_path"] == "" ):
            error("Config Validity Check: raw data is seq however sequencing raw files are missing!" )
            return False
    elif rdt == "alignment":
        if ( rdf != "SAM" and rdf != "BAM" and rdf != "BED"):
            error("Config Validity Check: raw data is alignment, then data format -- %s should be either SAM, BAM or BED!" % rdf)
            return False
        elif ( configs["data.treatment_ali_file_path"] == "" ): #or configs["data.control_ali_file_path"] == "" ):
            error("Config Validity Check: raw data is alignment however alignment raw files are missing!" )
            return False

    # other required options:
    if not configs["bowtie.bowtie_main"]:
        error("Config Validity Check: bowtie main is missing!")
        return False
    if not configs["bowtie.bowtie_genome_index_path"]:
        error("Config Validity Check: bowtie genome index is missing!")
        return False
    if not configs["samtools.samtools_main"]:
        error("Config Validity Check: samtools main is missing!")
        return False
    if not configs["samtools.samtools_chrom_len_path"]:
        error("Config Validity Check: samtools chromosome length file is missing!")
        return False    
    if not configs["macs.macs_main"]:
        error("Config Validity Check: macs main is missing!")
        return False
    if not configs["ceas.ceas_main"]:
        error("Config Validity Check: ceas main is missing!")
        return False
    if not configs["ceas.ceas_genetable_path"]:
        error("Config Validity Check: ceas genetable is missing!")
        return False
    if not configs["venn.venn_diagram_main"]:
        error("Config Validity Check: Venn diagram main is missing!")
        return False
    if not configs["bedtools.intersectbed_main"]:
        error("Config Validity Check: intersectBed main is missing!")
        return False
    if not configs["bedtools.dhs_bed_path"]:
        error("Config Validity Check: DHS bed file is missing!")
        return False
    if not configs["correlation.wig_correlation_main"]:
        error("Config Validity Check: wig correlation main is missing!")
        return False
    avail = ["mean","median","sample"]
    wcm = configs["correlation.wig_correlation_method"]
    if avail.count(wcm) == 0:
        error("Config Validity Check: Correlation method '%s' is invalid! It should be either mean, median, or sample!" % wcm)
    if not configs["conservation.conserv_plot_main"]:
        error("Config Validity Check: conservation plot main is missing!")
        return False
    if not configs["conservation.conserv_plot_phast_path"]:
        error("Config Validity Check: PhastCons data file folder is missing!")
        return False
    if not configs["seqpos.seqpos_main"]:
        error("Config Validity Check: seqpos main is missing!")
        return False
    #if not configs["seqpos.seqpos_motif_db_path"]:
    #    error("Config Validity Check: seqpos motif db path is missing!")
    #    return False
    sms = configs["seqpos.seqpos_motif_db_selection"].split(",")
    avail = ["transfac.xml","pbm.xml", "jaspar.xml", "hpdi.xml", "y1h.xml"]
    for sm in sms:
        if avail.count(sm) == 0:
            error("Config Validity Check: seqpos motif db %s is invalid! It should be either transfac.xml, pbm.xml, jaspar.xml, hpdi.xml, or y1h.xml!" % sm)
            return False
    return True

def check_file_validity(configs):
    """A data file validity test. Return false if any file can't be found.

    """

    if configs["data.raw_data_type"] == 'seq':
        # check the raw data file option
        if configs.has_key("data.control_seq_file_path") and configs["data.control_seq_file_path"]:
            configs["data.has_control"] = True
            info("Data has control.")
        else:
            configs["data.has_control"] = False
        tfiles = configs["data.treatment_seq_file_path"].split(",")
        for tfile in tfiles:
            if not os.path.isfile(tfile):
                error("File Validity Check: %s can't be found!" % tfile)
                return False
        if configs["data.has_control"]:
            cfiles = configs["data.control_seq_file_path"].split(",")
            for cfile in cfiles:
                if not os.path.isfile(cfile):
                    error("File Validity Check: %s can't be found!" % cfile)
                    return False
    elif configs["data.raw_data_type"] == 'alignment':
        if configs.has_key("data.control_ali_file_path") and configs["data.control_ali_file_path"]:
            info("Data has control.")
            configs["data.has_control"] = True
        else:
            configs["data.has_control"] = False
        # check the alignment data file option
        tfiles = configs["data.treatment_ali_file_path"].split(",")
        for tfile in tfiles:
            if not os.path.isfile(tfile):
                error("File Validity Check: %s can't be found!" % tfile)
                return False
        if configs["data.has_control"]:            
            cfiles = configs["data.control_ali_file_path"].split(",")
            for cfile in cfiles:
                if not os.path.isfile(cfile):
                    error("File Validity Check: %s can't be found!" % cfile)
                    return False

    return True

def check_cmd_validity (configs):
    """Check if command line can be found.
    
    """
    if not os.path.isfile(configs["bowtie.bowtie_main"]):
       error("CMD Validity Check: bowtie can't be found!")
       return False
    if not os.path.isfile(configs["samtools.samtools_main"]):
       error("CMD Validity Check: samtools can't be found!")
       return False
    if not os.path.isfile(configs["macs.macs_main"]):
        error("CMD Validity Check: macs can't be found!")
        return False
    if not os.path.isfile(configs["macs.bedgraphtobigwig_main"]):
        error("CMD Validity Check: bedGraphToBigWig can't be found!")
        return False
    if not os.path.isfile(configs["ceas.ceas_main"]):
        error("CMD Validity Check: ceas can't be found!")
        return False
    if not os.path.isfile(configs["venn.venn_diagram_main"]):
       error("CMD Validity Check: Venn diagram can't be found!")
       return False
    if not os.path.isfile(configs["bedtools.intersectbed_main"]):
       error("CMD Validity Check: BedTools intersectBed can't be found!")
       return False
    if not os.path.isfile(configs["correlation.wig_correlation_main"]):
        error("CMD Validity Check: wig correlation can't be found!")
        return False
    if not os.path.isfile(configs["conservation.conserv_plot_main"]):
        error("CMD Validity Check: conservation plot can't be found!")
        return False
    if not os.path.isfile(configs["seqpos.seqpos_main"]):
       error("CMD Validity Check: seqpos can't be found!")
       return False
    return True

def check_lib_validity (configs):
    """Check if the library files for command line can be found.
    
    """
    if not os.path.isfile(configs["bowtie.bowtie_genome_index_path"]+".1.ebwt"):
        error("Library Files Validity Check: bowtie genome index can't be found!")
        return False
    if not os.path.isfile(configs["samtools.samtools_chrom_len_path"]):
        error("Library Files Validity Check: samtools chromosome length file can't be found!")
        return False
    else:
        # clone the chrom_len_path
        configs["macs.bedgraphtobigwig_chrom_len_path"]=configs["samtools.samtools_chrom_len_path"]
    if not os.path.isfile(configs["ceas.ceas_genetable_path"]):
        error("Library Files Validity Check: ceas genetable can't be found!")
        return False
    if not os.path.isfile(configs["bedtools.dhs_bed_path"]):
        error("Library Files Validity Check: DHS bed file can't be found!")
        return False
    if not os.path.isdir(configs["conservation.conserv_plot_phast_path"]):
        error("Library Files Validity Check: PhastCons data file folder can't be found!")
        return False
    #sms = configs["seqpos.seqpos_motif_db_selection"].split(",")
    #for sm in sms:
    #    if not os.path.isfile(pjoin(configs["seqpos.seqpos_motif_db_path"],sm)):
    #        error("Library Files Validity Check: seqpos motif db %s can't be found!" % sm)
    #        return False
    return True

def prepare_output_file_names ( configs ):
    """Generate intermedia file names.

    """
    sampleid = configs["sample.sample_id"]
    # decide the number of replicates as the number of comma in TREATMENT path:
    rdt = configs["data.raw_data_type"]
    # check if the raw data format matches raw data type
    if rdt == "seq":
        configs["data.number_replicates"] = len(configs["data.treatment_seq_file_path"].split(","))
    elif rdt == "alignment":
        configs["data.number_replicates"] = len(configs["data.treatment_ali_file_path"].split(","))
        
    nr = configs["data.number_replicates"]
    info("Replicates in your sample is: %d" % nr)

    # for replicates, we don't perform QC analysis, so we only keep
    # peaks.bed and treat.wig files for replicates
    configs["bowtie.treat_output_replicates"] = [sampleid+"_rep"+str(i)+"_treat.sam" for i in range(1,nr+1)]
    configs["bowtie.treat_output"] = sampleid+"_treat.sam"
    configs["bowtie.control_output"] = sampleid+"_control.sam"    

    configs["samtools.treat_output_replicates"] = [sampleid+"_rep"+str(i)+"_treat.bam" for i in range(1,nr+1)]
    configs["samtools.treat_output"] = sampleid+"_treat.bam"
    configs["samtools.control_output"] = sampleid+"_control.bam"    

    configs["macs.output_xls"] = sampleid+"_peaks.xls"
    configs["macs.output_bed_replicates"] = [sampleid+"_rep"+str(i)+"_peaks.bed" for i in range(1,nr+1)]    
    configs["macs.output_bed"] = sampleid+"_peaks.bed"
    configs["macs.output_summits"] = sampleid+"_summits.bed"
    configs["macs.output_treat_wig_replicates"] = [sampleid+"_rep"+str(i)+"_treat.wig" for i in range(1,nr+1)]        
    configs["macs.output_treat_wig"] = sampleid+"_treat.wig"
    configs["macs.output_control_wig"] = sampleid+"_control.wig"    
    configs["macs.output_treat_bdg_replicates"] = [sampleid+"_rep"+str(i)+"_treat.bdg" for i in range(1,nr+1)]        
    configs["macs.output_treat_bdg"] = sampleid+"_treat.bdg"
    configs["macs.output_control_bdg"] = sampleid+"_control.bdg"    
    configs["macs.output_treat_bw_replicates"] = [sampleid+"_rep"+str(i)+"_treat.bw" for i in range(1,nr+1)]        
    configs["macs.output_treat_bw"] = sampleid+"_treat.bw"
    configs["macs.output_control_bw"] = sampleid+"_control.bw"    

    configs["ceas.output_xls"] =  sampleid+"_ceas.xls"
    configs["ceas.output_pdf"] = sampleid+"_ceas.pdf"
    configs["ceas.output_R"] = sampleid+"_ceas.R"    

    configs["venn.replicates_output_png"] = sampleid+"_venn_replicates.png"
    #configs["venn.dhs_output_png"] = sampleid+"_venn_dhs.png"

    configs["bedtools.dhs_output_txt"] = sampleid+"_bedtools_dhs.txt"

    configs["correlation.output_pdf"] = sampleid+"_cor.R.pdf"
    configs["correlation.output_R"] = sampleid+"_cor.R"

    configs["conservation.output_bmp"] = sampleid+"_conserv.bmp"
    configs["conservation.output_R"] = sampleid+"_conserv.R"    

    configs["seqpos.output_zip"] = sampleid+"_seqpos.zip"

    configs["config_file"] = sampleid+".conf"
    return configs

# wrapper to run command 
def run_cmd ( command ):
    info ("Run: %s" % command)
    subpcall (command,shell=True)
    return

# All the pipeline command calls
def step1_bowtie (configs):
    """Step1: run bowtie to map reads to genome.
    
    """
    # check the startstep whether to pass this step

    if configs["others.startstep"] <= 1 and 1 <= configs["others.endstep"]:
        info("Step 1: BOWTIE...")
    else:
        info("Step 1 Bowtie is skipped as requested.")
        return False
    if configs["data.raw_data_type"] == "seq":
        pass
    else:
        info("Since raw data typs is not sequencing, bowtie is skipped.")
        return False

    # check the input
    tfiles = configs["data.treatment_seq_file_path"].split(",")
    cfiles = configs["data.control_seq_file_path"].split(",")
    
    for tfile in tfiles:
        if not os.path.isfile(tfile):
            error("Input for bowtie is missing: %s can't be found!" % tfile)
            sys.exit(1)
    if configs["data.has_control"]:
        for cfile in cfiles:
            if not os.path.isfile(cfile):
                error("Input for bowtie is missing: %s can't be found!" % cfile)
                sys.exit(1)

    idata_format = configs["data.raw_data_format"]

    # combine input data
    if configs["data.has_control"]:
        if len(cfiles)>=1:
            combined_input_file = "combined_input." + idata_format
            command_line = "cat "+ " ".join(cfiles) + " > " + combined_input_file
            run_cmd(command_line)
    
    # run bowtie
    if idata_format == "fastq":
        bowtie_format_option = " -q "
    elif idata_format == "fasta":
        bowtie_format_option = " -f "
    elif idata_format == "sequences":
        bowtie_format_option = " -r "

    if configs["bowtie.bowtie_max_alignment"]:
        bowtie_max_alignment_option = " -m "+configs["bowtie.bowtie_max_alignment"]+" "
    else:
        bowtie_max_alignment_option = " -m 1 "        
    # for each replicates of treatment:
    for i in range(1,configs["data.number_replicates"]+1):
        command_line = configs["bowtie.bowtie_main"]+" -S "+bowtie_format_option+bowtie_max_alignment_option+configs["bowtie.bowtie_genome_index_path"]+" "+tfiles[i-1]+" "+configs["bowtie.treat_output_replicates"][i-1]
        run_cmd(command_line)
        # convert sam to bam
        command_line = configs["samtools.samtools_main"]+" view -bt "+configs["samtools.samtools_chrom_len_path"]+" "+configs["bowtie.treat_output_replicates"][i-1]+" -o "+configs["samtools.treat_output_replicates"][i-1]
        run_cmd(command_line)

    # combine replicates:

    if len(tfiles)>1:
        # samtools merge command
        command_line = "samtools merge "+configs["samtools.treat_output"]+" "+" ".join(configs["samtools.treat_output_replicates"])
        run_cmd(command_line)
    else:
        # only one replicate, simply clone it.
        command_line = "cp "+configs["samtools.treat_output_replicates"][0]+" "+configs["samtools.treat_output"]
        run_cmd(command_line)
    
    # for the control data:
    if configs["data.has_control"]:
        if len(cfiles)>=1:
            combined_input_file = "combined_input." + idata_format
            command_line = configs["bowtie.bowtie_main"]+" -S "+bowtie_format_option+bowtie_max_alignment_option+configs["bowtie.bowtie_genome_index_path"]+" "+combined_input_file+" "+configs["bowtie.control_output"]
            run_cmd(command_line)
            # convert sam to bam
            command_line = configs["samtools.samtools_main"]+" view -bt "+configs["samtools.samtools_chrom_len_path"]+" "+configs["bowtie.control_output"]+" > "+configs["samtools.control_output"]
            run_cmd(command_line)
            run_cmd("rm -f %s" % combined_input_file)
    
    return True

def step2_macs (configs):
    """Step2: run MACS to call peaks on replicates, then run again after combine replicates.
    
    """
    # check the startstep whether to pass this step

    if configs["others.startstep"] <= 2 and 2 <= configs["others.endstep"]:
        info("Step 2: MACS...")
    else:
        info("Step 2 MACS is skipped as requested.")
        return False
    if configs["data.raw_data_type"] == "alignment":
        _step2_macs_alignment(configs)
    elif configs["data.raw_data_type"] == "seq":
        _step2_macs_seq(configs)
    else:
        info("Since raw data typs is not alignment or sequences, step 2 MACS is skipped.")
        return False

    # refine the peak, remove negative coordinates in the output bed file
    info("Remove peaks with negative coordinates. Modified by Jianxing Feng (Mon Mar 21 16:12:52 CST 2011). Modified by me then...")
    command_line = "awk '{if ($2 >= 0 && $2 < $3) print}' " + configs["macs.output_bed"] + " > " + configs["macs.output_bed"]+".temp"
    run_cmd(command_line)
    command_line = "mv " + configs["macs.output_bed"] + ".temp " + configs["macs.output_bed"]
    run_cmd(command_line)

    # refine the peak, remove negative coordinates in the output summit file
    # Tue Mar 29 17:17:50 CST 2011
    info("Remove peaks with negative coordinates. Modified by Jianxing Feng (Mon Mar 21 16:12:52 CST 2011). Modified by me then...")
    command_line = "awk '{if ($2 >= 0 && $2 < $3) print}' " + configs["macs.output_summits"] + " > " + configs["macs.output_summits"]+".temp"
    run_cmd(command_line)
    command_line = "mv " + configs["macs.output_summits"] + ".temp " + configs["macs.output_summits"]
    run_cmd(command_line)


def median (nums):
    """Calculate Median.

    Parameters:
    nums:  list of numbers
    Return Value:
    median value
    """
    p = sorted(nums)
    l = len(p)
    if l%2 == 0:
        return (p[l/2]+p[l/2-1])/2
    else:
        return p[l/2]
    
def __summarize_peaks ( peak_file ):
    """get summary of peak file from MACS.

    """
    fhd = open( peak_file,"r" )
    d_wo_FDR = []
    d_w_FDR = []
    t = ""
    for i in fhd:
        i = i.strip()
        if i and not i.startswith("#") and not i.startswith("chr\t"):
            fs = i.split("\t")
            fc = fs[7]
            if len(fs) == 9:
                # has FDR
                d_w_FDR.append((float(fc),float(fs[8])))
            else:
                d_wo_FDR.append((float(fc)))
    if d_w_FDR:
        d = sorted(d_w_FDR,cmp=lambda x,y:cmp(x[0],y[0]))
        fdr = [x[1] for x in d if x>=20 ]
        t += "peaks_fc_ge_20 = %d\n" % len(fdr)
        t += "max_FDR_of_fc_ge_20 = %.2f\n" % max(fdr)
        t += "median_FDR_of_fc_ge_20 = %.2f\n" % median(fdr)        
    else:
        d = sorted(d_wo_FDR)
        d = [x for x in d if x>=20]
        t += "peaks_fc_le_20 = %d\n" % len(d)
    return t

def _step2_macs_alignment (configs):
    """Step2 MACS if the raw data type is alignment.
    
    """
    # check the input
    tfiles = configs["data.treatment_ali_file_path"].split(",")
    cfiles = configs["data.control_ali_file_path"].split(",")

    for tfile in tfiles:
        if not os.path.isfile(tfile):
            error("Input for MACS is missing: %s can't be found!" % tfile)
            sys.exit(1)
    if configs["data.has_control"]:
        for cfile in cfiles:
            if not os.path.isfile(cfile):
                error("Input for MACS is missing: %s can't be found!" % cfile)
                sys.exit(1)

    idata_format = configs["data.raw_data_format"]

    # combine treatment/input data
    if len(tfiles)>1:
        if idata_format == "BAM":
            # samtools merge command
            combined_treat_ali_file = "combined_treat.bam"
            command_line = "samtools merge "+combined_treat_ali_file+" "+" ".join(tfiles)
            run_cmd(command_line)
        elif idata_format == "SAM" or idata_format == "BED":
            # samtools merge command
            combined_treat_ali_file = "combined_treat."+idata_format
            command_line = "cat "+ " ".join(tfiles) + " > " + combined_treat_ali_file
            run_cmd(command_line)
        else:
            error("Format %s not recognized!" % idata_format)
            sys.exit(1)

    # Jianxing Feng
    # Mon Mar 28 09:58:41 CST 2011
    # if len(tfiles) == 1, combined_treat_ali_file would be undefined at line 697:
    # command_line = "mv "+combined_treat_ali_file+" "+configs["samtools.treat_output"]
    # BEGIN
    elif len(tfiles)==1:
        combined_treat_ali_file = tfiles[0]
    # END

    if configs["data.has_control"]:
        if idata_format == "BAM":
            # samtools merge command
            combined_input_ali_file = "combined_input.bam"
            if len(cfiles)>1:
                command_line = "samtools merge "+combined_input_ali_file+" "+" ".join(cfiles)
            else:
                command_line = "cp "+cfiles[0]+" "+combined_input_ali_file
            run_cmd(command_line)
        elif idata_format == "SAM" or idata_format == "BED":
            # cat them... * remember, SAM headers may be redundant, so it may cause some problem if you later convert it to BAM.
            combined_input_ali_file = "combined_input."+idata_format
            command_line = "cat "+ " ".join(cfiles) + " > " + combined_input_ali_file
            run_cmd(command_line)
        else:
            error("Format %s not recognized!" % idata_format)
            sys.exit(1)

    # run MACS, first for each replicate
    for i in range(1,configs["data.number_replicates"]+1):
        if configs["data.has_control"]:
            # run MACS w/ control
            command_line = configs["macs.macs_main"]+" -w -S -t "+tfiles[i-1]+" -c "+ combined_input_ali_file + " -n "+configs["sample.sample_id"]+"_rep"+str(i)
            run_cmd(command_line)
            # copy out and rename the wiggle file
            command_line = "zcat "+configs["sample.sample_id"]+"_rep"+str(i)+"_MACS_wiggle/treat/"+configs["sample.sample_id"]+"_rep"+str(i)+"_treat_afterfiting_all.wig.gz > "+configs["macs.output_treat_wig_replicates"][i-1]
            run_cmd(command_line)

            # second run for bedGraph then to bigWig
            # run MACS w/ control
            command_line = configs["macs.macs_main"]+" -B -S -t "+tfiles[i-1]+" -c "+ combined_input_ali_file + " -n "+configs["sample.sample_id"]+"_rep"+str(i)
            run_cmd(command_line)
            # copy out and rename the bdg file
            command_line = "zcat "+configs["sample.sample_id"]+"_rep"+str(i)+"_MACS_bedGraph/treat/"+configs["sample.sample_id"]+"_rep"+str(i)+"_treat_afterfiting_all.bdg.gz > "+configs["macs.output_treat_bdg_replicates"][i-1]
            run_cmd(command_line)
            command_line = configs["macs.bedgraphtobigwig_main"]+" "+configs["macs.output_treat_bdg_replicates"][i-1]+" "+configs["macs.bedgraphtobigwig_chrom_len_path"]+" "+configs["macs.output_treat_bw_replicates"][i-1]
            run_cmd(command_line)

        else:
            # run MACS w/o control
            command_line = configs["macs.macs_main"]+" -w -S -t "+tfiles[i-1]+" -n "+configs["sample.sample_id"]+"_rep"+str(i)
            run_cmd(command_line)            
            # copy out and rename the wiggle file
            command_line = "zcat "+configs["sample.sample_id"]+"_rep"+str(i)+"_MACS_wiggle/treat/"+configs["sample.sample_id"]+"_rep"+str(i)+"_treat_afterfiting_all.wig.gz > "+configs["macs.output_treat_wig_replicates"][i-1]
            run_cmd(command_line)

            # second run for bedGraph then to bigWig
            # run MACS w/o control
            command_line = configs["macs.macs_main"]+" -B -S -t "+tfiles[i-1]+" -n "+configs["sample.sample_id"]+"_rep"+str(i)
            run_cmd(command_line)            
            # copy out and rename the bdg file
            command_line = "zcat "+configs["sample.sample_id"]+"_rep"+str(i)+"_MACS_bedGraph/treat/"+configs["sample.sample_id"]+"_rep"+str(i)+"_treat_afterfiting_all.bdg.gz > "+configs["macs.output_treat_bdg_replicates"][i-1]
            run_cmd(command_line)
            command_line = configs["macs.bedgraphtobigwig_main"]+" "+configs["macs.output_treat_bdg_replicates"][i-1]+" "+configs["macs.bedgraphtobigwig_chrom_len_path"]+" "+configs["macs.output_treat_bw_replicates"][i-1]
            run_cmd(command_line)

    # run MACS for the combined treatment
    if configs["data.number_replicates"] == 1:
        # no need to run MACS again, simply copy the previous results
        command_line = "cp "+configs["sample.sample_id"]+"_rep1_peaks.xls"+" "+configs["macs.output_xls"]
        run_cmd(command_line)
        command_line = "cp "+configs["sample.sample_id"]+"_rep1_peaks.bed"+" "+configs["macs.output_bed"]
        run_cmd(command_line)
        command_line = "cp "+configs["sample.sample_id"]+"_rep1_summits.bed"+" "+configs["macs.output_summits"]
        run_cmd(command_line)
        command_line = "cp "+configs["macs.output_treat_wig_replicates"][0]+" "+configs["macs.output_treat_wig"]
        run_cmd(command_line)
        command_line = "cp "+configs["macs.output_treat_bdg_replicates"][0]+" "+configs["macs.output_treat_bdg"]
        run_cmd(command_line)
        # convert bdg to bw
        command_line = configs["macs.bedgraphtobigwig_main"]+" "+configs["macs.output_treat_bdg"]+" "+configs["macs.bedgraphtobigwig_chrom_len_path"]+" "+configs["macs.output_treat_bw"]
        run_cmd(command_line)
        
        if configs["data.has_control"]:
            # copy the wiggle file for control
            command_line = "zcat "+configs["sample.sample_id"]+"_rep1_MACS_wiggle/control/"+configs["sample.sample_id"]+"_rep1_control_afterfiting_all.wig.gz > "+configs["macs.output_control_wig"]
            run_cmd(command_line)
            # copy the bedGraph for control
            command_line = "zcat "+configs["sample.sample_id"]+"_rep1_MACS_bedGraph/control/"+configs["sample.sample_id"]+"_rep1_control_afterfiting_all.bdg.gz > "+configs["macs.output_control_bdg"]
            run_cmd(command_line)
            # convert it to bigwig
            command_line = configs["macs.bedgraphtobigwig_main"]+" "+configs["macs.output_control_bdg"]+" "+configs["macs.bedgraphtobigwig_chrom_len_path"]+" "+configs["macs.output_control_bw"]
            run_cmd(command_line)
            
    else:
        # run MACS on combined alignment files
        if configs["data.has_control"]:
            command_line = configs["macs.macs_main"]+" -w -S -t "+combined_treat_ali_file+" -c "+combined_input_ali_file+" -n "+configs["sample.sample_id"]
            run_cmd(command_line)
            # copy out and rename the wiggle file
            command_line = "zcat "+configs["sample.sample_id"]+"_MACS_wiggle/treat/"+configs["sample.sample_id"]+"_treat_afterfiting_all.wig.gz > "+configs["macs.output_treat_wig"]
            run_cmd(command_line)
            command_line = "zcat "+configs["sample.sample_id"]+"_MACS_wiggle/control/"+configs["sample.sample_id"]+"_control_afterfiting_all.wig.gz > "+configs["macs.output_control_wig"]
            run_cmd(command_line)

            # second run for bedGraph
            command_line = configs["macs.macs_main"]+" -B -S -t "+combined_treat_ali_file+" -c "+combined_input_ali_file+" -n "+configs["sample.sample_id"]
            run_cmd(command_line)
            # copy out and rename the wiggle file
            command_line = "zcat "+configs["sample.sample_id"]+"_MACS_bedGraph/treat/"+configs["sample.sample_id"]+"_treat_afterfiting_all.bdg.gz > "+configs["macs.output_treat_bdg"]
            run_cmd(command_line)
            # convert it to bigwig
            command_line = configs["macs.bedgraphtobigwig_main"]+" "+configs["macs.output_treat_bdg"]+" "+configs["macs.bedgraphtobigwig_chrom_len_path"]+" "+configs["macs.output_treat_bw"]
            run_cmd(command_line)
            
            command_line = "zcat "+configs["sample.sample_id"]+"_MACS_bedGraph/control/"+configs["sample.sample_id"]+"_control_afterfiting_all.bdg.gz > "+configs["macs.output_control_bdg"]
            run_cmd(command_line)
            # convert it to bigwig
            command_line = configs["macs.bedgraphtobigwig_main"]+" "+configs["macs.output_control_bdg"]+" "+configs["macs.bedgraphtobigwig_chrom_len_path"]+" "+configs["macs.output_control_bw"]
            run_cmd(command_line)

        else:
            command_line = configs["macs.macs_main"]+" -w -S -t "+combined_treat_ali_file+" -n "+configs["sample.sample_id"]
            run_cmd(command_line)
            # copy out and rename the wiggle file
            command_line = "zcat "+configs["sample.sample_id"]+"_MACS_wiggle/treat/"+configs["sample.sample_id"]+"_treat_afterfiting_all.wig.gz > "+configs["macs.output_treat_wig"]
            run_cmd(command_line)

            # second run for bedGraph
            command_line = configs["macs.macs_main"]+" -B -S -t "+combined_treat_ali_file+" -n "+configs["sample.sample_id"]
            run_cmd(command_line)
            # copy out and rename the wiggle file
            command_line = "zcat "+configs["sample.sample_id"]+"_MACS_bedGraph/treat/"+configs["sample.sample_id"]+"_treat_afterfiting_all.bdg.gz > "+configs["macs.output_treat_bdg"]
            run_cmd(command_line)
            # convert it to bigwig
            command_line = configs["macs.bedgraphtobigwig_main"]+" "+configs["macs.output_treat_bdg"]+" "+configs["macs.bedgraphtobigwig_chrom_len_path"]+" "+configs["macs.output_treat_bw"]
            run_cmd(command_line)


            
    # rename input files by faking samtools output
    for i in xrange(len(tfiles)):
        command_line = "mv "+tfiles[i]+" "+configs["samtools.treat_output_replicates"][i]
        run_cmd(command_line)
    command_line = "mv "+combined_treat_ali_file+" "+configs["samtools.treat_output"]
    run_cmd(command_line)
    if configs["data.has_control"]:
        command_line = "mv "+combined_input_ali_file+" "+configs["samtools.control_output"]
        run_cmd(command_line)
    return True

def _step2_macs_seq (configs):
    """Step2 MACS if the raw data type is seq. So it will use the output from step1.
    
    """
    # check the input
    t_rep_files = configs["samtools.treat_output_replicates"]
    t_comb_file = configs["samtools.treat_output"]
    c_comb_file = configs["samtools.control_output"]
    macs_genome_option = " -g "+ configs["sample.species"]+" "
    
    # run MACS, first for each replicate
    for i in range(1,configs["data.number_replicates"]+1):
        if configs["data.has_control"]:
            # run MACS w/ control
            command_line = configs["macs.macs_main"]+macs_genome_option+" -w -S -t "+t_rep_files[i-1]+" -c "+ c_comb_file + " -n "+configs["sample.sample_id"]+"_rep"+str(i)
            run_cmd(command_line)
            # copy out and rename the wiggle file
            command_line = "zcat "+configs["sample.sample_id"]+"_rep"+str(i)+"_MACS_wiggle/treat/"+configs["sample.sample_id"]+"_rep"+str(i)+"_treat_afterfiting_all.wig.gz > "+configs["macs.output_treat_wig_replicates"][i-1]
            run_cmd(command_line)

            # second run for bedGraph
            # run MACS w/ control
            command_line = configs["macs.macs_main"]+macs_genome_option+" -B -S -t "+t_rep_files[i-1]+" -c "+ c_comb_file + " -n "+configs["sample.sample_id"]+"_rep"+str(i)
            run_cmd(command_line)
            # copy out and rename the bdg file
            command_line = "zcat "+configs["sample.sample_id"]+"_rep"+str(i)+"_MACS_bedGraph/treat/"+configs["sample.sample_id"]+"_rep"+str(i)+"_treat_afterfiting_all.bdg.gz > "+configs["macs.output_treat_bdg_replicates"][i-1]
            run_cmd(command_line)
            # convert bdg to bw
            command_line = configs["macs.bedgraphtobigwig_main"]+" "+configs["macs.output_treat_bdg_replicates"][i-1]+" "+configs["macs.bedgraphtobigwig_chrom_len_path"]+" "+configs["macs.output_treat_bw_replicates"][i-1]
            run_cmd(command_line)
            
        else:
            # run MACS w/o control
            command_line = configs["macs.macs_main"]+macs_genome_option+" -w -S -t "+t_rep_files[i-1]+" -n "+configs["sample.sample_id"]+"_rep"+str(i)
            run_cmd(command_line)            
            # copy out and rename the wiggle file
            command_line = "zcat "+configs["sample.sample_id"]+"_rep"+str(i)+"_MACS_wiggle/treat/"+configs["sample.sample_id"]+"_rep"+str(i)+"_treat_afterfiting_all.wig.gz > "+configs["macs.output_treat_wig_replicates"][i-1]
            run_cmd(command_line)

            # second run for bedGraph
            # run MACS w/o control
            command_line = configs["macs.macs_main"]+macs_genome_option+" -B -S -t "+t_rep_files[i-1]+" -n "+configs["sample.sample_id"]+"_rep"+str(i)
            run_cmd(command_line)            
            # copy out and rename the bdg file
            command_line = "zcat "+configs["sample.sample_id"]+"_rep"+str(i)+"_MACS_bedGraph/treat/"+configs["sample.sample_id"]+"_rep"+str(i)+"_treat_afterfiting_all.bdg.gz > "+configs["macs.output_treat_bdg_replicates"][i-1]
            run_cmd(command_line)
            # convert bdg to bw
            command_line = configs["macs.bedgraphtobigwig_main"]+" "+configs["macs.output_treat_bdg_replicates"][i-1]+" "+configs["macs.bedgraphtobigwig_chrom_len_path"]+" "+configs["macs.output_treat_bw_replicates"][i-1]
            run_cmd(command_line)


    # run MACS for the combined treatment
    if configs["data.number_replicates"] == 1:
        # no need to run MACS again, simply copy the previous results
        command_line = "cp "+configs["sample.sample_id"]+"_rep1_peaks.xls"+" "+configs["macs.output_xls"]
        run_cmd(command_line)
        command_line = "cp "+configs["sample.sample_id"]+"_rep1_peaks.bed"+" "+configs["macs.output_bed"]
        run_cmd(command_line)
        command_line = "cp "+configs["sample.sample_id"]+"_rep1_summits.bed"+" "+configs["macs.output_summits"]
        run_cmd(command_line)
        command_line = "cp "+configs["macs.output_treat_wig_replicates"][0]+" "+configs["macs.output_treat_wig"]
        run_cmd(command_line)
        command_line = "cp "+configs["macs.output_treat_bdg_replicates"][0]+" "+configs["macs.output_treat_bdg"]
        run_cmd(command_line)
        # convert bdg to bw
        command_line = configs["macs.bedgraphtobigwig_main"]+" "+configs["macs.output_treat_bdg"]+" "+configs["macs.bedgraphtobigwig_chrom_len_path"]+" "+configs["macs.output_treat_bw"]
        run_cmd(command_line)        
        if configs["data.has_control"]:
            command_line = "zcat "+configs["sample.sample_id"]+"_rep1_MACS_wiggle/control/"+configs["sample.sample_id"]+"_rep1_control_afterfiting_all.wig.gz > "+configs["macs.output_control_wig"]
            run_cmd(command_line)
            # for bdg
            command_line = "zcat "+configs["sample.sample_id"]+"_rep1_MACS_bedGraph/control/"+configs["sample.sample_id"]+"_rep1_control_afterfiting_all.bdg.gz > "+configs["macs.output_control_bdg"]
            run_cmd(command_line)
            # convert bdg to bw
            command_line = configs["macs.bedgraphtobigwig_main"]+" "+configs["macs.output_control_bdg"]+" "+configs["macs.bedgraphtobigwig_chrom_len_path"]+" "+configs["macs.output_control_bw"]
            run_cmd(command_line)        

    else:
        # run MACS on combined alignment files
        if configs["data.has_control"]:
            command_line = configs["macs.macs_main"]+macs_genome_option+" -w -S -t "+t_comb_file+" -c "+c_comb_file+" -n "+configs["sample.sample_id"]
            run_cmd(command_line)
            # copy out and rename the wiggle file
            command_line = "zcat "+configs["sample.sample_id"]+"_MACS_wiggle/treat/"+configs["sample.sample_id"]+"_treat_afterfiting_all.wig.gz > "+configs["macs.output_treat_wig"]
            run_cmd(command_line)
            command_line = "zcat "+configs["sample.sample_id"]+"_MACS_wiggle/control/"+configs["sample.sample_id"]+"_control_afterfiting_all.wig.gz > "+configs["macs.output_control_wig"]
            run_cmd(command_line)

            # second run for bedGraph
            command_line = configs["macs.macs_main"]+macs_genome_option+" -B -S -t "+t_comb_file+" -c "+c_comb_file+" -n "+configs["sample.sample_id"]
            run_cmd(command_line)
            # copy out and rename the bdg file
            command_line = "zcat "+configs["sample.sample_id"]+"_MACS_bedGraph/treat/"+configs["sample.sample_id"]+"_treat_afterfiting_all.bdg.gz > "+configs["macs.output_treat_bdg"]
            run_cmd(command_line)
            command_line = "zcat "+configs["sample.sample_id"]+"_MACS_bedGraph/control/"+configs["sample.sample_id"]+"_control_afterfiting_all.bdg.gz > "+configs["macs.output_control_bdg"]
            run_cmd(command_line)
            # convert bdg to bw for treat
            command_line = configs["macs.bedgraphtobigwig_main"]+" "+configs["macs.output_treat_bdg"]+" "+configs["macs.bedgraphtobigwig_chrom_len_path"]+" "+configs["macs.output_treat_bw"]
            run_cmd(command_line)
            # convert bdg to bw for control
            command_line = configs["macs.bedgraphtobigwig_main"]+" "+configs["macs.output_control_bdg"]+" "+configs["macs.bedgraphtobigwig_chrom_len_path"]+" "+configs["macs.output_control_bw"]
            run_cmd(command_line)        
            
        else:
            command_line = configs["macs.macs_main"]+macs_genome_option+" -w -S -t "+t_comb_file+" -n "+configs["sample.sample_id"]
            run_cmd(command_line)
            # copy out and rename the wiggle file
            command_line = "zcat "+configs["sample.sample_id"]+"_MACS_wiggle/treat/"+configs["sample.sample_id"]+"_treat_afterfiting_all.wig.gz > "+configs["macs.output_treat_wig"]
            run_cmd(command_line)

            # second run for bedGraph
            command_line = configs["macs.macs_main"]+macs_genome_option+" -B -S -t "+t_comb_file+" -n "+configs["sample.sample_id"]
            run_cmd(command_line)
            # copy out and rename the wiggle file
            command_line = "zcat "+configs["sample.sample_id"]+"_MACS_bedGraph/treat/"+configs["sample.sample_id"]+"_treat_afterfiting_all.bdg.gz > "+configs["macs.output_treat_bdg"]
            run_cmd(command_line)
            # convert bdg to bw for treat
            command_line = configs["macs.bedgraphtobigwig_main"]+" "+configs["macs.output_treat_bdg"]+" "+configs["macs.bedgraphtobigwig_chrom_len_path"]+" "+configs["macs.output_treat_bw"]
            run_cmd(command_line)
            
    return True

def step3_ceas (configs):
    """Step3: run CEAS for the combined result.

    """
    # check the startstep whether to pass this step

    if configs["others.startstep"] <= 3 and 3 <= configs["others.endstep"]:
        info("Step 3: CEAS...")
    else:
        info("Step 3 CEAS is skipped as requested.")
        return False

    # check the input
    peak_bed_file = configs["macs.output_bed"]
    wiggle_file = configs["macs.output_treat_wig"]

    if not os.path.isfile(peak_bed_file):
        error("Input for CEAS is missing: peak file %s can't be found!" % peak_bed_file)
        sys.exit(1)
    if not os.path.isfile(wiggle_file):
        error("Input for CEAS is missing: wiggle file %s can't be found!" % wiggle_file)
        sys.exit(1)

    # run CEAS
    if configs["ceas.ceas_genetable_path"]:
        ceas_gt_option = " -g "+configs["ceas.ceas_genetable_path"]+" "
    else:
        ceas_gt_option = ""
    if configs["ceas.ceas_promoter_sizes"]:
        ceas_sizes_option = " --sizes "+configs["ceas.ceas_promoter_sizes"]+" "
    else:
        ceas_sizes_option = ""
    if configs["ceas.ceas_bipromoter_sizes"]:
        ceas_bisizes_option = " --bisizes "+configs["ceas.ceas_bipromoter_sizes"]+" "
    else:
        ceas_bisizes_option = ""
    if configs["ceas.ceas_rel_dist"]:
        ceas_rel_dist_option = " --rel-dist "+configs["ceas.ceas_rel_dist"]+" "        
    else:
        ceas_rel_dist_option = ""
    ceas_name_option = " --name "+configs["sample.sample_id"]+"_ceas "
    
    command_line = configs["ceas.ceas_main"]+ceas_name_option+ceas_gt_option+ceas_sizes_option+ceas_bisizes_option+ceas_rel_dist_option+" -b "+peak_bed_file+" -w "+wiggle_file
    run_cmd(command_line)
    
    return True

def step4_venn (configs):
    """Step4: run Venn diagram: 1) compare replicates; 2) overlap with human/mouse DHS.

    """
    # check the startstep whether to pass this step

    if configs["others.startstep"] <= 4 and 4 <= configs["others.endstep"]:
        info("Step 4: Venn diagram...")
    else:
        info("Step 4 Venn diagram is skipped as requested.")
        return False

    # check the input
    peak_bed_file_replicates = configs["macs.output_bed_replicates"]
    peak_bed_file = configs["macs.output_bed"]
    DHS_bed_file = configs["bedtools.dhs_bed_path"]

    for f in peak_bed_file_replicates:
        if not os.path.isfile(f):
            error("Input for Venn diagram is missing: peak file %s can't be found!" % f)
            sys.exit(1)
    if not os.path.isfile(peak_bed_file):
        error("Input for Venn diagram is missing: peak file %s can't be found!" % peak_bed_file)
        sys.exit(1)
    if not os.path.isfile(DHS_bed_file):
        error("Input for BedTools is missing: peak file %s can't be found!" % DHS_bed_file)
        sys.exit(1)
        
    if configs["data.number_replicates"] > 3:
        # can't process > 3 replicates. This may cause error in the following steps, so simply skip it.
        warn("Venn diagram can't process > 3 files!")
        command_line = "touch "+configs["venn.replicates_output_png"]
        run_cmd(command_line)
    elif configs["data.number_replicates"] == 1:
        # no replicates, no Venn diagram
        info("No replicates, so no Venn diagram for replicates")
        command_line = "touch "+configs["venn.replicates_output_png"]
        run_cmd(command_line)
    else:
        # run Venn diagram for replicates
        command_line = configs["venn.venn_diagram_main"]+" -t Overlap_of_Replicates"+" "+" ".join(peak_bed_file_replicates)+" "+" ".join(map(lambda x:"-l replicate_"+str(x),xrange(1,configs["data.number_replicates"]+1)))
        run_cmd(command_line)
        command_line = "mv venn_diagram.png "+configs["venn.replicates_output_png"]
        run_cmd(command_line)

    # run Venn for DHS overlap
    overlapped_bed_file = "overlapped_bed_file"
    command_line = configs["bedtools.intersectbed_main"]+" -wa -u -a "+peak_bed_file+" -b "+DHS_bed_file+" > "+overlapped_bed_file
    run_cmd(command_line)
    # count number of rows
    fhd = open(peak_bed_file,"r")
    num_total_peaks = len(fhd.readlines())
    fhd.close()
    fhd = open(overlapped_bed_file,"r")
    num_overlapped_peaks = len(fhd.readlines())
    fhd.close()
    fhd = open(configs["bedtools.dhs_output_txt"],"w")
    fhd.write("total_peaks = %d\n" % num_total_peaks)
    fhd.write("peaks_overlapped_with_DHSs = %d\n" % num_overlapped_peaks)
    fhd.write("percentage_of_peaks_overlapped_with_DHSs = %.2f%%\n" % (float(num_overlapped_peaks)/num_total_peaks*100))
    fhd.close()
    
    return True

def step5_cor (configs):
    """Step5: run correlation plot tool on replicates.

    """
    # check the startstep whether to pass this step

    if configs["others.startstep"] <= 5 and 5 <= configs["others.endstep"]:
        info("Step 5: Correlation plot...")
    else:
        info("Step 5 Correlation plot is skipped as requested.")
        return False

    # check the input
    wiggle_file_replicates = configs["macs.output_treat_wig_replicates"]

    for f in wiggle_file_replicates:
        if not os.path.isfile(f):
            error("Input for correlation plot is missing: wiggle file %s can't be found!" % f)
            sys.exit(1)

    if configs["data.number_replicates"] == 1:
        # no replicates, no correlation plot
        info("No replicates, so no correlation plot for replicates")
        command_line = "touch "+configs["correlation.output_pdf"]
        run_cmd(command_line)
        command_line = "touch "+configs["correlation.output_R"]
        run_cmd(command_line)
        return True
        
    # parameters
    if configs["correlation.wig_correlation_step"]:
        cor_step_option = " -s "+configs["correlation.wig_correlation_step"]+" "
    else:
        cor_step_option = " -s 10 "

    if configs["correlation.wig_correlation_method"]:
        cor_method_option = " -m "+configs["correlation.wig_correlation_method"]+" "
    else:
        cor_method_option = " -m mean"

    if configs["correlation.wig_correlation_min"]:
        cor_min_option = " --min-score "+configs["correlation.wig_correlation_min"]+" "
    else:
        cor_min_option = " --min-score 2 "

    if configs["correlation.wig_correlation_max"]:
        cor_max_option = " --max-score "+configs["correlation.wig_correlation_max"]+" "
    else:
        cor_max_option = " --max-score 50 "

    cor_db_option = " -d "+configs["sample.assembly_name"]+" "

    # run correlation plot for replicates
    command_line = configs["correlation.wig_correlation_main"]+cor_db_option+cor_step_option+\
                   cor_method_option+cor_min_option+cor_max_option+\
                   " -r "+configs["correlation.output_R"]+" "+" ".join(wiggle_file_replicates)+\
                   " "+" ".join(map(lambda x:"-l replicate_"+str(x),xrange(1,configs["data.number_replicates"]+1)))
    run_cmd(command_line)
    command_line = "Rscript "+configs["correlation.output_R"]
    run_cmd(command_line)

    return True

def step6_conserv (configs):
    """Step6: conservation plot on peak summits of combined runs.

    """
    if configs["others.startstep"] <= 6 and 6 <= configs["others.endstep"]:
        info("Step 6: Conservation plot...")
    else:
        info("Step 6 Conservation plot is skipped as requested.")
        return False

    # check the input
    peak_summits_file = configs["macs.output_summits"]

    if not os.path.isfile(peak_summits_file):
        error("Input for conservation plot is missing: peak file %s can't be found!" % peak_summits_file)
        sys.exit(1)
        
    # run Venn diagram for replicates
    command_line = configs["conservation.conserv_plot_main"]+" -t Conservation_at_summits"+" -d "+configs["conservation.conserv_plot_phast_path"]+" -l Peak_summits "+peak_summits_file
    run_cmd(command_line)
    command_line = "mv tmp.R "+configs["conservation.output_R"]
    run_cmd(command_line)
    command_line = "mv tmp.bmp "+configs["conservation.output_bmp"]
    run_cmd(command_line)
    return True

def step7_seqpos (configs):
    """Step7: SeqPos on the top 1000 binding sites summits against TRANSFAC, JASPAR and de novo motifs.
    
    """
    if configs["others.startstep"] <= 7 and 7 <= configs["others.endstep"]:
        info("Step 7: Conservation plot...")
    else:
        info("Step 7 SeqPos is skipped as requested.")
        return False

    # check the input
    peak_summits_file = configs["macs.output_summits"]

    if not os.path.isfile(peak_summits_file):
        error("Input for SeqPos is missing: peak file %s can't be found!" % peak_summits_file)
        sys.exit(1)

    # generate top # of peaks
    psf_fhd = open(peak_summits_file)
    p_list = []
    for i in psf_fhd:
        p_list.append( (i,float(i.split()[-1])) )
    top_n = int(configs["seqpos.seqpos_top_peaks"])
    top_n_summits = map(lambda x:x[0],sorted(p_list,key=lambda x:x[1],reverse=True)[:top_n])
    top_n_summits_file = "top"+str(top_n)+"_summits.bed"
    top_n_summits_fhd = open(top_n_summits_file,"w")
    for i in top_n_summits:
        top_n_summits_fhd.write(i)
    top_n_summits_fhd.close()
    info("Top %d summits are written to %s" % (top_n,top_n_summits_file))
    
    # run SeqPos: use the current daisy version as standard, you may need to modify the options.
    # options
    if configs["seqpos.seqpos_width"]:
        seqpos_width_option = " -w "+configs["seqpos.seqpos_width"]+" "
    else:
        seqpos_width_option = " -w 600 "
    if configs["seqpos.seqpos_pvalue_cutoff"]:
        seqpos_pvalue_option = " -p "+configs["seqpos.seqpos_pvalue_cutoff"]+" "
    else:
        seqpos_pvalue_option = " -p 0.001 "
    if configs["seqpos.seqpos_motif_db_selection"]:
        seqpos_motif_option = " -m "+configs["seqpos.seqpos_motif_db_selection"]+" "
    else:
        seqpos_motif_option = " -m transfac.xml,pbm.xml,jaspar.xml "
    seqpos_filter_option = " -s "+configs["sample.species"]
    
    command_line = configs["seqpos.seqpos_main"]+" -d "+seqpos_width_option+seqpos_pvalue_option+seqpos_motif_option+seqpos_filter_option+" "+top_n_summits_file+" "+configs["sample.assembly_name"]
    run_cmd(command_line)
    command_line = "zip -r "+configs["seqpos.output_zip"]+" results/"
    run_cmd(command_line)
    return True

def step8_package_result ( configs ):
    """Package result and generate a summary file. -> a subfolder
    named as sample#sample_id and zip it as sample#sample_id.tar.bz2

    """
    if configs["others.startstep"] <= 8 and 8 <= configs["others.endstep"]:
        info("Step 8: Packaging results...")
    else:
        info("Step 8 Packaging is skipped as requested.")
        return False

    subfolder = "sample"+configs["sample.sample_id"]
    command_line = "mkdir "+subfolder
    run_cmd(command_line)
    
    all_files = []
    e = all_files.extend
    a = all_files.append
    
    e(configs["samtools.treat_output_replicates"]) # treatment bam files for replicates
    a(configs["samtools.treat_output"])            # treatment bam file for combined
    a(configs["samtools.control_output"])          # control bam file for combined
    a(configs["macs.output_xls"])
    e(configs["macs.output_bed_replicates"])
    a(configs["macs.output_bed"])
    a(configs["macs.output_summits"])
    e(configs["macs.output_treat_wig_replicates"])
    e(configs["macs.output_treat_bw_replicates"])    
    a(configs["macs.output_treat_wig"])
    a(configs["macs.output_treat_bw"])
    a(configs["macs.output_control_wig"])
    a(configs["macs.output_control_bw"])    
    a(configs["ceas.output_xls"])
    a(configs["ceas.output_pdf"])
    a(configs["ceas.output_R"])
    a(configs["venn.replicates_output_png"])
    a(configs["bedtools.dhs_output_txt"])
    a(configs["correlation.output_pdf"])
    a(configs["correlation.output_R"])
    a(configs["conservation.output_bmp"])
    a(configs["conservation.output_R"])
    a(configs["seqpos.output_zip"])

    f = open(configs["macs.output_bed"])
    number_of_peaks = len(f.readlines())
    logfhd.write("----\nNumber of peaks: %d\n" % number_of_peaks)
    f.close()
    f = open(configs["macs.output_xls"])
    d_value = 0
    for l in f:
        l.rstrip()
        if l.startswith("# d = "):
            d_value = int(l[6:])
            break
    logfhd.write("Value d from MACS is %d\n----\n" % d_value)
    f.close()

    # this part is to write a summary file
    sum_fhd = open("sample"+configs["sample.sample_id"]+"_summary.txt","w")
    sum_content = """# This file summarizes the output from pipeline. Use ConfigParser to parse it.
[replicates]
treatment_bam = %s
macs_peaks = %s
macs_treat_wig = %s
macs_treat_bw = %s    
[sample]
sample_id = %s
username = %s
treat_bam = %s
control_bam = %s
macs_xls = %s
macs_peaks = %s
macs_summits = %s
macs_treat_wig = %s
macs_treat_bw = %s
macs_control_wig = %s
macs_control_bw = %s
ceas_xls = %s
ceas_pdf = %s
ceas_R = %s
venn_diagram_png = %s
dhs_summary_txt = %s
correlation_pdf = %s
correlation_R = %s
conservation_bmp = %s
conservation_R = %s
seqpos_zip = %s
""" % (
",".join(configs["samtools.treat_output_replicates"]),
",".join(configs["macs.output_bed_replicates"]),
",".join(configs["macs.output_treat_wig_replicates"]),
",".join(configs["macs.output_treat_bw_replicates"]),
configs["sample.sample_id"],
configs["sample.username"],
configs["samtools.treat_output"],
configs["samtools.control_output"],
configs["macs.output_xls"],
configs["macs.output_bed"],
configs["macs.output_summits"],
configs["macs.output_treat_wig"],
configs["macs.output_treat_bw"],
configs["macs.output_control_wig"],
configs["macs.output_control_bw"],
configs["ceas.output_xls"],
configs["ceas.output_pdf"],
configs["ceas.output_R"],
configs["venn.replicates_output_png"],
configs["bedtools.dhs_output_txt"],
configs["correlation.output_pdf"],
configs["correlation.output_R"],
configs["conservation.output_bmp"],
configs["conservation.output_R"],
configs["seqpos.output_zip"],
)
    sum_fhd.write(sum_content)

    sum_content2="""
[summary]
%s
%s
d = %d
""" % (
file(configs["bedtools.dhs_output_txt"]).read(),
__summarize_peaks(configs["macs.output_xls"]),
d_value
)
    sum_fhd.write(sum_content2)
    sum_fhd.close()

    command_line = "mv "+"sample"+configs["sample.sample_id"]+"_summary.txt "+subfolder+"/"
    run_cmd(command_line)
    command_line = "mv "+" ".join(all_files)+" "+subfolder+"/"
    run_cmd(command_line)
    command_line = "cp log "+subfolder+"/"
    run_cmd(command_line)
    command_line = "cp "+configs["orig_config_file"]+" "+subfolder+"/"+configs["config_file"]
    run_cmd(command_line)
    command_line = "tar -zcf "+subfolder+".tar.gz "+subfolder+"/"
    run_cmd(command_line)
    info("File is packaged! Please send the tar.gz file to Cistrome Aspera dropbox!\n")


# ------------------------------------
# Main function
# ------------------------------------
def main():
    usage = "usage: %prog <config file>"
    description = "ChIP-seq pipeline demo"
    
    optparser = OptionParser(version="%prog 0.1",description=description,usage=usage,add_help_option=False)
    optparser.add_option("-h","--help",action="help",help="Show this help message and exit.")
    optparser.add_option("-s","--step",dest="startstep",type="int",
                         help="Select the step to start from, use it if you want to resume the pipeline after any interruption. Step 1: bowtie mapping; step 2: macs peak calling; step 3: CEAS analysis; step 4: Venn diagram; step 5: correlation; step 6: conservation; step 7: seqpos; step 8: packaging the results. Default is blank, so that the pipeline will start from the step 1.", default=1)
    optparser.add_option("-S",dest="stopatstep",action="store_true",default=False,
                         help="If True, the pipeline will stop after it finished the step specified by -s option.")    
    (options,args) = optparser.parse_args()

    startstep = options.startstep
    stopatstep = options.stopatstep

    if not args or startstep<1 or startstep>8:
        optparser.print_help()
        sys.exit(1)

    # parse the config file
    config_file = args[0]
    configs = read_config(config_file)
    configs["orig_config_file"] = config_file

    # decide the start step and end step of the pipeline
    configs["others.startstep"] = startstep
    if stopatstep:
        configs["others.endstep"] = startstep
    else:
        configs["others.endstep"] = 8

    configs["others.cwd"] = os.getcwd()
    
    if not check_conf_validity(configs):
        error("Exit as failing config file validity check!")
        sys.exit(1)
    else:
        info("Pass the conf file validity check!")

    if not check_file_validity(configs):
        error("Exit as failing data file validity check!")
        sys.exit(1)
    else:
        info("Pass the data file validity check!")

    if not check_cmd_validity(configs):
        error("Exit as failing command validity check!")
        sys.exit(1)
    else:
        info("Pass the command line validity check!")

    if not check_lib_validity(configs):
        error("Exit as failing tool libraries validity check!")
        sys.exit(1)
    else:
        info("Pass the tool libraries file validity check!")

    info("All checks are passed! Prepare the pipeline...")

    steps = [step1_bowtie,step2_macs,step3_ceas,step4_venn,step5_cor,step6_conserv,step7_seqpos,step8_package_result]
    prepare_output_file_names(configs)
    steps[0](configs)
    steps[1](configs)
    steps[2](configs)
    steps[3](configs)
    steps[4](configs)
    steps[5](configs)                    
    steps[6](configs)
    steps[7](configs)    
    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.stderr.write("User interrupt me! ;-) See you!\n")
        sys.exit(0)

    
logfhd.close()
