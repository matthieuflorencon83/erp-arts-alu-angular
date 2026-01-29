import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const router = express.Router();

// Path to images directory (absolute path from project root)
// Note: __dirname in ESM points to the controller directory
// We need to go up to project root: controllers -> bibliotheque -> modules -> src -> backend-node -> project root
const IMAGES_DIR = path.resolve(__dirname, '../../../../../installux_arcelor');

/**
 * GET /api/images/:filename
 * Serve product images
 */
router.get('/:filename', (req, res) => {
    const filename = req.params.filename;

    // Security: Only allow PNG files and prevent path traversal
    if (!filename.endsWith('.png') || filename.includes('..') || filename.includes('/') || filename.includes('\\\\')) {
        return res.status(400).json({ error: 'Invalid filename' });
    }

    const filePath = path.join(IMAGES_DIR, filename);

    // Check if file exists
    if (!fs.existsSync(filePath)) {
        return res.status(404).json({ error: 'Image not found' });
    }

    // Serve the image
    res.sendFile(filePath);
});

export default router;
