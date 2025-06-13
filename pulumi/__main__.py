import pulumi
import lbrlabs_pulumi_scaleway as scaleway

runnerPublicIp = scaleway.InstanceIp("runnerPublicIp")
serverPublicIp = scaleway.InstanceIp("serverPublicIp")

modelTrainingCCIRunner = scaleway.InstanceServer(
    "runnerServerLinux",
    zone="fr-par-2",
    type="DEV1-S",  # Change to a type you have quota for
    image="34e2e0d1-899e-40a7-9f08-a75ab3c59fb8",  # Standard Ubuntu 24.04 x86_64 image
    ip_id=runnerPublicIp.id,
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
    zone="fr-par-2",
    type="DEV1-S",  # or any CPU type you have quota for
    image="34e2e0d1-899e-40a7-9f08-a75ab3c59fb8",  # Ubuntu 24.04 x86_64
    ip_id=serverPublicIp.id,
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