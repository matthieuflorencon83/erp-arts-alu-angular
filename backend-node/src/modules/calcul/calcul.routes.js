import express from 'express';
import { calculController } from './controllers/CalculController.js';

const router = express.Router();

// Routes /api/calcul
// Routes /api/calcul
router.post('/optimize/:affaireId?', (req, res) => calculController.optimize(req, res));
router.get('/health', (req, res) => calculController.health(req, res));

export default router;
