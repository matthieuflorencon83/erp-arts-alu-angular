import fs from 'fs';
import csv from 'csv-parser';
import db from './src/config/knex.js';

const RESULTS = {
    updated: 0,
    notFound: 0,
    errors: 0
};

async function importPrices() {
    console.log('🚀 Starting Price Import...');

    const rows = [];

    // 1. Read CSV
    fs.createReadStream('import_source.csv')
        .pipe(csv({ separator: ';' }))
        .on('data', (data) => rows.push(data))
        .on('end', async () => {
            console.log(`📊 Found ${rows.length} rows in CSV.`);
            await processRows(rows);
        });
}

async function processRows(rows) {
    try {
        for (const row of rows) {
            const refFournisseur = row['Ref fournisseur'];
            const designation = row['Désignation'];
            const rawPrice = row['Prix/U HT'];
            const nomFournisseur = row['Fournisseur'];

            // Clean price (replace ',' with '.' and remove currency symbols if any)
            const price = parseFloat(rawPrice?.replace(',', '.').replace(/[^\d.]/g, ''));

            if (!refFournisseur || isNaN(price)) {
                continue;
            }

            // 2. Find Article by 'ref_fournisseur' OR 'designation' if needed
            // Strategy: Search in article_fournisseur via ref_fournisseur
            // OR search in article via ref_fabricant (if same as ref_fournisseur)

            // Try to match in article_fournisseur first
            // We need to resolve Supplier ID from Name first?
            // "ACDIS" -> "FRN-ACDIS..."

            // Step 2a: Get Supplier ID
            const supplier = await db('fournisseur')
                .where('nom_court', nomFournisseur)
                .orWhere('nom_client', nomFournisseur)
                .first();

            if (!supplier) {
                // console.log(`⚠️ Supplier not found: ${nomFournisseur}`);
                RESULTS.notFound++;
                continue;
            }

            // Step 2b: Update or Insert into article_fournisseur
            // We need the article ID (code_art).
            // Let's assume 'Ref fournisseur' matches 'code_art' OR we search by Designation/Ref

            // Try matching article by Ref
            let article = await db('article').where('code_art', refFournisseur).first();

            if (!article) {
                // Try matching by Designation (fuzzy)
                article = await db('article').where('designation', designation).first();
            }

            if (article) {
                const code_art = article.code_art;
                const code_fou = supplier.code_fou;

                // Check if link exists
                const existingLink = await db('article_fournisseur')
                    .where({ code_art, code_fou })
                    .first();

                if (existingLink) {
                    await db('article_fournisseur')
                        .where({ id: existingLink.id })
                        .update({ prix: price });
                    RESULTS.updated++;
                } else {
                    // Create link
                    await db('article_fournisseur').insert({
                        code_art,
                        code_fou,
                        prix: price,
                        reference_fournisseur: refFournisseur
                    });
                    RESULTS.updated++;
                }
            } else {
                RESULTS.notFound++;
            }
        }
    } catch (err) {
        console.error('Fatal Error:', err);
    } finally {
        console.log('✅ Import Complete');
        console.log(RESULTS);
        await db.destroy();
    }
}

importPrices();
