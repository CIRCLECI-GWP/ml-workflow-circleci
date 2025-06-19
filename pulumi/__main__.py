import pulumi
import lbrlabs_pulumi_scaleway as scaleway
from lbrlabs_pulumi_scaleway import get_image

# 1️⃣ CONFIG
zone = "fr-par-1"

# 2️⃣ MAKE YOUR IP ADDRESSES
runner_ip = scaleway.InstanceIp("runnerPublicIp", zone=zone)
server_ip = scaleway.InstanceIp("serverPublicIp", zone=zone)

# 3️⃣ LOOK UP A JAMMY IMAGE (must be SBS-based!)
jammy = get_image(
    label="ubuntu_jammy",          # from `scw marketplace local-image list`
    arch="x86_64",                 # pick the ARCH you need
    marketplace_type="instance_sbs",  # SBS-backed images only
    zone=zone,
)

# 4️⃣ CREATE THE TRAINER (GPU)  
#    – make sure you have quota for GP1-XS; otherwise pick another GPU flavor
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
    user_data={"cloud-init": open("runner_cloud_init.yml").read()},
)

# 5️⃣ CREATE THE INFERENCE SERVER (CPU)
#    – pick DEV1-L (or any other you have quota for)
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
    user_data={"cloud-init": open("modelserver_cloud_init.yml").read()},
)

# 6️⃣ EXPORT THE RESULTS
pulumi.export("cci_runner_ip", modelTrainingCCIRunner.public_ip)
pulumi.export("cci_runner_id", modelTrainingCCIRunner.id)
pulumi.export("modelserver_ip", tensorflowServer.public_ip)
pulumi.export("modelserver_id", tensorflowServer.id)
