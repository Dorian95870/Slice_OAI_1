import math
import tkinter as tk
import json
import logging
from tkinter import ttk, messagebox
from slice_orchestrator2 import SliceOrchestrator
from csmf2 import CSMF
from nsmf import NSMF
from nssmf import CoreNSSMF
from nfvo import NFVO

logging.basicConfig(level=logging.DEBUG, filename='slice_management.log', filemode='w',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class SliceManagementUI:
    def __init__(self, master):
        self.master = master
        master.title("Slice Management UI")

        # Initialiser les composants
        self.so = SliceOrchestrator()
        self.csmf = CSMF("config/network_slice_templates/gst_template2.json")
        self.nsmf = NSMF()
        self.nssmf = CoreNSSMF()
        self.nfvo = NFVO()
        
        self.so.set_components(self.csmf, self.nsmf, self.nssmf)
        self.csmf.set_slice_orchestrator(self.so)

        self.service_type = tk.StringVar()
        self.service_type.set(CSMF.valid_slice_types[0])  # Valeur par défaut

        # Créer les widgets
        self.create_widgets()

    def create_widgets(self):
        # Frame pour la création de slice
        create_frame = ttk.LabelFrame(self.master, text="Create Slice")
        create_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Slice Type
        ttk.Label(create_frame, text="Slice Type:").grid(row=0, column=0, sticky="w")
        self.slice_type = tk.StringVar()
        slice_type_combo = ttk.Combobox(create_frame, textvariable=self.slice_type)
        slice_type_combo['values'] = ["eMBB", "URLLC", "mMTC"]
        slice_type_combo.grid(row=0, column=1)

        # Slice Differentiator
        ttk.Label(create_frame, text="Slice Differentiator:").grid(row=1, column=0, sticky="w")
        self.slice_differentiator = tk.StringVar()
        ttk.Entry(create_frame, textvariable=self.slice_differentiator).grid(row=1, column=1)

        # QoS Parameters
        ttk.Label(create_frame, text="Latency (ms):").grid(row=2, column=0, sticky="w")
        self.latency = tk.IntVar()
        ttk.Entry(create_frame, textvariable=self.latency).grid(row=2, column=1)

        ttk.Label(create_frame, text="Throughput (Mbps):").grid(row=3, column=0, sticky="w")
        self.throughput = tk.IntVar()
        ttk.Entry(create_frame, textvariable=self.throughput).grid(row=3, column=1)

        ttk.Label(create_frame, text="Reliability (%):").grid(row=4, column=0, sticky="w")
        self.reliability = tk.DoubleVar()
        ttk.Entry(create_frame, textvariable=self.reliability).grid(row=4, column=1)

        # Resource Requirements
        ttk.Label(create_frame, text="CPU (vCPUs):").grid(row=5, column=0, sticky="w")
        self.cpu = tk.IntVar()
        ttk.Entry(create_frame, textvariable=self.cpu).grid(row=5, column=1)

        ttk.Label(create_frame, text="Memory (MB):").grid(row=6, column=0, sticky="w")
        self.memory = tk.IntVar()
        ttk.Entry(create_frame, textvariable=self.memory).grid(row=6, column=1)

        ttk.Label(create_frame, text="Storage (GB):").grid(row=7, column=0, sticky="w")
        self.storage = tk.IntVar()
        ttk.Entry(create_frame, textvariable=self.storage).grid(row=7, column=1)

        ttk.Label(create_frame, text="Bandwidth (Mbps):").grid(row=8, column=0, sticky="w")
        self.bandwidth = tk.IntVar()
        ttk.Entry(create_frame, textvariable=self.bandwidth).grid(row=8, column=1)

        ttk.Button(create_frame, text="Create Slice", command=self.create_slice).grid(row=9, column=0, columnspan=2, pady=10)

        # Frame pour la gestion de slice
        manage_frame = ttk.LabelFrame(self.master, text="Manage Slice")
        manage_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        ttk.Label(manage_frame, text="Slice ID:").grid(row=0, column=0, sticky="w")
        self.slice_id = ttk.Entry(manage_frame)
        self.slice_id.grid(row=0, column=1)

        ttk.Button(manage_frame, text="Get Status", command=self.get_status).grid(row=1, column=0)
        ttk.Button(manage_frame, text="Modify Slice", command=self.modify_slice).grid(row=1, column=1)
        ttk.Button(manage_frame, text="Delete Slice", command=self.delete_slice).grid(row=2, column=0, columnspan=2)
        ttk.Button(manage_frame, text="List Slices", command=self.list_network_slices).grid(row=3, column=1, columnspan=2)

        # Frame pour les résultats
        self.result_frame = ttk.LabelFrame(self.master, text="Results")
        self.result_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.result_text = tk.Text(self.result_frame, height=10, width=50)
        self.result_text.pack(expand=True, fill="both")

    def validate_slice_parameters(self):
        slice_type = self.slice_type.get()
        if slice_type == "URLLC":
            if self.latency.get() > 1 or self.reliability.get() < 99.999:
                raise ValueError("URLLC requires latency <= 1ms and reliability >= 99.999%")
        elif slice_type == "eMBB":
            if self.throughput.get() < 100:
                raise ValueError("eMBB requires throughput >= 100 Mbps")

    def check_resource_availability(self):
        available_cpu = 10  
        available_memory = 1000  
        if self.cpu.get() > available_cpu or self.memory.get() > available_memory:
            raise ValueError("Requested resources exceed available resources")

    def create_slice(self):
        try:
            logging.debug("Starting slice creation with parameters:")
            logging.debug(f"Slice Type: {self.slice_type.get()}")
            logging.debug(f"Slice Differentiator: {self.slice_differentiator.get()}")
            logging.debug(f"Latency: {self.latency.get()} ms")
            logging.debug(f"Throughput: {self.throughput.get()} Mbps")
            logging.debug(f"Reliability: {self.reliability.get()}%")
            logging.debug(f"CPU: {self.cpu.get()} vCPUs")
            logging.debug(f"Memory: {self.memory.get()} MB")
            logging.debug(f"Storage: {self.storage.get()} GB")
            logging.debug(f"Bandwidth: {self.bandwidth.get()} Mbps")

            self.validate_slice_parameters()
            self.check_resource_availability()

            service_request = {
                "slice_type": self.slice_type.get(),
                "slice_differentiator": self.slice_differentiator.get() or None,
                "qos": {
                    "latency": {"value": self.latency.get(), "unit": "ms"},
                    "throughput": {"value": self.throughput.get(), "unit": "Mbps"},
                    "reliability": {"value": self.reliability.get(), "unit": "%"}
                },
                "resources": {
                    "cpu": {"value": self.cpu.get(), "unit": "vCPUs"},
                    "memory": {"value": self.memory.get(), "unit": "MB"},
                    "storage": {"value": self.storage.get(), "unit": "GB"},
                    "bandwidth": {"value": self.bandwidth.get(), "unit": "Mbps"}
                }
            }

            logging.debug(f"Service request: {json.dumps(service_request, indent=2)}")

            slice_id = self.csmf.process_communication_service_request(service_request)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Created slice with ID: {slice_id}\n")

            # Obtenir la configuration VCN
            vcn_config = self.nsmf.generate_nsi_config(slice_id, service_request)
            self.result_text.insert(tk.END, "\nVCN Configuration:\n")
            self.result_text.insert(tk.END, json.dumps(vcn_config, indent=2))
            
            # Appel à NFVO pour instancier les VNFs
            vnf_instances = self.nfvo.instantiate_vnfs(service_request)
            self.result_text.insert(tk.END, "\n\nInstantiated VNFs:\n")
            self.result_text.insert(tk.END, json.dumps(vnf_instances, indent=2))

        except ValueError as ve:
            logging.error(f"Validation error: {str(ve)}")
            messagebox.showerror("Configuration Error", str(ve))
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def get_status(self):
        try:
            slice_id = self.slice_id.get()
            if not slice_id:
                raise ValueError("Please enter a slice ID")
            
            logging.debug(f"Getting status for slice ID: {slice_id}")
            status = self.so.get_slice_status(slice_id)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Status of slice {slice_id}:\n")
            self.result_text.insert(tk.END, json.dumps(status, indent=2))
            
            # Obtenir le statut des VNFs via NFVO
            vnf_status = self.nfvo.get_vnf_status(slice_id)
            self.result_text.insert(tk.END, "\n\nVNF Status:\n")
            self.result_text.insert(tk.END, json.dumps(vnf_status, indent=2))
        except Exception as e:
            logging.error(f"Error getting slice status: {str(e)}", exc_info=True)
            messagebox.showerror("Error", str(e))

    def modify_slice(self):
        try:
            slice_id = self.slice_id.get()
            if not slice_id:
                raise ValueError("Please enter a slice ID")
            
            logging.debug(f"Modifying slice ID: {slice_id}")
            modifications = {
                "qos": {
                    "latency": {"value": self.latency.get(), "unit": "ms"},
                    "throughput": {"value": self.throughput.get(), "unit": "Mbps"}
                }
            }
            
            result = self.so.modify_slice(slice_id, modifications)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Modified slice {slice_id}:\n")
            self.result_text.insert(tk.END, json.dumps(result, indent=2))
            
            # Modifier les VNFs via NFVO si nécessaire
            vnf_modifications = self.nfvo.modify_vnfs(slice_id, modifications)
            self.result_text.insert(tk.END, "\n\nVNF Modifications:\n")
            self.result_text.insert(tk.END, json.dumps(vnf_modifications, indent=2))
        except Exception as e:
            logging.error(f"Error modifying slice: {str(e)}", exc_info=True)
            messagebox.showerror("Error", str(e))

    def delete_slice(self):
        try:
            slice_id = self.slice_id.get()
            if not slice_id:
                raise ValueError("Please enter a slice ID")
            
            logging.debug(f"Deleting slice ID: {slice_id}")
            result = self.so.delete_slice(slice_id)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Deleted slice {slice_id}:\n")
            self.result_text.insert(tk.END, json.dumps(result, indent=2))
            
            # Supprimer les VNFs associées via NFVO
            vnf_deletion = self.nfvo.terminate_vnfs(slice_id)
            self.result_text.insert(tk.END, "\n\nVNF Termination:\n")
            self.result_text.insert(tk.END, json.dumps(vnf_deletion, indent=2))
        except Exception as e:
            logging.error(f"Error deleting slice: {str(e)}", exc_info=True)
            messagebox.showerror("Error", str(e))

    def list_network_slices(self):
        try:
            logging.debug("Listing network slices")
            slices = self.so.list_slices()
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "Network Slices:\n")
            self.result_text.insert(tk.END, json.dumps(slices, indent=2))
            
        # Lister les VNFs via NFVO
            vnfs = self.nfvo.list_vnfs()
            self.result_text.insert(tk.END, "\n\nVNF Instances:\n")
            self.result_text.insert(tk.END, json.dumps(vnfs, indent=2))
        except Exception as e:
            logging.error(f"Error listing network slices: {str(e)}", exc_info=True)
            messagebox.showerror("Error", str(e))

def main():
    root = tk.Tk()
    SliceManagementUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()