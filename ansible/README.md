ansible-playbook -i inventory.yml network_setup.yml
ansible-playbook -i inventory.yml packages.yml
ansible-playbook -i inventory.yml firewall.yml
ansible-playbook -i inventory.yml nfs_setup.yml
ansible-playbook -i inventory.yml mlflow.yml
