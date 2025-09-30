export default async function handler(req, res) {
  // 1️⃣ Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', 'https://exam.sanand.workers.dev'); // Your frontend
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  // 2️⃣ Handle preflight OPTIONS request
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // 3️⃣ Your API logic
  // Example response
  res.status(200).json({ message: '✅ CORS is working!' });
}
