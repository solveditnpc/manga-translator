import express from "express";
import axios from "axios";
import fs from "fs";
const router = express.Router();

// Load config.json
const config = JSON.parse(fs.readFileSync("./config.json", "utf8"));

// Environment token
const CAIYUN_TOKEN = process.env.CAIYUN_TOKEN;

if (!CAIYUN_TOKEN) {
    console.error("Missing Caiyun API Token. Please set CAIYUN_TOKEN in your environment.");
    process.exit(1);
}



// Supported languages by Caiyun
const SUPPORTED_LANGUAGES = {
    "zh": "Chinese",
    "en": "English",
    "ja": "Japanese"
};

/**
 * POST /translate
 * Body: { text: "你好世界", from: "zh", to: "en" }
 */
router.post("/", async (req, res) => {
    const { text, from = config.from_lan || "auto", to = config.to_lan || "en" } = req.body;

    if (!text) {
        return res.status(400).json({ error: "Text is required." });
    }

    if (!SUPPORTED_LANGUAGES[to]) {
        return res.status(400).json({
            error: `Unsupported target language: ${to}. Supported: ${Object.keys(SUPPORTED_LANGUAGES).join(", ")}`
        });
    }

    try {
        const response = await axios.post(
            "https://api.interpreter.caiyunai.com/v1/translator",
            {
                source: text,
                trans_type: `${from}2${to}`, // auto2en, zh2ja, etc.
                request_id: "manga-translator",
                detect: true
            },
            {
                headers: {
                    "Content-Type": "application/json",
                    "x-authorization": `token ${CAIYUN_TOKEN}`
                }
            }
        );

        return res.json({
            text,
            from,
            to,
            translated: response.data.target
        });
    } catch (error) {
        console.error("Caiyun API Error:", error.response?.data || error.message);
        return res.status(500).json({
            error: "Translation failed",
            details: error.response?.data || error.message
        });
    }
});

module.exports=router;
