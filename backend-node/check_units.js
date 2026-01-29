import db from './src/config/knex.js';

async function checkUnits() {
    try {
        const units = await db('unite').select('*');
        console.log('Units in DB:', units);
    } catch (e) {
        console.error(e);
    } finally {
        await db.destroy();
    }
}
checkUnits();
