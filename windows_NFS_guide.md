## **🛠 Steps to Mount an NFS Share on Windows Client**


### **Step 1: Enable NFS Client on Windows 10**

1. **Open Control Panel**:
   - Press **Windows + R**, type `control`, and hit Enter.

2. **Go to "Programs"**:
   - Click **"Programs"** and then **"Turn Windows features on or off"** under the Programs and Features section.

3. **Enable NFS Client**:
   - In the "Windows Features" window, scroll down and find **"Services for NFS"**.
   - Expand it and check **"Client for NFS"**.
   - Click **OK** to apply the changes.
   - Windows will install the required files. It might ask you to restart your computer.

---

### **Step 2: Map the NFS Share in File Explorer**

1. **Open File Explorer**:
   - Press **Windows + E** or click on the File Explorer icon from the taskbar.

2. **Go to "This PC"**:
   - In the left sidebar, click **"This PC"**.

3. **Right-click on "This PC"**:
   - Select **"Map Network Drive..."** from the context menu.

4. **Map the NFS Share**:
   - In the "Map Network Drive" window, do the following:
     - Select a **Drive letter** from the drop-down list.
     - In the **Folder** field, type the NFS server path. This will be in the format:

       ```
       \\<MLFLOW_SERVER_IP>\<NFS_SHARE_PATH>
       ```

       For example:

       ```
       \\192.168.1.147\opt\mlflow
       ```

5. **Reconnect at sign-in**:
   - If you want to reconnect to this drive automatically every time you log in, check the box **"Reconnect at sign-in"**.

6. **Finish**:
   - Click **Finish**. Windows will attempt to connect to the NFS share.
   - If everything is set up correctly, the share will be mounted, and you can access it from **This PC**.

---

### **Alternative: Using Command Line (PowerShell)**

If you prefer using PowerShell, follow these steps:

1. **Open PowerShell as Administrator**:
   - Press **Windows + X** and select **"Windows PowerShell (Admin)"**.

2. **Mount the NFS Share**:
   Use the `New-PSDrive` cmdlet to map the NFS share as follows:

   ```powershell
   New-PSDrive -Name "N" -PSProvider FileSystem -Root "\\<MLFLOW_SERVER_IP>\<NFS_SHARE_PATH>" -Persist
   ```

   Example:

   ```powershell
   New-PSDrive -Name "N" -PSProvider FileSystem -Root "\\192.168.1.100\mnt\mlflow" -Persist
   ```

3. **Access the NFS Share**:
   - Once the drive is mounted, it will appear under **This PC** as a network drive.

---

### **Troubleshooting**
- **Ensure NFS Server is Active**: The NFS server on the Linux machine should be properly configured and running.
- **Firewall Rules**: Ensure that the firewall on both the client (Windows) and server (Linux) allows NFS traffic.

