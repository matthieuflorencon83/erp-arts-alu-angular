import { pythonService } from '../services/PythonService.js';

class CalculController {

    async optimize(req, res) {
        try {
            const { affaireId } = req.params;
            const payload = req.body;

            /* 
               Verification basique : on s'assure que le payload contient 'barres' et 'pieces'.
            */
            if (!payload.barres || !payload.pieces) {
                return res.status(400).json({ error: "Payload invalide : 'barres' et 'pieces' requis." });
            }

            console.log(`[CalculController] Optimisation demandée pour l'affaire ${affaireId || 'Unknown'}`);

            // Transformation du payload (Node Interface -> Python Interface)
            const pythonPayload = {
                stock_options: payload.barres.map(b => ({
                    ref: `Barre ${b.longueur}`,
                    len_mm: b.longueur
                })),
                cuts_mm: payload.pieces.flatMap(p => Array(p.quantite).fill(p.longueur)),
                saw_kerf: 4,
                scrap_end: 0
            };

            // Call Python Engine
            const result = await pythonService.optimize(pythonPayload);

            return res.json({
                success: true,
                source: 'python-engine',
                data: result
            });

        } catch (error) {
            console.error('[CalculController] Error:', error.message);
            return res.status(500).json({ error: error.message });
        }
    }

    async health(req, res) {
        const isAlive = await pythonService.checkHealth();
        res.json({ status: isAlive ? 'UP' : 'DOWN', service: 'python-engine' });
    }
}

export const calculController = new CalculController();
