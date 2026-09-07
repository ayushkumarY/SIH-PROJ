const express = require("express");
const cors = require("cors");
const axios = require("axios");

const app = express();

const PORT = 5000;
const ML_ENGINE_URL = "http://127.0.0.1:8000";

app.use(cors());
app.use(express.json());


// ==========================================
// HEALTH CHECK
// ==========================================

app.get("/api/health", (req, res) => {
    res.json({
        status: "success",
        message: "Node.js backend is running"
    });
});


// ==========================================
// ML ENGINE HEALTH CHECK
// ==========================================

app.get("/api/ml-health", async (req, res) => {

    try {

        const response = await axios.get(
            `${ML_ENGINE_URL}/`
        );

        res.json({
            status: "success",
            ml_engine: response.data
        });

    } catch (error) {

        res.status(500).json({
            status: "error",
            message: "Python ML engine is not available",
            error: error.message
        });

    }

});


// ==========================================
// RUN UNIFIED ANALYSIS
// ==========================================

app.get("/api/analyze", async (req, res) => {

    try {

        console.log(
            "Starting CV TrustGuard analysis..."
        );

        const response = await axios.get(
            `${ML_ENGINE_URL}/analyze`
        );

        res.json({
            status: "success",
            data: response.data
        });

    } catch (error) {

        console.error(
            "ML Engine Error:",
            error.message
        );

        res.status(500).json({

            status: "error",

            message:
                "Failed to communicate with Python ML engine",

            error:
                error.message

        });

    }

});


// ==========================================
// START SERVER
// ==========================================

app.listen(PORT, () => {

    console.log(
        `CV TrustGuard backend running on port ${PORT}`
    );

});