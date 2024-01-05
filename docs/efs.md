# EFS with EKS Fargate Clusters

AWS got requirements from customers about data persistence and shared storage of containerized applications since launching EKS support for Fargate. EFS is built for on-demand petabyte growth without application interruption, and it automatically grows and shrinks as files are added and removed, eliminating the need to provision and manage capacity to accommodate growth. EFS Access Points is also ideal for security sensitive workloads as it can encrypt data in the file system and data in transit.

Now customers can also configure their pods running on Fargate to access an EFS file system using standard Kubernetes APIs. With this update, customers can run stateful workloads that require highly available file systems as well as workloads that require access to shared storage. **Using the EFS CSI driver, all data in transit is encrypted by default.**

## How it works

The Amazon EFS CSI driver makes it easy to configure elastic file storage for both EKS and self-managed Kubernetes clusters running on AWS using standard Kubernetes interfaces. If a Kubernetes pod is terminated and relaunched, the CSI driver reconnects the EFS file system, even if the pod is relaunched in a different AWS Availability Zone.

Usually standard EC2 worker nodes would require the EFS CSI driver to be deployed as a set of pods and Daemonsets (which are not supported with Fargate).

For Fargate **this step is not required and you do not need to install the EFS CSI driver**, as it is installed in the Fargate stack and support for EFS is provided out of the box. Customers can use EFS with Fargate for EKS without spending the time and resources to install and update the CSI driver.

## How to setup

1. StorageClass
2. PersistentVolume
3. PersistentVolumeClaim

Once an EFS file system is created, we will configure the mount settings using SC and PV. 

# EFS Performance Testing 

https://docs.gitlab.com/ee/administration/operations/filesystem_benchmarking.html
https://www.vipmind.me/infra/aws/how-to-enable-efs-support-in-fargate-for-eks.html
https://github.com/aws-samples/amazon-efs-tutorial/blob/master/performance/README.md