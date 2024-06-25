import React, { useState } from 'react';
import axios from 'axios';

const SlicingForm = () => {
    const [formData, setFormData] = useState({
        SliceProfile: {
            sST: "",
            sliceProfileId: "",
            plmnIdList: [{ mcc: "", mnc: "" }],
            snssai: { sst: "", sd: "" },
            sliceProfileName: "",
            description: "",
            maxNumberofUEs: "",
            coverageAreaTAList: [""],
            latency: { latencyTime: "", latencyUnit: "ms" },
            ulThptPerUE: { value: "", unit: "Mbps" },
            dlThptPerUE: { value: "", unit: "Mbps" },
            availability: "",
            reliability: "",
            packetDelayBudget: "",
            maxNumberofConns: "",
            resources: {
                cpu: { value: "", unit: "vCPUs" },
                memory: { value: "", unit: "GB" },
                storage: { value: "", unit: "TB" }
            }
        },
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        const keys = name.split('.');
        setFormData(prevState => {
            const newState = { ...prevState };
            let currentLevel = newState;
            for (let i = 0; i < keys.length - 1; i++) {
                currentLevel = currentLevel[keys[i]];
            }
            currentLevel[keys[keys.length - 1]] = value;
            return newState;
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('/api/slice', formData);
            console.log('Slice created successfully:', response.data);
        } catch (error) {
            console.error('Error creating slice:', error);
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <div className="form-section">
                <h2>Slice Profile</h2>
                <label>
                    SST:
                    <input type="text" name="SliceProfile.sST" value={formData.SliceProfile.sST} onChange={handleChange} />
                </label>
                <label>
                    Slice Profile ID:
                    <input type="text" name="SliceProfile.sliceProfileId" value={formData.SliceProfile.sliceProfileId} onChange={handleChange} />
                </label>
                <label>
                    MCC:
                    <input type="text" name="SliceProfile.plmnIdList.0.mcc" value={formData.SliceProfile.plmnIdList[0].mcc} onChange={handleChange} />
                </label>
                <label>
                    MNC:
                    <input type="text" name="SliceProfile.plmnIdList.0.mnc" value={formData.SliceProfile.plmnIdList[0].mnc} onChange={handleChange} />
                </label>
                <label>
                    SNSSAI SST:
                    <input type="text" name="SliceProfile.snssai.sst" value={formData.SliceProfile.snssai.sst} onChange={handleChange} />
                </label>
                <label>
                    SNSSAI SD:
                    <input type="text" name="SliceProfile.snssai.sd" value={formData.SliceProfile.snssai.sd} onChange={handleChange} />
                </label>
                <label>
                    Slice Profile Name:
                    <input type="text" name="SliceProfile.sliceProfileName" value={formData.SliceProfile.sliceProfileName} onChange={handleChange} />
                </label>
                <label>
                    Description:
                    <input type="text" name="SliceProfile.description" value={formData.SliceProfile.description} onChange={handleChange} />
                </label>
                <label>
                    Max Number of UEs:
                    <input type="number" name="SliceProfile.maxNumberofUEs" value={formData.SliceProfile.maxNumberofUEs} onChange={handleChange} />
                </label>
                <label>
                    Coverage Area TA List:
                    <input type="text" name="SliceProfile.coverageAreaTAList.0" value={formData.SliceProfile.coverageAreaTAList[0]} onChange={handleChange} />
                </label>
                <label>
                    Latency Time:
                    <input type="number" name="SliceProfile.latency.latencyTime" value={formData.SliceProfile.latency.latencyTime} onChange={handleChange} />
                </label>
                <label>
                    UL Throughput per UE:
                    <input type="number" name="SliceProfile.ulThptPerUE.value" value={formData.SliceProfile.ulThptPerUE.value} onChange={handleChange} />
                </label>
                <label>
                    DL Throughput per UE:
                    <input type="number" name="SliceProfile.dlThptPerUE.value" value={formData.SliceProfile.dlThptPerUE.value} onChange={handleChange} />
                </label>
                <label>
                    Availability:
                    <input type="number" name="SliceProfile.availability" value={formData.SliceProfile.availability} onChange={handleChange} />
                </label>
                <label>
                    Reliability:
                    <input type="number" name="SliceProfile.reliability" value={formData.SliceProfile.reliability} onChange={handleChange} />
                </label>
                <label>
                    Packet Delay Budget:
                    <input type="number" name="SliceProfile.packetDelayBudget" value={formData.SliceProfile.packetDelayBudget} onChange={handleChange} />
                </label>
                <label>
                    Max Number of Connections:
                    <input type="number" name="SliceProfile.maxNumberofConns" value={formData.SliceProfile.maxNumberofConns} onChange={handleChange} />
                </label>
            </div>    
            <div className="form-section">
                <h3>Resources</h3>
                <label>
                    CPU:
                    <input type="number" name="SliceProfile.resources.cpu.value" value={formData.SliceProfile.resources.cpu.value} onChange={handleChange} />
                </label>
                <label>
                    Memory:
                    <input type="number" name="SliceProfile.resources.memory.value" value={formData.SliceProfile.resources.memory.value} onChange={handleChange} />
                </label>
                <label>
                    Storage:
                    <input type="number" name="SliceProfile.resources.storage.value" value={formData.SliceProfile.resources.storage.value} onChange={handleChange} />
                </label>
            </div>
            <button type="submit">Create Slice</button>
        </form>
    );
};

export default SlicingForm;


