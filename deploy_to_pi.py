import paramiko
import os
import zipfile
from scp import SCPClient

def zip_project(zip_name):
    print(f"Zipping project to {zip_name}...")
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('.'):
            if 'node_modules' in dirs: dirs.remove('node_modules')
            if '.git' in dirs: dirs.remove('.git')
            if 'dist' in dirs: dirs.remove('dist')
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, '.')
                if arcname == zip_name or arcname == 'deploy_to_pi.py' or arcname.endswith('.py'):
                    if arcname not in ['docker-compose.pi.yml', 'Dockerfile']:
                        continue
                zipf.write(file_path, arcname)

def deploy():
    host = os.getenv("PI_HOST", "192.168.1.15")
    user = os.getenv("PI_USER", "sdpi")
    password = os.getenv("PI_PASSWORD", "199611cm")
    remote_path = "/home/sdpi/brewblox-ui"
    zip_name = "project.zip"

    zip_project(zip_name)

    print(f"Connecting to {host}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, username=user, password=password)

        # Clean and prepare
        ssh.exec_command(f"rm -rf {remote_path} && mkdir -p {remote_path}")

        print("Uploading project...")
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(zip_name, f"{remote_path}/{zip_name}")

        print("Extracting and building via Docker direct (NO BUILDKIT)...")
        # Disable BuildKit to avoid phantom file errors
        cmd_chain = (
            f"cd {remote_path} && "
            f"unzip -q {zip_name} && "
            f"DOCKER_BUILDKIT=0 docker build --no-cache -t brewblox-ui-pi:latest . && "
            f"docker compose -f docker-compose.pi.yml up -d"
        )

        print(f"Executing: {cmd_chain}")
        stdin, stdout, stderr = ssh.exec_command(cmd_chain)

        # Stream output
        while True:
            line = stdout.readline()
            if not line: break
            print(line, end='')

        err = stderr.read().decode()
        if err: print(f"Error/Stderr: {err}")

        print("Deployment finished!")
        print(f"URL: http://{host}:8085")

    finally:
        ssh.close()
        if os.path.exists(zip_name): os.remove(zip_name)

if __name__ == "__main__":
    deploy()
