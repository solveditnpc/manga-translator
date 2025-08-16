require('dotenv').config();
const express = require('express');
const axios = require('axios');
const router = express.Router();


const APP_ID = process.env.YOUDAO_APP_ID;
const APP_KEY = process.env.YOUDAO_APP_KEY;
const ENDPOINT = 'https://openapi.youdao.com/api';

if (!APP_ID || !APP_KEY) {
  console.error("Missing Youdao credentials! Set YOUDAO_APP_ID and YOUDAO_APP_KEY.");
  process.exit(1);
}

const SUPPORTED_LANGS = [
 "auto","zh-CHS","zh-CHT","en","ja","ko","fr","es","pt","ru","vi","de","ar","id","it",
  "ms","th","tr","bn","fa","hi","km","lo","my","ne","si","sr","uk","he","el","sv","da",
  "fi","no","pl","ro","hu","cs","sk","bg","hr","lt","lv","et","sl","ca","af","sw","ga",
  "mt","mi","cy","is","mk","sq","az","eu","be","gl","ka","tt","ug","ur","ps","ku","ky",
  "tg","mn","hy","te","mr","gu","ta","kn","ml","pa","am","so","yo","zu","xh","st","sn",
  "rw","ny","ha","ig","lb","gd","sm","to","fj","ht","qu","la","sa","bo","dv","yi"];

/**
 * POST /translate/youdao
 * Body: { text: "Hello", from: "auto", to: "zh-CHS" }
 */
router.post('/', async (req, res) => {
  const { text, from = 'auto', to = 'en' } = req.body;

  if (!text) {
    return res.status(400).json({ error: "Text is required." });
  }

  if (!SUPPORTED_LANGS.includes(to)) {
    return res.status(400).json({ 
      error: "Unsupported target language.", 
      supported: SUPPORTED_LANGS 
    });
  }

  try {
    const params = {
      q: text,
      from,
      to,
      appKey: APP_ID,
      salt: Date.now().toString(),
    };
    const sign = require('crypto')
      .createHash('md5')
      .update(params.appKey + params.q + params.salt + APP_KEY)
      .digest('hex');
    params.sign = sign;

    const response = await axios.get(ENDPOINT, { params });
    if (response.data.errorCode && response.data.errorCode !== '0') {
      throw new Error(`Youdao error: ${response.data.errorCode}`);
    }

    return res.json({
      text,
      from,
      to,
      translated: response.data.translation?.[0] || ""
    });
  } catch (err) {
    res.status(500).json({
      error: "Translation failed",
      details: err.response?.data || err.message
    });
  }
});

module.exports=router;
