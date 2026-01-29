import axios from 'axios';

const payload = {
    barres: [{ id: 1, longueur: 6000, quantite: 10 }],
    pieces: [{ id: 101, longueur: 1500, quantite: 3 }]
};

async function test() {
    try {
        console.log('Testing Bridge (Node -> Python)...');
        const res = await axios.post('http://localhost:3000/api/calcul/optimize', payload);
        console.log('✅ Success:', JSON.stringify(res.data, null, 2));
    } catch (err) {
        console.error('❌ Error:', err.message);
        if (err.response) {
            console.error('Status:', err.response.status);
            console.error('Data:', err.response.data);
        }
    }
}

test();
