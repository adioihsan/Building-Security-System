import paramiko
from scp import SCPClient
import io

class FileServer():
    def __init__(self):
        self.server ="192.168.1.2"
        self.port = 22
        self.user ="FileServer"
        self.password = "yahboom"
        self.ssh = self.createSSHClient()
        self.scp = SCPClient(self.ssh.get_transport())

    def createSSHClient(self):
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.server, self.port, self.user, self.password)
        return client
    
    def uploadFile(self,file,path):
        self.scp.put(file,remote_path=path)
    
    def uploadBytes(self,buffer,path):
        self.scp.putfo(fl=buffer,remote_path=path)

    def downloadFile(self):
        self.scp.get()
    
    def downloadFile(self,path):
        temp_file = "storage/temp_file.jpg"
        self.scp.get(remote_path=path,local_path=temp_file)
        return temp_file
    
    def close_connection(self):
        self.scp.close()