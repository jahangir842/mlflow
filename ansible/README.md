# **MLflow Server Deployment Guide**

## **On the Ansible Managed Node**

### **Step 1: Server Preparation**

Ensure your Ansible control node is properly set up before proceeding. Refer to the following guide for detailed configuration instructions:

🔗 [Ansible Control Node Configuration Guide](https://github.com/jahangir842/ansible/blob/main/README.md)

---

## **From the Ansible Control Node**

### **Step 1: Deploy the MLflow Server**

1. Verify that your `inventory.yml` file contains the correct host details for your managed node(s).

2. Run the following Ansible playbooks sequentially:

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

## Clone the Mlflow Server

```bash
ansible-playbook -i inventory.yml ./playbooks/clone_mlflow.yml
```


### Set Up Environment Variables

Create a copy of the example environment file and rename it:

```bash
cp ./docker_compose_installation/.env.example ./docker_compose_installation/.env
```

Edit the `.env` file to input your environment-specific credentials and configurations.

> ⚠️ **Important:** Never commit sensitive information to version control. Ensure `.env` is listed in `.gitignore`.



## Run the Mlflow Server

```bash
ansible-playbook -i inventory.yml ./playbooks/run_mlflow.yml
```

---

### **Accessing MLflow**

Once deployment is complete, open your browser and visit the MLflow server:

```
http://<your-server-ip>:5000/
```

Replace `<your-server-ip>` with the actual IP address of the server (e.g., `192.168.18.50`).

---
