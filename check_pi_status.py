import paramiko

def check_status():
    host = "192.168.1.15"
    user = "sdpi"
    password = "199611cm"
    remote_path = "/home/sdpi/brewblox-ui"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, username=user, password=password)

        commands = [
            f"cd {remote_path} && docker compose -f docker-compose.pi.yml ps",
            f"cd {remote_path} && docker compose -f docker-compose.pi.yml logs --tail 20"
        ]

        for cmd in commands:
            print(f"\n--- Output of: {cmd} ---")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            print(stdout.read().decode())
            err = stderr.read().decode()
            if err:
                print(f"Error: {err}")

    finally:
        ssh.close()

if __name__ == "__main__":
    check_status()
