const express = require("express");
const tencentcloud = require("tencentcloud-sdk-nodejs");

const router = express.Router();


const SECRET_ID = "YOUR_TENCENT_SECRET_ID";
const SECRET_KEY = "YOUR_TENCENT_SECRET_KEY";
const REGION = "ap-guangzhou";

// Init Tencent TMT client
const TmtClient = tencentcloud.tmt.v20180321.Client;
const clientConfig = {
  credential: {
    secretId: SECRET_ID,
    secretKey: SECRET_KEY,
  },
  region: REGION,
  profile: {
    httpProfile: {
      endpoint: "tmt.tencentcloudapi.com",
    },
  },
};
const client = new TmtClient(clientConfig);

// --- API route ---
router.post("/", async (req, res) => {
  const { text, target, source = "auto" } = req.body;

  if (!text || !target) {
    return res.status(400).json({ error: "Missing text or target language" });
  }

  try {
    const params = {
      SourceText: text,
      Source: source,
      Target: target,
      ProjectId: 0,
    };

    const response = await client.TextTranslate(params);
    res.json({
      original: text,
      translated: response.TargetText,
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports=router;
