import pulumi
import pulumiverse_scaleway.iam as scaleway_iam
from pulumiverse_scaleway.instance import Server, Ip

config = pulumi.Config()

runner_token = config.require("circleciRunnerToken")
ssh_pub_key = config.require("sshPublicKey")

zone = "fr-par-1"

# Reserve public IPs
runner_ip = Ip("runnerPublicIp", zone=zone)
server_ip = Ip("serverPublicIp", zone=zone)

# Read and inject the runner token into the cloud-init script
with open("runner_cloud_init_base.yml") as f:
    cloud_init_runner = f.read().replace("RUNNER_TOKEN", runner_token)
cloud_init_runner = f"""#cloud-config
ssh_authorized_keys:
  - {ssh_pub_key}
{cloud_init_runner}
"""

with open("modelserver_cloud_init.yml") as f:
    cloud_init_modelserver = f.read()

cloud_init_modelserver = f"""#cloud-config
users:
  - name: demo
    shell: /bin/bash
    sudo: ALL=(ALL) NOPASSWD:ALL
    ssh-authorized-keys:
      - {ssh_pub_key}
runcmd:
  - mkdir -p /home/demo/.ssh
  - echo '{ssh_pub_key}' > /home/demo/.ssh/authorized_keys
  - chown -R demo:demo /home/demo/.ssh
  - chmod 700 /home/demo/.ssh
  - chmod 600 /home/demo/.ssh/authorized_keys
  - echo "=== AUTHORIZED_KEYS FOR DEMO ==="
  - cat /home/demo/.ssh/authorized_keys
  - echo "=== END AUTHORIZED_KEYS ==="
{cloud_init_modelserver}
"""

# GPU runner
modelTrainingCCIRunner = Server(
    "runnerServerLinux",
    zone=zone,
    type="GP1-XS",
    image="ubuntu_jammy",
    ip_id=runner_ip.id,
    root_volume={
        "size_in_gb": 80,
        "volume_type": "sbs_volume",
    },
    cloud_init=cloud_init_runner,
)

# CPU model server
tensorflowServer = Server(
    "tensorflowServerLinux",
    zone=zone,
    type="DEV1-L",
    image="ubuntu_jammy",
    ip_id=server_ip.id,
    root_volume={
        "size_in_gb": 40,
        "volume_type": "sbs_volume",
    },
    cloud_init=cloud_init_modelserver,
)

# Export outputs
pulumi.export("cci_runner_ip", modelTrainingCCIRunner.public_ips)
pulumi.export("cci_runner_id", modelTrainingCCIRunner.id)
pulumi.export("modelserver_id", tensorflowServer.id)
pulumi.export("modelserver_ip", server_ip.address)
