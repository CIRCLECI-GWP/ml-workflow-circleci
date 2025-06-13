import pulumi
import lbrlabs_pulumi_scaleway as scaleway

runnerPublicIp = scaleway.InstanceIp("runnerPublicIp")
serverPublicIp = scaleway.InstanceIp("serverPublicIp")

modelTrainingCCIRunner = scaleway.InstanceServer("runnerServerLinuxGPU",
    type="GPU-3070-S",
    image="ubuntu_jammy_gpu_os_12",
    ip_id=runnerPublicIp.id,
    root_volume=scaleway.InstanceServerRootVolumeArgs(
        size_in_gb=80,
        volume_type="b_ssd",
    ),
    user_data={
        "cloud-init": (lambda path: open(path).read())(f"runner_cloud_init.yml"),
    }
)

tensorflowServer = scaleway.InstanceServer("tensorflowServerLinux",
    type="PRO2-M",
    image="ubuntu_jammy",
    ip_id=serverPublicIp.id,
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