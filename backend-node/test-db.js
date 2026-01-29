
import db from './src/config/knex.js';

console.log('--- TEST LIAISON BASSE (Node <-> MySQL) ---');
console.log('Dialecte: mysql2 (supposé via knex config)');

async function testLowLevel() {
    try {
        console.log('Tentative de connexion...');
        await db.raw('SELECT 1');
        console.log('✅ SELECT 1 : SUCCÈS');
        console.log('Liaison Base de Données OK.');
        process.exit(0);
    } catch (error) {
        console.error('❌ ÉCHEC SELECT 1');
        console.error('Code Erreur:', error.code);
        console.error('Message:', error.message);
        process.exit(1);
    }
}

testLowLevel();
