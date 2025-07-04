import pulumi
from pulumiverse_scaleway.instance import Server, Ip
import os

config = pulumi.Config()

runner_token = config.require("circleciRunnerToken")
zone = "fr-par-1"

# Reserve public IPs
runner_ip = Ip("runnerPublicIp", zone=zone)
server_ip = Ip("serverPublicIp", zone=zone)

# Read and inject the runner token into the cloud-init script
with open("runner_cloud_init_base.yml") as f:
    cloud_init_runner = f.read().replace("RUNNER_TOKEN", runner_token)
cloud_init_runner = f"""#cloud-config
{cloud_init_runner}
"""

with open("modelserver_cloud_init.yml") as f:
    cloud_init_modelserver = f.read()

with open(os.path.expanduser("~/.ssh/id_rsa_modelserver.pub")) as f:
    public_key = f.read().strip()

cloud_init_modelserver = f"""#cloud-config
users:
  - name: demo
    shell: /bin/bash
    sudo: ALL=(ALL) NOPASSWD:ALL
    groups: docker
    home: /home/demo
    create_groups: true
    ssh-authorized-keys:
      - {public_key}

package_update: true
package_upgrade: true

runcmd:
  - apt-get update -y
  - apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
  - curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
  - echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list
  - apt-get update -y
  - apt-get install -y docker-ce docker-ce-cli containerd.io
  - systemctl enable docker
  - systemctl start docker
  - usermod -aG docker demo
  - mkdir -p /var/models/staging
  - mkdir -p /var/models/prod
  - chown -R demo:docker /var/models
  - chmod -R 775 /var/models
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
