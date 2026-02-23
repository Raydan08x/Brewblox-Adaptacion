import paramiko
import os
import zipfile
from scp import SCPClient

def zip_project(zip_name):
    print(f"Zipping project to {zip_name}...")
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Include dist, Dockerfile, docker-compose.pi.yml
        paths_to_include = ['dist', 'Dockerfile', 'docker-compose.pi.yml']
        for path in paths_to_include:
            if os.path.isfile(path):
                zipf.write(path, path)
            elif os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, file_path)

def deploy():
    host = os.getenv("PI_HOST", "192.168.1.15")
    user = os.getenv("PI_USER", "sdpi")
    password = os.getenv("PI_PASSWORD", "199611cm")
    remote_path = "/home/sdpi/brewblox-ui"
    zip_name = "project_prod.zip"

    if not os.path.exists('dist'):
        print("Error: 'dist' folder not found. Build locally first if possible, or ensure it exists.")
        # return # Commented out to allow attempting with whatever is there

    zip_project(zip_name)

    print(f"Connecting to {host}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, username=user, password=password)

        ssh.exec_command(f"rm -rf {remote_path} && mkdir -p {remote_path}")

        print("Uploading production bundle...")
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(zip_name, f"{remote_path}/{zip_name}")

        print("Extracting and running...")
        cmd_chain = (
            f"cd {remote_path} && "
            f"unzip -q {zip_name} && "
            f"docker compose -f docker-compose.pi.yml up --build -d"
        )

        print(f"Executing: {cmd_chain}")
        stdin, stdout, stderr = ssh.exec_command(cmd_chain)
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err: print(f"Error/Stderr: {err}")

        print("Deployment finished!")
        print(f"URL: http://{host}:8085")

    finally:
        ssh.close()
        if os.path.exists(zip_name): os.remove(zip_name)

if __name__ == "__main__":
    deploy()
