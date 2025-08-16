
const express = require('express');

const { translate } = require('bing-translate-api');
const router = express.Router();




const BING_LANGUAGES = {
  "af": "Afrikaans", "am": "Amharic", "ar": "Arabic", "as": "Assamese", "az": "Azerbaijani",
  "ba": "Bashkir", "be": "Belarusian", "bg": "Bulgarian", "bho": "Bhojpuri", "bn": "Bangla",
  "bo": "Tibetan", "brx": "Bodo", "bs": "Bosnian", "ca": "Catalan", "cs": "Czech",
  "cy": "Welsh", "da": "Danish", "de": "German", "doi": "Dogri", "dsb": "Lower Sorbian",
  "dv": "Divehi", "el": "Greek", "en": "English", "es": "Spanish", "et": "Estonian",
  "eu": "Basque", "fa": "Persian", "fi": "Finnish", "fil": "Filipino", "fj": "Fijian",
  "fo": "Faroese", "fr": "French", "fr-CA": "French (Canada)", "ga": "Irish",
  "gl": "Galician", "gom": "Konkani", "gu": "Gujarati", "ha": "Hausa", "he": "Hebrew",
  "hi": "Hindi", "hne": "Chhattisgarhi", "hr": "Croatian", "hsb": "Upper Sorbian",
  "ht": "Haitian Creole", "hu": "Hungarian", "hy": "Armenian", "id": "Indonesian",
  "ig": "Igbo", "ikt": "Inuinnaqtun", "is": "Icelandic", "it": "Italian", "iu": "Inuktitut",
  "iu-Latn": "Inuktitut (Latin)", "ja": "Japanese", "ka": "Georgian", "kk": "Kazakh",
  "km": "Khmer", "kmr": "Kurdish (Northern)", "kn": "Kannada", "ko": "Korean", "ks": "Kashmiri",
  "ku": "Kurdish (Central)", "ky": "Kyrgyz", "lb": "Luxembourgish", "ln": "Lingala",
  "lo": "Lao", "lt": "Lithuanian", "lug": "Ganda", "lv": "Latvian",
  "lzh": "Chinese (Literary)", "mai": "Maithili", "mg": "Malagasy", "mi": "Māori",
  "mk": "Macedonian", "ml": "Malayalam", "mn-Cyrl": "Mongolian (Cyrillic)",
  "mn-Mong": "Mongolian (Traditional)", "mni": "Manipuri", "mr": "Marathi", "ms": "Malay",
  "mt": "Maltese", "mww": "Hmong Daw", "my": "Myanmar (Burmese)", "nb": "Norwegian",
  "ne": "Nepali", "nl": "Dutch", "nso": "Sesotho sa Leboa", "nya": "Nyanja", "or": "Odia",
  "otq": "Querétaro Otomi", "pa": "Punjabi", "pl": "Polish", "prs": "Dari", "ps": "Pashto",
  "pt": "Portuguese (Brazil)", "pt-PT": "Portuguese (Portugal)", "ro": "Romanian",
  "ru": "Russian", "run": "Rundi", "rw": "Kinyarwanda", "sd": "Sindhi", "si": "Sinhala",
  "sk": "Slovak", "sl": "Slovenian", "sm": "Samoan", "sn": "Shona", "so": "Somali",
  "sq": "Albanian", "sr-Cyrl": "Serbian (Cyrillic)", "sr-Latn": "Serbian (Latin)",
  "st": "Sesotho", "sv": "Swedish", "sw": "Swahili", "ta": "Tamil", "te": "Telugu",
  "th": "Thai", "ti": "Tigrinya", "tk": "Turkmen", "tlh-Latn": "Klingon (Latin)",
  "tlh-Piqd": "Klingon (pIqaD)", "tn": "Setswana", "to": "Tongan", "tr": "Turkish",
  "tt": "Tatar", "ty": "Tahitian", "ug": "Uyghur", "uk": "Ukrainian", "ur": "Urdu",
  "uz": "Uzbek (Latin)", "vi": "Vietnamese", "xh": "Xhosa", "yo": "Yoruba",
  "yua": "Yucatec Maya", "yue": "Cantonese (Traditional)", "zh-Hans": "Chinese Simplified",
  "zh-Hant": "Chinese Traditional", "zu": "Zulu"
};

// Translate endpoint
router.post('/', async (req, res) => {
  let { text, from, to } = req.body;

  if (!text) {
    return res.status(400).json({ error: "Text is required" });
  }

  // If target not provided, pick a random supported language
  if (!to) {
    const keys = Object.keys(BING_LANGUAGES);
    to = keys[Math.floor(Math.random() * keys.length)];
  }

  // Validate target
  if (!Object.keys(BING_LANGUAGES).includes(to)) {
    return res.status(400).json({
      error: "Invalid target language",
      supportedLanguages: BING_LANGUAGES
    });
  }
translate(text, from, to)
    .then(result => {
      res.status(200).json({ translated:result.translation });
    })
    .catch(error => {
      console.error('Translation error:', error);
      res.status(500).json({ error: 'Translation failed' });
    });

});

module.exports = router;



/* require('dotenv').config();
 const axios = require('axios');

 const KEY = process.env.BING_KEY;
 const REGION = process.env.BING_REGION;
 const ENDPOINT =
   process.env.BING_ENDPOINT ||
   "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0";

   official api  later if needed
  const apiRes = await axios.post(
   `${ENDPOINT}&from=${from || ""}&to=${to}`,
   [{ Text: text }],
   {
     headers: {
       "Ocp-Apim-Subscription-Key": KEY,
       "Ocp-Apim-Subscription-Region": REGION,
       "Content-Type": "application/json; charset=UTF-8"
     }
   }

 res.json({
   from: from || "auto",
   to,
   translatedText: apiRes.data[0].translations[0].text,
   detectedLanguage: apiRes.data[0].detectedLanguage || null
     });
    */