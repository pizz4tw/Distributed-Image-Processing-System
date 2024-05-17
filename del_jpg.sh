#!/bin/bash
# del_jpg.sh

LOGFILE="/shared/del_jpg.log"
echo "Script started at $(date)" >> $LOGFILE

# Your delete commands here
rm - /shared/*.jfif /shared/*.gif /shared/*.JPG /shared/*.PNG /shared/*.jpeg /shared/*.png  /shared/*.jpg /shared/*.zip >> $LOGFILE 2>&1

if [ $? -eq 0 ]; then
    echo "Files deleted successfully at $(date)" >> $LOGFILE
else
    echo "Error deleting files at $(date)" >> $LOGFILE
fi
