
from django.core.management import setup_environ
import sys
sys.path.insert(0,'/home/boqin/DC/newdc')
import settings
from openpyxl.reader.excel import load_workbook
setup_environ(settings)


#load the django model
from datacollection import models
#samples = models.Samples.objects.all()


#sample for load 

wb = load_workbook("valade_results_0419-2012.xls")
sheet = wb.get_active_sheet()
cols = []
entries = [] 
for (i,r) in enumerate(sheet.rows):
    if i == 0:
        cols = [c.value for c in r] 
    else:
        tmp = {}
        for (key, cell) in zip(cols, r):
            tmp.__setitem__(key, cell.value)
        entries.append(tmp)

#print len(entries)

#missing files consiste of simple chip_id_missing and none GEO data
CHIP_ID_missing=0 # for missing files
None_GEO=0

for sample in entries:
    control_list=[]
    treat_list=[]
    if sample['ChIP_tech_ID']:
        #create a new entry
        temp=models.Datasets()
        #treat_list=[]
        treat = sample['ChIP_tech_ID'].split(',')
        #3. add the treatments infor
        temp.treatments = sample['ChIP_tech_ID']
        for i in treat:
            if i[:3]=="GSM":
                treat_list.append(i)
            else:
                None_GEO = None_GEO+1
        #0. set id
        temp.id= sample['Datasets_ID']
        #1. set user
        #temp.user = sample['Uploader_Name']
        #2. set paper
        #PMID: sample['PMID']
        try:
            temp.paper=models.Papers.objects.get(pmid=sample['PMID'])
        except:
            continue
        #5. set peak_file, name should be sample['Zip_File_Location_DFCI']+"/"+sample['Datasets_ID']+"_peaks.bed"
        temp.peak_file = sample['Zip_File_Location_DFCI']+"/"+str(sample['Datasets_ID'])+"_peaks.bed"
        #6. set peak_xls_file, name shoule be sample['Zip_File_Location_DFCI']+"/"+sample['Datasets_ID']+"_peaks.xls"
        temp.peak_xls_file = sample['Zip_File_Location_DFCI']+"/"+str(sample['Datasets_ID'])+"_peaks.xls"
        #7. set summit_file, name should be sample['Zip_File_Location_DFCI']+"/"+sample['Datasets_ID']+"_summits.bed"
        temp.summit_file = sample['Zip_File_Location_DFCI']+"/"+str(sample['Datasets_ID'])+"_summits.bed"
        #8. set treat_bw_file, name shold be sample['Zip_File_Location_DFCI']+"/"+sample['Datasets_ID']+"_treat.bw"
        temp.treat_bw_file = sample['Zip_File_Location_DFCI']+"/"+str(sample['Datasets_ID'])+"_treat.bw"
        #9. set cont_bw_file, name should be sample['Zip_File_Location_DFCI']+"/"+str(sample['Datasets_ID'])+"_control_lambda.bw"
        #problem, for those data generated earlier, we might need to use the name like control_lambda.bw
        temp.cont_bw_file = sample['Zip_File_Location_DFCI']+"/"+str(sample['Datasets_ID'])+"_control_.bw"
        #10. set conservation_file, name should be sample['Zip_File_Location_DFCI']+"/"+sample['Datasets_ID']+"_conserv.png"
        temp.conservation_file = sample['Zip_File_Location_DFCI']+"/"+str(sample['Datasets_ID'])+"_conserv.png"
        #problem remained, some of the name for conservaton or format is not standard
        #11. set conservation_r_file, name should be sample['Zip_File_Location_DFCI']+"/"+sample['Datasets_ID']+"conserv.R"
        temp.conservation_r_file = sample['Zip_File_Location_DFCI']+"/"+str(sample['Datasets_ID'])+"conserv.R"
        #12. set ceas_file, name should be sample['Zip_File_Location_DFCI']+"/"+sample['Datasets_ID']+"_ceas_combined.pdf"
        temp.ceas_file = sample['Zip_File_Location_DFCI']+"/"+str(sample['Datasets_ID'])+"_ceas_combined.pdf"
        #13. set ceas_r_file, name should be sample['Zip_File_Location_DFCI']+"/"+sample['Datasets_ID']+"_ceas_CI.R"
        temp.ceas_r_file = sample['Zip_File_Location_DFCI']+"/"+str(sample['Datasets_ID'])+"_ceas_CI.R" 
        #problem remained, is that name standard?
        #14. set ceas_xls_file
        temp.ceas_xls_file = sample['Zip_File_Location_DFCI']+"/"+str(sample['Datasets_ID'])+"_ceas.xls"
        #15. set venn_file, name should be sample['Zip_File_Location_DFCI']+"/"+str(sample['Datasets_ID'])+"_ceas_CI.R"
        #problem remained, could be a blank file and came back for those with replicates
        temp.venn_file = sample['Zip_File_Location_DFCI']+"/"+str(sample['Datasets_ID'])+"_veen_replicates.png"
        #16. set seqpos_file, name should be sample['Zip_File_Location_DFCI']+"/"+str(sample['Datasets_ID'])+"_seqpos.zip"
        temp.seqpos_file = sample['Zip_File_Location_DFCI']+"/"+str(sample['Datasets_ID'])+"_seqpos.zip"
        #potenional problem remained, for thoes non-GEO datasets, that way to handle these replicates may not be proper
        #17 set rep_treat_bw
        rep_treat_bw_list=[]
        for i in range(len(treat_list)):
            #id is like i+1
            j=i+1
            #name like sample['Zip_File_Location_DFCI']+"/"+str(sample['Datasets_ID'])+"_rep"+j+"_peaks.bed"
            rep_treat_bw_list.append(sample['Zip_File_Location_DFCI']+"/"+str(sample['Datasets_ID'])+"_rep"+str(j)+"_peaks.bed")
            
        temp.rep_treat_bw = ",".join(rep_treat_bw_list)
        #18 set rep_treat_peaks
        rep_treat_peaks_list=[]
        for i in range(len(treat_list)):
            j=i+1
            rep_treat_peaks_list.append(sample['Zip_File_Location_DFCI']+"/"+str(sample['Datasets_ID'])+"_rep"+str(j)+"_peaks.bed")
        temp.rep_treat_peaks = ",".join(rep_treat_peaks_list)
        #19 set rep_treat_summits
        #do we store the rep summits file now?
        #20. set rep_cont_bw
        #do we even store the file?
        #21. set cor_pdf_file
        temp.cor_pdf_file = sample['Zip_File_Location_DFCI']+"/"+str(sample['Datasets_ID'])+"_cor.R.pdf"
        #22. set cor_r_file
        temp.cor_r_file = sample['Zip_File_Location_DFCI']+"/"+str(sample['Datasets_ID'])+"_cor.R"
        #22. set conf_file, name should be sample['Zip_File_Location_DFCI']+"/"+ str(sample['Datasets_ID'])+".conf"
        #problem remained, is the name standard?
        temp.conf_file = sample['Zip_File_Location_DFCI']+"/"+str(sample['Datasets_ID'])+".conf"
        #23. set log_file, name should besample['Zip_File_Location_DFCI']+"/"+ "log"
        temp.log_file = sample['Zip_File_Location_DFCI']+"/"+ "log"
        #24. set summary_file, name should be sample['Zip_File_Location_DFCI']+"/"+"dataset"+str(sample['Datasets_ID'])"+"_summary.txt"
        temp.summary_file = sample['Zip_File_Location_DFCI']+"/"+"dataset"+str(sample['Datasets_ID'])+"_summary.txt"   
        #26. set dhs_file
        temp.dhs_file = sample['Zip_File_Location_DFCI']+"/"+str(sample['Datasets_ID'])+"_bedtools_dhs.txt"
        #27. date_created
        #trouble shooting
        #temp.date_created = sample['Curate_Time']
        #creat a new entry in Qc
        qc = models.Qc()
        #add QC measures
        qc.qc1 = sample['QC1']
        qc.qc2 = sample['QC2']
        qc.qc3 = sample['QC3']
        qc.qc4 = sample['QC4']
        qc.qc5 = sample['QC5']
        qc.qc6 = sample['QC6']
        qc.qc7 = sample['QC7']
        qc.qc8 = sample['QC8']
        qc.qc9 = sample['QC9']
        qc.qc10 = sample['QC10']
        qc.id= sample['Datasets_ID']
        qc.save()

        
    else:
        CHIP_ID_missing = CHIP_ID_missing+1
        print "warning!!! treatment file missing!"
    if sample['Control_tech_ID']:
        #control_list=[]
        #4. add the control infor,although optional
        temp.controls =sample['Control_tech_ID']
        control =sample['Control_tech_ID'].split(',')
        for j in control:
            control_list.append(j)
    temp.save()


print CHIP_ID_missing
print None_GEO


print "notes: some of the none_GEO datasets are also imported, which may need further check later"
'''
for i in samples:
    print i.pmid

test=models.Datasets()
#test.user="bo"
test.paper=models.Papers.objects.get(pk=1)
test.treatments=1
test.treatment_file="/mnt/storage/test1"

test.comments="CistromeMap"
test.id=123

test.save()

temp=models.Samples.objects.get(unique_id=j)
#here you got an object with the unique id
print temp.factor
'''
