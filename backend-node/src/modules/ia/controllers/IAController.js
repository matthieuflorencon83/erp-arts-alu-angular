import { iaService } from "../services/IAService.js";

class IAController {

    async analyze(req, res) {
        try {
            if (!req.file) {
                return res.status(400).json({ success: false, message: "No file uploaded." });
            }

            console.log(`[AI] Analyzing file: ${req.file.originalname} (${req.file.mimetype})`);

            const result = await iaService.analyzeDocument(req.file.buffer, req.file.mimetype);

            return res.json({
                success: true,
                message: "Analysis complete.",
                data: result
            });

        } catch (error) {
            console.error("Controller Error:", error);
            return res.status(500).json({ success: false, message: error.message });
        }
    }
}

export const iaController = new IAController();
