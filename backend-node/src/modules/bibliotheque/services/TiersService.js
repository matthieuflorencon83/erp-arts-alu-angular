import db from '../../../config/knex.js';

/**
 * Service: Tiers (Clients & Fournisseurs)
 * Standard MySQL Schema
 */
class TiersService {

    // --- Clients ---

    async getAllClients() {
        // Schema: code_cli, nom_client, adresse, tel, mail, type...
        return db('client')
            .select('code_cli', 'nom_client', 'type', 'ville', 'tel');
    }

    async getAllClientsFull() {
        return db('client').select('*');
    }

    async getClient(code_cli) {
        return db('client')
            .where({ code_cli })
            .first();
    }

    async createClient(clientData) {
        await db('client').insert(clientData);
        return this.getClient(clientData.code_cli);
    }

    // --- Fournisseurs ---

    async getAllFournisseurs() {
        return db('fournisseur')
            .select('code_fou', 'nom_client', 'nom_court', 'type', 'tel');
    }

    async getFournisseur(code_fou) {
        return db('fournisseur')
            .where({ code_fou })
            .first();
    }

    async createFournisseur(fournisseurData) {
        await db('fournisseur').insert(fournisseurData);
        return this.getFournisseur(fournisseurData.code_fou);
    }
}

export default new TiersService();
