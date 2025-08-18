const express = require(express);
const axios = require("axios");
const crypto = require("crypto");
const router = express.Router();

const APP_ID = process.env.YOUR_APP_ID;
const SECRET_KEY = process.env.YOUR_SECRET_KEY;
const BAIDU_API_URL = "https://fanyi-api.baidu.com/api/trans/vip/translate";
const PORT=3000;
const supportedLanguages = [
  "auto",
  "zh",
  "en",
  "yue",
  "wyw",
  "jp",
  "kor",
  "fra",
  "spa",
  "th",
  "ara",
  "ru",
  "pt",
  "de",
  "it",
  "el",
  "nl",
  "pl",
  "bul",
  "est",
  "dan",
  "fin",
  "cs",
  "rom",
  "slo",
  "swe",
  "hu",
  "cht",
  "vie",
];

router.post("/", async (req, res) => {
  const { text, from = "auto", to } = req.body;
  if (!text) {
    return res.status(400).json({ error: "Text is required" });
  }
  if (!to || !supportedLanguages.includes(to)) {
    return res
      .status(400)
      .json({
        error: "Invalid or missing target language",
        supportedLanguages,
      });
  }

  const salt = Date.now();
  const sign = crypto
    .createHash("md5")
    .update(APP_ID + text + salt + SECRET_KEY)
    .digest("hex");
  try {
    const response = await axios.get(BAIDU_API_URL, {
      params: {
        q: text,
        from,
        to,
        appid: APP_ID,
        salt,
        sign,
      },
    });
    res.json(response.data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports=router;
