## MLflow Server Deployment Guide

### Step 1: Configure the Ansible Control Node

Please refer to the documentation below to ensure proper configuration of your Ansible control node:

🔗 [Ansible Control Node Configuration Guide](https://github.com/jahangir842/ansible/blob/main/README.md)

---

### Step 2: Configure Environment Variables

Copy the example environment file and rename it as `.env`:

```bash
cp ./docker_compose_installation/.env.example ./docker_compose_installation/.env
```

Edit the newly created `.env` file to update the necessary credentials and configuration values.

> **Note:** To avoid exposing sensitive information, ensure that the `.env` file is listed in your `.gitignore` and not committed to the Git repository.

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

---

Open a web browser and navigate to the MLflow server using the following URL:

```
http://192.168.18.50:5000/
```

Replace the IP address with the actual IP address of your MLflow server.

---

