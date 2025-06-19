import pulumi
import lbrlabs_pulumi_scaleway as scaleway
from lbrlabs_pulumi_scaleway import get_marketplace_image

zone = "fr-par-1"

runner_ip = scaleway.InstanceIp("runnerPublicIp", zone=zone)
server_ip = scaleway.InstanceIp("serverPublicIp", zone=zone)

jammy = get_marketplace_image(
    label="ubuntu_jammy",
    image_type="instance_sbs",
    zone=zone,
)


# Pick the Ubuntu Jammy local-image ID you saw
# JAMMY_ID = "e17b585e-c52f-44b0-97f6-07c18bb5bb86"

modelTrainingCCIRunner = scaleway.InstanceServer(
    "runnerServerLinux",
    zone=zone,
    type="GP1-XS",  # Change to a type you have quota for
    image=jammy.id,  # Standard Ubuntu 24.04 x86_64 image
    ip_id=runner_ip.id,
    routed_ip_enabled=True,
    root_volume=scaleway.InstanceServerRootVolumeArgs(
        size_in_gb=80,
        volume_type="b_ssd",
    ),
    user_data={
         "cloud-init": (lambda path: open(path).read())(f"runner_cloud_init.yml"),
    }
)

tensorflowServer = scaleway.InstanceServer(
    "tensorflowServerLinux",
    zone=zone,
    type="DEV1-L",  # or any CPU type you have quota for
    image=jammy.id,  # Ubuntu 24.04 x86_64
    ip_id=server_ip.id,
    routed_ip_enabled=True,
    root_volume=scaleway.InstanceServerRootVolumeArgs(
        size_in_gb=40,
        volume_type="b_ssd",
    ),
    user_data={
         "cloud-init": (lambda path: open(path).read())(f"modelserver_cloud_init.yml")
    }
)


# Export the name and IP address of the new server
pulumi.export("cci_runner_ip", modelTrainingCCIRunner.public_ip)
pulumi.export("cci_runner_id", modelTrainingCCIRunner.id)
pulumi.export("modelserver_id", tensorflowServer.id)
pulumi.export("modelserver_ip", tensorflowServer.public_ip)