# import pulumi
# import pulumi_scaleway as scaleway
# from pulumi_scaleway import get_marketplace_image

import pulumi
import lbrlabs_pulumi_scaleway as scaleway
from lbrlabs_pulumi_scaleway import get_marketplace_image

zone = "fr-par-1"

# Allocate public IPs
runner_ip = scaleway.InstanceIp("runnerPublicIp", zone=zone)
server_ip = scaleway.InstanceIp("serverPublicIp", zone=zone)

# Look up the Ubuntu Jammy image from the marketplace
jammy = get_marketplace_image(
    label="ubuntu_jammy",
    zone=zone,
)

# GPU runner (make sure you have quota for GP1-XS)
modelTrainingCCIRunner = scaleway.InstanceServer(
    "runnerServerLinux",
    zone=zone,
    type="GP1-XS",
    image=jammy.id,
    ip_id=runner_ip.id,
    routed_ip_enabled=True,
    root_volume=scaleway.InstanceServerRootVolumeArgs(
        size_in_gb=80,
        volume_type="b_ssd",
    ),
    user_data={
        "cloud-init": open("runner_cloud_init.yml").read(),
    },
)

# CPU model server (DEV1-L has 4 vCPUs / 8 GiB)
tensorflowServer = scaleway.InstanceServer(
    "tensorflowServerLinux",
    zone=zone,
    type="DEV1-L",
    image=jammy.id,
    ip_id=server_ip.id,
    routed_ip_enabled=True,
    root_volume=scaleway.InstanceServerRootVolumeArgs(
        size_in_gb=40,
        volume_type="b_ssd",
    ),
       user_data={
        "cloud-init": open("modelserver_cloud_init.yml").read(),
    },
)

# Exports
pulumi.export("cci_runner_ip", modelTrainingCCIRunner.public_ip)
pulumi.export("cci_runner_id", modelTrainingCCIRunner.id)
pulumi.export("modelserver_id", tensorflowServer.id)
pulumi.export("modelserver_ip", tensorflowServer.public_ip)
