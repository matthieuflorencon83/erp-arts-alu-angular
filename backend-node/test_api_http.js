
import http from 'http';

const options = {
    hostname: 'localhost',
    port: 3000,
    path: '/api/bibliotheque/articles',
    method: 'GET',
};

const req = http.request(options, (res) => {
    console.log(`STATUS: ${res.statusCode}`);
    let data = '';

    res.on('data', (chunk) => {
        data += chunk;
    });

    res.on('end', () => {
        console.log('Response Body (truncated):', data.substring(0, 200));
        if (res.statusCode === 200) {
            console.log('API is working!');
        } else {
            console.log('API failed.');
        }
    });
});

req.on('error', (e) => {
    console.error(`problem with request: ${e.message}`);
});

req.end();
