# Arg 1 is the input file
# Arg 2 (-u) is optional and will update the PDSFileList.pkl file.
#   - This will increase run time
#
source activate shaddai
python gopher.py ../input/SHADDAIinput.txt -o ../output/test2 -i sharad -p edr
#python gopher.py ../input/SHADDAIinput.txt -p rdr
#python gopher.py ../input/SHADDAIinput.txt -p usrdr
source deactivate shaddai
