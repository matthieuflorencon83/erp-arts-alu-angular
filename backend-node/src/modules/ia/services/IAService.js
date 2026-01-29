import { GoogleGenerativeAI } from "@google/generative-ai";

class IAService {
    constructor() {
        if (!process.env.GOOGLE_API_KEY) {
            console.error("GOOGLE_API_KEY is missing in environment variables.");
        }
        this.genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);
        this.model = this.genAI.getGenerativeModel({ model: "gemini-1.5-flash" });
    }

    /**
     * Converts a file buffer to the format expected by Gemini.
     */
    fileToGenerativePart(buffer, mimeType) {
        return {
            inlineData: {
                data: buffer.toString("base64"),
                mimeType
            },
        };
    }

    /**
     * Analyzes a document (PDF or Image) and extracts structured data.
     * @param {Buffer} fileBuffer 
     * @param {string} mimeType 
     */
    async analyzeDocument(fileBuffer, mimeType) {
        try {
            const imagePart = this.fileToGenerativePart(fileBuffer, mimeType);

            const prompt = `
            You are an expert ERP Data Entry Clerk. Analyze the provided document (Order or Technical Drawing).
            Extract the following information in a strict JSON format:
            - client_name: The name of the client or company (string or null).
            - order_date: The date of the document in YYYY-MM-DD format (string or null).
            - order_reference: The document number or reference (string or null).
            - items: An array of detected items, where each item has:
                - reference: The product code or name (string).
                - description: Brief description (string).
                - quantity: number (integer).
                - dimensions: A string representing dimensions if found (e.g., "6500mm"), or null.
            
            Return ONLY the JSON. Do not include markdown formatting like \`\`\`json.
            `;

            const result = await this.model.generateContent([prompt, imagePart]);
            const response = await result.response;
            const text = response.text();

            // Clean up potentially persistent markdown
            const cleanText = text.replace(/```json/g, "").replace(/```/g, "").trim();

            return JSON.parse(cleanText);

        } catch (error) {
            console.error("AI Analysis Failed:", error);
            throw new Error("Failed to analyze document with AI.");
        }
    }
}

export const iaService = new IAService();
