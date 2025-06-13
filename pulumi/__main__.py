import pulumi
import lbrlabs_pulumi_scaleway as scaleway

runnerPublicIp = scaleway.InstanceIp("runnerPublicIp")
serverPublicIp = scaleway.InstanceIp("serverPublicIp")

modelTrainingCCIRunner = scaleway.InstanceServer(
    "runnerServerLinuxGPU",
    zone="fr-par-2",
    type="GPU-3070-S",
    image="15210e89-33e4-48ba-a438-33daa4a7594c",
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
    type="GPU-3070-S",
    image="15210e89-33e4-48ba-a438-33daa4a7594c",
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