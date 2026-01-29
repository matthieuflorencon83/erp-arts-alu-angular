import fs from 'fs';
import csv from 'csv-parser';
import db from './src/config/knex.js';

/**
 * Import Strategy:
 * 1. Read CSV row.
 * 2. Get/Create Supplier (fournisseur).
 * 3. Create/Update Article (article).
 * 4. Create/Update Link (article_fournisseur).
 * 5. Add Price History (prix_article).
 */

const RESULTS = {
    articles: { created: 0, updated: 0 },
    suppliers: { created: 0, existing: 0 },
    units: { created: 0, existing: 0 },
    links: { created: 0, updated: 0 },
    errors: 0
};

async function importCatalog() {
    console.log('🚀 Starting Full Catalog Import...');
    const rows = [];
    fs.createReadStream('import_source.csv')
        .pipe(csv({ separator: ';' }))
        .on('data', (data) => rows.push(data))
        .on('end', async () => {
            console.log(`📊 Processing ${rows.length} rows...`);
            await processRows(rows);
        });
}

function cleanPrice(val) {
    if (!val) return 0;
    return parseFloat(val.replace(',', '.').replace(/[^\d.-]/g, '')) || 0;
}

function cleanBoolean(val) {
    return (val && val.toLowerCase() === 'oui') ? 1 : 0;
}

function generateCode(name, prefix) {
    // Simple code generation: PREFIX-XXXX (random/hash or slug)
    // For Suppliers: FRN-NAME-123
    const slug = name.replace(/[^a-zA-Z0-9]/g, '').toUpperCase().substring(0, 6);
    return `${prefix}-${slug}-${Math.floor(Math.random() * 1000)}`;
}

async function processRows(rows) {
    const suppliersCache = new Map(); // Name -> Code
    const unitsCache = new Set();

    // Pre-load units
    const existingUnits = await db('unite').pluck('code');
    existingUnits.forEach(u => unitsCache.add(u));

    try {
        await db.transaction(async (trx) => {

            for (const row of rows) {
                const nomFournisseur = row['Fournisseur'];
                const refArticle = row['Ref fournisseur']; // Use as code_art if available
                const designation = row['Désignation'];
                let uniteCsv = row['Unité Qte']; // e.g. "UN", "ML"

                if (!nomFournisseur || !designation) {
                    // console.log('Skipping invalid row:', row);
                    continue;
                }

                // --- 1. SUPPLIER ---
                let codeFou = suppliersCache.get(nomFournisseur);
                if (!codeFou) {
                    const existingFou = await trx('fournisseur')
                        .where('nom_client', nomFournisseur)
                        .orWhere('nom_court', nomFournisseur)
                        .first();

                    if (existingFou) {
                        codeFou = existingFou.code_fou;
                        RESULTS.suppliers.existing++;
                    } else {
                        codeFou = generateCode(nomFournisseur, 'FRN');
                        await trx('fournisseur').insert({
                            code_fou: codeFou,
                            nom_client: nomFournisseur,
                            nom_court: nomFournisseur,
                            type: 'IMPORT'
                        });
                        RESULTS.suppliers.created++;
                    }
                    suppliersCache.set(nomFournisseur, codeFou);
                }

                // --- 1.5 UNIT ---
                // Handle "UN" vs "U" mapping manually if preferred, or just create "UN"
                // Let's create what's in CSV to be safe
                if (uniteCsv) {
                    if (!unitsCache.has(uniteCsv)) {
                        // Create it
                        await trx('unite').insert({
                            code: uniteCsv,
                            unite_1: uniteCsv // Generic label
                        });
                        unitsCache.add(uniteCsv);
                        RESULTS.units.created++;
                    }
                } else {
                    uniteCsv = null; // No unit
                }

                // --- 2. ARTICLE ---
                // If ref is empty, generate one? No, ref is critical.
                const codeArt = refArticle && refArticle.trim() !== '' ? refArticle : generateCode(designation, 'ART');

                const articleData = {
                    code_art: codeArt,
                    designation: designation,
                    famille: row['Famille'] || null,
                    ssfamille: row['Sous famille'] || null,
                    type: null, // Not in CSV directly ?
                    Fabricant: row['Fabricant'] || null,
                    tenu_en_stock: cleanBoolean(row['tenu en stock']),
                    Conditionnement: row['Conditionnement'] || null,
                    unite: uniteCsv
                    // dimension: row['Multiple cde'] // Maybe?
                };

                // Check existence
                const existingArt = await trx('article').where('code_art', codeArt).first();
                if (existingArt) {
                    await trx('article').where('code_art', codeArt).update(articleData);
                    RESULTS.articles.updated++;
                } else {
                    await trx('article').insert(articleData);
                    RESULTS.articles.created++;
                }

                // --- 3. LINK (Article_Fournisseur) ---
                const prix = cleanPrice(row['Prix/U HT']);

                const linkData = {
                    code_art: codeArt,
                    code_fou: codeFou,
                    prix_u_ht: prix,
                    code_art_fou: row['Ref fournisseur'] || codeArt, // Often same
                    Multiple_cde: row['Multiple cde'] || null
                };

                // Using raw query for "INSERT ... ON DUPLICATE KEY UPDATE" or just check/update
                const existingLink = await trx('article_fournisseur')
                    .where({ code_art: codeArt, code_fou: codeFou })
                    .first();

                if (existingLink) {
                    await trx('article_fournisseur')
                        .where({ code_art: codeArt, code_fou: codeFou })
                        .update(linkData);
                    RESULTS.links.updated++;
                } else {
                    await trx('article_fournisseur').insert(linkData);
                    RESULTS.links.created++;
                }

                // --- 4. PRICE HISTORY ---
                if (prix > 0) {
                    await trx('prix_article').insert({
                        code_art: codeArt,
                        prix_u_ht: prix,
                        date_saisie: new Date(),
                        date_validite: new Date(), // Just now
                        commentaire: 'Import Initial'
                    });
                }
            }
        });
    } catch (err) {
        console.error('TRANSACTION ERROR:', err);
    } finally {
        console.log('✅ Full Import Complete');
        console.log(RESULTS);
        await db.destroy();
    }
}

importCatalog();
