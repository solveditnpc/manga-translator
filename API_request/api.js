require('dotenv').config();  // install dotenv using npm install dotenv
const express = require('express');  // install express using npm install express
const app = express();
app.use(express.json());
const port = 3000;
const { GoogleGenerativeAI } = require('@google/generative-ai');  // install @google/generative-ai using npm install @google/generative-ai
const genAI = new GoogleGenerativeAI(process.env.API_KEY);   // import your key here which you will generate from ai.google.dev



app.post("/translate", async(req, res) => {
    try {
        const { text, targetLanguage } = req.body;
        if(!text || !targetLanguage) res.status(404).json({ message : "Enter the text" });
        const model = genAI.getGenerativeModel({ model : "gemini-2.5-pro" });
        const prompt = `
        Translate the following text to ${targetLanguage}:
        """
        ${text}
        """


        Strictly follow these rules : 
        1.Output only the raw translation ONLY
        2.Output should be what asked only nothing else
        3.No commas or any other symbol unless given in my original text`
        const result = await model.generateContent(prompt);
        const response = await result.response;
        const translatedText = response.text().trim();
        res.status(200).json({ translation : translatedText });
    } catch(error) {
        console.error("🚨 Full Error:", {
            message: error.message,
            stack: error.stack,
            requestBody: req.body
        });
        res.status(500).json({ message : "Server error" });
    }
});

app.listen(port,() => {
    console.log(`server is working on port ${port}`);
});