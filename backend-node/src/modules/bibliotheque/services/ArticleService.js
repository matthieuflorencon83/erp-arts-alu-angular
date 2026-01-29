import db from '../../../config/knex.js';

/**
 * Service: Article
 * Handles Article Repository with standard MySQL schema
 */
class ArticleService {

    /**
     * List all articles with basic info
     */
    async getAllArticles() {
        // Subquery to get the cheapest supplier for each article
        const primarySupplier = db('article_fournisseur')
            .select('code_art', 'code_fou', 'prix_u_ht')
            .rowNumber('rn', ['code_art'], ['prix_u_ht']); // This implies Knex supports logic, but Knex doesn't have .rowNumber built-in like this.

        // Reverting to Raw Query for the subquery part as Knex builder for Window Functions is verbose
        // Reverting to Raw Query for the subquery part as Knex builder for Window Functions is verbose
        const subquery = db.select('code_art', 'code_fou', 'prix_u_ht')
            .from(function () {
                this.select('af.code_art', 'af.code_fou', 'af.prix_u_ht',
                    db.raw('ROW_NUMBER() OVER (PARTITION BY af.code_art ORDER BY (f.nom_court IS NOT NULL AND f.nom_court != "") DESC, af.prix_u_ht ASC) as rn'))
                    .from('article_fournisseur as af')
                    .leftJoin('fournisseur as f', 'af.code_fou', 'f.code_fou')
                    .as('ranked');
            })
            .where('rn', 1)
            .as('af');

        return db('article as a')
            .leftJoin('unite as u', 'a.unite', 'u.code')
            .leftJoin('image as i', 'a.id_image', 'i.id')
            .leftJoin(subquery, 'a.code_art', 'af.code_art')
            .leftJoin('fournisseur as f', 'af.code_fou', 'f.code_fou')
            .select(
                'a.code_art',
                'a.designation',
                'a.famille',
                'a.type',
                'a.tenu_en_stock',
                'u.unite_1 as libelle_unite',
                'i.chemin as image_url',
                'f.nom_court as fournisseur',
                'af.prix_u_ht as prix_unitaire',
                'a.poid as poids'
            );
    }

    /**
     * Get full article details
     */
    async getArticle(code_art) {
        const article = await db('article as a')
            .leftJoin('unite as u', 'a.unite', 'u.code')
            .leftJoin('image as i', 'a.id_image', 'i.id')
            .select(
                'a.*',
                'u.unite_1 as libelle_unite',
                'i.chemin as image_url',
                'a.poid as poids'
            )
            .where('a.code_art', code_art)
            .first();

        if (!article) return null;

        article.metadata = {}; // Placeholder

        // Retrieve Supplier prices
        const suppliers = await db('article_fournisseur as af')
            .leftJoin('fournisseur as f', 'af.code_fou', 'f.code_fou')
            .select('af.*', 'f.nom_court')
            .where('af.code_art', code_art);

        article.suppliers = suppliers;

        return article;
    }

    /**
     * Create a new article
     */
    async createArticle(data) {
        await db('article').insert(data);
        return this.getArticle(data.code_art);
    }
}

export default new ArticleService();
