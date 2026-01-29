import axios from 'axios';
import process from 'process';

class PythonService {
    constructor() {
        this.baseUrl = process.env.PYTHON_API_URL || 'http://127.0.0.1:8000';
    }

    /**
     * Envoie une requête d'optimisation au moteur Python.
     * @param {Object} payload - Les données de l'affaire et des barres.
     * @returns {Promise<Object>} - Le résultat de l'optimisation.
     */
    async optimize(payload) {
        try {
            console.log(`[PythonService] Sending optimization request to ${this.baseUrl}/optimize...`);
            const response = await axios.post(`${this.baseUrl}/optimize`, payload, {
                timeout: 300000 // 5 minutes timeout for heavy calculations
            });
            console.log('[PythonService] Optimization successful.');
            return response.data;
        } catch (error) {
            console.error('[PythonService] Error communicating with Python engine:', error.message);
            if (error.code === 'ECONNREFUSED') {
                throw new Error('Le moteur de calcul Python semble éteint (Port 8000 inaccessible).');
            }
            throw new Error(`Erreur lors du calcul: ${error.message}`);
        }
    }

    /**
     * Vérifie la santé du moteur Python.
     */
    async checkHealth() {
        try {
            const response = await axios.get(`${this.baseUrl}/health`);
            return response.status === 200;
        } catch (error) {
            return false;
        }
    }
}

export const pythonService = new PythonService();
