import { drizzle } from 'drizzle-orm/neon-http';
import { neon } from '@neondatabase/serverless';
import * as schema from './schema';

// Using environment variable for the database URL
const sql = neon(process.env.DATABASE_URL!);

// Create db instance with query builder
export const db = drizzle(sql, { schema });

// Helper function to get the database URL based on environment
export function getDatabaseUrl() {
  const url = process.env.DATABASE_URL;
  if (!url) {
    throw new Error('DATABASE_URL environment variable is not set');
  }
  return url;
}

// Export schema for use in other files
export { schema }; 