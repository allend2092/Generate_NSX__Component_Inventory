#!/usr/bin/env python3
"""
NSX-T Inventory Auto-Generator (with unique file names)

Author: Daryl Allen
Email: daryl.allen.jr@gmail.com

"""

import json
import os
import re
import sys
from typing import Dict, List

import requests
from requests.auth import HTTPBasicAuth
import urllib3
from urllib.parse import urljoin

# ─── User settings ────────────────────────────────────────────────
NSX_MANAGER_IP = "172.17.0.200"
USERNAME       = "admin"
PASSWORD       = "VMware1!VMware1!"        # ← production: use env vars or secrets
VERIFY_TLS: bool | str = False        # CA bundle path, True, or False

if not VERIFY_TLS:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ─── Helper funcs ────────────────────────────────────────────────
def safe_label(raw: str) -> str:
    """Return string usable inside a filename (alnum → keep, else '_')."""
    return re.sub(r"[^A-Za-z0-9]", "_", raw)

def nsx_get(session: requests.Session, base: str, path: str) -> Dict:
    url = urljoin(base, path.lstrip("/"))
    r = session.get(url, timeout=10)
    r.raise_for_status()
    return r.json()

def collect_manager_inventory(s: requests.Session, base: str) -> List[Dict]:
    cluster = nsx_get(s, base, "/api/v1/cluster/status")
    out: List[Dict] = []

    for grp in cluster.get("detailed_cluster_status", {}).get("groups", []):
        if grp.get("group_type") != "DATASTORE":
            continue
        for m in grp.get("members", []):
            uuid = m["member_uuid"]
            node_status = nsx_get(s, base, f"/api/v1/cluster/nodes/{uuid}/status")
            out.append({
                "uuid": uuid,
                "ip":   m.get("member_ip"),
                "fqdn": m.get("member_fqdn"),
                "version": node_status.get("version")
            })

    out.sort(key=lambda x: x["fqdn"] or x["ip"])
    return out

def collect_transport_nodes(s: requests.Session, base: str) -> tuple[List[Dict], List[Dict]]:
    results = nsx_get(s, base, "/api/v1/transport-nodes").get("results", [])
    edges, hosts = [], []

    for n in results:
        uuid = n["id"]
        basic = {
            "uuid":         uuid,
            "display_name": n.get("display_name"),
            "ip":           n.get("node_deployment_info", {}).get("ip_addresses", ["N/A"])[0],
            "conn_status":  None,
            "software_version": None,
        }
        st = nsx_get(s, base, f"/api/v1/transport-nodes/{uuid}/status")
        basic["conn_status"]      = st.get("status")
        basic["software_version"] = st.get("node_status", {}).get("software_version")

        rtype = n.get("node_deployment_info", {}).get("resource_type")
        if rtype == "EdgeNode":
            basic["component_type"] = "EDGE"
            edges.append(basic)
        else:
            basic["component_type"] = "HOST_TN"
            hosts.append(basic)

    edges.sort(key=lambda x: x["display_name"])
    hosts.sort(key=lambda x: x["display_name"])
    return edges, hosts

def write_json(fname: str, obj: Dict) -> None:
    with open(fname, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2)
    print(f"[+] wrote {os.path.abspath(fname)}")

# ─── Main ────────────────────────────────────────────────────────
def main() -> None:
    base = f"https://{NSX_MANAGER_IP}"
    try:
        with requests.Session() as s:
            s.auth    = HTTPBasicAuth(USERNAME, PASSWORD)
            s.verify  = VERIFY_TLS
            s.headers.update({"Accept": "application/json"})

            # Managers (needed first so we know the label)
            mgr_list = collect_manager_inventory(s, base)
            mgr_label_source = mgr_list[0].get("fqdn") or NSX_MANAGER_IP
            label = safe_label(mgr_label_source)

            edge_list, host_list = collect_transport_nodes(s, base)

            edge_obj = {"NSX Edge Transport Node Inventory": edge_list}
            host_obj = {"NSX Host / Transport Node Inventory": host_list}
            mgr_obj  = {"NSX Manager Cluster Inventory": mgr_list}

            # Display to console
            print(json.dumps(edge_obj, indent=2))
            print(json.dumps(host_obj, indent=2))
            print(json.dumps(mgr_obj, indent=2))

            # Dynamic filenames
            edge_file = f"nsx_{label}_edge_inventory.json"
            host_file = f"nsx_{label}_host_tn_inventory.json"
            mgr_file  = f"nsx_{label}_manager_cluster_inventory.json"

            write_json(edge_file, edge_obj)
            write_json(host_file, host_obj)
            write_json(mgr_file,  mgr_obj)

    except requests.HTTPError as e:
        print(f"[ERR] HTTP {e.response.status_code}: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as e:
        print(f"[ERR] {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
