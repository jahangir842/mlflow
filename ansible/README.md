## MLflow Server Deployment Guide

#### Step 1: Configure the Ansible Client Node

Refer to the following documentation to configure your Ansible client node properly:

🔗 [Configure the Ansible Client Node](https://github.com/jahangir842/ansible/blob/main/README.md)

---

#### Step 2: Install MLflow Server (From Control Node)

To deploy the MLflow server, first ensure your `inventory.yml` is correctly configured with the appropriate host details.

Then, execute the following Ansible playbooks in the order listed below:

```bash
ansible-playbook -i inventory.yml ./playbooks/network_setup.yml

```

```bash
ansible-playbook -i inventory.yml ./playbooks/packages.yml
```

```bash
ansible-playbook -i inventory.yml ./playbooks/firewall.yml
```

```bash
ansible-playbook -i inventory.yml ./playbooks/nfs_setup.yml
```

```bash
ansible-playbook -i inventory.yml ./playbooks/mlflow.yml
```

Each playbook addresses a specific aspect of the deployment process—ranging from network configuration to package installation, firewall rules, NFS setup, and finally the MLflow server deployment. This structured approach ensures a consistent, automated, and reliable MLflow environment.
