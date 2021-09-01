---
title: Using the AWS Marketplace Ingress Controller Image
description: 
weight: 2300
doctypes: [""]
toc: true
---

This document will walk you through the steps needed to use the NGINX Ingress Controller through the AWS Marketplace. There are additional steps that must be followed in order for the AWS Marketplace NGINX Ingress Controller to work properly.

> **IMPORTANT**: This document uses EKS version 1.19. EKS versions < 1.19 require additional security settings within the NGINX Pod to work properly with marketplace images. 
> This document discusses using eksctl to perform necessary steps to enable the Kubernetes cluster access to deploy NGINX Ingress Controller from the Marketplace. Please make sure you are running a newer version of eksctl and AWS cli.

> **NOTE**: NGINX Ingress controller from the Marketplace does NOT work in AWS Region US-West-1.

## Instructions
Instructions for using AWS Marketplace:

1. Ensure you have a working AWS EKS cluster. If you do not have a EKS cluster, you can create one using either the AWS console, or using the AWS tool eksctl. See [this guide](https://docs.aws.amazon.com/EKS/latest/userguide/getting-started-eksctl.html) for details on getting started with EKS using eksctl.

2. You must create a new IAM service account that will be used with NGINX Ingress Controller as the ServiceAccount. This IAM service account will have a specific IAM policy that allows you to monitor the usage of the AWS NGINX Ingress Controller image. This is a required step. If it is omitted, AWS Marketplace NGINX ingress controller will not work properly and NGINX Ingress will not start.

3. You must apply the service account to your ServiceAccount in your EKS cluster. When you do so, your “ServiceAccount” Kubernetes object will have a annotation, showing the link to the IAM service account. For example:

```
apiVersion: v1
kind: ServiceAccount
metadata:
  annotations:
    EKS.amazonaws.com/role-arn: arn:aws:iam::001234567890:role/eksctl-json-us-west2-addon-iamserviceaccount-Role1-IJJ6CF9Y8IPY
  labels:
    app.kubernetes.io/managed-by: eksctl
  name: nginx-ingress
  namespace: nginx-ingress
secrets:
- name: nginx-ingress-token-zm728
```

In the above example, the “ServiceAccount” was created using eksctl. The name of the account is ngix-ingress. When you create this ServiceAccount, EKS will automatically assign the annotation to your ServiceAccount, with the valid IAM policy required.

> **NB** You must associate your AWS EKS cluster with an OIDC provider before you can create your IAM Service account! This is required.

## Step by step instructions using eksctl utility.

This assumes you have an existing EKS cluster up and running. If not, please create one before proceeding.

1. Associate your EKS cluster with a “OIDC IAM provider” (replace --cluster <name> and --region <region> with the values of your environment).
```
eksctl utils associate-iam-oidc-provider --region=eu-west-1 --cluster=json-eu-east1 --approve
```

2.  Now create your IAM service account for your cluster. Substitute --name --namespace and --region with your values.
```
eksctl create iamserviceaccount --name nginx-ingress --namespace nginx-ingress --cluster json-test01 --region us-east-2 --attach-policy-arn arn:aws:iam::aws:policy/AWSMarketplaceMeteringRegisterUsage --approve
 ```

This will automatically create the service account for you with the required annotations needed for your AWS cluster. Since eksctl is creating it for you, you do not need to apply any other .yaml files for your NGINX Ingress controller deployments.

Make sure you match the name you are creating for the service account, to the account that will be in the `rbac.yaml` file for manifest deployment.
If using helm, make sure it matches `controller.serviceAccount.name`

Sample output from the `rbac.yaml` file, matching the IAM service account that was created above:

```
kind: ClusterRoleBinding
  apiVersion: rbac.authorization.k8s.io/v1
  metadata:
    name: nginx-ingress
  subjects:
  - kind: ServiceAccount
    name: nginx-ingress
    namespace: nginx-ingress
  roleRef:
    kind: ClusterRole
    name: nginx-ingress
    apiGroup: rbac.authorization.k8s.io
```
Small snippet from helm values.yaml file:

```
    serviceAccount:
      name: nginx-ingress
```
For example, if you create the service account name to awskic01, change the rbac.yaml file to reflect the change:

```
kind: ClusterRoleBinding
  apiVersion: rbac.authorization.k8s.io/v1
  metadata:
    name: aws-kic-image
  subjects:
  - kind: ServiceAccount
    name: awskic01
    namespace: nginx-ingress
  roleRef:
    kind: ClusterRole
    name: awskic01
    apiGroup: rbac.authorization.k8s.io
```

3. Log into the AWS ECR registry that is specified in the instructions from the AWS Marketplace portal. 

**Note:** AWS Labs also provides a credential helper - see [their GitHub repo](https://github.com/awslabs/amazon-ecr-credential-helper) for instructions on how to setup and configure. 

4. Update the image in the `nginx-plus-ingress.yaml` manifest, or for Helm, update the `controller.image.repository` (and `controller.image.tag` if required).

