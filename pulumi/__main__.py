import pulumi
import lbrlabs_pulumi_scaleway as scaleway
from lbrlabs_pulumi_scaleway import get_marketplace_image

# ── config ──────────────────────────────────────────────────
cfg  = pulumi.Config()
zone = cfg.get("zone") or "fr-par-1"

# ── load cloud-init once ───────────────────────────────────
def load_ci(path):
    return {"cloud-init": open(path).read()}

runner_ci      = load_ci("runner_cloud_init.yml")
modelserver_ci = load_ci("modelserver_cloud_init.yml")

# ── public IPs ─────────────────────────────────────────────
runner_ip = scaleway.InstanceIp("runnerPublicIp",  zone=zone)
server_ip = scaleway.InstanceIp("serverPublicIp",  zone=zone)

# ── lookup an SBS Ubuntu Jammy image ───────────────────────
jammy = get_marketplace_image(
    label="ubuntu_jammy",
    type="instance_sbs",   # ← filter for SBS images
    zone=zone,
)

# ── GPU runner ─────────────────────────────────────────────
runner = scaleway.InstanceServer(
    "runnerServerLinux",
    zone=zone,
    type="GP1-XS",        # make sure you have quota
    image=jammy.id,       
    ip_id=runner_ip.id,
    routed_ip_enabled=True,
    root_volume=scaleway.InstanceServerRootVolumeArgs(
        size_in_gb=80, volume_type="b_ssd"
    ),
    user_data=runner_ci,
)

# ── CPU model server ────────────────────────────────────────
modelsvr = scaleway.InstanceServer(
    "tensorflowServerLinux",
    zone=zone,
    type="DEV1-L",        # pick a quota-available size
    image=jammy.id,
    ip_id=server_ip.id,
    routed_ip_enabled=True,
    root_volume=scaleway.InstanceServerRootVolumeArgs(
        size_in_gb=40, volume_type="b_ssd"
    ),
    user_data=modelserver_ci,
)

# ── exports ────────────────────────────────────────────────
pulumi.export("cci_runner_ip", runner.public_ip)
pulumi.export("cci_runner_id", runner.id)
pulumi.export("modelserver_ip", modelsvr.public_ip)
pulumi.export("modelserver_id", modelsvr.id)
