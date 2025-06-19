import pulumi
import lbrlabs_pulumi_scaleway as scaleway
from lbrlabs_pulumi_scaleway import get_marketplace_image

# import lbrlabs_pulumi_scaleway
# from  lbrlabs_pulumi_scaleway import get_image as scaleway
# from lbrlabs_pulumi_scaleway import get_image as scaleway_get_image


# runnerPublicIp = scaleway.InstanceIp("runnerPublicIp")
# serverPublicIp = scaleway.InstanceIp("serverPublicIp")

runner_ip = scaleway.InstanceIp("runnerPublicIp")
server_ip = scaleway.InstanceIp("serverPublicIp")

zone = "fr-par-1"

# jammy = get_marketplace_image(
#     image_label="ubuntu_jammy",
#     arch="x86_64",
#     type="instance_local",
#     zone=zone,
#     latest=True,
# )

jammy = get_marketplace_image(
    label="ubuntu_jammy",       # the LABEL from `scw marketplace local-image list`
    arch="x86_64",              # match the ARCH column
    type="instance_local",      # match the TYPE column
    zone=zone,
)


modelTrainingCCIRunner = scaleway.InstanceServer(
    "runnerServerLinux",
    zone=zone,
    type="GPU-3070-S",  # Change to a type you have quota for
    image=jammy.id,  # Standard Ubuntu 24.04 x86_64 image
    ip_id=runner_ip.id,
    routed_ip_enabled=True,
    root_volume=scaleway.InstanceServerRootVolumeArgs(
        size_in_gb=80,
        volume_type="b_ssd",
    ),
    user_data={
        "cloud-init": open("runner_cloud_init.yml").read(),
    }
)

tensorflowServer = scaleway.InstanceServer(
    "tensorflowServerLinux",
    zone=zone,
    type="PRO2-M",  # or any CPU type you have quota for
    image=jammy.id,  # Ubuntu 24.04 x86_64
    ip_id=server_ip.id,
    routed_ip_enabled=True,
    root_volume=scaleway.InstanceServerRootVolumeArgs(
        size_in_gb=40,
        volume_type="b_ssd",
    ),
    user_data={
        "cloud-init": open("modelserver_cloud_init.yml").read(),
    }
)


# Export the name and IP address of the new server
pulumi.export("cci_runner_ip", modelTrainingCCIRunner.public_ip)
pulumi.export("cci_runner_id", modelTrainingCCIRunner.id)
pulumi.export("modelserver_id", tensorflowServer.id)
pulumi.export("modelserver_ip", tensorflowServer.public_ip)