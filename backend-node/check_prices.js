import db from './src/config/knex.js';

async function checkPrices() {
    try {
        console.log('--- Checking article_fournisseur ---');
        const exists = await db.schema.hasTable('article_fournisseur');
        console.log('Table exists:', exists);

        if (exists) {
            const columns = await db('article_fournisseur').columnInfo();
            console.log('Columns:', Object.keys(columns));

            const count = await db('article_fournisseur').count('* as c').first();
            console.log('Row count:', count.c);

            const sample = await db('article_fournisseur').select('*').limit(5);
            console.log('Sample Data:', sample);
        } else {
            console.log('Table article_fournisseur NOT FOUND in this DB.');

            // List all tables to be sure
            const tables = await db.raw('SHOW TABLES');
            console.log('Available Tables:', tables[0].map(t => Object.values(t)[0]));
        }

    } catch (err) {
        console.error('Error:', err);
    } finally {
        await db.destroy();
    }
}

checkPrices();
