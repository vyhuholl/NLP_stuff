rmdir "./kz_uz_records/__MACOSX"
chmod -R 777 "./kz_uz_records/"
find "./kz_uz_records/" -name "*.wav" -exec afinfo {} \; | awk '/estimated duration/ { print $3 }' | paste -sd+ - | bc | awk '{printf("%02d:%02d\n",($1/60%60),($1%60))}'
