
import knex from 'knex';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

// Handling __dirname in ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Initialiser dotenv avec le chemin correct vers le fichier .env racine
dotenv.config({ path: path.resolve(__dirname, '../../.env') });

const db = knex({
    client: 'mysql2',
    connection: {
        host: process.env.DB_HOST || 'localhost',
        user: process.env.DB_USER || 'root',
        password: process.env.DB_PASSWORD || '',
        database: process.env.DB_NAME || 'erp_arts_alu',
        port: process.env.DB_PORT || 3306
    },
    pool: { min: 2, max: 10 }
});

export default db;
