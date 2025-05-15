import { serial, text, timestamp, integer, pgTable, doublePrecision, jsonb, varchar } from 'drizzle-orm/pg-core';
import { sql } from 'drizzle-orm';

export const locations = pgTable('locations', {
  id: serial('id').primaryKey(),
  name: varchar('name', { length: 255 }).notNull(),
  youtubeStreamId: varchar('youtube_stream_id', { length: 255 }),
  createdAt: timestamp('created_at').defaultNow()
});

export const sensors = pgTable('sensors', {
  id: serial('id').primaryKey(),
  locationId: integer('location_id').references(() => locations.id),
  name: varchar('name', { length: 255 }).notNull(),
  type: varchar('type', { length: 50 }).notNull(),
  unit: varchar('unit', { length: 50 }),
  createdAt: timestamp('created_at').defaultNow()
});

export const sensorData = pgTable('sensor_data', {
  id: serial('id').primaryKey(),
  sensorId: integer('sensor_id').references(() => sensors.id),
  value: doublePrecision('value').notNull(),
  timestamp: timestamp('timestamp').defaultNow()
});

export const acquisitionSessions = pgTable('acquisition_sessions', {
  id: serial('id').primaryKey(),
  locationId: integer('location_id').references(() => locations.id),
  startTime: timestamp('start_time').defaultNow(),
  endTime: timestamp('end_time'),
  numDataPoints: integer('num_data_points').notNull(),
  status: varchar('status', { length: 50 }).default('active')
});

export const acquisitionData = pgTable('acquisition_data', {
  id: serial('id').primaryKey(),
  sessionId: integer('session_id').references(() => acquisitionSessions.id),
  sensorId: integer('sensor_id').references(() => sensors.id),
  dataPoints: jsonb('data_points').notNull(), // Array of {timestamp, value}
  analysisResults: jsonb('analysis_results'), // Store FFT, mean, std, etc.
  createdAt: timestamp('created_at').defaultNow()
});

export const ballMillPositions = pgTable('ball_mill_positions', {
  id: serial('id').primaryKey(),
  locationId: integer('location_id').references(() => locations.id),
  x: doublePrecision('x').notNull(),
  y: doublePrecision('y').notNull(),
  z: doublePrecision('z').notNull(),
  timestamp: timestamp('timestamp').defaultNow()
}); 