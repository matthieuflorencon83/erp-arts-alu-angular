import db from '../../../config/knex.js';

class SearchService {
    async globalSearch(query) {
        if (!query || query.length < 2) return [];

        const searchTerm = `%${query}%`;

        // Parallel queries
        const [articles, clients, commandes] = await Promise.all([
            // 1. Articles
            db('articles')
                .select('code_art as id', 'designation as label')
                .where('code_art', 'like', searchTerm)
                .orWhere('designation', 'like', searchTerm)
                .limit(5)
                .then(rows => rows.map(r => ({ ...r, type: 'article' }))),

            // 2. Clients (Tiers)
            db('clients')
                .select('code_cli as id', 'nom_client as label')
                .where('code_cli', 'like', searchTerm)
                .orWhere('nom_client', 'like', searchTerm)
                .limit(5)
                .then(rows => rows.map(r => ({ ...r, type: 'client' }))),

            // 3. Commandes
            db('commandes')
                .select('num_oa as id', 'designation as label')
                .where('num_oa', 'like', searchTerm)
                .orWhere('designation', 'like', searchTerm)
                .limit(5)
                .then(rows => rows.map(r => ({ ...r, type: 'order' })))
        ]);

        return [...articles, ...clients, ...commandes];
    }
}

export default new SearchService();
