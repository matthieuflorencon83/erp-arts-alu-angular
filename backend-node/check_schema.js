import db from './src/config/knex.js';

async function checkSchema() {
    try {
        console.log('--- Schema Inspection ---');
        const tables = ['article', 'article_fournisseur', 'prix_article', 'unite', 'fournisseur'];

        for (const table of tables) {
            console.log(`\nTABLE: ${table}`);
            const columns = await db(table).columnInfo();
            console.log(JSON.stringify(columns, null, 2));
        }

    } catch (err) {
        console.error('Error:', err);
    } finally {
        await db.destroy();
    }
}

checkSchema();
