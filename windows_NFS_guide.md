Since your **NFS server is working fine**, here are the exact steps for a **Windows client** to mount the NFS share.  

---

### **🛠 Steps to Mount an NFS Share on Windows Client**

### **1️⃣ Enable NFS Client on Windows**
> **Note:** NFS support is only available on **Windows 10/11 Pro, Enterprise, and Windows Server** editions.

1. Open **PowerShell as Administrator**.
2. Run the following command to install the NFS client:

   ```powershell
   Install-WindowsFeature -Name NFS-Client
   ```

3. Restart your computer.

---

### **2️⃣ Mount the NFS Share (Temporary)**
To temporarily mount the NFS share (until reboot), open **Command Prompt as Administrator** and run:

```cmd
mount -o anon \\<NFS-SERVER-IP>\<NFS-SHARE> Z:
```

🔹 **Example:**  
If your NFS server is `192.168.1.100` and the shared directory is `/nfs/mlflow_artifacts`, run:

```cmd
mount -o anon \\192.168.1.147\nfs\mlflow_artifacts Z:
```

Now, you can access the share via `Z:\` in **File Explorer**.

---

### **3️⃣ Persistent Mount (After Reboot)**
To automatically mount the NFS share **after reboot**, use:

```cmd
net use Z: \\192.168.1.100\nfs\mlflow_artifacts /persistent:yes
```

---

### **4️⃣ Verify the Mount**
To check if the NFS share is mounted, run:

```cmd
net use
```

You should see something like:

```
Z:  \\192.168.1.100\nfs\mlflow_artifacts
```

---

### **5️⃣ Access the NFS Share**
- Open **File Explorer**.
- Navigate to `Z:\` to see the files.

✅ Now, your **Windows user can send MLflow logs** to the NFS-mounted directory.

Let me know if you need further help! 🚀
