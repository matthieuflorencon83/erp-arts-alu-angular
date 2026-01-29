import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import bibliothequeRoutes from './src/modules/bibliotheque/routes.js';
import besoinRoutes from './src/modules/liste_besoin/routes.js';

import affaireRoutes from './src/modules/affaire/routes.js';
import commandeRoutes from './src/modules/commande/routes.js';
import searchRoutes from './src/modules/search/routes.js'; // NEW
import db from './src/config/knex.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Imports Modules
import { calculController } from './src/modules/calcul/controllers/CalculController.js';
import { iaController } from './src/modules/ia/controllers/IAController.js';
import multer from 'multer';

// Upload Config (Memory Storage for AI analysis)
const upload = multer({
    storage: multer.memoryStorage(),
    limits: { fileSize: 10 * 1024 * 1024 } // 10MB limit
});

// Routes
app.get('/health', (req, res) => {
    res.json({ status: 'ok', server: 'node-backend' });
});

/* --- API ROUTES --- */

// IA (Gemini)
app.post('/api/ia/analyze', upload.single('file'), (req, res) => iaController.analyze(req, res));

// Calcul
app.post('/api/calcul/optimize', (req, res) => calculController.optimize(req, res));
app.get('/api/calcul/health', (req, res) => calculController.checkHealth(req, res)); // NEW MODULE V2

app.use('/api/bibliotheque', bibliothequeRoutes);
app.use('/api/besoins', besoinRoutes);
// app.use('/api/optimize', optimizationRoutes); // DEPRECATED V1
app.use('/api/affaires', affaireRoutes);
app.use('/api/commandes', commandeRoutes);
app.use('/api/search', searchRoutes); // NEW

// Images
import imageController from './src/modules/bibliotheque/controllers/ImageController.js';
app.use('/api/images', imageController);


// Health Check
app.get('/db-health', async (req, res) => {
    try {
        await db.raw('SELECT 1');
        res.json({ status: 'OK', db: 'Connected' });
    } catch (err) {
        res.status(500).json({ status: 'ERROR', db: err.message });
    }
});

// Start Server
if (process.env.NODE_ENV !== 'test') {
    app.listen(PORT, () => {
        console.log(`✅ Server running on port ${PORT}`);
        console.log(`👉 Docs: http://localhost:${PORT}/api/bibliotheque/articles`);
    });
}

export default app;
