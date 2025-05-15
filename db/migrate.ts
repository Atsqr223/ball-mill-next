import { drizzle } from 'drizzle-orm/neon-http';
import { migrate } from 'drizzle-orm/neon-http/migrator';
import { neon } from '@neondatabase/serverless';
import { getDatabaseUrl } from './index';

async function runMigration() {
  const sql = neon(getDatabaseUrl());
  const db = drizzle(sql);

  console.log('Running migrations...');
  
  await migrate(db, { migrationsFolder: 'drizzle' });
  
  console.log('Migrations completed!');
  
  process.exit(0);
}

runMigration().catch((err) => {
  console.error('Migration failed!', err);
  process.exit(1);
}); 