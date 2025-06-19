import pulumi
import lbrlabs_pulumi_scaleway as scaleway

zone = "fr-par-1"

# Reserve two public IPs
runner_ip = scaleway.InstanceIp("runnerPublicIp", zone=zone)
server_ip = scaleway.InstanceIp("serverPublicIp", zone=zone)

# SBS-backed Ubuntu Jammy image (looked up manually)
JAMMY_SBS_ID = "e17b585e-c52f-44b0-97f6-07c18bb5bb86"

# GPU runner
modelTrainingCCIRunner = scaleway.InstanceServer(
    "runnerServerLinux",
    zone=zone,
    type="GP1-XS",
    image=JAMMY_SBS_ID,
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

# CPU model server
tensorflowServer = scaleway.InstanceServer(
    "tensorflowServerLinux",
    zone=zone,
    type="DEV1-L",
    image=JAMMY_SBS_ID,
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

# Export outputs
pulumi.export("cci_runner_ip", modelTrainingCCIRunner.public_ip)
pulumi.export("cci_runner_id", modelTrainingCCIRunner.id)
pulumi.export("modelserver_id", tensorflowServer.id)
pulumi.export("modelserver_ip", tensorflowServer.public_ip)
