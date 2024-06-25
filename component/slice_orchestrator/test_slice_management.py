import uuid
from slice_orchestrator import SliceOrchestrator
from csmf import CSMF
from nsmf import NSMF
from nssmf import NSSMF

def main():
    so = SliceOrchestrator()
    print("Slice Orchestrator initialized")

    csmf = CSMF("config/network_slice_templates/gst_template2.json")
    print("CSMF initialized")

    nsmf = NSMF()
    nssmf = NSSMF()
    print("NSMF and NSSMF initialized")

    so.set_components(csmf, nsmf, nssmf)
    print("Slice Orchestrator configured with all components")

    csmf.set_slice_orchestrator(so)
    print("CSMF configured with Slice Orchestrator")

    # Exemple de demande de service
    service_request = {
        "service_type": "eMBB",
        "latency": {"value": 10, "unit": "ms"},
        "throughput": {"value": 100, "unit": "Mbps"}
    }

    try:
        # Créer un service (slice)
        slice_id = csmf.process_communication_service_request(service_request)
        print(f"Service created with slice ID: {slice_id}")

        # Obtenir le statut du service
        status = csmf.get_communication_service_status(slice_id)
        print(f"Service status: {status}")

        modification = {"performance_req": {"latency": 5}}
        so.modify_slice(slice_id, modification)
        print(f"Service modified. New status: {so.get_slice_status(slice_id)}")
        
        # Mettre à jour le service
        update_request = {
            "latency": {"value": 5, "unit": "ms"}
        }
        csmf.update_communication_service(slice_id, update_request)
        print("Service updated")

        # Obtenir le nouveau statut
        status = csmf.get_communication_service_status(slice_id)
        print(f"Updated service status: {status}")

        # Terminer le service
        csmf.terminate_communication_service(slice_id)
        print("Service terminated")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
