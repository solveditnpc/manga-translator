require("dotenv").config();
const express = require("express");
const axios = require("axios");

const router = express.Router();


const DEEPL_KEY = process.env.DEEPL_KEY;
const ENDPOINT = "https://api-free.deepl.com/v2/translate";

// DeepL supported target languages (ISO codes)
const DEEPL_LANGUAGES = [
  "BG","CS","DA","DE","EL","EN-GB","EN-US","EN","ES",
  "ET","FI","FR","HU","ID","IT","JA","KO","LT","LV",
  "NB","NL","PL","PT-BR","PT-PT","PT","RO","RU","SK",
  "SL","SV","TR","UK","ZH"
];

// Translate endpoint
router.post("/", async (req, res) => {
  const { text, target_lang, source_lang } = req.body;

  if (!text) {
    return res.status(400).json({ error: "Text is required" });
  }

  if (!DEEPL_LANGUAGES.includes(target_lang)) {
    return res.status(400).json({
      error: "Invalid or missing target language",
      supported: DEEPL_LANGUAGES
    });
  }

  try {
    const response = await axios.post(
      ENDPOINT,
      new URLSearchParams({
        auth_key: DEEPL_KEY,
        text,
        target_lang,
        ...(source_lang ? { source_lang } : {}) // optional
      })
    );

    res.json(response.data);
  } catch (e) {
    res.status(500).json({ error: e.response?.data || e.message });
  }
});

module.exports=router;
