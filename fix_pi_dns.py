import paramiko

def fix_dns():
    host = "192.168.1.15"
    user = "sdpi"
    password = "199611cm"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, username=user, password=password)

        # Add Google DNS to /etc/resolv.conf
        # Note: This might be temporary if controlled by dhcpcd, but good for a test
        commands = [
            "echo 'nameserver 8.8.8.8' | sudo tee /etc/resolv.conf",
            "docker pull alpine:latest" # Test pull
        ]

        for cmd in commands:
            print(f"Executing: {cmd}")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            print(stdout.read().decode())
            print(stderr.read().decode())

    finally:
        ssh.close()

if __name__ == "__main__":
    fix_dns()
