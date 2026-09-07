import axios from "axios";

const API = axios.create({
    baseURL: "http://127.0.0.1:8000",
});

export const getSystemStatus = async () => {
    const response = await API.get("/system-status");
    return response.data;
};

export const getAnalysis = async () => {
    const response = await API.get("/analyze");
    return response.data;
};

export const getProvenanceStatus = async () => {
    const response = await API.get("/provenance-status");
    return response.data;
};

export const getAuditStatus = async () => {
    const response = await API.get("/audit-status");
    return response.data;
};

export const submitAnalystAction = async (
    finding,
    action,
    analyst = "Security Analyst"
) => {

    const response = await API.post(
        "/analyst-action",
        {
            finding,
            action,
            analyst,
        }
    );

    return response.data;
};

export default API;