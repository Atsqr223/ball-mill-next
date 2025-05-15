import { pgTable, serial, varchar, timestamp, integer, doublePrecision, jsonb, index, uniqueIndex } from 'drizzle-orm/pg-core'

export const locations = pgTable('locations', {
  id: serial('id').primaryKey(),
  name: varchar('name', { length: 255 }).notNull(),
  youtubeStreamId: varchar('youtube_stream_id', { length: 255 }),
  status: varchar('status', { length: 50 }).notNull().default('active'),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
})

export const sensors = pgTable('sensors', {
  id: serial('id').primaryKey(),
  name: varchar('name', { length: 255 }).notNull(),
  type: varchar('type', { length: 50 }).notNull(),
  locationId: integer('location_id').references(() => locations.id).notNull(),
  status: varchar('status', { length: 50 }).notNull().default('active'),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
}, (table) => ({
  locationIdx: index('sensors_location_idx').on(table.locationId),
  typeIdx: index('sensors_type_idx').on(table.type),
  nameLocationIdx: uniqueIndex('sensors_name_location_idx').on(table.name, table.locationId),
}))

export const acquisitionSessions = pgTable('acquisition_sessions', {
  id: serial('id').primaryKey(),
  locationId: integer('location_id').references(() => locations.id).notNull(),
  sensorId: integer('sensor_id').references(() => sensors.id).notNull(),
  status: varchar('status', { length: 50 }).notNull().default('in_progress'),
  fileName: varchar('file_name', { length: 255 }),
  startTime: timestamp('start_time').notNull(),
  endTime: timestamp('end_time'),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
}, (table) => ({
  locationIdx: index('acquisition_sessions_location_idx').on(table.locationId),
  sensorIdx: index('acquisition_sessions_sensor_idx').on(table.sensorId),
  statusIdx: index('acquisition_sessions_status_idx').on(table.status),
}))

export const sensorData = pgTable('sensor_data', {
  id: serial('id').primaryKey(),
  sessionId: integer('session_id').references(() => acquisitionSessions.id).notNull(),
  sensorId: integer('sensor_id').references(() => sensors.id).notNull(),
  value: integer('value').notNull(),
  timestamp: timestamp('timestamp').notNull(),
  createdAt: timestamp('created_at').defaultNow(),
}, (table) => ({
  sessionIdx: index('sensor_data_session_idx').on(table.sessionId),
  sensorIdx: index('sensor_data_sensor_idx').on(table.sensorId),
  timestampIdx: index('sensor_data_timestamp_idx').on(table.timestamp),
}))

export const ballMillPositions = pgTable('ball_mill_positions', {
  id: serial('id').primaryKey(),
  locationId: integer('location_id').notNull(),
  x: doublePrecision('x').notNull(),
  y: doublePrecision('y').notNull(),
  z: doublePrecision('z').notNull(),
  timestamp: timestamp('timestamp').defaultNow(),
  createdAt: timestamp('created_at').defaultNow(),
}, (table) => ({
  locationIdx: index('ball_mill_positions_location_idx').on(table.locationId),
  timestampIdx: index('ball_mill_positions_timestamp_idx').on(table.timestamp),
})) 
