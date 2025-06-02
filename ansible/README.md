### MLflow Server Installation

## configure ansible 

https://github.com/jahangir842/ansible

---

### Enable SSH Password Authentication (Manual Method)

1. **Open the SSH daemon configuration file** using a text editor:

   ```bash
   sudo nano /etc/ssh/sshd_config
   ```

2. **Locate the following directive**:

   ```bash
   #PasswordAuthentication no
   ```

3. **Uncomment and modify it as follows** to enable password authentication:

   ```bash
   PasswordAuthentication yes
   ```

4. **Save and close the file** (`Ctrl + O`, `Enter`, then `Ctrl + X` in `nano`).

5. **Restart the SSH service** to apply the configuration changes:

   ```bash
   sudo systemctl restart ssh
   ```

> 🔐 **Important**: Enabling password authentication can increase security risks, especially on public-facing servers. Ensure strong passwords and consider additional security measures (e.g., fail2ban, firewalls).

---

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
