import pulumi
import lbrlabs_pulumi_scaleway as scaleway

runnerPublicIp = scaleway.InstanceIp("runnerPublicIp")
serverPublicIp = scaleway.InstanceIp("serverPublicIp")

modelTrainingCCIRunner = scaleway.InstanceServer("runnerServerLinuxGPU",
    type="DEV1-S",
    image="ubuntu_jammy_gpu_os_12",
    ip_id=runnerPublicIp.id,
    routed_ip_enabled=True,
    root_volume=scaleway.InstanceServerRootVolumeArgs(
        size_in_gb=125,
        volume_type="b_ssd",
    ),
    user_data={
        "cloud-init": open("runner_cloud_init.yml").read(),
    }
)

tensorflowServer = scaleway.InstanceServer("tensorflowServerLinux",
    type="DEV1-S",
    image="ubuntu_jammy_sbs",
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