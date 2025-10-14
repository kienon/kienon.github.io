import express from "express";
import fetch from "node-fetch";

const app = express();
app.use(express.json({ limit: "10mb" }));

// Target = Google Apps Script webhook kau
const TARGET_URL = "https://script.google.com/macros/s/AKfycbw0PldrQad37vGqpicexWgrOqCIKrvFr5zjsX6NFCjX3xpIyMaOLKjP6YGoApojVE7SCg/exec";

// Handle POST request (from your GitHub site)
app.post("/", async (req, res) => {
  try {
    const response = await fetch(TARGET_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req.body)
    });

    const text = await response.text();
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.type("json").send(text);
  } catch (err) {
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.status(500).json({ error: err.message });
  }
});

// Handle OPTIONS (CORS preflight)
app.options("/", (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.status(204).end();
});

const PORT = process.env.PORT || 10000;
app.listen(PORT, () => console.log("✅ PRAN Proxy running on port " + PORT));
