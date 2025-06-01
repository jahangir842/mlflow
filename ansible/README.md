### MLflow Server Installation

## configure ansible 

https://github.com/jahangir842/ansible

### 🔓 Configure Passwordless `sudo` (Optional)

To avoid password prompts entirely, configure passwordless `sudo` for your user:

```bash
sudo visudo
```

Then add the following line (replace `jahangir` with your actual username):

```bash
userid ALL=(ALL) NOPASSWD:ALL
```

> ⚠️ Use with caution; this has security implications in multi-user or production environments.

---


To install the MLflow server, execute the following Ansible playbooks in the specified order:

```bash
ansible-playbook -i inventory.yml network_setup.yml
ansible-playbook -i inventory.yml packages.yml
ansible-playbook -i inventory.yml firewall.yml
ansible-playbook -i inventory.yml nfs_setup.yml
ansible-playbook -i inventory.yml mlflow.yml
```

Each playbook performs a specific role in the setup process, ensuring a consistent and reliable MLflow deployment environment.
