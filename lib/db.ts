import { drizzle } from 'drizzle-orm/neon-http'
import { neon } from '@neondatabase/serverless'
import * as schema from './schema'

if (!process.env.DATABASE_URL) {
  throw new Error('DATABASE_URL is not set')
}

const sql = neon(process.env.DATABASE_URL!)
export const db = drizzle(sql, { schema })

// Helper function to handle database errors
export function handleDatabaseError(error: unknown): never {
  console.error('Database error:', error)
  if (error instanceof Error) {
    throw new Error(`Database operation failed: ${error.message}`)
  }
  throw new Error('An unknown database error occurred')
} 
