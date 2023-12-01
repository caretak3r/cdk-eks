# Fargate

## Considerations

1. cert-manager 
2. fluent-bit
3. ALB 
4. Daemonsets
5. kube-proxy
6. secrets-operator
---

1. Using cert-manager with fargate will work, so long as the webhook port is not using 10250, since kubelet listens on this. Change it to 10260. 

2. [fluent-bit](https://aws.amazon.com/blogs/containers/fluent-bit-for-amazon-eks-on-aws-fargate-is-here/) is automatically supported on EKS (no maintaining charts or images), just configure the log router to send `stdout` or `stderr` to CloudWatch. Under the hood, EKS on Fargate uses a version of Fluent Bit for AWS, an upstream conformant distribution of Fluent Bit managed by AWS. This means there are no sidecars to install or maintain. You simply select where you want to send your data and logs are routed to a destination of your choice.

![Alt text](image.png)

3. EKS on Fargate with an ALB requires the use of Instance IP to map rules to pods. We cannot use Instance because Fargate is a serverless construct with no nodes, hence we rely on the IP of the pod. 

4. EKS on Fargate does not support using daemonsets. 

5. EKS on Fargate does not require kube-proxy to operate.

6. EKS on Fargate support for external-secrets operator [here](https://aws.amazon.com/blogs/containers/leverage-aws-secrets-stores-from-eks-fargate-with-external-secrets-operator/)

![Alt text](image-3.png)