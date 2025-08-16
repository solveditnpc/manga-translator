require("dotenv").config();
const express = require("express");
const axios = require("axios");
const router = express.Router();


const APP_KEY = process.env.XIAONIU_APP_KEY;
const ENDPOINT = "http://api.niutrans.com/NiuTransServer/translation";

// Full supported languages from Niutrans (Xiaoniu)
const SUPPORTED_LANGS = [
  "auto","zh","en","yue","wyw","jp","kor","fra","spa","ara","bg","et","cs","dan",
  "fin","ro","sl","sw","hu","cht","nl","el","it","de","tr","ru","pl","th","pt",
  "vi","id","ms","hi","bn","fa","sr","uk","he","mn","ne","si","km","lo","my",
  "am","az","ka","pa","te","ta","mr","gu","kn","ml","ur"
];

// ---------------- Translation API ----------------
router.post("/", async (req, res) => {
  const { text, source, target } = req.body;

  if (!text) {
    return res.status(400).json({ error: "Text is required" });
  }
  if (!target || !SUPPORTED_LANGS.includes(target.toLowerCase())) {
    return res.status(400).json({
      error: "Invalid or missing target language",
      supported: SUPPORTED_LANGS,
    });
  }

  try {
    const response = await axios.post(
      ENDPOINT,
      null,
      {
        params: {
          from: source || "auto",
          to: target,
          apikey: APP_KEY,
          src_text: text,
        },
      }
    );

    res.json({
      from: source || "auto",
      to: target,
      original: text,
      translated: response.data?.tgt_text || "",
    });
  } catch (e) {
    res.status(500).json({ error: e.response?.data || e.message });
  }
});



module.exports=router;

