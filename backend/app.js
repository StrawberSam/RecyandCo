import express from 'express';
import { userRoutes, authRoutes} from './routes/index.js';
const app = express();

// Utilisation des routes
app.use('/api/users', userRoutes);
app.use('/api/auth', authRoutes)

// Lancement serveur
app.listen(5000, () => {
  console.log('Serveur démarré sur le port 5000');
})
