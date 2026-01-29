import express from 'express';
import { searchController } from './controllers/SearchController.js';

const router = express.Router();

router.get('/', (req, res) => searchController.search(req, res));

export default router;
