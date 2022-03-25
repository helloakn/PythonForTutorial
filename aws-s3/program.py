# Default Module
import math,os
import sys
# Installed Module
import boto
from boto.s3.key import Key
from filechunkio import FileChunkIO

class EnvFile:
    content = []
    def __init__(self, _filename):
        self.envFileName = _filename
        f = open(self.envFileName, "r")
        for x in f:
            arr = x.split("=")
            if len(arr)==2:
                arr[1] = arr[1].replace("\n","")
                self.content.append(arr)
    def getValue(self,_key):
        x = [element[1] for element in self.content if element[0] == _key]
        return x[0] if len(x)>=1 else ""

envfile     = EnvFile(".env");

s3_bucket   = envfile.getValue('s3_backet')
s3_key      = envfile.getValue('s3_key')
s3_secret   = envfile.getValue('s3_secret')
s3_folder   = envfile.getValue('s3_folder')

scan_dir    = 'directory path'

argements   = sys.argv

if len(argements)!=2 :
    print("Example")
    print("python3 program.py /var/www/html")
    quit()
else:
    scan_dir = argements[1]

s3          = boto.connect_s3(s3_key,s3_secret)
adaBucket   = s3.get_bucket(s3_bucket) 


# ========================== BEGIN Functiion ===================================================

def percent_cb(complete, total):
    sys.stdout.write('.')
    sys.stdout.flush()

def upload(_sourceFile):
    source_path = _sourceFile
    dis_path = _sourceFile
    source_size = os.stat(_sourceFile).st_size
    dis_path = dis_path.replace(scan_dir,"")
    #mp = bucket.initiate_multipart_upload(s3_folder+"/"+os.path.basename(source_path))
    mp = adaBucket.initiate_multipart_upload(s3_folder+"/"+dis_path)

    chunk_size = 52428800
    chunk_count = int(math.ceil(source_size / float(chunk_size)))
    print("chunk_count")
    print(chunk_count)
    for i in range(chunk_count):
        offset = chunk_size * i
        bytes = min(chunk_size, source_size - offset)
        with FileChunkIO(source_path, 'r', offset=offset,bytes=bytes) as fp:
            print(i)
            mp.upload_part_from_file(fp, part_num=i + 1)
    mp.complete_upload()


def isDir(_path):
    print("is dir : "+_path)
    return os.path.isdir(_path)

def scanDirectory(_path):
    obj = os.scandir(_path)
    print("Scanning Files and Directories in '% s':" % _path)
    for entry in obj :
        if entry.is_dir() or entry.is_file():
            print(entry.name)
            scan_obj = _path + "/" + entry.name
            if isDir(scan_obj):
                scanDirectory(scan_obj)
            else:
                upload(scan_obj)

# ========================== END Functiion ===================================================
print(scan_dir)
scanDirectory(scan_dir)


