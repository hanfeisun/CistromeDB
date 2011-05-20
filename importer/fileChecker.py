#!/usr/bin/python
"""
SYNOPSIS: given a _summary.txt file as a param, checks to make sure that the 
all of the files in that .txt file exist
"""
import os
import sys
import optparse
import ConfigParser

USAGE = """USAGE: fileChecker
Options:
         -f - pipeline package summary file
"""

def checkFiles(config, format="f"):
    """Returns a list of missing files
    format allows us to print just the files (f), just the keys (k) or both (b)
    """
    #file fields to check: form is XXX.YYY where xxx is the section and yyy
    #is the fieldname, e.g. replicates.treatment_bam =
    #[replicates]
    #treatment_bam
    file_fields = ["replicates.treatment_bam", "replicates.macs_peaks",
                   "replicates.macs_treat_wig", "replicates.macs_treat_bw",
                   "sample.treat_bam", "sample.control_bam", 
                   "sample.macs_xls", "sample.macs_peaks", 
                   "sample.macs_summits", "sample.macs_treat_wig", 
                   "sample.macs_treat_bw", "sample.macs_control_wig",
                   "sample.macs_control_bw", "sample.ceas_xls",
                   "sample.ceas_pdf", "sample.ceas_R",
                   "sample.venn_diagram_png", "sample.dhs_summary_txt",
                   "sample.correlation_pdf", "sample.correlation_R",
                   "sample.conservation_bmp", "sample.conservation_R",
                   "sample.seqpos_zip",
                   ]

    missing_files = []
    for f in file_fields:
        tmp = f.split(".")
        val = config.get(tmp[0], tmp[1])
        if not os.path.exists(val):
            #print "%s:%s" % (".".join(tmp), val)
            if format is "b":
                missing_files.append("%s=%s" % (".".join(tmp), val))
            elif format is "k":
                missing_files.append(".".join(tmp))
            else:#default files only
                missing_files.append(val)

    return missing_files

def main():
    parser = optparse.OptionParser(usage=USAGE)
    parser.add_option("-f", "--file", 
                      help="pipeline package summary file")
    parser.add_option("-k", "--keys", action="store_true",
                      help="print the keys that have missing files")
    parser.add_option("-b", "--both", action="store_true",
                      help="print both the keys and missing files")
    (opts, args) = parser.parse_args(sys.argv)

    if not opts.file:
        print USAGE
        sys.exit(-1)

    config = ConfigParser.ConfigParser()
    config.readfp(open(opts.file))

    format = ""
    if opts.keys: format = "k"
    if opts.both: format = "b"

    missing = checkFiles(config, format)
    print missing

if __name__ == "__main__":
    main()
