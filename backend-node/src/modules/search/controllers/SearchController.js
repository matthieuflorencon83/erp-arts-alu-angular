import searchService from '../services/SearchService.js';

export const searchController = {
    async search(req, res) {
        try {
            const { q } = req.query;
            const results = await searchService.globalSearch(q);
            res.json({ success: true, results });
        } catch (error) {
            console.error('Search error:', error);
            res.status(500).json({ success: false, error: 'Search failed' });
        }
    }
};
