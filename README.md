# Test PV and PVC that uses GPFS NFS exported fileset

1- After creating the cluster if you get an error related to flannel , you can delete the cni0 interface and the flannel pod on both master and worker

 ip link delete cni0

 kubectl delete pod -n kube-flannel -l app=flannel

2- Create the GPFS PV

 kubectl apply -f pv.yml

3-Create the PVC

 kubectl apply -f pvc.yml

4-Create the test POD

 kubectl apply -f testpod.yml

6-Check the POD state

kubectl get pods

# Pull Errors

If you get some errors , that you reached the limit 

  Warning  Failed     26s                kubelet            Failed to pull image "busybox": reading manifest latest in docker.io/library/busybox: toomanyrequests: You have reached your pull rate limit. You may increase the limit by authenticating and upgrading: https://www.docker.com/increase-rate-limit

-Then you need to first create and account on docker hub :

https://hub.docker.com/
