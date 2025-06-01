### MLflow Server Installation

To install the MLflow server, execute the following Ansible playbooks in the specified order:

```bash
ansible-playbook -i inventory.yml network_setup.yml
ansible-playbook -i inventory.yml packages.yml
ansible-playbook -i inventory.yml firewall.yml
ansible-playbook -i inventory.yml nfs_setup.yml
ansible-playbook -i inventory.yml mlflow.yml
```

Each playbook performs a specific role in the setup process, ensuring a consistent and reliable MLflow deployment environment.
