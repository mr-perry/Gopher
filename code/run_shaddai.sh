# Arg 1 is the input file
# Arg 2 (-u) is optional and will update the PDSFileList.pkl file.
#   - This will increase run time
#
source activate shaddai
python shaddai.py $1 $2 
source deactivate shaddai
