import pulumi
import pulumiverse_scaleway as scaleway
from pulumiverse_scaleway.instance import Server, Ip, get_image

zone = "fr-par-1"

# Reserve two public IPs
runner_ip = Ip("runnerPublicIp", zone=zone)
server_ip = Ip("serverPublicIp", zone=zone)

# SBS-backed Ubuntu Jammy image (looked up manually)
# JAMMY_SBS_ID = "e17b585e-c52f-44b0-97f6-07c18bb5bb86"
# jammy = get_image(label="ubuntu_jammy", zone=zone, volume_type="b_ssd")

# GPU runner
modelTrainingCCIRunner = Server(
    "runnerServerLinux",
    zone=zone,
    type="GP1-XS",
    image="ubuntu_jammy",
    ip_id=runner_ip.id,
    root_volume={
        "size_in_gb": 80,
        "volume_type":"sbs_volume",
    },
    cloud_init=open("runner_cloud_init.yml").read(),
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
    cloud_init=open("modelserver_cloud_init.yml").read(),
)

# Export outputs
pulumi.export("cci_runner_ip", modelTrainingCCIRunner.public_ips)
pulumi.export("cci_runner_id", modelTrainingCCIRunner.id)
pulumi.export("modelserver_id", tensorflowServer.id)
pulumi.export("modelserver_ip", tensorflowServer.public_ips)
