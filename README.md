# Create Dockerfile from images
## Help options
`python3 DockerFileCreator.py --help`
## Example scenario
Say a docker image name `openvswitch/ovs` with tag `2.12.0_debian_4.15.0-66-generic` requires the following command to execute
```
docker run -itd --net=host --name=ovsdb-server openvswitch/ovs: 2.11.2_debian ovsdb-server
```
First add `-itd --net=host` in `dockerRunOpts` and then use the following command to generate the Dockerfile and relevant files inside a folder `ovs`

```
python3 DockerFileCreator.py -i openvswitch/ovs:2.12.0_debian_4.15.0-66-generic -e ovsdb-server -o ovs
```
