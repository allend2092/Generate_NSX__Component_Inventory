# NSX Inventory Auto-Generator

Collects upgrade-relevant inventory data from a VMware NSX-T environment and writes it to three clearly separated JSON files:

* NSX **Edge Transport Nodes**
* NSX **Host Transport Nodes**
* NSX **Manager Cluster** members

---

## ✨ Key features

* **One-shot discovery** – log in once, gather Managers, Edges, and Hosts.
* **Upgrade-centric fields** – UUID, display name, IP, connection status, running NSX version.
* **Clean separation** – each component type is its own JSON object.
* **Collision-proof filenames** – output filenames include the Manager’s FQDN (or IP), so running the script against multiple environments never overwrites previous data.
* **Human-friendly console output** – see the inventory immediately, then find the same data on disk.

---

## 🗂 Output example

    nsx_nsx-t-manager1_edge_inventory.json
    nsx_nsx-t-manager1_host_tn_inventory.json
    nsx_nsx-t-manager1_manager_cluster_inventory.json

Example contents of the Edge file:

    {
      "NSX Edge Transport Node Inventory": [
        {
          "uuid": "43cc5bf9-754a-4da9-bcdd-797a89027f7f",
          "display_name": "lab_edge_node",
          "ip": "172.17.0.50",
          "conn_status": "UP",
          "software_version": "4.1.1.0.0.22224325",
          "component_type": "EDGE"
        }
      ]
    }

---

## 🔧 Requirements

* Python 3.9 or newer  
* `requests` Python package

Optional:

* A CA bundle that trusts your NSX Manager certificate  
  – or –  
  set `VERIFY_TLS = False` in the script (fine for a lab, insecure for production).

---

## 🚀 Quick start

1. Clone or download the repository  

       git clone https://github.com/your-org/nsx-inventory-auto-generator.git
       cd nsx-inventory-auto-generator

2. (Optional) create a virtual environment  

       python -m venv .venv
       # Linux/macOS
       source .venv/bin/activate
       # Windows
       .venv\Scripts\activate

3. Install the only dependency  

       pip install requests

4. Edit *generate_nsx_inventory_items.py* and set:  

       NSX_MANAGER_IP = "your.manager.ip.or.fqdn"
       USERNAME       = "admin"
       PASSWORD       = "yourPassword"
       VERIFY_TLS     = False   # or path to CA bundle

5. Run the script  

       python generate_nsx_inventory_items.py

6. Check the console output and the three JSON files created in the current directory.

> **Tip:**  
> Point the script at a second NSX Manager by changing `NSX_MANAGER_IP`, `USERNAME`, and `PASSWORD`.  
> The new JSON files will include the second Manager’s FQDN/IP in the filename, so nothing is overwritten.

---

## ⚙️ Script internals (high level)

| Function                              | Purpose                                                           |
|---------------------------------------|-------------------------------------------------------------------|
| `safe_label()`                        | Sanitises FQDN/IP for safe use in filenames.                      |
| `nsx_get()`                           | Thin wrapper around `requests.get` with error handling.           |
| `collect_manager_inventory()`         | Queries `/api/v1/cluster/status` and per-manager status endpoints |
| `collect_transport_nodes()`           | Queries `/api/v1/transport-nodes` and per-node status endpoints   |
| `write_json()`                        | Dumps JSON to disk with pretty indentation                        |
| `main()`                              | Orchestrator: log in, gather data, print, write files             |

Feel free to modify field selection, add upgrade-eligibility checks, or integrate the JSON into an existing dashboard.

# NSX Inventory Auto-Generator

Collects upgrade-relevant inventory data from a VMware NSX-T environment and writes it to three clearly separated JSON files:

* NSX **Edge Transport Nodes**
* NSX **Host Transport Nodes**
* NSX **Manager Cluster** members

---

## ✨ Key features

* **One-shot discovery** – log in once, gather Managers, Edges, and Hosts.
* **Upgrade-centric fields** – UUID, display name, IP, connection status, running NSX version.
* **Clean separation** – each component type is its own JSON object.
* **Collision-proof filenames** – output filenames include the Manager’s FQDN (or IP), so running the script against multiple environments never overwrites previous data.
* **Human-friendly console output** – see the inventory immediately, then find the same data on disk.

---

## 🗂 Output example

    nsx_nsx-t-manager1_edge_inventory.json
    nsx_nsx-t-manager1_host_tn_inventory.json
    nsx_nsx-t-manager1_manager_cluster_inventory.json

Example contents of the Edge file:

    {
      "NSX Edge Transport Node Inventory": [
        {
          "uuid": "43cc5bf9-754a-4da9-bcdd-797a89027f7f",
          "display_name": "lab_edge_node",
          "ip": "172.17.0.50",
          "conn_status": "UP",
          "software_version": "4.1.1.0.0.22224325",
          "component_type": "EDGE"
        }
      ]
    }

---

## 🔧 Requirements

* Python 3.9 or newer  
* `requests` Python package

Optional:

* A CA bundle that trusts your NSX Manager certificate  
  – or –  
  set `VERIFY_TLS = False` in the script (fine for a lab, insecure for production).

---

## 🚀 Quick start

1. Clone or download the repository  

       git clone https://github.com/your-org/nsx-inventory-auto-generator.git
       cd nsx-inventory-auto-generator

2. (Optional) create a virtual environment  

       python -m venv .venv
       # Linux/macOS
       source .venv/bin/activate
       # Windows
       .venv\Scripts\activate

3. Install the only dependency  

       pip install requests

4. Edit *generate_nsx_inventory_items.py* and set:  

       NSX_MANAGER_IP = "your.manager.ip.or.fqdn"
       USERNAME       = "admin"
       PASSWORD       = "yourPassword"
       VERIFY_TLS     = False   # or path to CA bundle

5. Run the script  

       python generate_nsx_inventory_items.py

6. Check the console output and the three JSON files created in the current directory.

> **Tip:**  
> Point the script at a second NSX Manager by changing `NSX_MANAGER_IP`, `USERNAME`, and `PASSWORD`.  
> The new JSON files will include the second Manager’s FQDN/IP in the filename, so nothing is overwritten.

---

## ⚙️ Script internals (high level)

| Function                              | Purpose                                                           |
|---------------------------------------|-------------------------------------------------------------------|
| `safe_label()`                        | Sanitises FQDN/IP for safe use in filenames.                      |
| `nsx_get()`                           | Thin wrapper around `requests.get` with error handling.           |
| `collect_manager_inventory()`         | Queries `/api/v1/cluster/status` and per-manager status endpoints |
| `collect_transport_nodes()`           | Queries `/api/v1/transport-nodes` and per-node status endpoints   |
| `write_json()`                        | Dumps JSON to disk with pretty indentation                        |
| `main()`                              | Orchestrator: log in, gather data, print, write files             |

Feel free to modify field selection, add upgrade-eligibility checks, or integrate the JSON into an existing dashboard.

---

## 📝 License

MIT – see `LICENSE` for full text.

