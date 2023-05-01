import os, sys, argparse, random, re, subprocess, docker, tarfile
#############################################################################
client = docker.from_env()
#############################################################################
def copy_to(src, dst,untar=True):
    to_container=True
    if(":" in dst):
        name, dst = dst.split(':')
        to_container=True
    elif(":" in src):
        name, src = src.split(':')
        to_container=False
    else:
        return(None)
    container = client.containers.get(name)
    if(to_container):
        os.chdir(os.path.dirname(src))
        filename = os.path.basename(src)
        data = open(filename, 'rb').read()
        container.put_archive(os.path.dirname(dst), data)
    else:
        filename = dst
        f = open(filename+".tar", 'wb')
        bits, stat = container.get_archive(src)
        for chunk in bits:
            f.write(chunk)
        f.close()
    if(untar):
        pass
        os.system("tar -x %s"%(filename+".tar"))
    return(filename)
#############################################################################
def parse_args():
    parser = argparse.ArgumentParser(description="Create Dockerfile from image")
    
    parser.add_argument('--image', '-i',
                        action="store",
                        required=True,
                        help="Image name with tag",
                        default="")
    parser.add_argument('--outputpath', '-o',
                        action="store",
                        help="Save the generated configuration in this folder",
                        default="NewDocker")
    parser.add_argument('--execute', '-e',
                        action="store",
                        help="Execute command inside the container",
                        default="")
    
    args = parser.parse_args()
    return args
#############################################################################
def exec_cmd(command_str):
    result = subprocess.run(command_str.split(), stdout=subprocess.PIPE)
    return(result.stdout.decode().strip())
#############################################################################
args=parse_args()
#############################################################################
''' STUB
args.image='openvswitch/ovs:2.12.0_debian_4.15.0-66-generic'
args.runcmd="-itd --net=host"
args.internalcmd="ovsdb-server"
'''
with open("runopts") as myfile:
    args.runcmd=myfile.readlines()[0]
print(args)
#############################################################################
IMAGEID=exec_cmd("sudo docker images %s --format=\"{{.ID}}\"" % args.image)
DOCKER_CMD="sudo docker run %s --name=tempContainer %s %s" %(args.runcmd,IMAGEID,args.execute)
DOCKER_FILE=args.outputpath+"/Dockerfile"
if(len(IMAGEID.split())>1):
    sys.exit('(%d) Images found. Please provide a valid docker image name'%len(IMAGEID.split()))
IMAGEID=re.sub(r'[^\w\s]', '', IMAGEID)
os.system("mkdir -p %s"%args.outputpath)
os.system("mkdir -p %s"%args.outputpath+"/files")
os.system("bash DockerFileCreator.sh %s %s"%(IMAGEID,DOCKER_FILE))
##########################################
hashed_key = {}
with open(DOCKER_FILE) as myfile:
    lines=[line for line in myfile.readlines()]
for i,line in enumerate(lines):
    if re.search(r'file:', line):
        hashed_key[i]=line.strip().split()
##########################################
keys=list(hashed_key.keys())
keys.reverse()
for k in keys:
    print(k)
    curr_dir=os.getcwd()
    stmt=hashed_key[k]
    if(stmt[0]=="COPY"):
        target=stmt[3]
        dest=os.path.basename(target)
        try:
            filename=copy_to("tempContainer:"+target,curr_dir+"/"+args.outputpath+"/files/"+dest)
            if(filename):
                stmt[2]=args.outputpath+"/files/"+filename
                del stmt[1]
                lines[k]= " ".join(stmt)+"\n"
        except:
            pass
    elif(stmt[0]=="ADD"):
        pass
    else:
        pass
    os.chdir(curr_dir)
##########################################
with open(DOCKER_FILE+".tmp", 'w') as f:
    for line in lines:
        f.write(line)
